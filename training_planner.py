import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

DATA_FILE = "trainings.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("750x500")

        # Данные
        self.trainings = []
        self.load_data()

        # Поля ввода
        input_frame = ttk.Frame(root, padding=10)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.type_entry = ttk.Entry(input_frame, width=20)
        self.type_entry.grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.duration_entry = ttk.Entry(input_frame, width=20)
        self.duration_entry.grid(row=2, column=1, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(root, padding=5)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Добавить тренировку", command=self.add_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # Фильтры
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=5)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="По типу:").grid(row=0, column=0, sticky=tk.W)
        self.filter_type = ttk.Entry(filter_frame, width=15)
        self.filter_type.grid(row=0, column=1, padx=5)
        ttk.Label(filter_frame, text="По дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky=tk.W)
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=3, padx=5)
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.refresh_table).grid(row=0, column=5, padx=5)

        # Таблица
        table_frame = ttk.Frame(root, padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=120, anchor=tk.CENTER)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=120, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_table()

    # Валидация
    def validate_inputs(self, date_str, type_str, duration_str):
        if not type_str.strip():
            return False, "Тип тренировки не может быть пустым."
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Дата должна быть в формате ГГГГ-ММ-ДД."
        try:
            duration = int(duration_str)
            if duration <= 0:
                return False, "Длительность должна быть положительным числом."
        except ValueError:
            return False, "Длительность должна быть целым положительным числом."
        return True, ""

    # Добавление записи
    def add_training(self):
        date = self.date_entry.get().strip()
        ttype = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()

        valid, msg = self.validate_inputs(date, ttype, duration)
        if not valid:
            messagebox.showerror("Ошибка ввода", msg)
         return

        self.trainings.append({
            "date": date,
            "type": ttype,
            "duration": int(duration)
        })
        self.date_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
        self.refresh_table()
        self.save_data()  # автоматическое сохранение

    # Заполнение таблицы (с фильтром или без)
    def refresh_table(self, filtered_list=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = filtered_list if filtered_list is not None else self.trainings
        for t in data:
            self.tree.insert("", tk.END, values=(t["date"], t["type"], t["duration"]))

    # Фильтрация
    def apply_filter(self):
        type_filter = self.filter_type.get().strip().lower()
        date_filter = self.filter_date.get().strip()
        filtered = []
        for t in self.trainings:
            match_type = (type_filter == "" or type_filter in t["type"].lower())
            match_date = (date_filter == "" or t["date"] == date_filter)
            if match_type and match_date:
                filtered.append(t)
        self.refresh_table(filtered)

    # Работа с JSON
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.trainings, f, indent=2, ensure_ascii=False)
            print(f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.trainings = []
            self.refresh_table()
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.trainings = json.load(f)
            self.refresh_table()
            print(f"Данные загружены из {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))
            self.trainings = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
