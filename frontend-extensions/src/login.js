// Обработка отправки формы
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault(); // Предотвращаем отправку формы

    // Получаем данные из формы
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Очищаем сообщение об ошибке
    document.getElementById('errorMessage').textContent = '';

    try {
        // Отправляем POST-запрос на сервер
        const response = await fetch('http://127.0.0.1:8000/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                { 
                    username: email, 
                    password: password,
                }
            ),
        });

        // Парсим ответ от сервера
        const data = await response.json();

        if (response.ok) {
            // Если вход успешен, перенаправляем пользователя
            window.location.href = './search.html';
        } else {
            if (response.status == 404)
                document.getElementById('errorMessage').textContent = 'Данной учетной записи не существует. Попробуйте зарегистрироваться!';
            if (response.status == 403)
                document.getElementById('errorMessage').textContent = 'Проверьте правильность введенных данных!';
        }
    } catch (error) {
        // Обработка ошибок сети или сервера
        document.getElementById('errorMessage').textContent = 'Ошибка сети. Попробуйте снова.';
        console.error('Ошибка:', error);
    }
});