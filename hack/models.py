from hack import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import date
import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    image = db.Column(db.String, default='default.png')
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(64),index=True)
    password = db.Column(db.String)
    products = db.relationship('UserProduct', backref='user')
    premium = db.Column(db.Integer, default=0)

    journal = db.Column(db.String, default=str(date.today()- datetime.timedelta(days=1)))
    meditate = db.Column(db.String, default=str(date.today()- datetime.timedelta(days=1)))
    video = db.Column(db.String, default=str(date.today()- datetime.timedelta(days=1)))
    pill = db.Column(db.String, default=str(date.today()- datetime.timedelta(days=1)))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, default='default.png')
    category = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class UserProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    qty = db.Column(db.Integer, default=1)

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String, default=str(date.today()))
    text = db.Column(db.String)
