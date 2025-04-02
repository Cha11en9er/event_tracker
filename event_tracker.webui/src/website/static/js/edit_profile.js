$(document).ready(function() {
    $('#editButton').click(function() {
        if ($(this).text() === 'Редактировать') {
            // Change text fields to input fields
            $('#fullname').html('<input type="text" id="fullnameInput" value="' + $('#fullname').text().trim() + '">');
            $('#email').html('<input type="text" id="emailInput" value="' + $('#email').text().trim() + '">');
            $('#telegram_id').html('<input type="text" id="telegramIdInput" value="' + $('#telegram_id').text().trim() + '">');
            $('#password').html('<input type="password" id="passwordInput" placeholder="Enter new password">');

            // Change button text to "Save"
            $(this).text('Сохранить');
        } else {
            // Collect data from input fields
            var userData = {
                fullname: $('#fullnameInput').val().trim(),
                email: $('#emailInput').val().trim(),
                telegram_id: $('#telegramIdInput').val().trim(),
                password: $('#passwordInput').val().trim(),
                user_id: $('#user_id').text().trim()
            };

            // Send AJAX request to Flask backend
            $.ajax({
                url: '/edit_profile',  // Flask route
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(userData),
                success: function(response) {
                    // Update the text fields with new data
                    $('#fullname').text(response.fullname);
                    $('#email').text(response.email);
                    $('#telegram_id').text(response.telegram_id);
                    $('#password').text('***');

                    // Change button text back to "Edit"
                    $('#editButton').text('Редактировать');
                },
                error: function(error) {
                    console.error('Error updating user data:', error);
                }
            });
        }
    });
});

$(document).ready(function() {
    // Открытие модального окна при нажатии на кнопку "Настроить"
    $('#setupButton').click(function() {
        $('#editProfileModal').modal('show');
    });

    // Обработка отправки формы для проверки Telegram ID
    $('#saveNotificationSettings').click(function() {
        const chatId = $('#telegramIdInput').val().trim();
        const messageContainer = $('#messageContainer');
        const alertDiv = messageContainer.find('.alert');
        
        if (!chatId) {
            showMessage('Пожалуйста, введите ID чата', false);
            return;
        }

        $.ajax({
            url: '/verify_telegram_id',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ chat_id: chatId }),
            success: function(response) {
                showMessage(response.message, response.success);
                if (response.success) {
                    // Обновляем отображение Telegram ID на странице
                    $('#telegram_id').text(chatId);
                }
            },
            error: function(xhr, status, error) {
                showMessage('Произошла ошибка при проверке ID чата', false);
            }
        });
    });

    function showMessage(message, isSuccess) {
        const messageContainer = $('#messageContainer');
        const alertDiv = messageContainer.find('.alert');
        
        // Устанавливаем класс и текст сообщения
        alertDiv.removeClass('alert-success alert-danger')
               .addClass(isSuccess ? 'alert-success' : 'alert-danger')
               .text(message);
        
        // Показываем контейнер
        messageContainer.show();
        
        // Скрываем сообщение через 5 секунд
        setTimeout(function() {
            messageContainer.fadeOut();
        }, 5000);
    }
});