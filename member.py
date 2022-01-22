import imp
from app import db

class UserRegister(db.Model):
    __tablename__ = 'UserRgeisters'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    
    def __repr__(self):
        return 'username:%s, email:%s' % (self.username, self.email)