import math  # Математические операции (округление)
import sqlite3  # Работа с базой данных SQLite
import tkinter as tk  # Графический интерфейс
from datetime import datetime, timedelta  # Работа с датой и временем
from tkinter import messagebox, simpledialog, ttk  # Диалоговые окна и виджеты

# Создаем или подключаемся к базе данных
conn = sqlite3.connect('scrap_metal.db')  # Подключение к файлу БД
cursor = conn.cursor()  # Создание курсора для выполнения SQL-запросов

# Создаем таблицу для хранения данных о металлоломе
cursor.execute('''
CREATE TABLE IF NOT EXISTS metals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    metal_type TEXT,                      
    weight REAL,                           
    price REAL,                            
    total REAL,                            
    date_time TEXT                         
)
''')
conn.commit()  # Сохранение изменений в БД


class ScrapMetalApp:
    def __init__(self, root):
        self.root = root  # Главное окно приложения
        self.root.title("Прием Металлолома")  # Заголовок окна

        # Доступные виды металла (список для выбора)
        self.metal_options = ["Медь", "Калорифер", "Латунь", "Нержавейка", "Алюминий",
                              "Аккумуляторы", "Банки пивные", "Цам", "Свинец", "Медь луженая", "Чер. мет.", "Другой"]

        # Переменная для выбора количества позиций (по умолчанию 1)
        self.num_positions_var = tk.IntVar(value=1)

        # Поля для хранения информации по каждой позиции
        self.entries = []  # Список для хранения переменных позиций
        self.widgets = []  # Список для хранения виджетов позиций

        # Общая сумма всех позиций
        self.total_sum_var = tk.DoubleVar(value=0)

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создает основные элементы интерфейса"""
        # Поле для выбора количества позиций
        tk.Label(self.root, text="Количество позиций:").grid(row=0, column=0)
        self.num_positions_menu = ttk.Combobox(self.root, textvariable=self.num_positions_var,
                                               values=list(range(1, 11)))  # Выбор от 1 до 10 позиций
        self.num_positions_menu.grid(row=0, column=1)
        # Привязка события выбора к созданию полей позиций
        self.num_positions_menu.bind("<<ComboboxSelected>>", lambda event: self.create_position_fields())

        # Кнопка для добавления записи в БД
        tk.Button(self.root, text="Клиент посчитан!", command=self.add_records).grid(row=1, column=0, columnspan=2,
                                                                                     pady=(10, 0))

        # Кнопка для очистки базы данных
        tk.Button(self.root, text="Очистить базу данных", command=self.clear_database).grid(row=2, column=0,
                                                                                            columnspan=2, pady=(10, 0))

        # Кнопка для отображения последних транзакций
        tk.Button(self.root, text="Последние транзакции", command=self.show_last_transactions).grid(row=3, column=0,
                                                                                                    columnspan=2,
                                                                                                    pady=(10, 0))

        # Кнопка для отображения статистики
        tk.Button(self.root, text="Статистика", command=self.show_statistics).grid(row=4, column=0, columnspan=2,
                                                                                   pady=(10, 0))

        # Кнопка для редактирования транзакции
        tk.Button(self.root, text="Редактировать транзакцию", command=self.edit_transaction).grid(row=5, column=0,
                                                                                                  columnspan=2,
                                                                                                  pady=(10, 0))

        # Кнопка для удаления транзакции
        tk.Button(self.root, text="Удалить транзакцию", command=self.delete_transaction).grid(row=6, column=0,
                                                                                              columnspan=2,
                                                                                              pady=(10, 0))

        # Изначально создаем поля для одной позиции
        self.create_position_fields()

        # Поле для отображения общей суммы (только для чтения)
        tk.Label(self.root, text="Общая сумма:").grid(row=7, column=0)
        tk.Entry(self.root, textvariable=self.total_sum_var, state="readonly").grid(row=7, column=1)

    def create_position_fields(self):
        """Создает поля ввода для каждой позиции металла"""
        # Очистка старых виджетов, если количество позиций было изменено
        for widget in self.widgets:
            widget.grid_forget()  # Скрытие виджетов
        self.widgets.clear()  # Очистка списка виджетов

        # Создаем новые поля на основе выбранного количества позиций
        self.entries = []  # Очистка списка позиций
        num_positions = self.num_positions_var.get()  # Получение количества позиций

        for i in range(num_positions):
            row_offset = i + 8  # Смещение строки для размещения виджетов

            # Выбор типа металла
            tk.Label(self.root, text=f"Позиция {i + 1}: Вид металла").grid(row=row_offset, column=0)
            metal_var = tk.StringVar()  # Переменная для хранения выбранного металла
            metal_menu = ttk.Combobox(self.root, textvariable=metal_var, values=self.metal_options)
            metal_menu.grid(row=row_offset, column=1)

            # Поле для ввода веса
            weight_var = tk.DoubleVar()  # Переменная для хранения веса
            tk.Label(self.root, text="Вес (кг):").grid(row=row_offset, column=2)
            weight_entry = tk.Entry(self.root, textvariable=weight_var)
            weight_entry.grid(row=row_offset, column=3)

            # Поле для ввода цены
            price_var = tk.DoubleVar()  # Переменная для хранения цены
            tk.Label(self.root, text="Цена за кг:").grid(row=row_offset, column=4)
            price_entry = tk.Entry(self.root, textvariable=price_var)
            price_entry.grid(row=row_offset, column=5)

            # Поле для отображения суммы (только для чтения)
            total_var = tk.DoubleVar()  # Переменная для хранения суммы
            tk.Label(self.root, text="Сумма:").grid(row=row_offset, column=6)
            total_entry = tk.Entry(self.root, textvariable=total_var, state="readonly")
            total_entry.grid(row=row_offset, column=7)

            # Обновление суммы при изменении веса или цены
            weight_entry.bind("<KeyRelease>",
                              lambda event, w=weight_var, p=price_var, t=total_var: self.calculate_total(w, p, t))
            price_entry.bind("<KeyRelease>",
                             lambda event, w=weight_var, p=price_var, t=total_var: self.calculate_total(w, p, t))

            # Сохраняем переменные и виджеты для каждой позиции
            self.entries.append((metal_var, weight_var, price_var, total_var))
            self.widgets.extend([metal_menu, weight_entry, price_entry, total_entry])

    def calculate_total(self, weight_var, price_var, total_var):
        """Рассчитывает сумму для конкретной позиции"""
        try:
            weight = weight_var.get()  # Получение веса
            price = price_var.get()  # Получение цены
            total = math.floor(weight * price)  # Округление вниз до целого числа
            total_var.set(total)  # Установка рассчитанной суммы
            self.update_total_sum()  # Обновление общей суммы
        except tk.TclError:  # Обработка ошибок ввода
            total_var.set(0)  # Установка нуля при ошибке

    def update_total_sum(self):
        """Вычисляет общую сумму всех позиций"""
        total_sum = sum(total_var.get() for _, _, _, total_var in self.entries)  # Суммирование всех позиций
        self.total_sum_var.set(total_sum)  # Установка общей суммы

    def add_records(self):
        """Добавляет все записи в базу данных"""
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Текущая дата и время

        for metal_var, weight_var, price_var, total_var in self.entries:
            metal_type = metal_var.get()  # Тип металла
            weight = weight_var.get()  # Вес
            price = price_var.get()  # Цена
            total = total_var.get()  # Сумма

            # Проверка на заполненность полей
            if metal_type and weight > 0 and price > 0:
                # Вставка данных в БД
                cursor.execute('''
                INSERT INTO metals (metal_type, weight, price, total, date_time)
                VALUES (?, ?, ?, ?, ?)
                ''', (metal_type, weight, price, total, date_time))

        conn.commit()  # Сохранение изменений в БД
        messagebox.showinfo("Успех", "Записи добавлены!")

        # Сбросить количество позиций к значению по умолчанию
        self.num_positions_var.set(1)
        self.create_position_fields()  # Пересоздание полей

    def clear_database(self):
        """Очищает всю базу данных"""
        # Запрашиваем подтверждение на очистку базы данных
        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите очистить базу данных? Это действие удалит все записи."):
            cursor.execute("DELETE FROM metals")  # Удаление всех записей
            conn.commit()  # Сохранение изменений
            messagebox.showinfo("Успех", "База данных успешно очищена!")

    def show_last_transactions(self):
        """Показывает последние 10 транзакций"""
        # Создаем новое окно для последних транзакций
        transactions_window = tk.Toplevel(self.root)
        transactions_window.title("Последние транзакции")

        # Заголовки таблицы
        tk.Label(transactions_window, text="ID").grid(row=0, column=0)
        tk.Label(transactions_window, text="Дата/Время").grid(row=0, column=1)
        tk.Label(transactions_window, text="Вид металла").grid(row=0, column=2)
        tk.Label(transactions_window, text="Вес (кг)").grid(row=0, column=3)
        tk.Label(transactions_window, text="Цена за кг").grid(row=0, column=4)
        tk.Label(transactions_window, text="Сумма").grid(row=0, column=5)

        # Получение последних 10 записей из БД
        cursor.execute('''
            SELECT id, metal_type, weight, price, total, date_time 
            FROM metals 
            ORDER BY id DESC 
            LIMIT 10
        ''')
        records = cursor.fetchall()  # Получение всех записей

        # Отображение записей в таблице
        for i, (record_id, metal_type, weight, price, total, date_time) in enumerate(records):
            tk.Label(transactions_window, text=record_id).grid(row=i + 1, column=0)
            tk.Label(transactions_window, text=date_time).grid(row=i + 1, column=1)
            tk.Label(transactions_window, text=metal_type).grid(row=i + 1, column=2)
            tk.Label(transactions_window, text=f"{weight:.2f} кг").grid(row=i + 1, column=3)
            tk.Label(transactions_window, text=f"{price:.2f}").grid(row=i + 1, column=4)
            tk.Label(transactions_window, text=f"{total:.2f}").grid(row=i + 1, column=5)

    def show_statistics(self):
        """Показывает статистику за выбранный период"""
        # Установка периода по умолчанию (последний час)
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Форматирование временных меток для отображения
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        # Создание окна для статистики
        statistics_window = tk.Toplevel(self.root)
        statistics_window.title("Статистика")

        # Поля для ввода периода
        tk.Label(statistics_window, text="Начало периода:").grid(row=0, column=0)
        start_entry = tk.Entry(statistics_window)
        start_entry.insert(0, start_time_str)  # Установка значения по умолчанию
        start_entry.grid(row=0, column=1)

        tk.Label(statistics_window, text="Конец периода:").grid(row=1, column=0)
        end_entry = tk.Entry(statistics_window)
        end_entry.insert(0, end_time_str)  # Установка значения по умолчанию
        end_entry.grid(row=1, column=1)

        # Кнопка для получения статистики
        tk.Button(statistics_window, text="Получить статистику",
                  command=lambda: self.fetch_statistics(start_entry.get(), end_entry.get(), statistics_window)).grid(
            row=2, column=0, columnspan=2)

        # Заголовки для таблицы статистики
        tk.Label(statistics_window, text="Металл").grid(row=3, column=0)
        tk.Label(statistics_window, text="Общий вес").grid(row=3, column=1)
        tk.Label(statistics_window, text="Общая сумма").grid(row=3, column=2)

    def fetch_statistics(self, start_time_str, end_time_str, statistics_window):
        """Получает статистику из БД за указанный период"""
        try:
            # Преобразование строк в объекты datetime
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

            # SQL-запрос для получения статистики по типам металлов
            cursor.execute('''
                SELECT metal_type, SUM(weight), SUM(total) 
                FROM metals 
                WHERE date_time BETWEEN ? AND ?
                GROUP BY metal_type
            ''', (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))
            stats = cursor.fetchall()  # Получение статистики

            # Очистка предыдущих результатов
            for widget in statistics_window.grid_slaves():
                if widget.grid_info()["row"] > 3:
                    widget.grid_forget()  # Удаление старых данных

            # Отображение новой статистики
            for i, (metal_type, total_weight, total_sum) in enumerate(stats):
                tk.Label(statistics_window, text=metal_type).grid(row=i + 4, column=0)
                tk.Label(statistics_window, text=f"{total_weight:.2f} кг").grid(row=i + 4, column=1)
                tk.Label(statistics_window, text=f"{total_sum:.2f}").grid(row=i + 4, column=2)

            if not stats:  # Если данных нет
                messagebox.showinfo("Информация", "Нет данных за указанный период.")

        except ValueError:  # Обработка ошибок формата даты
            messagebox.showerror("Ошибка",
                                 "Пожалуйста, введите даты и время в корректном формате (ГГГГ-ММ-ДД ЧЧ:ММ:СС).")

    def edit_transaction(self):
        """Редактирует существующую транзакцию"""
        # Запрос ID транзакции для редактирования
        transaction_id = simpledialog.askinteger("Редактирование", "Введите ID транзакции для редактирования:")
        if not transaction_id:  # Если ID не введен
            return

        # Получение записи из БД
        cursor.execute('SELECT metal_type, weight, price, total FROM metals WHERE id = ?', (transaction_id,))
        record = cursor.fetchone()  # Получение одной записи

        if record:
            # Создание окна редактирования
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактирование транзакции")

            # Установка текущих значений
            metal_var = tk.StringVar(value=record[0])
            weight_var = tk.DoubleVar(value=record[1])
            price_var = tk.DoubleVar(value=record[2])
            total_var = tk.DoubleVar(value=record[3])

            # Поля для редактирования
            tk.Label(edit_window, text="Вид металла").grid(row=0, column=0)
            metal_menu = ttk.Combobox(edit_window, textvariable=metal_var, values=self.metal_options)
            metal_menu.grid(row=0, column=1)

            tk.Label(edit_window, text="Вес (кг)").grid(row=1, column=0)
            weight_entry = tk.Entry(edit_window, textvariable=weight_var)
            weight_entry.grid(row=1, column=1)

            tk.Label(edit_window, text="Цена за кг").grid(row=2, column=0)
            price_entry = tk.Entry(edit_window, textvariable=price_var)
            price_entry.grid(row=2, column=1)

            tk.Label(edit_window, text="Сумма").grid(row=3, column=0)
            total_entry = tk.Entry(edit_window, textvariable=total_var, state="readonly")
            total_entry.grid(row=3, column=1)

            # Обновление суммы при изменении
            weight_entry.bind("<KeyRelease>", lambda event: self.calculate_total(weight_var, price_var, total_var))
            price_entry.bind("<KeyRelease>", lambda event: self.calculate_total(weight_var, price_var, total_var))

            # Кнопка сохранения
            save_button = tk.Button(edit_window, text="Сохранить",
                                    command=lambda: self.save_transaction(transaction_id, metal_var, weight_var,
                                                                          price_var, total_var, edit_window))
            save_button.grid(row=4, column=0, columnspan=2)
        else:
            messagebox.showerror("Ошибка", "Транзакция не найдена.")

    def save_transaction(self, transaction_id, metal_var, weight_var, price_var, total_var, edit_window):
        """Сохраняет изменения в транзакции"""
        # Получение новых значений
        metal_type = metal_var.get()
        weight = weight_var.get()
        price = price_var.get()
        total = total_var.get()

        # Проверка корректности данных
        if metal_type and weight > 0 and price > 0:
            # Обновление записи в БД
            cursor.execute('''
                UPDATE metals 
                SET metal_type = ?, weight = ?, price = ?, total = ?, date_time = ? 
                WHERE id = ?
            ''', (metal_type, weight, price, total, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), transaction_id))
            conn.commit()  # Сохранение изменений

            messagebox.showinfo("Успех", "Транзакция успешно обновлена!")
            edit_window.destroy()  # Закрытие окна редактирования
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля корректными значениями.")

    def delete_transaction(self):
        """Удаляет транзакцию по ID"""
        # Запрос ID транзакции
        transaction_id = simpledialog.askinteger("Удаление", "Введите ID транзакции для удаления:")
        if transaction_id is None:  # Если ID не введен
            return

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение удаления",
                               f"Вы уверены, что хотите удалить транзакцию с ID {transaction_id}?"):
            cursor.execute("DELETE FROM metals WHERE id = ?", (transaction_id,))  # Удаление записи
            conn.commit()  # Сохранение изменений
            messagebox.showinfo("Успех", "Транзакция успешно удалена!")


if __name__ == "__main__":
    root = tk.Tk()  # Создание главного окна
    app = ScrapMetalApp(root)  # Создание экземпляра приложения
    root.mainloop()  # Запуск главного цикла приложения