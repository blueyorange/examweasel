from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.forms import LoginForm, SaveForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Question, Image, File

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
        if next_page is None or next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# redirect user to login page upon logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# main app page - question database viewer
@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    filename = 'untitled'
    questions = Question.query.all()
    form = SaveForm()
    # file has been saved
    if request.method == 'POST':
        print('POSTed')
        # get question ids from POSTed data, split into list
        ids = request.form.get('ids').strip('][').split(',')
        # turn list of strings into list of integers
        ids = [int(id) for id in ids]
        print(current_user.id)
        # get posted filename from form data
        filename = request.form.get('filename')
        flash("File saved successfully.")
        # get file_id from posted data to check if new file
        file_id = request.form.get('file_id')
        print(file_id)
        if file_id == 'null':
            print('No file: creating new entry')
            # No file id sent: create new database entry
            file = File(author=current_user.id,filename=filename,question_list=ids)
        else:
            # file id submitted: query for file entry and update
            file = File.query.filter_by(id=file_id).first()
            file.author=current_user.id
            file.question_list = ids
            file.filename = filename
        db.session.add(file)
        db.session.commit()
        data = {'filename':filename, 'file_id':file.id}
        return(jsonify(data))
    # query files for document loader
    documents = File.query.all()
    return render_template('index.html', questions=questions, saveForm=form, filename=filename, documents=documents)

@app.route('/get_image')
def get_image():
    question_id = request.args.get('question_id',1,type=int)
    q = Question.query.get(question_id)
    print(q)
    url = str(q.images.first().path)
    print(str(url),type(url))
    return jsonify(url)

