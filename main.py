import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary — Дневник погоды")
        self.root.geometry("750x600")
        self.root.resizable(True, True)

        self.data_file = "weather_data.json"
        self.records = []
        self.load_data()

        self.setup_ui()
        self.refresh_table()

    # ========================
    #   РАБОТА С ДАННЫМИ
    # ========================

    def load_data(self):
        """Загрузка записей из JSON-файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.records = []
        else:
            self.records = []

    def save_data(self):
        """Сохранение записей в JSON-файл"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные:\n{e}")

    # ========================
    #   ИНТЕРФЕЙС
    # ========================

    def setup_ui(self):
        # --- Фрейм добавления записи ---
        add_frame = ttk.LabelFrame(self.root, text="Добавить запись о погоде", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(add_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_date = ttk.Entry(add_frame, width=20)
        self.entry_date.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Температура
        ttk.Label(add_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=(20, 0), pady=3)
        self.entry_temp = ttk.Entry(add_frame, width=10)
        self.entry_temp.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        # Описание
        ttk.Label(add_frame, text="Описание:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_desc = ttk.Entry(add_frame, width=60)
        self.entry_desc.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=3)

        # Осадки
        self.rain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(add_frame, text="Осадки (дождь/снег)", variable=self.rain_var).grid(
            row=2, column=1, sticky="w", pady=5
        )

        # Кнопка добавления
        ttk.Button(add_frame, text="➕ Добавить запись", command=self.add_record).grid(
            row=2, column=3, sticky="e", pady=5
        )

        # --- Фрейм фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация записей", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.filter_temp = ttk.Entry(filter_frame, width=10)
        self.filter_temp.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter).grid(
            row=0, column=4, padx=10
        )
        ttk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter).grid(
            row=0, column=5, padx=5
        )

        # --- Таблица записей ---
        table_frame = ttk.LabelFrame(self.root, text="Записи о погоде", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=120, anchor="center")
        self.tree.column("temperature", width=130, anchor="center")
        self.tree.column("description", width=280, anchor="w")
        self.tree.column("precipitation", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления
        ttk.Button(table_frame, text="🗑️ Удалить выбранную запись", command=self.delete_record).pack(
            anchor="e", pady=5
        )

    # ========================
    #   ВАЛИДАЦИЯ
    # ========================

    def validate_record(self, date_str, temp_str, desc):
        """Возвращает список ошибок (пустой — если всё ок)"""
        errors = []

        # Проверка даты
        try:
            datetime.strptime(date_str.strip(), "%d.%m.%Y")
        except ValueError:
            errors.append("❌ Дата должна быть в формате ДД.ММ.ГГГГ (например, 01.01.2024)")

        # Проверка температуры
        try:
            float(temp_str.strip())
        except ValueError:
            errors.append("❌ Температура должна быть числом (например, -5, 23.5)")

        # Проверка описания
        if not desc.strip():
            errors.append("❌ Описание погоды не может быть пустым")
        elif len(desc) > 200:
            errors.append("❌ Описание слишком длинное (макс. 200 символов)")

        return errors

    # ========================
    #   ДЕЙСТВИЯ
    # ========================

    def add_record(self):
        date_str = self.entry_date.get()
        temp_str = self.entry_temp.get()
        desc = self.entry_desc.get()
        rain = "Да" if self.rain_var.get() else "Нет"

        errors = self.validate_record(date_str, temp_str, desc)
        if errors:
            messagebox.showerror("Ошибка валидации", "\n".join(errors))
            return

        record = {
            "date": date_str.strip(),
            "temperature": float(temp_str.strip()),
            "description": desc.strip(),
            "precipitation": rain
        }

        self.records.append(record)
        self.save_data()

        # Очистка полей
        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.rain_var.set(False)

        self.refresh_table()
        messagebox.showinfo("Успех", "✅ Запись добавлена!")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        index = self.tree.index(selected[0])
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            del self.records[index]
            self.save_data()
            self.refresh_table()

    def refresh_table(self, filtered_records=None):
        """Обновление таблицы (можно передать отфильтрованный список)"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = filtered_records if filtered_records is not None else self.records

        for rec in data:
            self.tree.insert("", "end", values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                rec.get("precipitation", "Нет")
            ))

    # ========================
    #   ФИЛЬТРАЦИЯ
    # ========================

    def apply_filter(self):
        date_filter = self.filter_date.get().strip()
        temp_filter = self.filter_temp.get().strip()

        filtered = self.records.copy()

        # Фильтр по дате
        if date_filter:
            try:
                datetime.strptime(date_filter, "%d.%m.%Y")
                filtered = [r for r in filtered if r["date"] == date_filter]
            except ValueError:
                messagebox.showerror("Ошибка", "Дата в фильтре должна быть в формате ДД.ММ.ГГГГ")
                return

        # Фильтр по температуре
        if temp_filter:
            try:
                min_temp = float(temp_filter)
                filtered = [r for r in filtered if r["temperature"] >= min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом")
                return

        self.refresh_table(filtered)

        if not filtered:
            messagebox.showinfo("Результат", "Нет записей, соответствующих фильтру")

    def reset_filter(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.refresh_table()


# ========================
#   ТОЧКА ВХОДА
# ========================

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()