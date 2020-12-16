$(document).ready(function()
{
    function parseId( id ) {
        // takes full string id and returns parsed integer id after '_'
        return parseInt(id.split('_')[1])
    }

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
        $('.trash').click(function() {
            console.log('question removed')
            // destroy cloned question element
            $(this).parent().remove();
            // remove disabled class from original question element
            $(`#question_${qid}`).removeClass('disabled')
            // restore draggable property of original question
            $(`#question_${qid}`).draggable('enable');
        })
    }

    $('#saveForm').on('submit', function(e) {
        e.preventDefault();
        // get question ids
        var ids = $('ul#userdocument').sortable("serialize");
        console.log(ids)
        // append question ids to form data for submission
        data = $('#saveForm').serialize() + '&' + ids
        console.log(data);
        $.post('/index', data, function() {
            $('#saveWindow').modal('hide');
        });
    })
});