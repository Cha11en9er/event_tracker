
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
            setTimeout(() => {
                $('#event_popup').modal('hide');
            }, 2000); // Закрыть модальное окно через 2 секунды
        } else {
            alert('Не удалось отправить уведомление');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке уведомления');
    });
}