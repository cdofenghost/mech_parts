// Обработка формы для VIN-кода
document.getElementById('vinForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const vin = document.getElementById('vin').value;
    const responseDiv = document.getElementById('response');

    try {
        const response = await fetch('/methods/get_car_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ vin }),
        });

        const data = await response.json();
        responseDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
        responseDiv.innerHTML = `Ошибка: ${error.message}`;
    }
});

// Обработка формы для номера детали
document.getElementById('partForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const qpn = document.getElementById('qpn').value;
    const responseDiv = document.getElementById('response');

    try {
        const response = await fetch('/methods/get_part_by_qpn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query_part_number: qpn,  query_match_type: "smart" }),
        });

        const data = await response.json();
        responseDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
        responseDiv.innerHTML = `Ошибка: ${error.message}`;
    }
});
