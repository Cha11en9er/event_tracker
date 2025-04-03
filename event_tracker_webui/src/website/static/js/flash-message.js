document.addEventListener("DOMContentLoaded", function() {
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        message.style.display = 'block'; // Показываем сообщение
        setTimeout(function() {
            message.style.opacity = '0'; // Плавное исчезновение
            setTimeout(function() {
                message.style.display = 'none'; // Скрываем сообщение
            }, 500); // Задержка перед скрытием
        }, 3000); // 3000 миллисекунд = 3 секунды
    });
});