// Открываем оверлей
cart_items = []

document.getElementById('openOverlay').addEventListener('click', function() {
    const overlay = document.getElementById('overlay');

    overlay.classList.add('active');
});

// Закрываем оверлей
document.getElementById('closeOverlay').addEventListener('click', function() {
    const overlay = document.getElementById('overlay');
    overlay.classList.remove('active');
});


function parseItems(cart_items) {
    result = ``;

    for (const item of cart_items) {
        index = cart_items.indexOf(item);
        result += `
                    <div class="cart-item">
                        <div class="item-details">
                            <h3>Ноутбук</h3>
                            <p>Цена: 50 000 ₽</p>
                            <div class="quantity-controls">
                                <button id="quantity-btn" onclick="updateQuantity(1, -1)">-</button>
                                <span class="quantity" id="quantity-${item.id}">${item.quantity}</span>
                                <button id="quantity-btn" onclick="updateQuantity(1, 1)">+</button>
                            </div>
                            <button id="remove-btn" onclick="removeItem(1)">Удалить</button>
                        </div>
                    </div>
        `
    }

    return result;
}

async function addToCart(productId, quantity) {
    const response = await fetch('http://127.0.0.1:8000/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity }),
    })
    .then(response => response.json())
    .then(data => {
        cart_items.push(data);
        console.log(data);
    });
}

function removeFromCart(productId, quantity) {
    fetch('http://127.0.0.1:8000/cart/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Товар добавлен в корзину:', data);
    });
}

// Цены товаров
const prices = {
    1: 50000, // Ноутбук
    2: 30000, // Смартфон
};

// Обновление количества товара
function updateQuantity(productId, change) {
    const quantityElement = document.getElementById(`quantity-${productId}`);
    let quantity = parseInt(quantityElement.textContent);
    quantity += change;

    if (quantity < 1) quantity = 1; // Минимальное количество
    quantityElement.textContent = quantity;

    calculateTotal();
}

// Удаление товара
function removeItem(productId) {
    const itemElement = document.querySelector(`.cart-item:nth-child(${productId})`);
    if (itemElement) {
        itemElement.remove();
        calculateTotal();
    }
}

// Расчет общей стоимости
function calculateTotal() {
    let total = 0;
    document.querySelectorAll(".cart-item").forEach((item) => {
        const productId = item.querySelector(".quantity").id.split("-")[1];
        const quantity = parseInt(item.querySelector(".quantity").textContent);
        total += prices[productId] * quantity;
    });

    document.getElementById("total-price").textContent = total.toLocaleString();
}

// Инициализация расчета при загрузке страницы
window.onload = calculateTotal;