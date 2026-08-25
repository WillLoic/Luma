from flask import request,make_response
from app import app
from models.users import User_model
from middlewares.authentificate import authentificate_user
from models.consultation import Consultation_model 

model=User_model()
@app.route('/verify_code',methods=['POST'])
def verify_code():
    #code=request.json['code']
    return model.verification_code()

@app.route('/regenerate_code',methods=['POST'])
def regenerate_code():
    return model.regenerate_code()

@app.route('/register',methods=['POST'])
def register():
    nom=request.form['nom']
    prenom=request.form['prenom']
    tel=request.form['tel']
    email=request.form['email']
    date_naiss=request.form['date_naiss']
    password=request.form['password']
    return model.register_user(nom,prenom,tel,email,date_naiss,password)

@app.route('/login_user',methods=['POST'])
def login_user():
    password=request.form['password']
    email=request.form['email']
    return model.login_user(email,password)

"""@app.route('/update_profil',methods=['PUT'])
@authentificate_user
def update_profil():
    taille=request.form['taille']
    poids=request.form['poids']
    adresse=request.form['adresse']
    genre=request.form['genre']
    groupe_sanguin=request.form['groupe_sanguin']
    allergie=request.form['allergie']
    tension=request.form['tension']
    maladie_chronique=request.form['maladie_chronique']
    antecedents_medicaux=request.form['antecedents_medicaux']
    antecedents_chirurgicaux=request.form['antecedents_chirurgicaux']
    antecedants_familiaux=request.form['antecedants_familiaux']
    vaccinations=request.form['vaccinations']
    traitements_en_cours=request.form['traitements_en_cours']
    resultats_examens=request.form['resultats_examens']
    consultations_precedentes=request.form['consultations_precedentes']
    notes=request.form['notes']
    donneur_organes=request.form['donneur_organes']
    medecin_traitant=request.form['medecin_traitant']
    return model.update_profil(taille,poids,adresse,genre,groupe_sanguin,allergie,tension,
                     maladie_chronique,antecedents_medicaux,antecedents_chirurgicaux,
                     antecedants_familiaux,vaccinations,traitements_en_cours,resultats_examens,
                     consultations_precedentes,notes,donneur_organes,medecin_traitant)
"""

@app.route('/update_profil',methods=['POST'])
@authentificate_user
def update_profil(current_user):
    data=request.form.to_dict()
    """data=request.get_json()
    if not data:
        return make_response({'msg':'Pas de donnees entres'},403)
    print(f'Data:{data}')"""
    return model.update_profil(current_user=current_user,**data)

@app.route('/telechareger_carnet',methods=['POST'])
@authentificate_user
def telecharger_carnet(current_user):
    date_debut=request.form['date_debut']
    date_fin=request.form['date_fin']
    return Consultation_model().telecharger_carnet(current_user,date_debut,date_fin)
@app.route('/telecharger_all_carnet',methods=['POST']) 
@authentificate_user
def telecharger_all_carnet(current_user):
    return Consultation_model().telecharger(current_user)

@app.route('/voir_carnet',methods=['POST'])
@authentificate_user
def voir_carnet(current_user):
    date_debut=request.form['date_debut']
    date_fin=request.form['date_fin']
    return Consultation_model().voir_carnet(current_user,date_debut,date_fin)
@app.route('/voir_all_carnet',methods=['POST'])
@authentificate_user
def voir_all_carnet(current_user):
    return Consultation_model().voir_all_carnet(current_user)

@app.route('/delete_notification',methods=['POST'])
@authentificate_user
def delete_notification(current_user):
    from models.notification import Notification_model
    return Notification_model().delete_notification(current_user)

@app.route('/get_notification',methods=['GET'])
@authentificate_user
def get_notification(current_user):
    from models.notification import Notification_model
    return Notification_model().get_notifications(current_user)

    