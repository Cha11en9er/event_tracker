var socket = io();
var currentPage = 1;
var itemsPerPage = 6;
var allData = [];

function fetchData() {
    socket.emit('request_schedule_data');
}

socket.on('schedule_data', function(data) {
    allData = data; // Сохраняем все данные
    renderTable();
    renderPagination();
});

function renderTable() {
    var display = $('#schedule_data');
    display.empty();
    
    // Вычисляем индекс начала и конца для текущей страницы
    var startIndex = (currentPage - 1) * itemsPerPage;
    var endIndex = startIndex + itemsPerPage;
    var paginatedData = allData.slice(startIndex, endIndex); // Получаем данные для текущей страницы

    paginatedData.forEach(function(item) {
        var row = $('<tr class="table_row"></tr>').click(function() {
            window.location.href = '/current_event/' + item.event_id + '?date=' + item.event_date + '&name=' + encodeURIComponent(item.event_name);
        });
        row.append($('<td></td>').text(item.event_date));
        row.append($('<td></td>').text(item.event_name));
        row.append($('<td class="disc_row"></td>').text(item.event_disc));
        row.append($('<td></td>').text(item.event_type));
        row.append($('<td></td>').text(item.participation_count));
        
        var subscribeButton = $('<button></button>')
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

        var unsubscribeButton = $('<button></button>')
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
                        alert('Вы отписались от ' + item.event_name);
                    },
                    error: function() {
                        alert('Вы не были подписаны на ' + item.event_name);
                    }
                });
            });

        row.append($('<td></td>').append(subscribeButton, unsubscribeButton));
        display.append(row);
    });
}

function renderPagination() {
    var pagination = $('#pagination');
    pagination.empty();
    
    var totalPages = Math.ceil(allData.length / itemsPerPage);
    
    for (var i = 1; i <= totalPages; i++) {
        var pageButton = $('<button></button>').text(i).click(function() {
            currentPage = parseInt($(this).text());
            renderTable(); // Обновляем таблицу при смене страницы
        });
        pagination.append(pageButton);
    }
}

$(document).ready(function() {
    fetchData();
});