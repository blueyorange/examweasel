$(document).ready(function()
{
    // ************** FILE CLASS ********************************************
    class File {
        constructor($panel) {
            this.name="New Document 1";
            this.question_array=[];
            this.changed=false;
            this.id = null;
            this.$filename = $panel.find( $('span.filename') );
            this.$filename.text(this.name);
            this.$list = $panel.find( $('ul.questionlist') );
            this.$list.droppable( {
                // question can be dropped into document
                drop: function( event, ui ) {
                    // get dropped object
                    var $question = $(ui.draggable);
                    console.log(`Question element: ${ ui.draggable }`);
                    // do nothing if question is a copy already in document list
                    if ($question.hasClass('copy')) {
                        return;
                    }
                    // File has been changed
                    file.file_changed = true;
                    // get droppable object <ul>
                    console.log('question dropped');
                    // add question to document (this droppable)
                    file.addQuestion($question);
                }
            });
            // Allow user selected questions to be sortable (drag to change order)
            this.$list.sortable({});
        }

        update() {
            this.question_array = this.$list.sortable("toArray").map(parseId)
            console.log(`List updated: ${this.question_array}`)
        }

        saveLocally() {
            this.update()
            localStorage.setItem('current_file_id',this.id);
        }

        saveToServer(data) {
            // update question_list to reflect sortable list
            this.update();
            // serialise question list
            var id_string = JSON.stringify(this.question_array);
            data = data + '&ids=' + this.question_array + '&file_id=' + this.id;
            console.log(`Sending: ${data}`);
            var $filename = this.$filename;
            $.post('/index', data, function(data) {
                console.log(data);
                $filename.html(data['filename']);
                this.id = data['file_id'];
                // File has been saved
                this.file_changed = false;
            });
        };

        addQuestion($question) {
            // adds question list item object to document list
            // create copy of question so that original stays in list
            // make sure copy is still clickable by setting 'withDataAndEvents' to true
            var id = $question.attr('id');
            console.log(`Adding question ${id} to list.`);
            // get integer id of dropped draggable question
            var qid = parseId( id );
            // clone original question
            var $question_copy = $question.clone(true);
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
            this.$list.append( $question_copy );
            // add trash glyphicon to clone
            const trashHTML = '<a href="#" class="trash"><span class="glyphicon glyphicon-trash"></span></a>';
            $question_copy.append(trashHTML)
            // set trash icon to remove item from list
            $('.trash').click( (event) => {
                var qid=parseId(event.currentTarget.parentElement.id);
                this.remove(qid);
            })
        }   

        loadFromServer(id) {
            // get filename and question_list from server with AJAX
            file = this;
            console.log(file)
            $.getJSON(`${$SCRIPT_ROOT}load_file`, {
                id: id
            }, function(data) {

                console.log("File received "+data.filename)
                // update visible filename in document window
                file.name = data.filename;
                file.$filename.text(data.filename)
                // clear list of questions
                file.clear();
                // update question list
                file.question_array = data.question_list;
                console.log(`Adding questions to document list: ${file.question_array}`);
                // Add each question from array into visible list as list items
                file.question_array.forEach( (qid) => {
                    id = "#question_" + qid;
                    var $element = $(id);
                    file.addQuestion($element)
                })
                // store file id locally
                file.saveLocally();
            });
        }

        remove(qid) {
            // Remove question from list
            console.log(`question ${qid} removed`)
            // destroy cloned question element
            $(`#document_${qid}`).remove();
            // remove disabled class from original question element
            $(`#question_${qid}`).removeClass('disabled');
            // restore draggable property of original question
            $(`#question_${qid}`).draggable('enable');
            // File has been changed
            this.update();
            this.file_changed = true;
        }

        clear() {
            this.question_array.forEach( (item) => this.remove(item) )
        }
    }

    // check for file in localstorage
    file_id = localStorage.getItem('current_file_id');
    $panel = $('div#panel-template');
    file = new File($panel);
    if (file_id) {
        console.log(`Retrieved file id ${file_id}`)
        file.loadFromServer(file_id);
    }
    else {
        console.log("No file stored locally.")
    }

    // new file button
    $('a#newFileButton').click( (e) => {
        e.preventDefault();
        console.log("New file button clicked")
        if (file.changed) {
            // show save changes modal dialog if true
            $('#savecurrentfiledialog').modal('show');
        } else {
            localStorage.removeItem('current_file_id');
            window.location.reload();
        }
    })

    // Setup buttons on save changes dialog
    $('#savefile').click( (e) => {
        var ids = getQuestionIDs();
        // retrieve current file id from browser
        var file_id = localStorage.getItem('current_file_id')
        save_file_to_server(ids, file_id);
    });
    $('#discardchanges').click( (event) => {
        // Discard changes: hide this dialog
        $('#savecurrentfiledialog').modal('hide');
    });
    $('#cancelload').click( (event) => {
        $('#savecurrentfiledialog').modal('hide');
        $('#loadwindow').modal('hide');
    });

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
                $('div#questionview').html(`<img src="${url}"></img>"`);
            })
        }
    });

    // allow questions to be dragged
    $('.question').draggable( {
        helper: 'clone',
        cursor: 'pointer'
    });

    // ********************** TABS *************************************
    $( "#tabs" ).tabs();

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
            file.file_changed = true;
            // get droppable object <ul>
            console.log('question dropped');
            // add question to document (this droppable)
            file.addQuestion($question);
        }
    });

    // ***********************SAVE***********************************
    $('a.saveButton').click( function(e) {
        e.preventDefault();
        console.log("Save button clicked.")
        // check file not empty
        file.update();
        if ( !file.question_array.length ) {
            console.log("Array empty.")
            alert("Please add at least one question before saving or downloading.");
        }
        else {
            $('div#saveWindow').modal('show');
        }
    });

    $('#saveForm').on('submit', function(e) {
        // prevent form from sending by default method and save file
        e.preventDefault();
        // append question ids to form data for submission
        file.filename = $('input#filename').val();
        console.log(file.filename);
        var data = $('#saveForm').serialize()
        file.saveToServer(data);
    });

    // ****************LOAD*******************************************
    $('#loadButton').click( function(e) {
        e.preventDefault();
        // load button clicked: get list of files available from server
        $.ajax({
            url: `${$SCRIPT_ROOT}get_file_list`,
            type: 'GET',
            success: (data) => {
                // fill in table with html for table body containing files list from database
                $('#load_table_body').html(data);
                // make file icons clickable and load file if clicked
                $("[id^='file'").click(function (event) {
                    // get file id
                    var file_id = event.target.id.split('_')[1];
                    console.log("Loading file " + file_id);
                    file.loadFromServer(file_id);
                    // hide modal window when file is loaded
                    $('#loadWindow').modal('hide');
                });
                // show modal load window
                $('#loadWindow').modal('show');
            },
            error: function(data) {
                console.log("Server error.")
                alert("Server error!");
                // hide modal load window
                $('#loadWindow').modal('hide');
            }
        })
    });
    
    
    function parseId( id ) {
        // takes full string id and returns parsed integer id after '_'
        return parseInt(id.split('_')[1])
    }

});

