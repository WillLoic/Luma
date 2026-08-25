from flask import request,make_response,session,current_app
from models.config import db,ma,mail,bcrypt
#from models.rendez_vous import Rendez_vous
#from app import app 
import secrets, jwt
from datetime import datetime,timedelta
from flask_mail import Message


#creation de la table user
class User(db.Model):
    __tablename__='users'
 
#ajout des champs de la table
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    nom=db.Column(db.String(60),nullable=False)
    prenom=db.Column(db.String(60))
    tel=db.Column(db.String(15))
    email=db.Column(db.String(50),nullable=False)
    date_naiss=db.Column(db.Date,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    code=db.Column(db.String(10))
    code_expired=db.Column(db.DateTime)
    user_actived=db.Column(db.Boolean,default=False)
    photo=db.Column(db.Text,default=False)
    taille=db.Column(db.Float,default=None)
    poids=db.Column(db.Float,default=None)
    adresse=db.Column(db.String(150),default=None)
    genre=db.Column(db.String(10),default=None)
    groupe_sanguin=db.Column(db.String(5),default=None)
    electrophorese=db.Column(db.String(5),default=None)
    allergie=db.Column(db.Text,default=None)
    tension=db.Column(db.String(20),default=None)
    maladie_chronique=db.Column(db.Text,default=None)
    antecedents_medicaux=db.Column(db.Text,default=None)
    antecedents_chirurgicaux=db.Column(db.Text,default=None)
    antecedants_familiaux=db.Column(db.Text,default=None)
    vaccinations=db.Column(db.Text,default=None)
    traitements_en_cours=db.Column(db.Text,default=None)
    resultats_examens=db.Column(db.Text,default=None)
    consultations_precedentes=db.Column(db.Text,default=None)
    notes=db.Column(db.Text,default=None)
    donneur_organes=db.Column(db.Boolean,default=None)
    medecin_traitant=db.Column(db.Text,default=None)
    carnet_principal=db.Column(db.LargeBinary(1024*1024),default=None)


    def __init__(self,nom,prenom,tel,email,date_naiss,password):
        self.nom=nom
        self.prenom=prenom
        self.tel=tel
        self.email=email
        self.date_naiss=date_naiss
        self.password=bcrypt.generate_password_hash(password) #mot de passe hache
#fonction pour comparer les mots de passe et retourner le resultat
    def get_password(self,password):
       return bcrypt.check_password_hash(self.password,password)

#chargement des tables 
#app_context()

#Sérialisation des données
class UserSchema(ma.SQLAlchemyAutoSchema):
  class Meta : 
    model = User

#Permet de sérialiser un objet
user_schema = UserSchema()
#Permet de sérialiser plusieurs objets à la fois
users_schema = UserSchema(many=True)

class User_model():
   def register_user(self,nom,prenom,tel,email,date_naiss,password):
      user=User(nom,prenom,tel,email,date_naiss,password)
      def get_code():
         return secrets.token_hex(3)
      def send_verification_email(email,code):
        msg=Message('Votre code de confirmation', recipients=[email])
        msg.body=f'Votre code de verification est : {code}'
        #mail.send(msg)
      code=get_code()
      
      send_verification_email(email,code)
      user.code=code
      user.code_expired=datetime.now() + timedelta(minutes=2)
      user.user_actived=False
      db.session.add(user)
      db.session.commit()
      return make_response({'msg':'Successfully registered, check your email for the verification code'},200)
   
   def verification_code(self):
      id=request.json.get('id')
      code=request.json.get('code')
      user=User.query.get(id)
      if user:
         if user.code_expired < datetime.now():
            return make_response({'msg':'Code expired regenerate the new code'},401)
         else:
            if code==user.code:
                user.user_actived=True
                db.session.commit()
                return make_response({'msg':'Compte actived'},200)
            else:
               return make_response({'msg':'Invalid code'},401)
      else:
         return({'msg':'Utilisateur non trouver'},403)
   
   def regenerate_code(self):
        id=request.json.get('id')
        user=User.query.get(id)
        if user:
            def get_code():
                return secrets.token_hex(3)
            def send_verification_email(email,code):
                msg=Message('Votre nouveau code de confirmation', recipients=[email])
                msg.body=f'Votre code de verification est : {code}'
                #mail.send(msg)
            code=get_code()  
            send_verification_email(user.email,code)
            user.code=code
            user.code_expired=datetime.now() + timedelta(minutes=2)
            db.session.commit()
            return make_response({'msg':'New code sent to your email'},200)
        else:
            return make_response({'msg':'Utilisateur non trouver'},401)
    
   def login_user(self,email,password):
      user=User.query.filter_by(email=email).first()
      if user:
         if user.get_password(password):
            payloads={'email':user.email,'exp':datetime.now()+timedelta(minutes=30)}
            token=jwt.encode(payloads,current_app.config['SECRET_KEY'],algorithm='HS256')
            return make_response({'msg':'Token creer','Token':token},200)
         else:
            return make_response({'msg':'Incorect password'},401)
      else:
         return make_response({'msg':'Incorect email'},403)
      
   """def update_profil(self,taille=None,poids=None,adresse=None,genre=None,groupe_sanguin=None,allergie=None,tension=None,
                     maladie_chronique=None,antecedents_medicaux=None,antecedents_chirurgicaux=None,
                     antecedants_familiaux=None,vaccinations=None,traitements_en_cours=None,resultats_examens=None,
                     consultations_precedentes=None,notes=None,donneur_organes=None,medecin_traitant=None,id=None):
        user=User.query.get(id)
        if user:
            user.taille=taille
            user.poids=poids
            user.adresse=adresse
            user.genre=genre
            user.groupe_sanguin=groupe_sanguin
            user.allergie=allergie
            user.tension=tension
            user.maladie_chronique=maladie_chronique
            user.antecedents_medicaux=antecedents_medicaux
            user.antecedents_chirurgicaux=antecedents_chirurgicaux
            user.antecedants_familiaux=antecedants_familiaux
            user.vaccinations=vaccinations
            user.traitements_en_cours=traitements_en_cours
            user.resultats_examens=resultats_examens
            user.consultations_precedentes=consultations_precedentes
            user.notes=notes
            user.donneur_organes=donneur_organes
            user.medecin_traitant=medecin_traitant
            db.session.commit()
            return make_response({'msg':'Profil mis a jour avec succes'},200)
        else:
            return make_response({'msg':'Utilisateur non trouver'},404)
   """   
   def update_profil(self, current_user, **kwargs):
       #user = User.query.get(current_user)
       if not current_user:
           return make_response({'msg': 'Utilisateur non trouver'}, 404)
        # Tu modifies l'utilisateur courant directement
       for key, value in kwargs.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
       db.session.commit()
       return make_response({'msg': 'Profil mis a jour avec succes'}, 200)
   
   
   
   
   