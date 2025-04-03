
function open_event_form() {
    document.getElementById('current_event_main').classList.add('blur');
    const formPopup = new bootstrap.Modal(document.getElementById('event_popup'));
    formPopup.show();
}

function close_event_form() {
    document.getElementById('current_event_main').classList.remove('blur');
    const formPopup = bootstrap.Modal.getInstance(document.getElementById('event_popup'));
    formPopup.hide();
}

function updateNotificationTime(time) {
    document.getElementById('notif_time').value = time;
}

function show_notif_result() {
    document.getElementById('notification_result').style.display = 'block';
}

function save_and_submit_notif() {
    const form = document.getElementById('notificationForm');
    const formData = new FormData(form);

    fetch(form.action, {
        method: form.method,
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            show_notif_result();
        } else {
            alert('Не удалось отправить уведомление');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке уведомления');
    });
}

function subscribeToEvent(button) {
    const userId = button.getAttribute('data-user-id');
    const eventId = button.getAttribute('data-event-id');

    console.log(eventId)

    const formData = new FormData();
    formData.append('event_id_from_js', eventId);
    formData.append('user_id_from_js', userId);

    fetch('/subscribe_to_event', {
        method: 'POST',
        body: formData
    })
}

function unSubscribeToEvent(button) {
    const userId = button.getAttribute('data-user-id');
    const eventId = button.getAttribute('data-event-id');

    console.log(eventId)

    const formData = new FormData();
    formData.append('event_id_from_js', eventId);
    formData.append('user_id_from_js', userId);

    fetch('/unsubscribe_from_event', {
        method: 'POST',
        body: formData
    })
}