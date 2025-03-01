$(document).ready(function() {
    // Открытие модального окна
    $('#openModalButton').click(function() {
        open_event_form();
    });

    // Закрытие модального окна
    $('#event_popup').on('hidden.bs.modal', function () {
        close_event_form();
    });
});

function open_event_form() {
    document.getElementById('current_event_main').classList.add('blur');
    const formPopup = new bootstrap.Modal(document.getElementById('event_popup'));
    formPopup.show(); // Используем метод Bootstrap для открытия модального окна
}

function close_event_form() {
    document.getElementById('current_event_main').classList.remove('blur');
    // Здесь не нужно скрывать модальное окно, так как это уже делает Bootstrap
}

$(document).ready(function() {
    $('#saveNotification').click(function() {
        var telegramId = this.getAttribute('data-telegram-id');
        var userId = this.getAttribute('data-user-id');
        var selectedTime = $('input[name="notificationTime"]:checked').val();
        var messageElement = $('#telegramMessage');

        console.log(telegramId, userId, selectedTime)

        if (typeof telegramId !== 'string' || telegramId.trim() === "None" || telegramId.trim() === "") {
            messageElement.removeClass('alert-success').addClass('alert-danger');
            messageElement.html(`Telegram id не указан. Это можно сделать в 
                <a href="{{ url_for('user_page.user_page', user_id_from_form=${userId}) }}">профиле</a>.`);
        } else {
            messageElement.removeClass('alert-danger').addClass('alert-success');
            messageElement.text('Мы вас оповестим через ' + selectedTime + ' минут.');
            
        }
        // Показываем сообщение
        messageElement.show();
    });
});