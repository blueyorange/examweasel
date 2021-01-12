import docx
from os import getcwd, path
from flask import current_app

def word(questions):
    '''Takes in a list of path names to images to return Word
    Doc with images of questions and mark schemes.
    questions: a list in form [{"q",[path,...]},{"ms",[path,...},...]'''
    print(questions)
    filename = 'New_Document.docx'
    filepath = current_app.config['DOWNLOAD_FOLDER']
    # Create word document object
    doc = docx.Document()
    resource_types = {'qp','ms'}
    headings = {'qp' : '' ,'ms' : "Mark Schemes"}
    # Create table with two columns and 'number of questions' rows
    for resource_type in resource_types:
        # Add heading if necessary
        if headings[resource_type]:
            doc.add_heading(headings[resource_type], 0)
        table = doc.add_table(rows=len(questions),cols=2)
        for question in questions:
            row_cells = table.add_row().cells
            row_cells[0].add_paragraph( str(questions.index(question)).join('.'))
            paragraph = row_cells[1].add_paragraph()
            paths = question[resource_type]
            if paths:
                for path in paths:
                    print(path)
                    run = paragraph.add_run()
                    run.add_picture(path)
    doc.save(filepath)
    return filename
