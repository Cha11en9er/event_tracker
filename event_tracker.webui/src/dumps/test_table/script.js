document.addEventListener('DOMContentLoaded', function() {
    const data = [
        { name: 'ASAP Rocky', email: 'flacko@asapmob.com', date: '03/20/2017', record: 'AT LONG.LAST.ASAP', location: 'NYC, NY', bestSong: 'LSD' },
        { name: 'Brand New', email: 'jesse@brandnewrock.com', date: '12/08/2017', record: 'The Devil and God are Raging In...', location: 'Long Island, NY', bestSong: 'Millstone' },
        { name: 'Childish Gambino', email: 'donald@childishgambino.com', date: '08/06/2017', record: 'Because The Internet', location: 'Atlanta, GA', bestSong: '3005' },
        // Add more data as needed
    ];

    const tableBody = document.querySelector('#dataTable tbody');
    const searchInput = document.querySelector('#searchInput');
    const paginationInfo = document.querySelector('#paginationInfo');
    const prevPage = document.querySelector('#prevPage');
    const nextPage = document.querySelector('#nextPage');
    const pageNumbers = document.querySelector('#pageNumbers');

    let currentPage = 1;
    const rowsPerPage = 7;

    function renderTable(data) {
        tableBody.innerHTML = '';
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const pageData = data.slice(start, end);

        pageData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.name}</td>
                <td>${row.email}</td>
                <td>${row.date}</td>
                <td>${row.record}</td>
                <td>${row.location}</td>
                <td>${row.bestSong}</td>
                <td><button class="btn btn-danger btn-sm">Delete</button></td>
            `;
            tableBody.appendChild(tr);
        });

        paginationInfo.textContent = `Showing ${start + 1} to ${Math.min(end, data.length)} of ${data.length} entries`;
    }

    function filterData(query) {
        return data.filter(item =>
            item.name.toLowerCase().includes(query) ||
            item.email.toLowerCase().includes(query) ||
            item.record.toLowerCase().includes(query)
        );
    }

    function updatePagination(data) {
        const totalPages = Math.ceil(data.length / rowsPerPage);
        pageNumbers.innerHTML = '';

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.classList.add('page-item');
            const a = document.createElement('a');
            a.classList.add('page-link');
            a.href = '#';
            a.textContent = i;
            a.addEventListener('click', () => {
                currentPage = i;
                renderTable(data);
            });
            li.appendChild(a);
            pageNumbers.appendChild(li);
        }

        prevPage.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderTable(data);
            }
        });

        nextPage.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderTable(data);
            }
        });
    }

    searchInput.addEventListener('input', function() {
        const query = searchInput.value.toLowerCase();
        const filteredData = filterData(query);
        currentPage = 1; // Reset to first page on new search
        renderTable(filteredData);
        updatePagination(filteredData);
    });

    renderTable(data);
    updatePagination(data);
});
