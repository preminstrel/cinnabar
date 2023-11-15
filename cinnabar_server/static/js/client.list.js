
$(document).ready(function () {

    url_index = document.getElementById("navIndex").getAttribute("href")
    ApiClientUrl = document.getElementById("clientList").getAttribute("apiurl")


    table = $('#clientList').DataTable({
        paging: true,
        pagingType: 'numbers',
        pageLength: 100,
        ordering: true,
        info: false,
        order: [[0, 'asc']],
        searchDelay: 500,
        stateSave: true,
        dom: '<"d-flex justify-content-between align-items-center"fp>rt<"d-flex justify-content-between align-items-center"lp>',
        ajax: ApiClientUrl,
        columns: [
            {
                data: 'name',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            var icons = "";
                            if (row.status == "offline") {
                                icons = `<i class="bi bi-circle-fill text-danger"> </i>`
                            } else {
                                icons = `<i class="bi bi-circle-fill text-success"> </i>`
                            }

                            return `<div class="d-flex text-nowrap">
                                        ${icons}&nbsp;
                                        <a href="${url_index}client/${data}" class="link-body-emphasis">${data}</a>
                                    </div>`
                        }
                    }
                    return data
                }
            },
            {
                data: 'ip',
                render: function (data, type, row) {
                    if (type === 'display') {
                        return `<span class="text-body-emphasis font-monospace text-nowrap">${data}</span>`
                    }
                    return data;
                },
            },
            {
                data: 'os',
                render: function (data, type) {
                    if (type === 'display') {
                        if (data != null) {
                            if (data.includes('Ubuntu')) {
                            return `<i class="bi bi-ubuntu" style="color: tomato"></i> ${data}`
                            } else if (data.includes('Windows')) {
                                return `<i class="bi bi-windows style="color: blue""></i> ${data}`
                            } else if (data.includes('Mac')) {
                                return `<i class="bi bi-apple"></i> ${data}`}
                              else if (data.includes('Red')) {
                                    return `<svg xmlns="http://www.w3.org/2000/svg" height="1.2em" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><style>svg{fill:#e52a2a}</style><path d="M341.52 285.56c33.65 0 82.34-6.94 82.34-47 .22-6.74.86-1.82-20.88-96.24-4.62-19.15-8.68-27.84-42.31-44.65-26.09-13.34-82.92-35.37-99.73-35.37-15.66 0-20.2 20.17-38.87 20.17-18 0-31.31-15.06-48.12-15.06-16.14 0-26.66 11-34.78 33.62-27.5 77.55-26.28 74.27-26.12 78.27 0 24.8 97.64 106.11 228.47 106.11M429 254.84c4.65 22 4.65 24.35 4.65 27.25 0 37.66-42.33 58.56-98 58.56-125.74.08-235.91-73.65-235.91-122.33a49.55 49.55 0 0 1 4.06-19.72C58.56 200.86 0 208.93 0 260.63c0 84.67 200.63 189 359.49 189 121.79 0 152.51-55.08 152.51-98.58 0-34.21-29.59-73.05-82.93-96.24"/></svg> Red Hat 9.3`}
                            else {
                                return `<i class="bi bi-question-circle"></i> ${data}`
                            }
                        } else {
                            return `<i class="bi bi-pc-display" style="color: orange"></i></i> N/A`;
                        }
                    } 
                    return data;
                },
            },
            {
                data: 'user',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            return `<i class="bi bi-person-circle" style="color: DodgerBlue"></i> ${data}</a>`
                        } else {
                            return `<i class="bi bi-question-circle" style="color: orange"></i> N/A</a>`
                        }
                    }
                    return data;
                },
            },
            {
                data: 'gpu',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            const formattedData = data.replace(/\n/g, '<br>');
                            return `${formattedData}`;
                        } else {
                            return `<i class="bi bi-gpu-card" style="color:orange"></i> N/A`
                        }
                    }
                    return data;
                },
            },
            {
                data: 'cpu',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            return `<i class="bi bi-cpu-fill" style="color: DarkCyan"></i> ${data}</a>`
                        } else {
                            return `<i class="bi bi-cpu-fill" style="color: orange"></i> N/A</a>`
                        }
                    }
                    return data;
                },
            },
            {
                data: 'memory',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            return `<i class="bi bi-memory" style="color: SlateBlue"></i> ${data}</a>`
                        } else {
                            return `<i class="bi bi-memory" style="color: orange"></i> N/A</a>`
                        }
                    }
                    return data;
                },
            },
            {
                data: 'timestamp',
                render: function (data, type) {
                    if (type === 'display') {
                        data = Date.parse(data) / 1000;
                        var now = new Date().getTime() / 1000;
                        var delta = now - data
                        if (data == null) {
                            return "NA"
                        } else if (delta < 60) {
                            return "<1m ago"
                        } else if (delta < 3600) {
                            return (delta / 60).toFixed(0) + "m ago"
                        } else if (delta < 3600 * 24) {
                            return (delta / 3600).toFixed(0) + "h ago"
                        } else {
                            return (delta / 3600 / 24).toFixed(0) + "d ago"
                        }
                    }
                    return data;
                },
            },
        ],
    });
});

