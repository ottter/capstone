from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    stu_id = IntegerField('Student ID', validators=[DataRequired(), NumberRange(min=983000000, max=984000000, message='Must enter a valid MGA Student ID')], render_kw={"placeholder": "MGA Student ID"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "MGA Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already registered. Please choose a different one.')

    def validate_stu_id(self, stu_id):
        user = User.query.filter_by(stu_id=stu_id.data).first()
        if user:
            raise ValidationError('That Student ID is already registered. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    about_me = TextAreaField('About me', validators=[Length(min=0, max=350)], render_kw={"placeholder": "Tell the community a little about yourself!"})
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already registered. Please choose a different one.')


class AddNotesForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], render_kw={"placeholder": "Prof Langdon's lecture on Julius Caesar"})
    description = TextAreaField('Briefly describe the contents', validators=[Length(min=0, max=250)], render_kw={"placeholder": "My shift key was broken so sorry about that!"})
    notes = FileField('Add Notes')
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], render_kw={"placeholder": "Announcement Title"})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": "What do you want to tell the community?"})
    submit = SubmitField('Post')


class CreateClassForm(FlaskForm):
    academic_catalog = [('itec', 'ITEC - Information Technology'), ('hist', 'HIST - History'),
                        ('math', 'MATH - Mathematics'), ('nurs', 'NURS - Nursing', )]
    program = SelectField('Program Name', choices=academic_catalog, validators=[DataRequired()])
    course_id = IntegerField('Course ID', render_kw={"placeholder": "e.g., 4750"},
                             validators=[DataRequired(), NumberRange(min=1000, max=9999, message='Must be in valid Course ID format')])
    course_name = StringField('Course Name', validators=[DataRequired()], render_kw={"placeholder": "e.g., Senior Capstone"})
    submit = SubmitField('Add Class')