from app import db
from app.models import Image
from os import walk,path

def sync_questions():
    log = open('log.txt','w')
    # syncs question table with images in question folder
    root='app/static/images/questions/'
    ext = '.png'
    for (parent,dirs,files) in walk(root, topdown=True):
        if files:
            for f in files:
                log.write(f+'/n')
                # check extension of file is '.png'
                if path.splitext(f)[1] == ext:
                    # split path into parent path, paper
                    (parent_path,paper) = path.split(parent)
                    year = path.split(parent)[1]
                    path_to_file = path.join(parent,f)
                    # check to see if already in image table
                    image_in_table = Image.query.filter_by(path=path_to_file)
                    #log.write(str(image_in_table))
                    if not image_in_table:
                        log.write('Image not found. Adding to table.')
                        # check for question already in table
                        q = Question.query.filter_by(paper=paper,year=year).first()
                        if not q:
                           log('Question not found. Adding to table.')
                           q = Question(paper=paper,year=year)
                           db.session.add(q)
                        i = Image(path=path_to_file,question=q)
                        db.session.add(im)
                        db.session.commit()
        return 'Database questions synced.'

def flush():
    # deletes all records in Question table
    Question.query.delete()
    db.session.commit()

sync_questions()