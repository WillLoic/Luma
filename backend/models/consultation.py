#from app import app 
from flask import request,make_response,send_file
from models.config import db,ma,mail
from models.users import User
from models.doctor import Doctor
from models.hopital import Hopital
from models.notification import Notification
from datetime import datetime
from docxtpl import DocxTemplate
from docx2pdf import convert
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os,pythoncom,shutil,re
from io import BytesIO
pythoncom.CoInitialize()

#creation de la table consultation
class Consultation(db.Model):
    __tablename__='consultation'

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    id_patient=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    id_doctor=db.Column(db.Integer,db.ForeignKey('doctor.id'),nullable=False)
    hopital_name=db.Column(db.Integer,db.ForeignKey('hopital.id'),nullable=False)
    date_consultation=db.Column(db.DateTime,default=db.func.now(),nullable=False)
    date_recherche=db.Column(db.DateTime)
    #carnet_principal=db.Column(db.largeBinary(1024*1024),default=None)
    #carnet_tampon=db.Column(db.LargeBinary(1024*1024),default=None)
   
    def __init__(self,id_patient,id_doctor,hopital_name):
        self.id_patient=id_patient
        self.id_doctor=id_doctor
        self.hopital_name=hopital_name
        #self.carnet_principal=carnet_principal
        
#chargement des tables
#app_context()

#serialisation des donnees
class ConsultationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Consultation

#serialisation d'un objet
consultation_schema=ConsultationSchema()
#serialisation de plusieurs objets
consultations_schema=ConsultationSchema(many=True)
    
def donnees(**kwargs):
    message = ""
    for key, value in kwargs.items():
        if hasattr(value, '__iter__') and not isinstance(value, str):
            message += f"{key}:\n"
            for item in value:
                message += f" - {item}\n"
        else:
            message += f"{key}: {value}\n"
    return message
def recherche(path,date_debut_str,date_fin_str,output_path):
    #on recupere le pdf ou on veut effectuer la recherche
    reader=PdfReader(path)
    writer=PdfWriter()
    #on convertis les dates initialement en str pour date
    date_debut=datetime.strptime(date_debut_str,"%Y-%m-%d")
    date_fin=datetime.strptime(date_fin_str,"%Y-%m-%d")
    #on fixe le format de date utiliser lors de la recherche
    pattern_date = r"\d{4}\s*-\s*\d{2}\s*-\s*\d{2}"
    copie_en_cours=False
    #pour chaque page on du fichier on conserve les dates(qui sont en str) dans le dictionnaire dates_trouves et le contenu des pages
    for page in reader.pages:
        texte = page.extract_text()
        dates_trouves = re.findall(pattern_date, texte)
        if dates_trouves:
            #pour chaque date presente dans le dictionnaire on enleve les espaces blancs et on la transforme en date
            for date_str in dates_trouves:
                try:
                    date_str=date_str.replace(" ","")
                    dates_trouve=datetime.strptime(date_str,"%Y-%m-%d")
                    #si la date rechercher est das un intervalle de date valide on ajoute une page dans notre nouveau pdf
                    if dates_trouve>=date_debut and dates_trouve<=date_fin:
                        writer.add_page(page)
                        copie_en_cours=True
                        break
                    elif copie_en_cours and dates_trouve > date_fin:
                        # Nouvelle date > date_fin → on arrête de copier
                        copie_en_cours = False
                        break
                    
                except:
                    continue

        elif copie_en_cours:
            # Aucune date trouvée mais on est dans une consultation à copier
            writer.add_page(page)

        #si le nombre de page de notre nouveau pdf est > 0 on ecrit tout ce qui se trouvait entre l'intervale dans le nouveau fichier
    if len(writer.pages)>0:
        with open(output_path,'wb') as fichier:
            writer.write(fichier)
        print("Operation de recherche reussi")
        return True
        #return send_file(output_path,as_attachment=decision,download_name='Mon_carnet.pdf',mimetype='application/pdf')
    else:
        print("Aucune consultation trouver entre c'est dates ")
        return False
        #return make_response({'msg':'Aucune consultation trouver entre c\'est dates'},403)
            
    


