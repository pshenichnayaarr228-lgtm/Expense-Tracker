import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("950x650")
        self.root.resizable(False, False)
        
        self.expenses = []
        self.load_data()
        self.setup_ui()
        self.update_table()
        self.update_total()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        
        form_frame = tk.LabelFrame(main_frame, text="➕ Добавить расход", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        form_frame.pack(fill="x", pady=(0, 10))
        
        # Сумма
        tk.Label(form_frame, text="Сумма (₽):", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(form_frame, width=15, font=("Arial", 10))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Категория
        tk.Label(form_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar(value="Еда")
        categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", 
                      "Одежда", "Коммунальные услуги", "Другое"]
        self.category_menu = ttk.Combobox(form_frame, textvariable=self.category_var, 
                                           values=categories, width=18, state="readonly")
        self.category_menu.grid(row=0, column=3, padx=5, pady=5)
        
        # Дата
        tk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = tk.Entry(form_frame, width=12, font=("Arial", 10))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = tk.Button(form_frame, text="Добавить расход", command=self.add_expense,
                                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # ========== ФИЛЬТРАЦИЯ ==========
        filter_frame = tk.LabelFrame(main_frame, text="🔍 Фильтрация", 
                                      font=("Arial", 12, "bold"), padx=10, pady=10)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        filter_categories = ["Все"] + categories
        self.filter_category_menu = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, 
                                                   values=filter_categories, width=18, state="readonly")
        self.filter_category_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по дате (от)
        tk.Label(filter_frame, text="Дата от:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.date_from_entry = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.date_from_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Фильтр по дате (до)
        tk.Label(filter_frame, text="Дата до:", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.date_to_entry = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.date_to_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопки фильтрации
        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter,
                                     bg="#2196F3", fg="white", font=("Arial", 10))
        self.filter_btn.grid(row=0, column=6, padx=5, pady=5)
        
        self.reset_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter,
                                    bg="#FF9800", fg="white", font=("Arial", 10))
        self.reset_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # ========== ТАБЛИЦА РАСХОДОВ ==========
        table_frame = tk.LabelFrame(main_frame, text="📋 Список расходов", 
                                     font=("Arial", 12, "bold"), padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("ID", "Дата", "Категория", "Сумма (₽)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("ID", text="№")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма (₽)", text="Сумма (₽)")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Дата", width=120, anchor="center")
        self.tree.column("Категория", width=150, anchor="center")
        self.tree.column("Сумма (₽)", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ========== НИЖНЯЯ ПАНЕЛЬ ==========
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill="x")
        
        self.total_label = tk.Label(bottom_frame, text="💰 Общая сумма расходов: 0 ₽", 
                                     font=("Arial", 14, "bold"), fg="#2E7D32")
        self.total_label.pack(side="left")
        
        self.delete_btn = tk.Button(bottom_frame, text="🗑 Удалить выбранный", command=self.delete_expense,
                                     bg="#f44336", fg="white", font=("Arial", 10), width=15)
        self.delete_btn.pack(side="right", padx=5)
    
    def validate_amount(self, amount):
        try:
            value = float(amount)
            if value <= 0:
                return False, "Сумма должна быть положительным числом!"
            if value > 999999:
                return False, "Сумма не может превышать 999 999 ₽!"
            return True, value
        except ValueError:
            return False, "Введите корректное число!"
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, date_str
        except ValueError:
            return False, "Неверный формат даты! Используйте ГГГГ-ММ-ДД"
    
    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get()
        date_str = self.date_entry.get().strip()
        
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму расхода!")
            return
        
        is_valid, result = self.validate_amount(amount_str)
        if not is_valid:
            messagebox.showerror("Ошибка", result)
            return
        amount = result
        
        is_valid, result = self.validate_date(date_str)
        if not is_valid:
            messagebox.showerror("Ошибка", result)
            return
        date = result
        
        expense = {
            "id": len(self.expenses) + 1,
            "date": date,
            "category": category,
            "amount": amount
        }
        self.expenses.append(expense)
        self.save_data()
        
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.update_table()
        self.update_total()
        messagebox.showinfo("Успех", f"Расход на сумму {amount:.2f} ₽ добавлен!")
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        item = selected[0]
        values = self.tree.item(item, "values")
        
        if messagebox.askyesno("Подтверждение", f"Удалить расход на сумму {values[3]} ₽?"):
            expense_id = int(values[0])
            self.expenses = [e for e in self.expenses if e["id"] != expense_id]
            self.reassign_ids()
            self.save_data()
            self.update_table()
            self.update_total()
            messagebox.showinfo("Успех", "Расход удалён!")
    
    def reassign_ids(self):
        for i, expense in enumerate(self.expenses):
            expense["id"] = i + 1
    
    def get_filtered_expenses(self):
        filtered = self.expenses.copy()
        
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]
        
        date_from = self.date_from_entry.get().strip()
        if date_from:
            is_valid, _ = self.validate_date(date_from)
            if is_valid:
                filtered = [e for e in filtered if e["date"] >= date_from]
        
        date_to = self.date_to_entry.get().strip()
        if date_to:
            is_valid, _ = self.validate_date(date_to)
            if is_valid:
                filtered = [e for e in filtered if e["date"] <= date_to]
        
        return filtered
    
    def apply_filter(self):
        self.update_table()
        self.update_total()
        messagebox.showinfo("Фильтр", "Фильтр применён!")
    
    def reset_filter(self):
        self.filter_category_var.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.update_table()
        self.update_total()
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered = self.get_filtered_expenses()
        for expense in filtered:
            self.tree.insert("", "end", values=(
                expense["id"],
                expense["date"],
                expense["category"],
                f"{expense['amount']:.2f}"
            ))
    
    def update_total(self):
        filtered = self.get_filtered_expenses()
        total = sum(expense["amount"] for expense in filtered)
        self.total_label.config(text=f"💰 Общая сумма расходов: {total:.2f} ₽")
    
    def load_data(self):
        try:
            with open("expenses.json", "r", encoding="utf-8") as file:
                self.expenses = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.expenses = []
    
    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as file:
            json.dump(self.expenses, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()