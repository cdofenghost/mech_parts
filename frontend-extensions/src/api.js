document.getElementById('vinForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const vin = document.getElementById('vin').value;
    const responseDiv = document.getElementById('response');
    const responseDiv2 = document.getElementById('response2');

    try {
        const response = await fetch('http://127.0.0.1:8000/search/car_info_by_vin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ vin }),
        });

        const data = await response.json();

        responseDiv.innerHTML = `
        <label for="collapse1" class="collapse-button"><b>${data['brand']} ${data['model']}</b></label>
        <input type="checkbox" id="collapse1" class="collapse-checkbox">

        <div class="collapse-content">
            <p><b>Полное название:</b> ${data['model_detail']}</p>
            <p><b>Год модели по VIN:</b> ${data['model_year_from_vin']}</p>
            <p><b>Год модели:</b> ${data['model_year']}</p>
            <p><b>Бренд:</b> ${data['brand']}</p>
            <p><b>Модель:</b> ${data['model']}</p>
            <p><b>Серия:</b> ${data['series']}</p>
            <p><b>Завод:</b> ${data['factory']}</p>
            <p><b>Лошадиных сил:</b> ${data['horse_power']}</p>
            <p><b>Киловатт:</b> ${data['kilowatt']}</p>
            <p><b>Лошадиных сил:</b> ${data['horse_power']}</p>
            <p><b>Киловатт:</b> ${data['kilowatt']}</p>
            <p><b>Вместимость:</b> ${data['capacity']}</p>
        </div>
        `;

        const response2 = await fetch('http://127.0.0.1:8000/search/get_all_part_numbers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ epc: data['epc'], vin: data['vin_id']}),
        });

        const data2 = await response2.json();
        
        responseDiv2.innerHTML = `
        <label for="collapse2" class="collapse-button"><b>Подходящие детали</b></label>
        <input type="checkbox" id="collapse2" class="collapse-checkbox">

        <div class="collapse-content">
            <div class="items">
            ${await parseParts(data2['numbers'])}
            </div>
        </div>


        `;
    } catch (error) {
        responseDiv.innerHTML = `Ошибка: ${error.message}`;
    }
});

async function parseParts(part_list) {
    result = `
        <style>
            .collapse-content  {
                overflow-y: auto;
            }
        </style>
    `;
    counter = 1;
    for (const item of part_list) {
        counter += 1
        if (counter > 10) {
            break;
        }
        index = part_list.indexOf(item);
        console.log(item);
        try {
            const response = await fetch('http://127.0.0.1:8000/search/part_info_by_number', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query_part_number: item,  query_match_type: "smart" }),
            });
    
            const data = await response.json();
            console.log(JSON.stringify(data));
            result += `
        <label for="collapse${index+3}" class="collapse-button"><b>${data['name']}</b></label>
        <input type="checkbox" id="collapse${index+3}" class="collapse-checkbox">

        <div class="collapse-content">
            <img src=http://resource.17vin.com/img/${data['img_src']} height=100 width=100>
            <p><b>Имя: </b>${data['name']}</p>
            <p><b>Имя бренда: </b>${data['brand_name']}</p>
            <p><b>Средняя цена: </b>${data['price']}₽</p>
            <button id="add-to-cart">Добавить в корзину</button>
        </div>
            `;
        } catch (error) {
            console.log(`Ошибка: ${error.message}`);
        }
    };
    return result;
}

// Обработка формы для номера детали
document.getElementById('partForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const qpn = document.getElementById('partNumber').value;
    const responseDiv = document.getElementById('response');

    try {
        const response = await fetch('http://127.0.0.1:8000/search/part_info_by_number', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query_part_number: qpn,  query_match_type: "smart" }),
        });

        const data = await response.json();
        responseDiv.innerHTML = `
        <style>
            .collapse-content  {
                overflow-y: auto;
            }
        </style>
        <label for="collapse1" class="collapse-button"><b>${data['name']}</b></label>
        <input type="checkbox" id="collapse1" class="collapse-checkbox">

        <div class="collapse-content">
            <img src=http://resource.17vin.com/img/${data['img_src']} height=100 width=100>
            <p><b>Имя: </b>${data['name']}</p>
            <p><b>Имя бренда: </b>${data['brand_name']}</p>
            <p><b>Средняя цена: </b>${data['price']}₽</p>
            <button id="add-to-cart">Добавить в корзину</button>
        </div>
        `;
    } catch (error) {
        responseDiv.innerHTML = `Ошибка: ${error.message}`;
    }
});
