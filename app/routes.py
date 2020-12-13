from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from app.forms import LoginForm, SaveForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Question, Image

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('next_page'))
    return render_template('login.html', title='Sign In', form=form)

# redirect user to login page upon logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_required
@app.route('/')
@app.route('/index', methods=['GET','POST'])
def index():
    questions = Question.query.all()
    save_form = SaveForm()
    if save_form.validate_on_submit():
        pass
    return render_template('index.html', questions=questions, saveForm=save_form)

@app.route('/get_image')
def get_image():
    question_id = request.args.get('question_id',1,type=int)
    q = Question.query.get(question_id)
    print(q)
    url = str(q.images.first().path)
    print(str(url),type(url))
    return jsonify(url)

@app.route('/add_question')
def add_question():
    question_id = request.args.get('question_id',1,type=int)
    print(question_id)
    q = Question.query.get(question_id).__dict__
    del q['_sa_instance_state']
    return jsonify(q)
