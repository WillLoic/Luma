from flask import make_response,request,current_app
from models.config import db,ma
from models.hopital import Hopital
#from app import app
from models.rendez_vous import Rendez_vous
from datetime import datetime
import jwt

#creation de la table doctor
class Doctor(db.Model):
    __tablename__='doctor'

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    nom=db.Column(db.String(100),nullable=False)
    prenom=db.Column(db.String(50))
    matricule=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(60))
    specialite=db.Column(db.String(100),nullable=False)
    service_id=db.Column(db.Integer,db.ForeignKey('service.id'))
    hopital_affilie=db.Column(db.String(150),db.ForeignKey('hopital.id'),nullable=False)
    rendez_vous=db.Column(db.Boolean,default=False)
    code=db.Column(db.String(10))
    code_expired=db.Column(db.DateTime)
    doctor_actived=db.Column(db.Boolean,default=False)
    #nom_hopital=db.Column(db.ForeignKey('hopital.nom'),nullable=False)

     #fonction constructeur
    def __init__(self,nom,prenom,matricule,email,specialite,hopital_affilie,service_id):
        self.nom=nom
        self.prenom=prenom
        self.matricule=matricule
        self.email=email
        self.specialite=specialite
        self.hopital_affilie=hopital_affilie
        self.service_id=service_id

#chargement des tables
#app_context()

#serialisation des donnees
class DoctorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Doctor

#serialisation d'un objet
doctor_schema=DoctorSchema()
#serialisation de plusieurs objets
doctors_schema=DoctorSchema(many=True)

class Doctor_model:
    def verify_doctor(self):
        id=request.json['id']
        code=request.json['code']
        doctor=Doctor.query.get(id)
        if not doctor:
            return make_response({'msg':'Doctor not found'},404)
        hopital=Hopital.query.get(doctor.hopital_affilie)
        if not hopital :
            return make_response({'msg':'Hopital not found'},404)
        if code==doctor.code :
            if doctor.code_expired>datetime.now():
                doctor.doctor_actived=True
                db.session.commit()
                payloads={'matricule_hopital':hopital.matricule,'matricule_doctor':doctor.matricule}
                token=jwt.encode(payloads,current_app.config['SECRET_KEY'],algorithm='HS256')
                return make_response({'Token':token,'msg':'Verification terminer'},200)
            else:
                return make_response({'msg':'code expirer regenerer le'},403)
        else:
            return make_response({'msg':'mauvais code entrer'},403)
            
    def accepter_RV(self,current_doctor):
        id=request.json['id']
        rendez_vous=Rendez_vous.query.filter_by(id=id,doctor_id=current_doctor.id).first()
        if not rendez_vous:
            return make_response({'message':'Rendez-vous non trouvé'},403)
        rendez_vous.statut=True
        db.session.commit()
        #ajuter une notification ici pour informer le patient
        return make_response({'message':'Rendez-vous accepté avec succès'},200)
    def refuser_RV(self,current_doctor):
        id=request.json['id']
        rendez_vous=Rendez_vous.query.filter_by(id=id,doctor_id=current_doctor.id).first()
        if not rendez_vous:
            return make_response({'message':'Rendez-vous non trouvé'},403)
        db.session.delete(rendez_vous)
        db.session.commit()
        #ajuter une notification ici pour informer le patient
        return make_response({'message':'Rendez-vous refusé avec succès'},200)
    
   
        