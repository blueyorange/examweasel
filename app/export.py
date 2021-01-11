import docx
from os import getcwd, path

def word(questions):
    '''Takes in a list of path names to images to return Word
    Doc with images of questions and mark schemes.
    questions: a list in form [{"q",[path,...]},{"ms",[path,...},...]'''
    filepath = os.path.join(os.getcwd(),'static/downloads/','New_Document.docx')
    doc = docx.Document()
    resource_types = {'q','ms'}
    headings = {'q' : '' ,'ms' : "Mark Schemes"}
    # Create table with two columns and 'number of questions' rows
    for resource_type in resource_types:
        # Add heading if necessary
        if headings[resource_type]:
            doc.add_heading(headings[resource_type], 0)
        table = doc.add_table(rows=questions.len(),cols=2)
        for question in questions:
            row_cells = table.add_row().cells
            row_cells[0].add_paragraph( str(question.index()).join('.') )
            paragraph = row_cells[1].add_paragraph()
            run = paragraph.add_run()
            run.add_picture(question['q'])
    
    doc.save(filepath)