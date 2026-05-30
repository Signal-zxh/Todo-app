import os

from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from flask_migrate import Migrate

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', '981008'),
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(app.instance_path, 'todo.db')}"
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.config.from_pyfile('config.py', silent=True)

# normalize relative SQLite path to absolute path for Flask-SQLAlchemy
db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
    db_path = db_uri.replace('sqlite:///', '', 1)
    if not os.path.isabs(db_path):
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath(db_path)}"

#initializate Flask-Login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

db = SQLAlchemy(app)

migrate = Migrate(app, db)

#Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#User model
class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(),
        Length(min=4, max=20)
    ])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=6)
    ])
    submit = SubmitField('注册')
    #自定义验证重名方法
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被占用')

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks = tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task_content = request.form['content']
    new_task = Task(content=task_content, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Task.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect('/')

@app.route('/toggle/<int:id>')
@login_required
def toggle(id):
    task=Task.query.get_or_404(id)
    task.done = not task.done
    db.session.commit()
    return redirect('/')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        #检查用户名是否已经存在（双重验证）
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('用户名已存在')
            return redirect(url_for('register'))
        #创建新用户
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('注册成功！请登录')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('无效的用户名或密码')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
