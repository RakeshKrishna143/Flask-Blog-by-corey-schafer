from application import db,login_manager
from datetime import datetime
from flask_login import UserMixin
from mongoengine import IntField,SequenceField,ReferenceField

@login_manager.user_loader
def load_user(id):
    return User.objects(id=id).first()

class Post(db.Document):
    post_id = db.SequenceField()
    title = db.StringField(max_length=20,required=True)
    date_posted = db.DateTimeField(required=True,default=datetime.utcnow)
    content = db.StringField(required=True)
    user_created = db.ReferenceField('application.User')
    
    
class User(db.Document,UserMixin):
    user_id = db.SequenceField()
    username = db.StringField(max_length=20,unique=True,required=True)
    email = db.StringField(max_length=120,unique=True,required=True)
    picture = db.StringField(max_length=20,required=True,default='default.jpg')
    password = db.StringField(max_length=60,required=True)
    posts = db.ListField(db.ReferenceField(Post,reverse_delete_rule=4))
    
