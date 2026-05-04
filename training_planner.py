import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Имя файла для сохранения данных
DATA_FILE = "trainings.json"


class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("700x500")

        # Список для хранения всех тренировок
        self.trainings = []

        # Создание GUI
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table()

        # Загрузка данных из файла
        self.load_data()

    def create_input_frame(self):
        """Панель для ввода новой тренировки"""
        input_frame = tk.LabelFrame(self.root, text="Добавить тренировку", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поле Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = tk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, "2026-05-04")  # Пример

        # Поле Тип тренировки
        tk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=5)
        self.type_entry = tk.Entry(input_frame, width=20)
        self.type_entry.grid(row=0, column=3, padx=5)
        self.type_entry.insert(0, "Бег")  # Пример

        # Поле Длительность
        tk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=5)
        self.duration_entry = tk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5)

        # Кнопка Добавить
        add_btn = tk.Button(input_frame, text="Добавить тренировку", command=self.add_training, bg="lightgreen")
        add_btn.grid(row=0, column=6, padx=10)

    def create_filter_frame(self):
        """Панель для фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтр", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        tk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_type_entry = tk.Entry(filter_frame, width=20)
        self.filter_type_entry.grid(row=0, column=1, padx=5)

        # Фильтр по дате
        tk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=3, padx=5)

        # Кнопка Применить фильтр
        filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter, bg="lightblue")
        filter_btn.grid(row=0, column=4, padx=10)

        # Кнопка Сбросить фильтр
        reset_btn = tk.Button(filter_frame, text="Сбросить", command=self.reset_filter, bg="lightgray")
        reset_btn.grid(row=0, column=5, padx=5)

    def create_table(self):
        """Таблица для отображения тренировок"""
        # Создаем фрейм для таблицы с прокруткой
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создаем Treeview (таблицу)
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Настройка заголовков
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")

        # Настройка ширины столбцов
        self.tree.column("date", width=150)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=150)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_training(self):
        """Добавление тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_entry.get().strip()
        duration_str = self.duration_entry.get().strip()

        # Проверка даты
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        # Проверка длительности
        try:
            duration = float(duration_str)
            if duration <= 0:
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть числом")
            return

        # Проверка типа (не пустой)
        if not training_type:
            messagebox.showerror("Ошибка", "Введите тип тренировки")
            return

        # Добавляем тренировку
        training = {
            "date": date,
            "type": training_type,
            "duration": duration
        }
        self.trainings.append(training)

        # Очищаем поля
        self.date_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

        # Обновляем таблицу
        self.update_table()
        self.save_data()

        messagebox.showinfo("Успех", "Тренировка добавлена")

    def update_table(self, filtered_trainings=None):
        """Обновление таблицы"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Выбираем данные для отображения
        if filtered_trainings is None:
            trainings_to_show = self.trainings
        else:
            trainings_to_show = filtered_trainings

        # Добавляем тренировки в таблицу
        for training in trainings_to_show:
            self.tree.insert("", "end", values=(
                training["date"],
                training["type"],
                training["duration"]
            ))

    def apply_filter(self):
        """Применение фильтра"""
        filter_type = self.filter_type_entry.get().strip().lower()
        filter_date = self.filter_date_entry.get().strip()

        if not filter_type and not filter_date:
            messagebox.showinfo("Информация", "Введите хотя бы один фильтр")
            return

        filtered = []
        for training in self.trainings:
            # Проверка соответствия фильтрам
            type_match = True
            date_match = True

            if filter_type:
                type_match = training["type"].lower() == filter_type

            if filter_date:
                # Проверка корректности даты фильтра
                if self.validate_date(filter_date):
                    date_match = training["date"] == filter_date
                else:
                    messagebox.showerror("Ошибка", "Неверный формат даты в фильтре")
                    return

            if type_match and date_match:
                filtered.append(training)

        if not filtered:
            messagebox.showinfo("Результат", "Тренировки не найдены")

        self.update_table(filtered)

    def reset_filter(self):
        """Сброс фильтра"""
        # Очищаем поля фильтров
        self.filter_type_entry.delete(0, tk.END)
        self.filter_date_entry.delete(0, tk.END)

        # Показываем все тренировки
        self.update_table()

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
                self.update_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()