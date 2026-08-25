from flask import make_response,request
from models.config import db,ma

class Notification(db.Model):
    id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    message=db.Column(db.Text)
    id_patient=db.Column(db.Integer,db.ForeignKey('users.id'))
    id_doctor=db.Column(db.Integer,db.ForeignKey('doctor.id'))

    def __init__(self,id_doctor,id_patient,message):
        self.id_doctor=id_doctor
        self.id_patient=id_patient
        self.message=message

#serialisation des donnees
class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Notification

#serialisation d'un objet
notification_schema=NotificationSchema()
#serialisation de plusieurs objets
notifications_schema=NotificationSchema(many=True)

class Notification_model:
    """def add_notification(self,current_doctor):
        id=request.json['id']
        message=request.json['message']
        notification=Notification(id_doctor=current_doctor.id,id_patient=id,message=message)
        db.session.add(notification)
        db.session.commit()
        return make_response({'msg':'Notification envoyer'},200)"""
    
    def delete_notification(self,current_user):
        id=request.json['id']
        notification=Notification.query.filter_by(id=id,id_patient=current_user.id).first()
        if not notification:
            return make_response({'msg':'Notification non trouver'},401)
        db.session.delete(notification)
        db.session.commit()
        return make_response({'msg':'Notification supprimer'},200)
    
    def get_notifications(self, current_user):
        notifications = Notification.query.filter_by(id_patient=current_user.id).all()
        return make_response({'notifications': notifications_schema.dump(notifications)}, 200)




