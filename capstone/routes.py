from flask import redirect, url_for, render_template, request, flash
from capstone.forms import RegistrationForm, LoginForm
from capstone.models import User
from capstone import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


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
def account():
    return render_template('account.html', title='Account')
app.add_url_rule("/account", 'account', account)