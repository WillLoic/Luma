from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_bcrypt import Bcrypt
#from app import app


bcrypt=Bcrypt()
db=SQLAlchemy()
ma=Marshmallow()
mail=Mail()
"""
def app_context():
    with app.app_context():
        db.drop_all()
        db.create_all()
"""
