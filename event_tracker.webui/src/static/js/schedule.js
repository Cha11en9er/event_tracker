function fetchData() {
    $.ajax({
        url: '/get_schedule_data',
        type: 'GET',
        success: function(data) {
            var display = $('#schedule_data');
            display.empty();
            data.forEach(function(item) {
                var row = $('<tr class="table_row"></tr>').click(function() {
                    window.location.href = '/current_event/' + item.event_id;
                });
                row.append($('<td></td>').text(item.event_date));
                row.append($('<td></td>').text(item.event_name));
                row.append($('<td></td>').text(item.event_disc));
                row.append($('<td></td>').text(item.event_type));
                row.append($('<td></td>').text(item.participation_count));
                var sybscribe_button = $('<button></button>')
                .text('Подписаться')
                .click(function() {
                    $.ajax({
                        url: '/subscribe_to_event',
                        type: 'POST',
                        data: {
                            event_id_from_js: item.event_id,
                            user_id_from_js: item.user_id
                        },
                        success: function() {
                            alert('Вы подписались на ' + item.event_name);
                        },
                        error: function() {
                            alert('Вы уже являетесь участником ' + item.event_name);
                        }
                    });
                }); 
                // var more_button = $('<button></button>')
                // .text('Подробнее');

                var unsubscribe_button = $('<button></button>')
                .text('Отписаться')
                .click(function() {
                    $.ajax({
                        url: '/unsubscribe_from_event',
                        type: 'POST',
                        data: {
                            event_id_from_js: item.event_id,
                            user_id_from_js: item.user_id
                        },
                        success: function() {
                            alert('Вы отписались от ' + item.event_name)
                        },
                        error: function() {
                            alert('Вы не были подписаны на ' + item.event_name)
                        }
                    })
                })
                row.append($('<td></td>').append(sybscribe_button, unsubscribe_button));

                display.append(row);
            });
        },
        error: function() {
            $('#schedule_data').html('<tr><td colspan="4">Ошибка при загрузке данных.</td></tr>');
        }
    });
}

$(document).ready(function() {
    fetchData();
    setInterval(fetchData, 5000);
});