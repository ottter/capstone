from app import db, login_manager, app
# from flask_login import UserMixin
from flask_user import UserManager, UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    stu_id = db.Column(db.String(9), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    about_me = db.Column(db.String(250))
    last_seen = db.Column(db.DateTime, default=datetime.today())
    password = db.Column(db.String(30), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    posts = db.relationship('Post', backref='author', lazy=True)
    roles = db.relationship('Role', secondary='user_roles')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.stu_id}')"

user_manager = UserManager(app, db, User)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.name}')"

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    def __repr__(self):
        return f"User('{self.user_id}', '{self.role_id}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"


class ClassList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_section = db.Column(db.String(10), unique=True, nullable=False)
    course_name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.course_section}', '{self.course_name}')"