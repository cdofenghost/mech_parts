from openpyxl import Workbook
from database import get_orders  # Предполагаем, что есть функция для получения заказов

def export_orders_to_excel():
    """Экспортирует заказы в Excel и сохраняет файл."""
    orders = get_orders()  # Получаем заказы из БД
    if not orders:
        return None  # Если заказов нет, не создаем файл

    wb = Workbook()
    ws = wb.active
    ws.title = "Заказы"

    # Заголовки
    ws.append(["Пользователь", "VIN/номер детали", "Статус", "Дата"])

    # Данные заказов
    for order in orders:
        ws.append([
            order.user.email,
            order.products,
            order.status,
            order.created_at.strftime("%Y-%m-%d %H:%M:%S")  # Приводим дату в читаемый формат
        ])

    file_path = "orders.xlsx"
    wb.save(file_path)
    return file_path

if __name__ == "__main__":
    file = export_orders_to_excel()
    if file:
        print(f"Файл успешно создан: {file}")
    else:
        print("Нет данных для экспорта.")
