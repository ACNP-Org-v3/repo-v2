from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from App.database import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

class RegularUser(db.User):
    __tablename__='regular_user'
    usercomps = db.relationship('UserCompetition', backref='user', lazy=True)
    
    def reg_comp(self, comp_id):
        register = Competitions.query.get(comp_id)
        if register:
            try:
                registercomp = UserCompetition(self.id, comp_id)
                db.session.add(registercomp)
                db.session.commit()
                return registercomp
            except Exception:
                db.session.rollback()
                return None
        return None

    def delete_comp(self, comp_id):
        comp = UserCompetition.query.filter_by(id=comp_id, user_id=self.id).first()
        if comp:
            db.session.delete(comp)
            db.session.commit()
            return True
        return None

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": 'regular user'
        }
    def __repr__(self):
        return f'<RegularUser {self.id} : {self.username} - {self.email}>'

class AdminUser(db.User):
    __tablename__='admin_user'
    comps = db.relationship('Competitions', backref='admin', lazy=True)

    def get_json(self):
     return {
        "id": self.id,
        "username": self.username,
        "email": self.email,
        "role": 'admin'
     }
    
    def update_comp_details(self, comp_id, details):
        comp = Competitions.query.filter_by(id=comp_id, user_id=self.id).first()
        if comp:
            comp.details= details
            db.session.add(comp)
            db.session.commit()
            return True
        return None

    def __repr__(self):
        return f'<AdminUser {self.id} : {self.username} - {self.email}>'

class UserCompetition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_user_id = db.Column(db.Integer, db.ForeignKey('regularuser.id'), nullable=False)
    comp_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)

class Competitions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    participant_count = db.Column(db.Integer, nullable=False)

    def view_comp_details(comp_id):
        comp = Competitions.query.filter_by(comp_id).first()
        if comp:
            return comp.description


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    reg_user_id = db.Column(db.Integer, db.ForeignKey('regularuser.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    
    def view_comp_results(comp_id):
        comp_results = Results.query.filter_by(comp_id)
        if comp_results:
            return [results.get_json() for results in comp_results]
        else:
            return []