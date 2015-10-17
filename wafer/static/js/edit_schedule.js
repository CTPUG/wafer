(function () {
    'use strict';

    jQuery.event.props.push('dataTransfer');

    var handleDragStart = function (e) {
        e.target.style.opacity = '0.4';  // this / e.target is the source node.
        e.target.classList.add('label-danger');

        //noinspection JSUnresolvedVariable
        e.dataTransfer.effectAllowed = 'move';
        //noinspection JSUnresolvedVariable
        e.dataTransfer.setData('text/plain', this.id);
    };
    var handleDragEnd = function (e) {
        e.target.style.opacity = '1';  // this / e.target is the source node.
        e.target.classList.remove('label-danger');
    };

    function handleDragOver(e) {
        if (e.preventDefault) {
            e.preventDefault(); // Necessary. Allows us to drop.
        }

        //noinspection JSUnresolvedVariable
        e.dataTransfer.dropEffect = 'move';
        return false;
    }

    function handleDragEnter(e) {
        e.target.classList.add('over');
    }

    function handleDragLeave(e) {
        e.target.classList.remove('over');
    }

    function handlePost(data){
        console.log(data);
    }

    function handleDrop(e) {
        // this / e.target is current target element.

        e.target.classList.remove('over');

        if (e.stopPropagation) {
            e.stopPropagation(); // stops the browser from redirecting.
        }

        var slot = e.target.getAttribute('data-slot');
        var venue = e.target.getAttribute('data-venue');

        //noinspection JSUnresolvedVariable
        var data = document.getElementById(
            event.dataTransfer.getData('text/plain'));
        var dataId = data.getAttribute('data-id');
        var dataType = data.getAttribute('data-type');
        var oldTargetType = event.target.getAttribute('data-type');
        var oldTargetId = event.target.getAttribute('data-id');
        event.target.id = data.id;
        event.target.innerHTML = data.getAttribute('title');
        event.target.setAttribute('data-id', dataId);
        event.target.setAttribute('data-type', dataType);
        event.preventDefault();

        var postData = {
            venue: venue, slots:[slot]
        };
        postData[dataType] = dataId;
        var otherDataType = dataType === 'talk' ? 'page' : 'talk';
        postData[otherDataType] = '';

        $.post(
            '/schedule/api/scheduleitems/',
            JSON.stringify(postData), handlePost);


        return false;
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
                xhr.setRequestHeader('Content-Type', 'application/json');
            }
        }
    });

    var draggableItems = document.querySelectorAll('.draggable');
    [].forEach.call(draggableItems, function (draggableItem) {
        draggableItem.addEventListener('dragstart', handleDragStart, false);
        draggableItem.addEventListener('dragend', handleDragEnd, false);
        draggableItem.addEventListener('dragover', handleDragOver, false);
    });

    var droppableItems = document.querySelectorAll('.droppable');
    [].forEach.call(droppableItems, function (droppableItem) {
        droppableItem.addEventListener('dragover', handleDragOver, false);
        droppableItem.addEventListener('dragenter', handleDragEnter, false);
        droppableItem.addEventListener('dragleave', handleDragLeave, false);
        droppableItem.addEventListener('drop', handleDrop, false);
    });
})();
