import csv
import pyodbc

# Подключение к базе данных 1С
# your_server - ip адрес; your_database - имя бд; your_username - имя пользователя с доступом к бд; your_password - пароль от пользователя
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_username;PWD=your_password')
cursor = conn.cursor()

# Чтение данных из CSV
with open('data.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Пропустить заголовок, если есть
    for row in reader:
        # Предположим, что у вас есть таблица "YourTable" с колонками "Column1", "Column2"
        cursor.execute("INSERT INTO YourTable (Column1, Column2) VALUES (?, ?)", row[0], row[1])

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()