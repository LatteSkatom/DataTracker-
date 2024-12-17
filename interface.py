import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt



class DataTracker:

    def __init__(self, root):


        try:
            if not os.path.exists('analiz.db'):
                raise sqlite3.OperationalError("Database file not found")

            self.conn = sqlite3.connect('analiz.db')
            self.cursor = self.conn.cursor()

        except sqlite3.OperationalError as e:
            messagebox.showerror("Ошибка", "Ошибка подключения к базе данных. Проверьте файл базы данных.")
            self.conn = None
            self.cursor = None  # проверка на соединение
            return

        self.root = root
        self.root.title("DataTracker")
        self.root.minsize(400, 300)
        self.root.configure(bg="#E5E5E5")




        self.root.resizable(False, False)


        # Подключение к  базе данных
        self.conn = sqlite3.connect('analiz.db')
        self.cursor = self.conn.cursor()



            # Инициализация классов для управления данными
        self.user_management = UserManagement(self.conn)
        self.achievements_manager = Achievements(self.conn)
        self.statistics_manager = Statistics(self.conn)

            # Хранение текущего user_id и роли
        self.current_user_id = None
        self.current_user_role = None

            # Заголовок
        self.label = tk.Label(root, text="DataTracker", font=("Arial", 16), bg="#E5E5E5")
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

            # Ввод уровня
        self.level_label = tk.Label(root, text="Введите уровень:", font=("Arial", 14), bg="#E5E5E5")
        self.level_label.grid(row=1, column=0, sticky='w', padx=10)

        self.level_entry = tk.Entry(root, bg="#E5E5E5", font=("Arial", 14))
        self.level_entry.grid(row=1, column=1, padx=10, sticky='ew')
        self.level_entry.config(state='disabled')  # Отключаем поле ввода

            # Ввод очков
        self.score_label = tk.Label(root, text="Введите количество очков:", font=("Arial", 14), bg="#E5E5E5")
        self.score_label.grid(row=2, column=0, sticky='w', padx=10)

        self.score_entry = tk.Entry(root, bg="#E5E5E5", font=("Arial", 14))
        self.score_entry.grid(row=2, column=1, padx=10, sticky='ew')
        self.score_entry.config(state='disabled')  # Отключаем поле ввода

            # Кнопка для добавления данных
        self.add_button = tk.Button(root, text="Добавить данные", command=self.add_data,
                                        width=20, height=2, bg="#8B8378", fg="black", font=("Arial", 12))
        self.add_button.grid(row=3, column=0, columnspan=2, pady=(5, 10), sticky='ew', padx=(20, 20))

            # Кнопка для анализа данных
        self.analyze_button = tk.Button(root, text="Анализировать данные", command=self.analyze_data,
                                            width=20, height=2, bg="#CDC0B0", fg="black", font=("Arial", 12))
        self.analyze_button.grid(row=4, column=0, columnspan=2, pady=(5, 10), sticky='ew', padx=(20, 20))

            # Кнопка для просмотра достижений
        self.achievements_button = tk.Button(root, text="Просмотр достижений", command=self.view_achievements,
                                                 width=20, height=2, bg="#EEDFCC", fg="black", font=("Arial", 12))
        self.achievements_button.grid(row=5, column=0, columnspan=2, pady=(5, 10), sticky='ew', padx=(20, 20))

            # Кнопка для авторизации пользователя
        self.login_button = tk.Button(root, text="Авторизация пользователя", command=self.open_login_window,
                                          width=20, height=2, bg="#CDC0B0", fg="black", font=("Arial", 12))
        self.login_button.grid(row=7, column=0, columnspan=2, pady=(5, 10), sticky='ew', padx=(20, 20))

            # Кнопка для регистрации пользователя
        self.register_button = tk.Button(root, text="Регистрация пользователя",
                                             command=self.open_registration_window,
                                             width=20, height=2, bg="#8B8378", fg="black", font=("Arial", 12))
        self.register_button.grid(row=8, column=0, columnspan=2, pady=(5, 10), sticky='ew', padx=(20, 20))

            # Кнопка для экспорта данных
        self.export_button = tk.Button(root, text="Экспорт данных", command=self.export_user_data, width=20, bg="#E5E5E5")
        self.export_button.grid(row=0, column=1, pady=(5, 5), padx=(5, 5), sticky='ne')



    def export_user_data(self):# Экспорт данных
        if not self.current_user_id:
            messagebox.showwarning("Предупреждение", "Пожалуйста, авторизуйтесь.")
            return

        # Получение данных пользователя
        query_user = "SELECT Login FROM users WHERE user_id = ?"
        user_login = self.cursor.execute(query_user, (self.current_user_id,))
        login_row = user_login.fetchone()

        if login_row is None:
            messagebox.showwarning("Предупреждение", "Пользователь не найден.")
            return

        user_login = login_row[0]

        # Получение максимального уровня и очков
        query_max_level = "SELECT MAX(level), score FROM game_data WHERE user_id = ?"
        max_level_score = self.cursor.execute(query_max_level, (self.current_user_id,))
        max_level_score_row = max_level_score.fetchone()

        if max_level_score_row is None or max_level_score_row[0] is None:
            messagebox.showwarning("Предупреждение", "Данные о уровне и очках не найдены.")
            return

        max_level, score = max_level_score_row

        # Создаем текстовый файл
        with open(f"{user_login}_level_data.txt", "w") as file:
            file.write(f"Логин: {user_login}\nМаксимальный уровень: {max_level}\nОчки: {score}\n")

        messagebox.showinfo("Инфо", f"Данные экспорировались в {user_login}_level_data.txt")

    def open_database_menu(self):  # меню базы данных для администратора
        db_menu_window = tk.Toplevel(self.root)
        db_menu_window.title("Меню базы данных")
        db_menu_window.geometry("400x200")

        # Получаем список таблиц из базы данных
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        # Создаем выпадающий список для выбора таблицы
        self.selected_table = tk.StringVar(db_menu_window)
        self.selected_table.set(tables[0][0] if tables else "")  # Устанавливаем значение по умолчанию

        table_label = tk.Label(db_menu_window, text="Выберите таблицу:", font=("Arial", 14))
        table_label.pack(pady=10)

        table_dropdown = tk.OptionMenu(db_menu_window, self.selected_table, *[table[0] for table in tables])
        table_dropdown.pack(pady=10)

        # Кнопка для открытия формы редактирования
        edit_button = tk.Button(db_menu_window, text="Редактировать данные", command=self.edit_table_data)
        edit_button.pack(pady=20)

    def view_achievements(self):
        if self.current_user_id is None:
            messagebox.showerror("Ошибка", "Пожалуйста, войдите в аккаунт.")
            return

        achievements_window = tk.Toplevel(self.root)
        achievements_window.title("Достижения")
        achievements_window.geometry('815x500')

        # Поле ввода для поиска достижений
        search_label = tk.Label(achievements_window, text="Поиск по названию:", font=("Arial", 12))
        search_label.pack(pady=5, anchor='w', padx=10)

        search_entry = tk.Entry(achievements_window, font=("Arial", 12))
        search_entry.pack(pady=5, fill='x', padx=10)

        # Создаем Canvas и Scrollbar для списка достижений
        canvas = tk.Canvas(achievements_window)
        scrollbar = tk.Scrollbar(achievements_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        current_user_id = self.current_user_id  # Изменено с selected_user_id на current_user_id

        def load_users():
            # Получаем список пользователей из базы данных
            self.cursor.execute("SELECT user_id, login FROM users")  # Убедитесь, что 'username' существует
            return self.cursor.fetchall()

        def load_achievements(user_id, search_query=None):  # Передаем user_id как аргумент
            # Очистка текущих виджетов в scrollable_frame
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            # SQL-запрос для получения достижений (с учетом поиска)
            if search_query:
                query_string = """
                    SELECT a.name, a.description, a.criteria, ua.date
                    FROM achievements a
                    JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
                    WHERE ua.user_id = ? AND a.name LIKE ?
                """
                self.cursor.execute(query_string, (user_id, f"%{search_query}%"))
            else:
                query_string = """
                    SELECT a.name, a.description, a.criteria, ua.date
                    FROM achievements a
                    JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
                    WHERE ua.user_id = ?
                """
                self.cursor.execute(query_string, (user_id,))

            achievements_list = self.cursor.fetchall()

            if not achievements_list:
                tk.Label(scrollable_frame, text="Достижения не найдены.", font=("Arial", 12)).pack(pady=10)
                return

            for achievement in achievements_list:
                name, description, criteria, date = achievement

                # Создаем рамку для каждого достижения
                frame = tk.Frame(scrollable_frame, bd=2, relief=tk.RIDGE, padx=10, pady=10)
                frame.pack(padx=10, pady=10, fill='x')

                tk.Label(frame, text=f"Достижение: {name}", font=("Arial", 14, 'bold')).pack(anchor='w')
                tk.Label(frame, text=f"Критерии получения: {criteria}", font=("Arial", 12), wraplength=600).pack(
                    anchor='w')
                tk.Label(frame, text=f"Описание: {description}", font=("Arial", 10), wraplength=600).pack(anchor='w')
                tk.Label(frame, text=f"Дата получения: {date}", font=("Arial", 10)).pack(anchor='w')
                tk.Label(frame, text="").pack()

        # Кнопка для выполнения поиска
        search_button = tk.Button(
            achievements_window,
            text="Найти",
            font=("Arial", 15),
            command=lambda: load_achievements(current_user_id, search_entry.get())  # Передаем current_user_id
        )
        search_button.pack(pady=5)

        if self.current_user_role == 'admin':
            users = load_users()

            user_var = tk.StringVar(achievements_window)

            #выпадающее меню
            user_combobox = ttk.Combobox(achievements_window,
                                         textvariable=user_var,
                                         values=[f"{username} ({user_id})" for user_id, username in users],
                                         state='readonly')  # Устанавливаем только для чтения
            user_combobox.pack(pady=5)

            def update_selected_user(event):
                selected_user_str = user_combobox.get()
                selected_user_id = selected_user_str.split(' ')[-1][1:-1]  # Извлекаем user_id из строки
                load_achievements(selected_user_id)  # Загружаем достижения выбранного пользователя

            user_combobox.bind("<<ComboboxSelected>>", update_selected_user)  # Обработчик события выбора

        # Загрузка всех достижений при открытии окна для текущего пользователя
        load_achievements(current_user_id)

    def open_registration_window(self): # окно регистрации пользователя
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Регистрация")

        tk.Label(registration_window, text="Имя пользователя:", font=("Arial", 12)).grid(row=0)
        username_entry = tk.Entry(registration_window)
        username_entry.grid(row=0, column=1)

        tk.Label(registration_window, text="Пароль:", font=("Arial", 12)).grid(row=1)
        password_entry = tk.Entry(registration_window, show='*')
        password_entry.grid(row=1, column=1)

        tk.Label(registration_window, text="Электронная почта:", font=("Arial", 12)).grid(row=2)
        email_entry = tk.Entry(registration_window)
        email_entry.grid(row=2, column=1)

        def register():
            username = username_entry.get()
            password = password_entry.get()
            email = email_entry.get()
            result_message = self.user_management.register_user(username=username, password=password, email=email)
            messagebox.showinfo("Регистрация", result_message)
            registration_window.destroy()

        register_button = tk.Button(registration_window, text="Зарегистрироваться", command=register)
        register_button.grid(row=3, columnspan=2, pady=(10))

    def open_login_window(self):# Открытие окна авторизации пользователя.
        login_window = tk.Toplevel(self.root)
        login_window.title("Авторизация")

        tk.Label(login_window, text="Имя пользователя:", font=("Arial", 12)).grid(row=0)
        username_entry = tk.Entry(login_window)
        username_entry.grid(row=0, column=1)

        tk.Label(login_window, text="Пароль:", font=("Arial", 12)).grid(row=1)
        password_entry = tk.Entry(login_window, show='*')
        password_entry.grid(row=1, column=1)

        def login():
            username = username_entry.get()
            password = password_entry.get()
            user_id, role = self.user_management.authenticate_user(username=username, password=password)

            if user_id is not None:
                self.current_user_id = user_id
                self.current_user_role = role
                login_window.destroy()

                # Изменение заголовка на логин пользователя
                self.label.config(text=f"{username}")

                # Обновление интерфейса, чтобы отобразить изменения
                self.root.update()

                # Включаем поля ввода после успешной авторизации
                self.level_entry.config(state='normal')
                self.score_entry.config(state='normal')



                if role == 'admin':
                    self.create_admin_buttons()
                else:
                    self.admin_button.destroy()



            else:
                messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")
                # Обновление интерфейса, чтобы отобразить изменения
                self.root.update()

        login_button = tk.Button(login_window, text="Войти", command=login)
        login_button.grid(row=2, columnspan=2, pady=(10))

    def create_admin_buttons(self):# Создание кнопки 'Изменить базу данных' для администраторов.

        self.admin_button = db_button = tk.Button(self.root, text="Изменить базу данных", command=self.open_database_menu, width=20, height=2, bg="#66CDAA", fg="black", font=("Arial", 12))
        db_button.grid(row=6, columnspan=2, pady=(5, 10), sticky='ew', padx=(20, 20))

    def open_database_menu(self):  # меню базы данных для администратора
        db_menu_window = tk.Toplevel(self.root)
        db_menu_window.title("Меню базы данных")
        db_menu_window.geometry("400x200")

        # Получаем список таблиц из базы данных
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        # Создаем переменную для хранения выбранной таблицы
        self.selected_table = tk.StringVar(db_menu_window)
        self.selected_table.set(tables[0][0] if tables else "")  # Устанавливаем значение по умолчанию

        table_label = tk.Label(db_menu_window, text="Выберите таблицу:", font=("Arial", 14))
        table_label.pack(pady=10)

        # Создаем Combobox для выбора таблицы
        table_combobox = ttk.Combobox(db_menu_window, textvariable=self.selected_table,
                                      values=[table[0] for table in tables],
                                      state='readonly')  # Устанавливаем только для чтения
        table_combobox.pack(pady=10)

        # Кнопка для открытия формы редактирования
        edit_button = tk.Button(db_menu_window, text="Редактировать данные", command=self.edit_table_data)
        edit_button.pack(pady=20)

        # Устанавливаем фокус на Combobox (по желанию)
        table_combobox.current(0)  # Устанавливаем первый элемент как выбранный

    def edit_table_data(self):  # окно для редактирования данных выбранной таблицы
        selected_table = self.selected_table.get()

        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование таблицы: {selected_table}")

        # Получаем данные из выбранной таблицы
        query_string = f"SELECT * FROM {selected_table};"
        self.cursor.execute(query_string)
        rows = self.cursor.fetchall()

        # Получаем названия столбцов
        column_names = [description[0] for description in self.cursor.description]

        # Создаем фрейм для размещения Treeview и Scrollbar
        frame = tk.Frame(edit_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Создаем Treeview для отображения данных
        tree = ttk.Treeview(frame, columns=column_names, show='headings')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Добавляем заголовки столбцов
        for column in column_names:
            tree.heading(column, text=column)
            tree.column(column, anchor="center")

        # Заполняем Treeview данными
        for row in rows:
            tree.insert("", tk.END, values=row)

        # Создаем полосу прокрутки
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree.configure(yscrollcommand=scrollbar.set)

        # Обработчик двойного клика для редактирования ячейки
        def on_double_click(event):
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите строку для редактирования.")
                return

            item = selected_item[0]  # Получаем выделенный элемент
            column = tree.identify_column(event.x)  # Получаем идентификатор колонки
            col_index = int(column.replace("#", "")) - 1  # Преобразуем в индекс

            current_value = tree.item(item, "values")[col_index]

            entry = tk.Entry(edit_window)
            entry.insert(0, current_value)
            entry.place(x=event.x, y=event.y)  # Размещаем поле ввода в окне


            def save_edit():
                new_value = entry.get()
                values = list(tree.item(item, "values"))
                values[col_index] = new_value  # Обновляем значение в списке
                tree.item(item, values=values)  # Сохраняем обновленные значения в Treeview

                # Формируем запрос на обновление в базе данных
                update_query = f"UPDATE {selected_table} SET {column_names[col_index]} = ? WHERE {column_names[0]} = ?;"
                try:
                    self.cursor.execute(update_query, (new_value, values[0]))
                    self.conn.commit()
                    messagebox.showinfo("Успех", "Данные успешно обновлены!")
                except sqlite3.Error as e:
                    messagebox.showerror("Ошибка", f"Ошибка при обновлении данных: {e}")
                entry.destroy()  # Удаляем поле ввода после сохранения

            entry.bind("<Return>", lambda event: save_edit())  # Сохраняем при нажатии Enter
            entry.focus_set()  # Устанавливаем фокус на поле ввода

        tree.bind("<Double-1>", on_double_click)  # Привязываем событие двойного клика

        def add_row():# Добавление новой строки в таблицу
            add_window = tk.Toplevel(edit_window)
            add_window.title("Добавить новую строку")

            entries = {}  # Словарь для хранения полей ввода

            # Создаем поля ввода только для необходимых столбцов
            row_index = 0
            for column in column_names:
                if column in ['user_id', 'role', 'Date']:  # Исключаем столбцы с автозаполнением
                    continue
                tk.Label(add_window, text=column).grid(row=row_index, column=0)
                entry = tk.Entry(add_window)
                entry.grid(row=row_index, column=1)
                entries[column] = entry  # Сохраняем ссылку на поле ввода
                row_index += 1

            def save_new_row():
                new_values = [entries[column].get() for column in column_names if
                              column not in ['user_id', 'role', 'Date']]

                try:
                    tree.insert("", tk.END, values=new_values)  # Добавляем новую строку в Treeview

                    insert_query = f"INSERT INTO {selected_table} ({', '.join(column for column in column_names if column not in ['user_id', 'role', 'Date'])}) VALUES ({', '.join(['?' for _ in new_values])})"
                    self.cursor.execute(insert_query, new_values)
                    self.conn.commit()

                    add_window.destroy()  # Закрываем окно после добавления
                    messagebox.showinfo("Успех", "Новая строка успешно добавлена!")
                except sqlite3.IntegrityError as e:
                    messagebox.showerror("Ошибка", f"Ошибка при добавлении строки: {e}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

            save_button = tk.Button(add_window, text="Сохранить", command=save_new_row)
            save_button.grid(row=row_index, columnspan=2)

        add_button = tk.Button(edit_window, text="Добавить строку", command=add_row)
        add_button.pack(pady=10)

        def save_changes():
            messagebox.showinfo("Уведомление", "Все изменения сохранены!")

        save_button = tk.Button(edit_window, text="Сохранить изменения", command=save_changes)
        save_button.pack(pady=10)

        delete_button = tk.Button(edit_window, text="Удалить строку", command=lambda: self.delete_row(tree, selected_table, column_names, self.cursor, self.conn))
        delete_button.pack(pady=10)

    def delete_row(self, tree, selected_table, column_names, cursor, conn): # Удаление выбранной строки из таблицы базы данных и виджета Treeview

        # Получаем выделенный элемент
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите строку для удаления.")
            return

        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту строку?")
        if not confirm:
            return

        try:
            # Получаем данные выбранной строки
            item = selected_item[0]  # ID элемента в Treeview
            values = tree.item(item, "values")  # Значения столбцов строки

            if not values:
                messagebox.showerror("Ошибка", "Не удалось получить данные выделенной строки.")
                return

            # Предполагаем, что первый столбец (column_names[0]) - это уникальный идентификатор
            unique_id = values[0]  # Уникальный идентификатор строки

            # Формируем запрос на удаление из базы данных
            delete_query = f"DELETE FROM {selected_table} WHERE {column_names[0]} = ?;"
            cursor.execute(delete_query, (unique_id,))  # Выполняем запрос на удаление
            conn.commit()  # Сохраняем изменения

            # Удаляем строку из Treeview
            tree.delete(item)

            # Уведомление об успехе
            messagebox.showinfo("Успех", "Строка успешно удалена!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении строки из базы данных: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def save_changes(self, table_name, rows, column_names, entries):# Сохранение изменений в выбранной таблице.
        try:
            for i in range(len(rows)):
                new_values = []
                for j in range(len(rows[i])):
                    # Получаем новое значение из соответствующего поля ввода
                    new_value = entries[i][j].get()  # Получаем значение из Entry
                    new_values.append(new_value)

                # Создаем SQL-запрос для обновления данных
                update_query = f"UPDATE {table_name} SET "
                update_query += ", ".join([f"{column_names[j]} = ?" for j in range(len(new_values))])
                update_query += f" WHERE rowid = ?;"  # Используем rowid вместо id

                # Добавляем rowid в конец списка значений
                new_values.append(rows[i][0])  # Предположим, что rowid находится в первой колонке

                # Выполняем запрос
                self.cursor.execute(update_query, new_values)

            # Сохраняем изменения в базе данных




        except sqlite3.Error as error:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении изменений: {error}")




    def add_data(self):# Добавление игровых данных в базу.
        try:
            level = int(self.level_entry.get())
            score = int(self.score_entry.get())

            if not hasattr(self, 'current_user_id') or self.current_user_id is None:
                messagebox.showerror("Ошибка", "Пожалуйста, войдите в систему.")
                return

            user_id = self.current_user_id

            query_string = "INSERT INTO game_data (user_id, level, score) VALUES (?, ?, ?)"
            self.cursor.execute(query_string, (user_id, level, score))

            # Сохраняем изменения в базе данных.
            self.conn.commit()

            # Очищаем поля ввода.
            self.level_entry.delete(0, tk.END)
            self.score_entry.delete(0, tk.END)



        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные значения.")

    def analyze_data(self):#Анализ игровых данных.
        try:
            if not hasattr(self, 'current_user_id') or self.current_user_id is None:
                messagebox.showerror("Ошибка", "Пожалуйста , войдите в систему.")
                return

            user_id = self.current_user_id
            query_string = "SELECT level , score FROM game_data WHERE user_id = ?"
            self.cursor.execute(query_string, (user_id,))
            data = self.cursor.fetchall()

            if not data:
                messagebox.showwarning("Предупреждение", "Нет данных для анализа.")
                return

            levels = [row[0] for row in data]
            scores = [row[1] for row in data]

            plt.plot(levels, scores, marker='o')
            plt.xlabel('Уровень')
            plt.ylabel('Очки')
            plt.title('Анализ игровых данных')
            plt.grid()
            plt.show()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def close_connection(self):# Закрытие соединения с базой данных.
        if hasattr(self.conn):
            self.conn.close()

class Achievements:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    def add_achievement(self, name, description, criteria=None):

        try:
            # Проверка на существование достижения с таким именем
            self.cursor.execute("SELECT * FROM achievements WHERE name = ?", (name,))
            if self.cursor.fetchone():
                return "Достижение с таким именем уже существует!"

            self.cursor.execute(
                "INSERT INTO achievements (name, description, criteria) VALUES (?, ?, ?)",
                (name, description, criteria)
            )
            self.conn.commit()
            return "Достижение успешно добавлено!"
        except Exception as e:
            return f"Ошибка при добавлении достижения: {e}"

    def get_user_achievements(self, user_id):# Получение достижений конкретного пользователя.

        try:
            self.cursor.execute("""
                SELECT a.name, a.description FROM achievements a
                JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
                WHERE ua.user_id = ?
            """, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            return f"Ошибка при получении достижений пользователя: {e}"

    def get_all_achievements(self):# Получение всех достижений.

        try:
            self.cursor.execute("SELECT name, description, criteria FROM achievements")
            return self.cursor.fetchall()
        except Exception as e:
            return f"Ошибка при получении списка достижений: {e}"

    def assign_achievement_to_user(self, user_id, achievement_id):

        try:
            # Проверка, было ли уже выдано достижение
            self.cursor.execute("""
                SELECT * FROM user_achievements
                WHERE user_id = ? AND achievement_id = ?
            """, (user_id, achievement_id))
            if self.cursor.fetchone():
                return "Достижение уже выдано этому пользователю!"

            self.cursor.execute(
                "INSERT INTO user_achievements (user_id, achievement_id, Date) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (user_id, achievement_id)
            )
            self.conn.commit()
            return "Достижение успешно выдано пользователю!"
        except Exception as e:
            return f"Ошибка при выдаче достижения пользователю: {e}"



class Statistics:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    def get_user_stats(self, user_id):
        self.cursor.execute("SELECT AVG(level), SUM(score) FROM game_data WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()  # Возвращает средний уровень и сумму очков


class UserManagement:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    def register_user(self, username, password, email):
        try:
            self.cursor.execute("INSERT INTO users (Login, password, email) VALUES (?, ?, ?)",
                                (username, password, email))
            self.conn.commit()
            return "Пользователь успешно зарегистрирован!"
        except sqlite3.IntegrityError:
            return "Имя пользователя или электронная почта уже заняты."
        except Exception as e:
            return f"Произошла ошибка: {e}"

    def authenticate_user(self, username, password):
        self.cursor.execute("SELECT user_id, role FROM users WHERE Login = ? AND password = ?",
                            (username, password))
        user = self.cursor.fetchone()

        if user:
            return user[0], user[1]  # Возвращаем user_id и роль
        return None, None  # Если пользователь не найден

    def delete_user(self, user_id):
        try:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return "Пользователь успешно удален."
        except Exception as e:
            return f"Произошла ошибка: {e}"

    def change_user_role(self, user_id, new_role):
        try:
            self.cursor.execute("UPDATE users SET role = ? WHERE user_id = ?", (new_role, user_id))
            self.conn.commit()
            return "Роль пользователя изменена."
        except Exception as e:
            return f"Произошла ошибка: {e}"





if __name__ == "__main__":
    root = tk.Tk()
    app = DataTracker(root)
    root.mainloop()