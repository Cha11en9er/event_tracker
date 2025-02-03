function open_form() {
    document.getElementById('schedule_main').classList.add('blur');
    const formPopup = document.getElementById('form_popup');
    formPopup.classList.add('show'); // Добавляем класс для плавного появления
}

function close_form() {
    document.getElementById('schedule_main').classList.remove('blur');
    const formPopup = document.getElementById('form_popup');
    formPopup.classList.remove('show'); // Удаляем класс для скрытия
}