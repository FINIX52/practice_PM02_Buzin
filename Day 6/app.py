"""
Приложение для управления таблицей "Товары" (Products) – вариант 4 "Складской учёт"
База данных: Variant4_Work
Поля: id, название, артикул, ед_изм
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime

def connect_db():
    """Подключение к MySQL БД Variant4_Work."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1092Qpow",
            database="variant4_work"
        )
        return connection
    except Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться: {e}")
        return None


class DatabaseApp:
    def __init__(self, root, table_name, columns):
        """
        table_name: имя таблицы (например, 'Products')
        columns: список словарей с описанием столбцов
        """
        self.root = root
        self.table_name = table_name
        self.columns = columns

        self.root.title(f"Управление таблицей: {table_name}")
        self.root.geometry("850x550")
        self.root.resizable(True, True)

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Создание всех элементов интерфейса."""
        input_frame = tk.LabelFrame(self.root, text="Данные товара", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        self.entries = {}
        row = 0
        col = 0
        for i, col_def in enumerate(self.columns):
            if col_def.get('pk') and col_def.get('auto_increment'):
                continue

            label = tk.Label(input_frame, text=f"{col_def['label']}:", width=20, anchor="e")
            label.grid(row=row, column=col*2, padx=5, pady=5, sticky="e")

            entry = tk.Entry(input_frame, width=30)
            entry.grid(row=row, column=col*2+1, padx=5, pady=5, sticky="w")
            self.entries[col_def['name']] = entry

            col += 1
            if col >= 2:
                col = 0
                row += 1

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="➕ Добавить", command=self.add_record,
                  bg="#90EE90", width=12).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="✏️ Обновить", command=self.update_record,
                  bg="#FFD700", width=12).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="🗑️ Удалить", command=self.delete_record,
                  bg="#FF6347", width=12).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="🧹 Очистить", command=self.clear_entries,
                  width=12).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="🔄 Показать всех", command=self.refresh_table,
                  width=15).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="📎 Экспорт CSV", command=self.export_to_csv,
                  width=12).grid(row=0, column=5, padx=5)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5, fill="x", padx=10)
        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍 Найти", command=self.search).pack(side=tk.LEFT)
        tk.Button(search_frame, text="❌ Сброс", command=self.refresh_table).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        columns_display = [col['name'] for col in self.columns]
        self.tree = ttk.Treeview(tree_frame, columns=columns_display, show="headings",
                                 yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)

        for col_def in self.columns:
            self.tree.heading(col_def['name'], text=col_def['label'])
            self.tree.column(col_def['name'], width=120, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_table(self):
        """Обновить данные в таблице Treeview (все записи)."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_select(self, event):
        """Заполнить поля ввода при выборе строки."""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])['values']
        idx = 0
        for col_def in self.columns:
            col_name = col_def['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                self.entries[col_name].insert(0, str(values[idx]) if values[idx] is not None else "")
            idx += 1

    def get_pk_name(self):
        """Вернуть имя первичного ключа."""
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None

    def add_record(self):
        """Добавить новую запись."""
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()

        for col_def in self.columns:
            col_name = col_def['name']
            if col_def.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Ошибка", f"Поле '{col_def['label']}' обязательно для заполнения")
                return

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Успех", "Запись добавлена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_record(self):
        """Обновить выбранную запись."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для обновления")
            return

        pk_name = self.get_pk_name()
        if not pk_name:
            return

        values_row = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values_row[pk_index]

        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Успех", "Запись обновлена")
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        """Удалить выбранную запись."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить запись?"):
            return

        pk_name = self.get_pk_name()
        if not pk_name:
            return

        values_row = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values_row[pk_index]

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Успех", "Запись удалена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def clear_entries(self):
        """Очистить все поля ввода."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def search(self):
        """Поиск по полям: название, артикул, ед_изм."""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        text_fields = ['название', 'артикул', 'ед_изм']
        conditions = " OR ".join([f"{field} LIKE %s" for field in text_fields])
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"
        try:
            like_pattern = f"%{keyword}%"
            cursor.execute(query, (like_pattern, like_pattern, like_pattern))
            rows = cursor.fetchall()
            for row in self.tree.get_children():
                self.tree.delete(row)
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            if not rows:
                messagebox.showinfo("Поиск", "Ничего не найдено")
        except Error as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def export_to_csv(self):
        """Экспорт всех данных в CSV."""
        filename = f"{self.table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                headers = [col['label'] for col in self.columns]
                writer.writerow(headers)
                writer.writerows(rows)
            messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()


def main():
    root = tk.Tk()
    columns = [
        {"name": "id", "label": "ID", "pk": True, "auto_increment": True},
        {"name": "название", "label": "Наименование", "required": True},
        {"name": "артикул", "label": "Артикул", "required": True},
        {"name": "ед_изм", "label": "Ед. изм.", "required": False}
    ]
    app = DatabaseApp(root, table_name="Products", columns=columns)
    root.mainloop()


if __name__ == "__main__":
    main()
