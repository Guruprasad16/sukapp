$(document).ready(function () {
    var currentSheet;
    var selectedColumn;
    $('#upload-form').on('submit', function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: formData,
            contentType: false,
            processData: false,
            success: function (sheets) {
                $('#sheet-selection').empty();
                sheets.forEach(function(sheet) {
                    $('#sheet-selection').append(new Option(sheet, sheet));
                });
                $('#sheet-selection, #submit-sheet').removeClass('hidden');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

    $('#submit-sheet').on('click', function(e) {
        document.getElementById("uploadDiv").classList.add("hidden");
        e.preventDefault();
        currentSheet = $('#sheet-selection').val();
        $.ajax({
            url: '/sheet',
            type: 'POST',
            data: JSON.stringify({ sheet: currentSheet }),
            contentType: 'application/json',
            success: function(data) {
                var table = $('#column-selection');
                table.empty();
                var headers = data.column_names;
                var rows = data.data_preview;
                var thead = $('<thead>');
                headers.forEach(function(header) {
                    thead.append('<th>' + header + '</th>');
                });
                table.append(thead);
                rows.forEach(function(row) {
                    var tr = $('<tr>');
                    headers.forEach(function(header) {
                        tr.append('<td>' + row[header] + '</td>');
                    });
                    table.append(tr);
                });
                $('#column-selection, #submit-column').removeClass('hidden');
            }
        });
    });

    $('#column-selection').on('click', 'th', function() {
        selectedColumn = $(this).text();
        $(this).siblings().removeClass('bg-primary text-white');
        $(this).addClass('bg-primary text-white');
    });

    $('#submit-column').on('click', function() {
        $.ajax({
            url: '/column',
            type: 'POST',
            data: JSON.stringify({ sheet: currentSheet, column: selectedColumn }),
            contentType: 'application/json',
            success: function(response) {
                if (response.status === 'success') {
                    window.location.href = '/unique_values';
                }
            }
        });
    });
});
