from app import app
from models.doctor import Doctor_model
from flask import request
from middlewares.authentificate import authentificate_doctor
#from models.rendez_vous import Rendez_vous_model


model=Doctor_model()
@app.route('/verify_code',methods=['POST'])
def verify_code():
    return model.verify_code()

@app.route('/accepter_RV',methods=['POST'])
@authentificate_doctor
def accepter_RV(current_doctor):
    return model.accepter_RV(current_doctor)

@app.route('/refuser_RV',methods=['POST'])
@authentificate_doctor
def refuser_RV(current_doctor):
    return model.refuser_RV(current_doctor)

@app.route('/faire_consultation',methods=['POST'])
@authentificate_doctor
def register_consultation(current_doctor):
    from models.consultation import Consultation_model
    #email=request.form['email']
    #id=request.form['id_doctor']
    return Consultation_model().register_consultation(current_doctor)

"""@app.route('/add_notification',methods=['POST'])
@authentificate_doctor
def add_notification(current_doctor):
    from models.notification import Notification_model
    return Notification_model().add_notification(current_doctor)"""