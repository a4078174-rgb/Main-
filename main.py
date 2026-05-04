import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from urllib.parse import urlparse

class GitHubUserFinder:
    GITHUB_API_SEARCH = "https://api.github.com/search/users?q={}&per_page=30"
    
    def init(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Данные
        self.search_results = []          # список кортежей (login, user_id, html_url)
        self.favorites = []               # список кортежей (login, user_id, html_url)
        
        # Загрузка избранного из файла
        self.load_favorites()
        
        # Создание элементов интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Верхняя панель: поле ввода и кнопка поиска
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(top_frame, text="Логин пользователя:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(top_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_users())
        
        search_btn = ttk.Button(top_frame, text="Поиск", command=self.search_users)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Панель с двумя списками
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левый блок: результаты поиска
        left_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.results_listbox = tk.Listbox(left_frame, height=20)
        self.results_listbox.pack(fill=tk.BOTH, expand=True)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_result_select)
        
        # Кнопки управления под результатами
        left_btn_frame = ttk.Frame(left_frame)
        left_btn_frame.pack(fill=tk.X, pady=5)
        add_fav_btn = ttk.Button(left_btn_frame, text="Добавить в избранное", command=self.add_to_favorites)
        add_fav_btn.pack(side=tk.LEFT, padx=2)
        
        # Правый блок: избранное
        right_frame = ttk.LabelFrame(main_frame, text="Избранное", padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        self.favorites_listbox = tk.Listbox(right_frame, height=20)
        self.favorites_listbox.pack(fill=tk.BOTH, expand=True)
        self.favorites_listbox.bind("<<ListboxSelect>>", self.on_favorite_select)
        
        right_btn_frame = ttk.Frame(right_frame)
        right_btn_frame.pack(fill=tk.X, pady=5)
        remove_fav_btn = ttk.Button(right_btn_frame, text="Удалить из избранного", command=self.remove_from_favorites)
        remove_fav_btn.pack(side=tk.LEFT, padx=2)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.update_favorites_display()
        self.status_var.set("Готов")
        
    def search_users(self):
        """Поиск пользователей через GitHub API"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Пустой запрос", "Введите логин для поиска.")
            return
        
        self.status_var.set("Поиск...")
        self.root.update()
        
        try:
            url = self.GITHUB_API_SEARCH.format(query)
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
items = data.get("items", [])
            if not items:
                self.results_listbox.delete(0, tk.END)
                self.search_results = []
                self.status_var.set("Пользователи не найдены.")
                return
            
            self.search_results = []
            self.results_listbox.delete(0, tk.END)
            for user in items:
                login = user["login"]
                user_id = user["id"]
                html_url = user["html_url"]
                self.search_results.append((login, user_id, html_url))
                self.results_listbox.insert(tk.END, f"{login} (ID: {user_id})")
            
            self.status_var.set(f"Найдено пользователей: {len(self.search_results)}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось выполнить запрос:\n{e}")
            self.status_var.set("Ошибка поиска")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")
            self.status_var.set("Ошибка")
    
    def on_result_select(self, event):
        """Обработчик выбора элемента в результатах поиска"""
        pass  # можно расширить (например, показать детали)
    
    def on_favorite_select(self, event):
        pass
    
    def add_to_favorites(self):
        """Добавить выбранного пользователя в избранное"""
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showinfo("Нет выбора", "Сначала выберите пользователя из результатов поиска.")
            return
        
        index = selection[0]
        user = self.search_results[index]
        # Проверка, не добавлен ли уже
        for fav in self.favorites:
            if fav[0] == user[0]:  # login
                messagebox.showinfo("Уже в избранном", f"Пользователь {user[0]} уже есть в избранном.")
                return
        
        self.favorites.append(user)
        self.save_favorites()
        self.update_favorites_display()
        self.status_var.set(f"Пользователь {user[0]} добавлен в избранное.")
    
    def remove_from_favorites(self):
        """Удалить выбранного пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showinfo("Нет выбора", "Выберите пользователя в списке избранного.")
            return
        
        index = selection[0]
        removed = self.favorites.pop(index)
        self.save_favorites()
        self.update_favorites_display()
        self.status_var.set(f"Пользователь {removed[0]} удалён из избранного.")
    
    def update_favorites_display(self):
        """Обновить отображение списка избранного"""
        self.favorites_listbox.delete(0, tk.END)
        for login, user_id, _ in self.favorites:
            self.favorites_listbox.insert(tk.END, f"{login} (ID: {user_id})")
    
    def load_favorites(self):
        """Загрузить избранное из JSON-файла"""
        if not os.path.exists("favorites.json"):
            self.favorites = []
            return
        try:
            with open("favorites.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # данные хранятся как список [login, user_id, html_url]
            self.favorites = [tuple(item) for item in data]
        except Exception as e:
            print(f"Ошибка загрузки избранного: {e}")
            self.favorites = []
    
    def save_favorites(self):
        """Сохранить избранное в JSON-файл"""
        try:
            with open("favorites.json", "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить избранное:\n{e}")

if name == "main":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
