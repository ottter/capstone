from flask import redirect, url_for, render_template, request, flash
from app.forms import RegistrationForm, EditProfileForm, LoginForm
from app.models import User
from datetime import datetime
from app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import binascii
import os


def home():
    return render_template('home.html')
app.add_url_rule('/', 'home', home)


def about():
    return render_template('about.html', title='About')
app.add_url_rule('/about', 'about', about)


def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, stu_id=form.stu_id.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
app.add_url_rule("/register", 'register', register, methods=['GET', 'POST'])


def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
app.add_url_rule("/login", 'login', login, methods=['GET', 'POST'])


def logout():
    logout_user()
    return redirect(url_for('home'))
app.add_url_rule("/logout", 'logout', logout)


@login_required
def account(stu_id):
    user = User.query.filter_by(stu_id=stu_id).first_or_404()
    image_file = url_for('static', filename=f'images/profile_pics/{current_user.image_file}')
    return render_template('account.html', user=user, title='Account', image_file=image_file)
app.add_url_rule("/user/<stu_id>", 'account', account)


def save_picture(form_picture): # save and rename uploaded profile picture to random hex string
    random_hex = binascii.b2a_hex(os.urandom(8))
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/profile_pics', picture_filename)

    output_size = (250, 250)    # resize the image before saving it on the file system
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_filename

@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('account', stu_id=current_user.stu_id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    # return redirect(url_for('account', stu_id=current_user.stu_id))
    return render_template('edit_profile.html', title='Edit Profile', form=form)
app.add_url_rule("/user/edit_profile", 'edit_profile', edit_profile, methods=['GET', 'POST'])


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()