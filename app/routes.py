from flask import redirect, url_for, render_template, request, flash, send_from_directory
from app.forms import RegistrationForm, EditProfileForm, LoginForm, PostForm, CreateClassForm, AddNotesForm
from app.models import User, Post, Role, UserRoles, ClassList, Notes
from datetime import datetime
from app import app, db, bcrypt, ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user, logout_user, login_required
from flask_user import roles_required
from PIL import Image
import binascii
import os

# Create my default account and assign it admin role (if not exist)
if not User.query.filter_by(stu_id='983204830').first():
    if not User.query.filter_by(email='james@mga.edu').first():
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        default_acc = User(username='James Cross', stu_id='983204830', email='james@mga.edu', password=hashed_password)
        db.session.add(default_acc)
        db.session.commit()

        role = Role.query.filter_by(name="admin").first()
        if role is None:
            role = Role(name="admin")
            db.session.add(role)
            db.session.commit()
        user_role = UserRoles(user_id=default_acc.id, role_id=role.id)
        db.session.add(user_role)
        db.session.commit()

def home():
    # Selects which profiles to use for site testimonials
    test_user_1 = User.query.filter_by(stu_id=983999997).first_or_404()
    test_user_2 = User.query.filter_by(stu_id=983999998).first_or_404()
    test_user_3 = User.query.filter_by(stu_id=983999999).first_or_404()
    return render_template('home.html', test1=test_user_1, test2=test_user_2, test3=test_user_3)
app.add_url_rule('/', 'home', home)


def about():
    return render_template('about.html', title='About')
app.add_url_rule('/about', 'about', about)


def classes():
    # TODO: Find a more intuitive way to list classes
    academic_catalog = {'itec': 'ITEC - Information Technology', 'hist': 'HIST - History',
                        'math': 'MATH - Mathematics', 'nurs': 'NURS - Nursing'}
    form = CreateClassForm()
    class_list = ClassList.query.order_by(ClassList.program.asc(),ClassList.course_id.asc()).all()
    if not current_user.is_authenticated:
        flash('That feature is for users only! Register an account first!', 'info')
        return redirect(url_for('register'))
    if current_user.is_authenticated:
        if current_user.has_role('admin'):
            if form.validate_on_submit():
                create_class = ClassList(program=form.program.data, course_id=form.course_id.data, course_name=form.course_name.data)
                db.session.add(create_class)
                db.session.commit()
                flash('Class has been created!', 'success')
                return redirect(url_for('class'))
    return render_template('class_list.html', title='Classes', form=form, class_list=class_list, academic_catalog=academic_catalog)
app.add_url_rule('/class', 'class', classes, methods=['GET', 'POST'])


def save_notes(form_notes): # save and rename uploaded profile picture to random hex string
    random_hex = binascii.b2a_hex(os.urandom(10)).decode("utf-8")
    _, f_ext = os.path.splitext(form_notes.filename)
    notes_filename = random_hex + f_ext
    return notes_filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
def course(program, course_id):
    form = AddNotesForm()
    notes_list = Notes.query.filter_by(program=program, course_id=course_id).all()
    if current_user.is_authenticated and request.method == 'POST':
        if form.validate_on_submit():
            if form.notes.data and allowed_file(form.notes.data.filename):
                notes_file = save_notes(form.notes.data)
                filename = secure_filename(notes_file)
                form.notes.data.save(os.path.join(app.config['NOTES_FOLDER'], filename))
                add_notes = Notes(program=program, course_id=course_id, notes_file=str(notes_file),
                                  user_id=current_user.stu_id, title=form.title.data, content=form.description.data,
                                  original_filename=form.notes.data.filename)
                db.session.add(add_notes)
                db.session.commit()
                flash('Your notes have been uploaded!', 'success')
            else:
                flash("Bad File! Your upload must be under 16MB and one of these filetypes:"
                      ".TXT, .PDF, .PNG, .JPG, .DOCX, .XFSX, .PPTX", 'error')
            return redirect(url_for('course', program=program, course_id=course_id))
        else:
            return redirect(url_for('course', program=program, course_id=course_id))
    return render_template('course_notes.html', title='Course', form=form, notes_list=notes_list, program=program, course_id=course_id)
app.add_url_rule("/class/<program>/<course_id>", 'course', course, methods=['GET', 'POST'])


@login_required
def download_file(filename):
    return send_from_directory(directory='data/notes/', filename=filename, as_attachment=True)
app.add_url_rule('/downloads/<filename>', 'download_file', download_file, methods=['GET', 'POST'])

@login_required
def delete_note_user(note_id):
    # TODO: Add admin function to delete too
    del_note = Notes.query.get_or_404(note_id)
    program, course_id = del_note.program, del_note.course_id
    if current_user.stu_id == del_note.user_id:
        db.session.delete(del_note)
        db.session.commit()
        flash('Your note has been deleted!', 'info')
    else:
        flash('How did you get this far?', 'error')
    return redirect(url_for('course', program=program, course_id=course_id))
app.add_url_rule('/downloads/<note_id>/delete', 'delete_note_user', delete_note_user, methods=['GET', 'POST'])


def news():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('news.html', title='News', posts=posts)
app.add_url_rule('/news', 'news', news)


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
            flash('Login Unsuccessful. Please check email and password', 'error')
    return render_template('login.html', title='Login', form=form)
app.add_url_rule("/login", 'login', login, methods=['GET', 'POST'])


def logout():
    logout_user()
    return redirect(url_for('home'))
app.add_url_rule("/logout", 'logout', logout)


@login_required
def account(stu_id):
    if not current_user.is_authenticated:
        flash('That feature is for users only! Register an account first!', 'info')
        return redirect(url_for('register'))
    user = User.query.filter_by(stu_id=stu_id).first_or_404()
    uploaded = Notes.query.filter_by(user_id=stu_id).order_by(Notes.id.desc()).all()
    return render_template('account_profile.html', user=user, uploaded=uploaded, title='Account')
app.add_url_rule("/user/<stu_id>", 'account', account)


def save_picture(form_picture): # save and rename uploaded profile picture to random hex string
    random_hex = binascii.b2a_hex(os.urandom(8)).decode("utf-8")
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/profile_pics', picture_filename)

    output_size = (250, 250)    # resize the image before saving it on the file system
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
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
        flash('No changes have been made.', 'success')
    return render_template('edit_profile.html', title='Edit Profile', form=form)
app.add_url_rule("/user/edit_profile", 'edit_profile', edit_profile, methods=['GET', 'POST'])


@roles_required('admin')
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('news'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')
app.add_url_rule('/news/post/new', 'new_post', new_post, methods=['GET', 'POST'])


def post(post_id):
    view_post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=view_post.title, post=view_post)
app.add_url_rule('/news/post/<int:post_id>', 'post', post)


@roles_required('admin')
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')
app.add_url_rule('/news/post/<int:post_id>/update', 'update_post', update_post, methods=['GET', 'POST'])


@roles_required('admin')
def delete_post(post_id):
    del_post = Post.query.get_or_404(post_id)
    db.session.delete(del_post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('news'))
app.add_url_rule('/news/post/<int:post_id>/delete', 'delete_post', delete_post, methods=['POST'])


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()