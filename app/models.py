from app import db,login
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# load current user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# model for individual questions
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String)
    sitting = db.Column(db.String)
    paper = db.Column(db.String)
    topic = db.Column(db.String)
    question_number = db.Column(db.Integer)
    question_type = db.Column(db.String)
    description = db.Column(db.String)
    # multiple choice questions need a text answer
    answer = db.Column(db.String)
    images = db.relationship('Image', backref='question', lazy='dynamic')

    def __repr__(self):
        return '<Question id={id}, paper={paper}>'.format(id=self.id,paper=self.paper)

# image files (questions and mark schemes), since more than one page can be associated with a question
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, unique=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    # is it a question or a mark scheme
    q_ms = db.Column(db.String)
    def __repr__(self):
        return '<Image {}>'.format(self.path)

# questions are organised into files created by the user (question papers)
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_list = db.Column(db.PickleType())
    filename = db.Column(db.String(120))
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True,default=datetime.utcnow)

    def __repr__(self):
        return '<File {} {}>'.format(self.filename, self.question_list)


