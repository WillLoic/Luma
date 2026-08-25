#from app import app
from flask import request,make_response
#from models.users import User_model
from models.config import db, ma
from time import sleep
#from models.doctor import Doctor

class Rendez_vous(db.Model):
    __tablename__='rendez_vous'

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    date_rv=db.Column(db.DateTime,nullable=False)
    heure_rv=db.Column(db.Time,nullable=False)
    motif=db.Column(db.String(200),nullable=False)
    statut=db.Column(db.Boolean,default=False)
    patient_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    doctor_id=db.Column(db.Integer,db.ForeignKey('doctor.id'),nullable=False)

    def __init__(self,date_rv,heure_rv,motif,patient_id,doctor_id):
        self.date_rv=date_rv
        self.heure_rv=heure_rv
        self.motif=motif
        self.patient_id=patient_id
        self.doctor_id=doctor_id

#serialisation des donnees
class Rendez_vousSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Rendez_vous

#serialisation d'un objet
rendez_vous_schema=Rendez_vousSchema()
#serialisation de plusieurs objets
rendez_vous_schema=Rendez_vousSchema(many=True)

#chargement des tables
#app_context()


class Rendez_vous_model:
    #patient
    def prendre_rendez_vous(self,current_user,date,heure,motif,doctor_id):
       rendez_vous=Rendez_vous(date,heure,motif,current_user.id,doctor_id)
       db.session.add(rendez_vous)
       db.session.commit()
       return make_response({'msg':'Rendez-vous pris avec succes'},200)
   
    """def get_all_rendez_vous(self,patient_id):
        all_rendez_vous=Rendez_vous.query.filter_by(patient_id=patient_id).all()
        return rendez_vous_schema.dump(all_rendez_vous)
    """
    #doctor
    def rendez_vous_accepter(self,current_doctor):
        all_rendez_vous=Rendez_vous.query.filter_by(doctor_id=current_doctor.id,statut=True).all()
        return rendez_vous_schema.dump(all_rendez_vous)
    #doctor
    def rendez_vous_en_attente(self,current_doctor):
        all_rendez_vous=Rendez_vous.query.filter_by(doctor_id=current_doctor.id,statut=False).all()
        return rendez_vous_schema.dump(all_rendez_vous)
    #patient
    def historique_rendez_vous_accepter(self,current_user):
        all_rendez_vous=Rendez_vous.query.filter_by(patient_id=current_user.id,statut=True).all()
        return rendez_vous_schema.dump(all_rendez_vous)
    #patient
    def historique_rendez_vous_en_cours(self,current_user):
        all_rendez_vous=Rendez_vous.query.filter_by(patient_id=current_user.id,statut=False).all()
        return rendez_vous_schema.dump(all_rendez_vous)
    #doctor
    def rendez_vous_terminer(self,current_doctor):
        id=request.json['id']
        rendez_vous=Rendez_vous.query.filter_by(id=id,doctor_id=current_doctor.id).first()
        if not rendez_vous:
            return make_response({'msg':'Rendez-vous non trouvé'},403)
        db.session.delete(rendez_vous)
        db.session.commit()
        return make_response({'msg':'Rendez-vous terminé avec succès'},200)
    
#NB faire une notification pour le patient lorsque le rendez-vous est accepté ou refusé par le docteur