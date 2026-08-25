from app import app
from models.users import User
from models.hopital import Hopital
from models.doctor import Doctor
from functools import wraps
from flask import request,make_response
import jwt

def authentificate_user(fonction):
    @wraps(fonction)
    def wrapper(*args,**kwargs):
        auth_headers=request.headers.get('Authorization')
        if auth_headers:
            try:
              token=auth_headers.split(" ")[1]
              token_decode=jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])
              
            except IndexError:
                        return make_response({'msg': 'Format du token invalide'}, 401)
            except jwt.ExpiredSignatureError:
                        return make_response({'msg': 'Token expire'}, 401)
            except jwt.InvalidTokenError:
                        return make_response({'msg': 'Token invalide'}, 401)
            user=User.query.filter_by(email=token_decode.get('email')).first()
            if user:
                  #kwargs['current_user'] = user  # On passe l'utilisateur ici
                  return fonction(user,*args,**kwargs)
            else :
              return make_response({'msg':'L\'email ne correspond pas' },401)
        else:
          return make_response({'msg':'pas de token'},401)

    return wrapper

def authentificate_hopital(fonction):
      @wraps(fonction)
      def wrapper(*args,**kwargs):
        auth_headers=request.headers.get('Authorization')
        if auth_headers:
            try:
              token=auth_headers.split(" ")[1]
              token_decode=jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])
              
            except IndexError:
                        return make_response({'msg': 'Format du token invalide'}, 401)
            except jwt.ExpiredSignatureError:
                        return make_response({'msg': 'Token expire'}, 401)
            except jwt.InvalidTokenError:
                        return make_response({'msg': 'Token invalide'}, 401)
            hopital=Hopital.query.filter_by(matricule=token_decode.get('matricule')).first()
            if hopital:
                  return fonction(hopital,*args,**kwargs)
            else :
              return make_response({'msg':'Le matricule de l\'hopital ne correspond pas' },401)
        else:
          return make_response({'msg':'pas de token'},401)
      return wrapper

def authentificate_doctor(fonction):
      @wraps(fonction)
      def wrapper(*args,**kwargs):
          auth_headers=request.headers.get('Authorization')
          if auth_headers:
            try:
              token=auth_headers.split(" ")[1]
              token_decode=jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])
              
            except IndexError:
                        return make_response({'msg': 'Format du token invalide'}, 401)
            except jwt.ExpiredSignatureError:
                        return make_response({'msg': 'Token expire'}, 401)
            except jwt.InvalidTokenError:
                        return make_response({'msg': 'Token invalide'}, 401)
            hopital=Hopital.query.filter_by(matricule=token_decode.get('matricule_hopital')).first()
            doctor=Doctor.query.filter_by(matricule=token_decode.get('matricule_doctor')).first()
            if not hopital:
                return make_response({'msg': 'Matricule hôpital invalide'}, 401)
            if not doctor:
                return make_response({'msg': 'Matricule docteur invalide'}, 401)
            return fonction(current_doctor=doctor, *args, **kwargs)
          else:
            return make_response({'msg':'pas de token'},401)
      return wrapper