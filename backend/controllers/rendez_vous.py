from flask import request
from app import app
#from models.users import User_model
from middlewares.authentificate import authentificate_user
from models.rendez_vous import Rendez_vous_model
from middlewares.authentificate import authentificate_doctor
model=Rendez_vous_model()

#action de prendre un rendez-vous effectuer par un patient
@app.route('/prendre_rendez_vous',methods=['POST'])
@authentificate_user
def prendre_rendez_vous(current_user):
    date=request.form['date']
    heure=request.form['heure']
    motif=request.form['motif']
    doctor_id=request.form['doctor_id']
    #patient_id=request.form['patient_id']
    return model.prendre_rendez_vous(current_user,date,heure,motif,doctor_id)

#action pour afficher les rendez-vous acceptés d'un docteur
@app.route('/rendez_vous_accepter',methods=['GET'])
@authentificate_doctor
def rendez_vous_accepter(current_doctor):
    return model.rendez_vous_accepter(current_doctor)

#action pour afficher les rendez-vous en attente d'un docteur
@app.route('/rendez_vous_en_attente',methods=['GET'])
@authentificate_doctor
def rendez_vous_en_attente(current_doctor):
    return model.rendez_vous_en_attente(current_doctor)

#action pour terminer un rendez-vous par le docteur
@app.route('/rendez_vous_terminer',methods=['POST'])
@authentificate_doctor
def rendez_vous_terminer(current_doctor):
    return model.rendez_vous_terminer(current_doctor)

#action pour afficher les rendez-vous acceptés d'un patient
@app.route('/historique_rendez_vous_accepter',methods=['POST'])
@authentificate_user
def historique_rendez_vous_accepter(current_user):
    return model.historique_rendez_vous_accepter(current_user)

#action pour afficher les rendez-vous en cours d'un patient
@app.route('/historique_rendez_vous_en_cours',methods=['POST'])
@authentificate_user
def historique_rendez_vous_en_cours(current_user):
    return model.historique_rendez_vous_en_cours(current_user)