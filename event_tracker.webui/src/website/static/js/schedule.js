var currentPage = 1;
var itemsPerPage = 6;
var allData = [];

$(document).ready(function() {
    fetchData();
    $('#search-form').submit(searchEvent);
});

function fetchData() {
    $.ajax({
        url: '/get_schedule_data',
        type: 'GET',
        success: function(data) {
            allData = data;
            renderTable();
            renderPagination();
        },
        error: function() {
            console.error('Ошибка при получении данных расписания');
        }
    });
}

function searchEvent(event) {
    event.preventDefault(); // Предотвращаем стандартную отправку формы
    var searchInfo = $('.search-input').val();

    $.ajax({
        url: '/get_search_event',
        type: 'GET',
        data: { search_info: searchInfo },
        success: function(data) {
            allData = data;
            currentPage = 1; // Сброс текущей страницы при поиске
            renderTable();
            renderPagination();
        },
        error: function() {
            console.error('Ошибка при выполнении поиска');
        }
    });
}

function renderTable() {
    var display = $('#schedule_data');
    display.empty();

    var startIndex = (currentPage - 1) * itemsPerPage;
    var endIndex = startIndex + itemsPerPage;
    var paginatedData = allData.slice(startIndex, endIndex);

    paginatedData.forEach(function(item) {
        var row = $('<tr class="table_row"></tr>').click(function() {
            window.location.href = '/current_event/' + item.event_id + '?date=' + item.event_date + '&datetime=' + item.datetime + '&time=' + item.event_time + '&name=' + encodeURIComponent(item.event_name) + '&disc=' + encodeURIComponent(item.event_disc);
        });
        row.append($('<td></td>').text(item.event_name));
        row.append($('<td class="disc_row"></td>').text(item.event_disc));
        row.append($('<td></td>').text(item.event_date));
        row.append($('<td></td>').text(item.event_type));
        row.append($('<td></td>').text(item.participation_count));

        function check_subscribe(number, arrayOfArrays) {
            return arrayOfArrays.some(innerArray => innerArray.includes(number));
        }

        var subscribeButton, unsubscribeButton;

        if (check_subscribe(item.event_id, item.user_participation)) {
            unsubscribeButton = $('<button class="btn btn-danger"></button>')
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
            row.append($('<td></td>').append(unsubscribeButton));
        } else {
            subscribeButton = $('<button class="btn btn-success"></button>')
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
            row.append($('<td></td>').append(subscribeButton));
        }

        display.append(row);
    });
}

function renderPagination() {
    var pagination = $('#pagination');
    pagination.empty();

    var totalPages = Math.ceil(allData.length / itemsPerPage);

    var paginationGroup = $('<div class="btn-group"></div>');

    for (var i = 1; i <= totalPages; i++) {
        var pageButton = $('<button type="button" class="btn btn-outline-secondary"></button>').text(i).click(function() {
            currentPage = parseInt($(this).text());
            renderTable(); // Обновляем таблицу при смене страницы
        });
        paginationGroup.append(pageButton);
    }

    pagination.append(paginationGroup);
}
