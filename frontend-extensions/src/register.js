// Обработка отправки формы
document.getElementById('registerForm').addEventListener('submit', async function (e) {
    e.preventDefault(); // Предотвращаем отправку формы

    // Получаем данные из формы
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const repeatPassword = document.getElementById('repeatPassword').value;

    // Очищаем сообщение об ошибке
    document.getElementById('errorMessage').textContent = '';

    // Проверка, что пароли совпадают
    if (password !== repeatPassword) {
        document.getElementById('errorMessage').textContent = 'Пароли не совпадают';
        return;
    }

    try {
        // Отправляем POST-запрос на сервер
        const response = await fetch('http://127.0.0.1:8000/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                username: email,
                password: password,
                }),
        });

        // Парсим ответ от сервера
        const data = await response.json();

        if (response.ok) {
            // Если регистрация успешна, перенаправляем пользователя
            window.location.href = '../search.html';
        } else {
            // Если регистрация неудачна, выводим сообщение об ошибке
            document.getElementById('errorMessage').textContent = data.message || 'Ошибка регистрации';
        }
    } catch (error) {
        // Обработка ошибок сети или сервера
        document.getElementById('errorMessage').textContent = 'Ошибка сети. Попробуйте снова.';
        console.error('Ошибка:', error);
    }
});