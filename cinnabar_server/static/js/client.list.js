
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

