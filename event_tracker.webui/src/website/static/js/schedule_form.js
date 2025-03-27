function open_form() {
    document.querySelector('.content-section').classList.add('blur');
    document.querySelector('.welcome-section').classList.add('blur');
    const formPopup = document.getElementById('form_popup');
    formPopup.style.display = 'block';
    setTimeout(() => {
        formPopup.classList.add('show');
    }, 10);
}

function close_form() {
    document.querySelector('.content-section').classList.remove('blur');
    document.querySelector('.welcome-section').classList.remove('blur');
    const formPopup = document.getElementById('form_popup');
    formPopup.classList.remove('show');
    setTimeout(() => {
        formPopup.style.display = 'none';
    }, 300);
}

function validateForm() {
    // Очистка предыдущих ошибок
    const errorMessages = document.getElementById('error_messages');
    errorMessages.innerHTML = '';

    // Получение значений из формы
    const eventDate = document.getElementById('event_date').value;
    const eventTime = document.getElementById('event_time').value;
    const eventName = document.getElementById('schedule_form').elements['event_name'].value;

    // Проверка даты
    if (!eventDate) {
        const errorDate = document.createElement('div');
        errorDate.textContent = 'Не введена дата';
        errorMessages.appendChild(errorDate);
        return false; // Останавливаем выполнение, если дата не введена
    }

    // Проверка времени
    if (!eventTime) {
        const errorTime = document.createElement('div');
        errorTime.textContent = 'Не введено время';
        errorMessages.appendChild(errorTime);
        return false; // Останавливаем выполнение, если дата не введена
    }

    // Проверка названия
    if (!eventName) {
        const errorName = document.createElement('div');
        errorName.textContent = 'Не введено название';
        errorMessages.appendChild(errorName);
        return false; // Останавливаем выполнение, если название не введено
    }

    // Если все проверки пройдены, возвращаем true для отправки формы
    return true;
}