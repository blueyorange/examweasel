from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.forms import LoginForm, SaveForm, DataForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Question, Image, File

@app.route('/login', methods=['GET','POST'])
def login():
    '''Returns login form and authenticates user.'''
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
    '''Logs user out (duh)!'''
    logout_user()
    return redirect(url_for('login'))

# main app page - question database viewer
@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    '''Returns the main app page and saves files'''
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
            file = File(author=current_user,filename=filename,question_list=ids)
        else:
            # file id submitted: query for file entry and update
            file = File.query.filter_by(id=file_id).first()
            file.author=current_user
            file.question_list = ids
            file.filename = filename
        db.session.add(file)
        db.session.commit()
        data = {'filename':filename, 'file_id':file.id}
        return jsonify(data)
    return render_template('index.html', questions=questions, saveForm=form, filename=filename)

@app.route('/get_viewer')
def get_viewer():
    '''Returns question viewer html when question is clicked.'''
    question_id = request.args.get('question_id',1,type=int)
    q = Question.query.get(question_id)
    # pass q to form for defaulyt values
    form = DataForm(obj=q)
    question_urls = [item.path for item in q.images.filter_by(resource_type='qp').all()]
    ms_urls = [item.path for item in q.images.filter_by(resource_type='ms').all()]
    form.exam_sitting = q.sitting
    print(q.sitting)
    return render_template('viewer.html', q=q,question_urls=question_urls,ms_urls=ms_urls, form=form)

@app.route('/get_file_list')
def get_file_list():
    '''Returns html for the table body of the load window - a file list.'''
    files = File.query.all()
    return render_template('load_table.html', files=files)

@app.route('/load_file')
def load_file():
    '''Takes an integer representing a file id and returns the filename and the list of questions.'''
    file_id = request.args.get('id',1,type=int)
    f = File.query.filter_by(id=file_id).first()
    print("Request for file " + str(f))
    return jsonify(filename=f.filename, question_list=f.question_list)