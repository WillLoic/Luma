from flask import Flask
from flask_cors import CORS
from models.config import db, ma, mail,bcrypt  # maintenant tu peux importer sans cercle


app=Flask(__name__)
CORS(app,origins="*")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/luma_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME'] = 'willloic36@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'willloic36@gmail.com'
app.config['SECRET_KEY']='1234'
#Initialise les extensions ici
db.init_app(app)
ma.init_app(app)
mail.init_app(app)
bcrypt.init_app(app)

from models import hopital,doctor, users, rendez_vous
from controllers import users,hopital,doctor,rendez_vous,administrator
#Création des tables
"""with app.app_context():
    db.drop_all()
    db.create_all()
"""    



if __name__ == '__main__':
    app.run()