class Consultation_model:
    def register_consultation(self,current_doctor):
        pythoncom.CoInitialize()
        data=request.get_json()
        user=User.query.filter_by(email=data.get('email')).first()
        doctor=Doctor.query.get(current_doctor.id)
        hopital=Hopital.query.get(doctor.hopital_affilie)
        
        if not user:
            return make_response({'msg':'Patient non trouve'},403)
        if not doctor:
            return make_response({'msg':'Docteur non trouve'},403)
        if not hopital:
            return make_response({'msg':'Hopital non trouve'},403)
        
        carnet=DocxTemplate('uploads/carnet_template.docx')
        carnet.render({
                'date':str(datetime.now().date()),
                'nom':user.nom,
                'prenom':user.prenom,
                'nom_medecin':doctor.nom,
                'specialite':doctor.specialite,
                'hopital':hopital.nom,
                'motif':data.get('motif',['Non specifie']),
                'symptome':data.get('symptomes',['Nom specifie']),
                'examen':data.get('examen_clinique',['Non specifie']),
                'diagnostic':data.get('diagnostic_suspecte',['Non specifie']),
                'examens_complementaires':data.get('examens_complementaires',['Aucun']),
                'traitement':data.get('traitement_prescrit',['Non specifie']),
                'recommandations':data.get('recommandations',['Aucune']),
                'observation':data.get('observations',['Aucune'])})
        carnet_path=f'uploads/carnet/carnet_{user.id}.docx'
        carnet.save(carnet_path)
        convert(carnet_path)
        os.remove(carnet_path)
        carnet_path_pdf=f'uploads/carnet/carnet_{user.id}.pdf'
        carnet_path_principal=f'uploads/carnet_principal/carnet_{user.id}.pdf'
        if user.carnet_principal==None:
            shutil.move(carnet_path_pdf,carnet_path_principal)
            with open(carnet_path_principal,'rb') as f:
                user.carnet_principal=f.read()
            consultation=Consultation(user.id,doctor.id,doctor.hopital_affilie)
            notification = Notification(id_doctor=doctor.id,id_patient=user.id,message=f"Une nouvelle consultation a été enregistrée par Dr. {doctor.nom}")
            db.session.add(notification)
            db.session.add(consultation)
            db.session.commit()
            pythoncom.CoUninitialize()
            return make_response({'msg':'Premiere Consultation enregistree avec succes'},200)
        else:
            merger=PdfMerger()
            merger.append(carnet_path_pdf)
            merger.append(carnet_path_principal)
            merger.write(f'uploads/carnet_principal/carnet_{user.id}.pdf')
            merger.close()
            os.remove(carnet_path_pdf)
            with open(carnet_path_principal,'rb') as f:
                user.carnet_principal=f.read()
            consultation=Consultation(user.id,doctor.id,doctor.hopital_affilie)
            notification = Notification(id_doctor=doctor.id,id_patient=user.id,message=f"Une nouvelle consultation a été enregistrée par Dr. {doctor.nom}")
            db.session.add(notification)
            db.session.add(consultation)
            db.session.commit()
            return make_response({'msg':'Consultation enregistree avec succes'},200)
        
    def telecharger(self,current_user):
        #user=User.query.get(id)
        if not current_user:
           return make_response({'msg':'Patient non trouve'},403)
        if current_user.carnet_principal != None:
            fichier=BytesIO(current_user.carnet_principal)
            return send_file(fichier,as_attachment=True,download_name=f'{current_user.nom}.pdf',mimetype='application/pdf')
        else:
            return make_response({'msg':'Vous devez faire une consultation avant de pouvoir telcharger un carnet'},401)

    
    def telecharger_carnet(self,current_user,date_debut,date_fin):
        #user=User.query.get(id)
        if not current_user:
           return make_response({'msg':'Patient non trouve'},403)
        recherche_path=f'uploads/carnet_principal/carnet_{current_user.id}.pdf'
        output_path=f'uploads/carnet_rechercher/carnet_recherche_{current_user.id}.pdf'
        if date_debut > date_fin:
            return make_response({'msg':'Date debut doit etre inferieur a date fin'},401)
        if not current_user.carnet_principal :
            return make_response({'msg':'Vous devez faire une consultation avant de pouvoir telcharger un carnet'},401)
        if recherche(recherche_path,date_debut,date_fin,output_path):
            return send_file(output_path,as_attachment=True,download_name='Mon_carnet.pdf',mimetype='application/pdf')  
        else:
            return make_response({'msg':'Aucune consultation trouver entre c\'est dates'},403)          
        

    def voir_carnet(self,current_user,date_debut,date_fin):
        #user=User.query.get(id)
        if not current_user:
            return make_response({'msg':'Patient non trouver'},403)
        recherche_path=f'uploads/carnet_principal/carnet_{current_user.id}.pdf'
        output_path=f'uploads/carnet_rechercher/carnet_recherche_{current_user.id}.pdf'
        if date_debut > date_fin:
            return make_response({'msg':'Date debut doit etre inferieur a date fin'},401)
        if not current_user.carnet_principal :
            return make_response({'msg':'Vous devez faire une consultation avant de pouvoir voir votre carnet'},401)
        if recherche(recherche_path,date_debut,date_fin,output_path):
            return send_file(output_path,as_attachment=False,download_name='Mon_carnet.pdf',mimetype='application/pdf')  
        else:
            return make_response({'msg':'Aucune consultation trouver entre c\'est dates'},403)          
        
    def voir_all_carnet(self,current_user):
        #user=User.query.get(id)
        if not current_user:
            return make_response({'msg':'Patient non trouver'},403)
        if not current_user.carnet_principal :
            return make_response({'msg':'Vous devez faire une consultation avant de pouvoir voir votre carnet'},401)
        fichier=BytesIO(current_user.carnet_principal)
        return send_file(fichier,as_attachment=False,download_name='Mon_carnet',mimetype='application/json')
       
    



    pythoncom.CoUninitialize()