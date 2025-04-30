$(document).ready(function() {
    // Сохраняем изначальные значения полей
    let originalValues = {
        fullname: $('#fullname').text().trim(),
        email: $('#email').text().trim(),
        telegram_id: $('#telegram_id').html().trim()
    };

    // Изменяем обработчик клика для динамически созданных элементов
    $(document).on('click', '#setupButton', function() {
        $('#editProfileModal').modal('show');
    });

    $('#editButton').click(function() {
        if ($(this).text() === 'Редактировать') {
            // Change text fields to input fields
            $('#fullname').html('<input type="text" id="fullnameInput" value="' + originalValues.fullname + '">');
            $('#email').html('<input type="text" id="emailInput" value="' + originalValues.email + '">');
            
            // Добавляем кнопку для Telegram вместо текста
            if ($('#telegram_id').text().trim() === 'Всё настроенно. Можете изменить, нажав кнопку "Редактировать"') {
                $('#telegram_id').html('<button class="btn btn-info" id="setupButton">Изменить</button>');
            }
            
            $('#password').html('<input type="password" id="passwordInput" placeholder="Enter new password">');

            // Change button text to "Save"
            $(this).text('Сохранить');
        } else {
            // Получаем новые значения
            const newFullname = $('#fullnameInput').val().trim();
            const newEmail = $('#emailInput').val().trim();
            const newPassword = $('#passwordInput').val().trim();

            // Проверяем, были ли изменения
            if (newFullname === originalValues.fullname && 
                newEmail === originalValues.email && 
                !newPassword) {
                
                // Показываем сообщение, что ничего не изменилось
                showFlashMessage('Вы не внесли никаких изменений');
                
                // Возвращаем оригинальные значения
                $('#fullname').text(originalValues.fullname);
                $('#email').text(originalValues.email);
                $('#telegram_id').html(originalValues.telegram_id);
                $('#password').text('***');
                
                // Меняем текст кнопки обратно
                $(this).text('Редактировать');
                return;
            }

            // Collect data from input fields
            var userData = {
                fullname: newFullname,
                email: newEmail,
                password: newPassword,
                user_id: $('#user_id').text().trim()
            };

            // Send AJAX request to Flask backend
            $.ajax({
                url: '/edit_profile',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(userData),
                success: function(response) {
                    // Update the text fields with new data
                    $('#fullname').text(response.fullname);
                    $('#email').text(response.email);
                    $('#telegram_id').html(originalValues.telegram_id);
                    $('#password').text('***');

                    // Обновляем оригинальные значения
                    originalValues.fullname = response.fullname;
                    originalValues.email = response.email;

                    // Change button text back to "Edit"
                    $('#editButton').text('Редактировать');
                    
                    showFlashMessage('Данные успешно обновлены');
                },
                error: function(error) {
                    console.error('Error updating user data:', error);
                    // В случае ошибки возвращаем оригинальные значения
                    $('#fullname').text(originalValues.fullname);
                    $('#email').text(originalValues.email);
                    $('#telegram_id').html(originalValues.telegram_id);
                    $('#password').text('***');
                    $('#editButton').text('Редактировать');
                    showFlashMessage('Произошла ошибка при обновлении данных');
                }
            });
        }
    });

    // Функция для показа флеш-сообщения
    function showFlashMessage(message) {
        const flashHtml = `
            <div class="flash-messages">
                <div class="flash-message" style="display: block;">
                    ${message}
                </div>
            </div>`;

        // Удаляем предыдущее сообщение, если оно есть
        $('.flash-messages').remove();
        
        // Добавляем новое сообщение
        $('body').append(flashHtml);

        // Удаляем сообщение через 3 секунды
        setTimeout(function() {
            $('.flash-messages').fadeOut(function() {
                $(this).remove();
            });
        }, 3000);
    }

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
                    // Закрываем модальное окно
                    $('#editProfileModal').modal('hide');
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
        
        alertDiv.removeClass('alert-success alert-danger')
               .addClass(isSuccess ? 'alert-success' : 'alert-danger')
               .text(message);
        
        messageContainer.show();
        
        setTimeout(function() {
            messageContainer.fadeOut();
        }, 5000);
    }
});