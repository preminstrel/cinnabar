function formatTimestamp(ts) {
    function digi2(num) {
        return (String(num).length == 1 ? '0' : '') + num;
    }
    const dateObj = new Date(ts);

    var YY = dateObj.getFullYear();
    var MM = digi2(dateObj.getMonth() + 1);
    var DD = digi2(dateObj.getDate());
    var hh = digi2(dateObj.getHours());
    var mm = digi2(dateObj.getMinutes());
    var ss = digi2(dateObj.getSeconds());

    return `${YY}-${MM}-${DD} ${hh}:${mm}`
}

function formatSeconds(seconds) {
    if (seconds > 3600) {
        h = parseInt(seconds / 3600)
        m = parseInt(seconds % 3600 / 60)
        return `${h}h${m}min`
    } else if (seconds > 60) {
        return `${parseInt(seconds / 60)}min`
    } else {
        return `<1min`
    }
}

$(document).ready(function () {

    url_index = document.getElementById("navIndex").getAttribute("href")
    ApiTaskUrl = document.getElementById("taskList").getAttribute("apiurl")


    table = $('#taskList').DataTable({
        paging: true,
        pagingType: 'numbers',
        pageLength: 100,
        ordering: true,
        info: false,
        order: [[0, 'desc']],
        searchDelay: 500,
        stateSave: true,
        dom: '<"d-flex justify-content-between align-items-center"fp>rt<"d-flex justify-content-between align-items-center"lp>',
        ajax: ApiTaskUrl,
        columns: [
            {
                data: 'id',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            return `<div class="d-flex"><input name="id" value="${data}" type="checkbox" class="form-check-input me-1" id="taskSel${row.id}"/><label class="form-check-label" for="taskSel${row.id}"><a href="${url_index}task/${data}" class="link-body-emphasis">${data}</a></label></div>`
                        }
                    }
                    return data
                }
            },
            {
                data: 'title',
                render: function (data, type) {
                    if (type === 'display') {
                        if (data != null) {
                            return `<div class="d-flex text-nowrap">
                                        ${data}
                                    </div>`
                        }
                    }
                    return data
                }
            },
            {
                data: 'client',
                render: function (data, type) {
                    if (type === 'display') {
                        if (data != null) {
                            return `<div class="d-flex text-nowrap">
                            <i class="bi bi-pc-display" style="color: DodgerBlue"></i>&nbsp;<a href="${url_index}client/${data}" class="link-body-emphasis">${data}</a>
                                    </div>`
                        }
                    }
                    return data
                }
            },
            {
                data: 'status',
                render: function (data, type, row) {
                    if (type == 'display') {
                        if (data == 'ONGOING') {
                            return `<span class="badge text-bg-warning">ONGOING</span>`
                        } else if (data == 'FINISH') {
                            return `<span class="badge text-bg-success">FINISH</span>`
                        } else if (data == 'QUEUE') {
                            return `<span class="badge text-bg-primary">QUEUE</span>`
                        }
                    }
                    return `${data}`
                }
            },
            {
                data: 'start_time',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data != null) {
                            // calculate test time
                            if (row.end_time != null) {
                                var time = (new Date(row.end_time) - new Date(data))/1000
                                return `<span class="text-body-emphasis font-monospace text-nowrap">${formatTimestamp(data)}</span>
                                <small class="d-none d-lg-inline text-body-secondary font-monospace">(${formatSeconds(time)})</small>`
                            } else {
                                return `<span class="text-body-emphasis font-monospace text-nowrap">${formatTimestamp(data)}</span>`
                            }
                        }
                        return null
                    }
                    return `${formatTimestamp(data)}`
                }
            },
            {
                data: 'result',
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data == null) {
                            return null
                        } else if (data == 'PASS') {
                            var color = "success";
                        } else if (data == 'FAIL') {
                            var color = "danger";
                        } else {
                            var color = "secondary"
                        }
                        return `<span class="badge text-bg-${color} opacity-75 me-1">${data}</span>
                                <small class="d-none d-lg-inline text-body-secondary text-nowrap"></small>`
                    }
                    return data;
                },
            },
        ],
    });
});

$("#taskDelete").click(function (event) {

    // find ids to delete
    var idCheckBoxes = document.querySelectorAll('[name="id"]');
    var ids = [];
    for (i in idCheckBoxes) {
        if (idCheckBoxes[i].checked) {
            ids.push(idCheckBoxes[i].value)
        }
    }

    // delete tasks
    $.ajax({
        type: "POST",
        url: `/api/task/`,
        data: JSON.stringify({
            "id": ids,
            "action": "delete",
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (resp) {
            alert(resp.message)
            location.reload()
        },
        error: function (resp) {
            console.log(`API ERROR: delete`);
        }
    });
})

$("#taskDuplicate").click(function (event) {

    // find ids to delete
    var idCheckBoxes = document.querySelectorAll('[name="id"]');
    var ids = [];
    for (i in idCheckBoxes) {
        if (idCheckBoxes[i].checked) {
            ids.push(idCheckBoxes[i].value)
        }
    }

    // duplicate tasks
    $.ajax({
        type: "POST",
        url: `/api/task/`,
        data: JSON.stringify({
            "id": ids,
            "action": "duplicate",
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (resp) {
            alert(resp.message)
            location.reload()
        },
        error: function (resp) {
            console.log(`API ERROR: task duplicate`);
        }
    });
})