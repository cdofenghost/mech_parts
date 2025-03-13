async function getCarInfo() {
    const vin = document.getElementById('vinInput').value;

    if (!vin) {
        alert('Пожалуйста, введите VIN-код.');
        return;
    }

    try {
        const response = await fetch('/methods/get_car_info/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ vin: vin })
        });

        if (!response.ok) {
            throw new Error('Ошибка при получении данных');
        }

        const data = await response.json();
        document.getElementById('result').innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('result').innerText = 'Произошла ошибка при запросе к серверу.';
    }
}
