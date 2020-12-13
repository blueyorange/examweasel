from app import app,db
from app.models import User,Question,File,Image
import os

basedir = os.getcwd()
root='app/'
cwd = os.path.join(basedir,root)
os.chdir(root)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,'Question' : Question,'File': File, 'sync': sync_questions, 'flush': flush}

def sync_questions():
    log = open('log.txt','w')
    # syncs question table with images in question folder
    path='static/images/questions'
    ext = '.png'
    for (parent,dirs,files) in os.walk(path, topdown=True):
        if files:
            for f in files:
                log.write('Found image: '+f+'\n')
                # check extension of file is '.png'
                if os.path.splitext(f)[1] == ext:
                    # get full path (combine path & filename)
                    path = os.path.join(parent,f)
                    # get course, sitting, paper, q/ms from filename in a dict
                    d = get_data_from_filename(f)
                    # check to see if already in image table
                    image_in_table = Image.query.filter_by(path=path).first()
                    log.write('query: '+str(image_in_table)+'\n')
                    if not image_in_table:
                        log.write('Image not found. Adding to table.')
                        # check for question already in table
                        q = Question.query.filter_by(course=d['course'],sitting=d['sitting'],
                            paper=d['paper'], question_number=d['q_no']).first()
                        # question not there: add new question to database
                        if not q:
                            q_type = get_question_type(d['paper'])
                            log.write('Question not found. Adding to table.')
                            q = Question(course=d['course'],sitting=d['sitting'],
                                paper=d['paper'], question_number=d['q_no'],question_type=q_type)
                            db.session.add(q)
                        # now that question is def in table, add child image and commit
                        im = Image(path=path,q_ms=d['q_ms'],question=q)
                        db.session.add(im)
                        db.session.commit()
                    else:
                        log.write('File already in database.')
    return 'Database questions synced.'

def get_data_from_filename(filename):
    # get part of filename before extension
    f = os.path.splitext(filename)[0]
    keys = ['course','sitting','q_ms','paper','Question','q_no']
    values = f.split('_')
    return dict(zip(keys, values))

def get_question_type(paper):
    paper = str(paper[0])
    dict = {
        '1' : 'Multiple Choice',
        '2' : 'Multiple Choice',
        '3' : 'Theory',
        '4' : 'Theory',
        '5' : 'Practical',
        '6' : 'Alternative to Practical'
            }
    return dict.get(paper,"Unknown")

def flush():
    # deletes all records in Question table and Images table
    Image.query.delete()
    Question.query.delete()
    db.session.commit()

def alter_url():
    # removes the 'app' prefix from url of all images
    images = Image.query.all()
    for image in images:
        url = image.path
