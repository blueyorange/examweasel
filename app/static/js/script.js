$(document).ready(function()
{
    // any changes to file this is set to true
    var file_changed = false;

    // Display image when li is clicked on
    $(".question").click(function()
    {
        // remove all active classes when clicked
        $(".question.active").removeClass("active");
        // activate question as selected if not already done so
        // and send result to server
        if(!$(this).hasClass('active'))
        {
            $(this).addClass('active');
            var id = $(this).attr('id');
            var qid = parseId( id );
            // ajax request to server
            $.getJSON(`${$SCRIPT_ROOT}get_image`, {
                // send question id
                question_id: qid
            }, (url) => {
                // display image of new question using returned url
                console.log(url);
                $('#questionview').html(`<img src="${url}" id="question-img"></img"`);
            })
        }
    });

    // allow questions to be dragged
    $('.question').draggable( {
        helper: 'clone',
        cursor: 'pointer'
    });

    // Allow user selected questions to be sortable (drag to change order)
        $('ul#userdocument').sortable({
            }
        );

    $('ul#userdocument').droppable( {
        // question can be dropped into document
        drop: function( event, ui ) {
            // get dropped object
            var $question = $(ui.draggable);
            // do nothing if question is a copy already in document list
            if ($question.hasClass('copy')) {
                return;
            }
            // File has been changed
            file_changed = true;
            // get droppable object <ul>
            console.log('question dropped');
            // add question to document (this droppable)
            addQuestionToList($question,$(this))
        }
    });
    
    function addQuestionToList($question, $document) {
        // adds question list item object to document list
        // create copy of question so that original stays in list
        // make sure copy is still clickable by setting 'withDataAndEvents' to true
        var id = $question.attr('id');
        console.log('Dropped: ',id);
        // get integer id of dropped draggable question
        var qid = parseId( id );
        // clone original question
        var $question_copy = $question.clone(withDataAndEvents=true);
        $question_copy.addClass('copy');
        $question_copy.removeClass('active');
        if ($question.draggable() ) {
            // destroy draggable behaviour of original
            $question.draggable('disable');
        }
        // 'gray out' original question
        $question.addClass('disabled');
        // set id for cloned element as document_#
        var clone_id = ['document',qid].join('_')
        $question_copy.attr('id',clone_id);
        // add clone to document list
        $document.append( $question_copy );
        // add trash glyphicon to clone
        const trashHTML = '<a href="#" class="trash"><span class="glyphicon glyphicon-trash"></span></a>';
        $question_copy.append(trashHTML)
        // set trash icon to remove item from list
        $('.trash').click( (event) => {
            var qid=parseId(event.currentTarget.parentElement.id);
            removeQuestion(qid);
        })
    }

    // Remove question from list
    function removeQuestion(qid) {
        console.log(`question ${qid} removed`)
        // destroy cloned question element
        $(`#document_${qid}`).remove();
        // remove disabled class from original question element
        $(`#question_${qid}`).removeClass('disabled');
        // restore draggable property of original question
        $(`#question_${qid}`).draggable('enable');
        // File has been changed
        file_changed = true;
    }
    // This is used by addQuestionToList and saveform functions to get numerical ids
    function parseId( id ) {
        // takes full string id and returns parsed integer id after '_'
        return parseInt(id.split('_')[1])
    }


    $('#saveForm').on('submit', function(e) {
        // prevent form from sending by default method
        e.preventDefault();
        save_file_to_server();
    })

    function save_file_to_server() {
        // get question ids
        ids = getQuestionIDs();
        var id_string = JSON.stringify(ids);
        console.log(id_string);
        // retrieve current file id from browser
        var file_id = localStorage.getItem('current_file_id')
        console.log('Retrieved file id: '+file_id);
        // append question ids to form data for submission
        // data = $('#saveForm').serialize() + '&ids=[' + ids + ']';
        data = $('#saveForm').serialize() + '&ids=' + id_string + '&file_id=' + file_id; 
        console.log(data);
        $.post('/index', data, function(data) {
            console.log(data);
            $('span#filename').html(data['filename']);
            // store file ID in local storage so that further saves write to the same 
            // database entry
            localStorage.setItem('current_file_id',data['file_id']);
            // File has been saved
            file_changed = false;
        });
    }

    function getQuestionIDs() {
        return $('ul#userdocument').sortable("toArray").map(parseId);
    }

    // ****************LOAD BUTTON CLICKED**************************************
    $('#loadButton').click(function(event) {
        event.preventDefault();
        // load button clicked: get list of files available from server
        $.ajax({
            url: `${$SCRIPT_ROOT}get_file_list`,
            type: 'GET',
            success: function(data) {
                // fill in table with html for table body containing files list from database
                $('#load_table_body').html(data);
                // make file icons clickable and load file if clicked
                $("[id^='file'").click(function(event) {
                    var file_id = event.target.id.split('_')[1]
                    console.log("Loading file " + file_id);
                    load_file_from_server(file_id);
                    // Check if current file has been changed
                    if (file_changed) {
                        saveChanges();
                    };
                });
                // show modal load window
                $('#loadWindow').modal('show');
            },
            error: function(data) {
                console.log("Server error.")
                alert("Server error!");
            }
        })
    })

    // ***************************LOAD FILE FROM SERVER**************************
    function load_file_from_server(id) {
        // get filename and question_list from server with AJAX
        $.getJSON(`${$SCRIPT_ROOT}load_file`, {
            id: id
        }, function(file) {
            // hide modal load window
            $('#loadWindow').modal('hide');
            console.log("File received "+file.filename)
            // update visible filename in document window
            $('span#filename').text(file.filename)
            // remove all question elements from list
            getQuestionIDs().forEach( (item) => removeQuestion(item) )
            // update question list
            var questions = file.question_list;
            console.log(`Adding questions to document list: ${questions}`);
            questions.forEach( (id) => {
                id = "#question_" + id;
                $element = $(id);
                addQuestionToList($element,$('ul#userdocument'))
            })
        });
    }

    // **********************SAVE CHANGES DIALOG****************************
    function saveChanges() {
        // show 'save changes?' dialog
        $('#savecurrentfiledialog').modal('show');
        $('#savefile').click( save_file_to_server() );
        $('#discardchanges').click( (event) => {
            // Discard changes: hide this dialog
            $('#savecurrentfiledialog').modal('hide');
        });
        $('#cancelload').click( (event) => {
            $('#savecurrentfiledialog').modal('hide');
            $('#loadwindow').modal('hide');
        });
    }
});