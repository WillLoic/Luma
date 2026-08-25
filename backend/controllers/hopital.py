from flask import request,session,make_response
from app import app
from models.hopital import Hopital_model
from middlewares.authentificate import authentificate_hopital

model=Hopital_model()

@app.route('/verify_hopital_code',methods=['POST'])
def verify_hopital_code():
    #code=request.form['code']
    return model.verification_code_hospital()

@app.route('/regenerate_hopital_code',methods=['POST'])
def regenerate_hopital_code():
    return model.regenerate_code_hospital()


@app.route('/register_hopital',methods=['POST'])
def register_hopital():
    nom=request.form['nom']
    email=request.form['email']
    matricule=request.form['matricule']
    lieu=request.files['lieu']
    tel=request.form['tel']
    #import des photos
    path_lieu = f"uploads/lieu/{lieu.filename}"
    lieu.save(path_lieu)
    return model.register_hopital(nom,email,matricule,lieu,tel)

@app.route('/login_hopital',methods=['POST'])
def login_hopital():
    matricule=request.form['matricule']
    return model.login_hopital(matricule)

@app.route('/add_services',methods=['POST'])
@authentificate_hopital
def add_service(current_hopital):
    nom=request.form['nom']
    description=request.form['description']
    return model.add_service(current_hopital,nom,description)

@app.route('/add_doctor',methods=['POST'])
@authentificate_hopital
def add_doctor(current_hopital):
    nom=request.form['nom']
    prenom=request.form['prenom']
    matricule=request.form['matricule']
    email=request.form['email']
    specialite=request.form['specialite']
    service_id=request.form['service_id']
    return model.add_doctor(current_hopital,nom,prenom,matricule,specialite,email,service_id)

@app.route('/get_service',methods=['GET'])
@authentificate_hopital
def get_service(current_hopital):
    return model.get_service(current_hopital)

@app.route('/get_doctor')
@authentificate_hopital
def get_doctor(current_hopital):
    return model.get_doctor(current_hopital)

@app.route('/get_doctor_by_service')
@authentificate_hopital
def get_doctor_by_service(current_hopital):
    return model.get_doctor_by_service(current_hopital)

@app.route('/delete_service',methods=['POST'])
@authentificate_hopital
def delete_service(current_hopital):
    return model.delete_service(current_hopital)

@app.route('/delete_doctor',methods=['POST'])
@authentificate_hopital
def delete_doctor(current_hopital):
    return model.delete_doctor(current_hopital)