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

    function handleItemUpdate(data) {
        console.log(data);
        var scheduleItemId = data.id;
        var venue = data.venue;
        var slots = data.slots;
        var talkId = data.talk;
        var pageId = data.page;
        var scheduleItemType;

        if (talkId) {
            scheduleItemType = 'talk';
        } else if (pageId) {
            scheduleItemType = 'page';
        }

        var newItem = document.querySelectorAll('[id=scheduleItemnull]')[0];

        newItem.id = 'scheduleItem' + scheduleItemId;
    }


    function handleItemDelete() {
        console.log(this);
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
        var scheduleItemId = data.getAttribute('data-scheduleitem-id');
        var scheduleItemType = data.getAttribute('data-type');
        event.target.innerHTML = data.getAttribute('title');
        event.target.setAttribute('data-schedule-item-id', scheduleItemId);
        event.target.setAttribute('data-type', scheduleItemType);
        event.target.id = 'scheduleItem' + scheduleItemId;
        event.preventDefault();

        var talkId = '';
        var pageId = '';

        if (scheduleItemType === 'talk') {
            talkId = data.getAttribute('data-talk-id');
        } else if (scheduleItemType === 'page') {
            pageId = data.getAttribute('data-page-id');
        }

        event.target.classList.remove('success');
        event.target.classList.remove('info');
        var typeClass = scheduleItemType === 'talk' ? 'success' : 'info';
        event.target.classList.add(typeClass);

        var ajaxData = {
            talk: talkId,
            page: pageId
        };
        if (scheduleItemId) {
            $.ajax({
                method: 'PATCH',
                url: '/schedule/api/scheduleitems/' + scheduleItemId + '/',
                data: JSON.stringify(ajaxData),
                success: handleItemUpdate
            });
        } else {
            ajaxData.venue = venue;
            ajaxData.slots = [slot];
            console.log(ajaxData);
            $.post(
                '/schedule/api/scheduleitems/',
                JSON.stringify(ajaxData), handleItemUpdate);
        }

        return false;
    }

    function handleClickDelete(mouseEvent) {
        var closeButton = mouseEvent.path[1];
        var scheduleItemCell = mouseEvent.path[2];

        var scheduleItemId = closeButton.getAttribute('data-id');

        scheduleItemCell.removeAttribute('id');
        scheduleItemCell.classList.remove('draggable');
        scheduleItemCell.classList.remove('info');
        scheduleItemCell.classList.remove('success');
        scheduleItemCell.removeAttribute('data-scheduleitem-id');
        scheduleItemCell.removeAttribute('data-talk-id');
        scheduleItemCell.removeAttribute('data-page-id');
        scheduleItemCell.removeAttribute('data-type');

        closeButton.removeAttribute('data-id');
        closeButton.classList.add('hide');
        scheduleItemCell.innerHTML = '';

        $.ajax(
            {
                type: 'DELETE',
                url: '/schedule/api/scheduleitems/' + scheduleItemId + '/',
                success: handleItemDelete
            }
        );
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

    var deletableItems = document.querySelectorAll('[id^=delete]');
    [].forEach.call(deletableItems, function (deletableItem) {
        deletableItem.addEventListener('click', handleClickDelete, false);
    });
})();
