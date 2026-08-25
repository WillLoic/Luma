from flask import make_response,request,session,current_app
from models.config import db,ma,mail
from models.doctor import Doctor,doctors_schema
#from app import app
from flask_mail import Message
import secrets, datetime, jwt
from datetime import datetime,timedelta

#creation de la table hopital
class Hopital(db.Model):
    __tablename__='hopital'

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    nom=db.Column(db.String(150),nullable=False)
    matricule=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False)
    lieu=db.Column(db.Text)
    tel=db.Column(db.String(15))
    services=db.relationship('Service',backref='hopital',lazy=True)
    code=db.Column(db.String(10))
    code_expired=db.Column(db.DateTime)
    hopital_actived=db.Column(db.Boolean)
    

    def __init__(self,nom,email,matricule,lieu,tel):
        self.nom=nom
        self.email=email
        self.matricule=matricule
        self.lieu=lieu
        self.tel=tel
        #self.services=services
class Service(db.Model):
    __tablename__='service'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    nom=db.Column(db.String(60))
    description=db.Column(db.Text)
    hopital_id=db.Column(db.Integer,db.ForeignKey('hopital.id'))
    doctor=db.relationship('Doctor',backref='service',lazy=True)

    """def __init__(self,hopital_id,nom,description):
        self.hopital_id=hopital_id
        self.nom=nom
        self.description=description"""

#chargement des tables
#app_context()

#serialisation des donnees
class HopitalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Hopital
class ServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Service

#serialisation de l'objet
hopital_schema=HopitalSchema()
service_schema=ServiceSchema
#serialisation de plusieurs objets
hopitals_schema=HopitalSchema(many=True)
services_schema=HopitalSchema(many=True)


class Hopital_model:
    def register_hopital(self,nom,email,matricule,lieu,tel):
        hopital=Hopital(nom,email,matricule,lieu,tel)
        def send_verification_email(nom,email,code):
            msg=Message('Bienvenue dans LUMA SANTE', recipients=[email])
            msg.body=f'Felicitation {nom} votre hopital a ete enregistre avec succes dans notre plateforme. Entrer le code ci-dessous pour confirmer votre inscription {code}!'
            #mail.send(msg)
        code=secrets.token_hex(3)
        send_verification_email(nom,email,code)
        hopital.code=code
        hopital.code_expired=datetime.datetime.now()+datetime.timedelta(minutes=15)
        hopital.hopital_actived=False
        db.session.add(hopital)
        db.session.commit()
        return make_response({'msg':'Successfully registered, check your email for the verification code'},200)
    
    def verification_code_hospital(self):
        id = request.json.get('id')
        code = request.json.get('code')
        hopital=Hopital.query.get(id)
        if hopital:
            if hopital.code_expired > datetime.datetime.now():
                if hopital.code==code:
                    hopital.hopital_actived=True
                    db.session.commit()
                    return make_response({'msg':'Hospital verified successfully'},200)
                else:
                    return make_response({'msg':'Invalid verification code'},401)
            else:
                hopital.code=secrets.token_hex(3)
                hopital.code_expired=datetime.datetime.now()+datetime.timedelta(minutes=15)
                db.session.commit()
                return make_response({'msg':'Verification code expired regenerate'},401)
        else:
            return make_response({'msg':'Hospital not found'},404)
        
    def regenerate_code_hospital(self):
        id = request.json.get('id')
        hopital=Hopital.query.get(id)
        if hopital:
            def send_verification_email(nom,email,code):
                msg=Message('Regeneration de code de verification', recipients=[email])
                msg.body=f'Felicitation {nom} votre code de verification a ete regenere. Entrer le code ci-dessous pour confirmer votre inscription {code}!'
                #mail.send(msg)
            code=secrets.token_hex(3)
            print(code)
            send_verification_email(hopital.nom,hopital.email,code)
            hopital.code=code
            hopital.code_expired=datetime.datetime.now()+datetime.timedelta(minutes=15)
            db.session.commit()
            return make_response({'msg':'New verification code sent to your email'},200)
        else:
            return make_response({'msg':'Hospital not found'},404)

    def login_hopital(self,matricule):
        hopital=Hopital.query.filter_by(matricule=matricule).first()
        if not hopital:
            return make_response({'msg':'Incorect matricule'},403)
        payloads={'matricule':hopital.matricule}#'exp':datetime.datetime.now()+datetime.timedelta(minutes=30)}
        token=jwt.encode(payloads,current_app.config['SECRET_KEY'],algorithm='HS256')
        return make_response({'Token':token})
    
    def add_service(self,current_hopital,nom,description):
        service=Service(hopital_id=current_hopital.id,nom=nom,description=description)
        db.session.add(service)
        db.session.commit()
        return make_response({'msg':'Nouveau service ajouter'},200)
    
    def add_doctor(self,current_hopital,nom,prenom,matricule,specialite,email,service_id):
        hopital=Hopital.query.get(current_hopital.id)
        service = Service.query.filter_by(id=service_id,hopital_id=current_hopital.id).first()
        if not hopital:
            return make_response({'msg','Hopital not found'},404)
        if not service:
            return make_response({'msg': 'Vous devez d\'abord ajouter un service correspondant au medecin'},403)
        doctor=Doctor(nom,prenom,matricule,specialite,email,current_hopital.id,service_id)
        db.session.add(doctor)
        def send_code_url(nom,email,hopital_nom,doctor_code,url):
            msg=Message('Bienvenue dans LUMA SANTE', recipients=[email])
            msg.body=f'Felicitation Dr.{nom} vous venez d\'etre ajouter en tant que medecin par {hopital_nom}. Votre code de validation : {doctor_code}! CLIQUEZ ICI : {url}'
            #mail.send(msg)
        doctor.code=secrets.token_hex(3)
        url=f"https://lumasante.com/verify_doctor?id={doctor.id}"
        send_code_url(doctor.nom,doctor.email,hopital.nom,doctor.code,url)
        doctor.code_expired=datetime.now() + timedelta(minutes=30)
        db.session.commit()
        return make_response({'msg':'Nouveau docteur ajouter en attente de sa validation'},200)
    
    def get_service(self, current_hopital):
        return services_schema.dump(current_hopital.services)
        
    def get_doctor(self,current_hopital):
        all_doctor=Doctor.query.filter_by(hopital_affilie=current_hopital.id).all()
        return doctors_schema.dump(all_doctor)
    
    def get_doctor_by_service(self,current_hopital):
        doctors=Doctor.query.filter_by(hopital_affilie=current_hopital.id).all()
        return doctors_schema.dump(doctors)
        
    def delete_service(self,current_hopital):
        id=request.json['id']
        service=Service.query.filter_by(hopital_id=current_hopital.id,id=id).first()
        if not service:
            return make_response({'msg':'Service absent'},403)
        db.session.delete(service)
        db.session.commit()
        return make_response({'msg':'Service supprimer avec succes'},200)
    
    def delete_doctor(self,current_hopital):
        id=request.json['id']
        doctor=Doctor.query.filter_by(hopital_affilie=current_hopital.id,id=id).first()
        if not doctor:
            return make_response({'msg':'Doctor absent'},403)
        db.session.delete(doctor)
        db.session.commit()
        return make_response({'msg':'Doctor supprimer avec succes'},200)
        pass
    
    
    
        
        
