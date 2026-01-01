import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("学生信息管理系统")
        self.root.geometry("800x600")
        
        # 初始化数据库
        self.init_database()
        
        # 创建主界面
        self.create_widgets()
        
    def init_database(self):
        """初始化SQLite数据库"""
        self.conn = sqlite3.connect('students.db')
        self.cursor = self.conn.cursor()
        
        # 创建学生表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                grade TEXT,
                score REAL,
                city TEXT
            )
        ''')
        self.conn.commit()
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建笔记本控件（选项卡）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标签页1：数据录入
        self.create_input_tab(notebook)
        
        # 标签页2：数据查看
        self.create_view_tab(notebook)
        
        # 标签页3：网络数据获取
        self.create_network_tab(notebook)
        
        # 标签页4：数据可视化
        self.create_chart_tab(notebook)
        
    def create_input_tab(self, notebook):
        """创建数据录入标签页"""
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="数据录入")
        
        # 输入控件
        tk.Label(input_frame, text="姓名:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="年龄:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.age_entry = tk.Entry(input_frame)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="年级:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.grade_entry = tk.Entry(input_frame)
        self.grade_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="分数:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.score_entry = tk.Entry(input_frame)
        self.score_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="城市:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.city_entry = tk.Entry(input_frame)
        self.city_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # 按钮
        tk.Button(input_frame, text="添加学生", command=self.add_student).grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(input_frame, text="清空输入", command=self.clear_input).grid(row=6, column=0, columnspan=2, pady=5)
        
    def create_view_tab(self, notebook):
        """创建数据查看标签页"""
        view_frame = ttk.Frame(notebook)
        notebook.add(view_frame, text="数据查看")
        
        # 创建表格
        columns = ("ID", "姓名", "年龄", "年级", "分数", "城市")
        self.tree = ttk.Treeview(view_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 按钮框架
        button_frame = tk.Frame(view_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="刷新数据", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="删除选中", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="导出数据", command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # 初始加载数据
        self.refresh_data()
        
    def create_network_tab(self, notebook):
        """创建网络数据获取标签页"""
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="网络数据")
        
        tk.Label(network_frame, text="获取天气数据（示例）").pack(pady=10)
        
        city_frame = tk.Frame(network_frame)
        city_frame.pack(pady=5)
        
        tk.Label(city_frame, text="城市:").pack(side=tk.LEFT)
        self.weather_city_entry = tk.Entry(city_frame)
        self.weather_city_entry.pack(side=tk.LEFT, padx=5)
        self.weather_city_entry.insert(0, "北京")
        
        tk.Button(city_frame, text="获取天气", command=self.get_weather).pack(side=tk.LEFT, padx=5)
        
        # 显示结果的文本框
        self.weather_text = tk.Text(network_frame, height=15, width=60)
        self.weather_text.pack(pady=10)
        
    def create_chart_tab(self, notebook):
        """创建数据可视化标签页"""
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="数据可视化")
        
        # 图表按钮
        button_frame = tk.Frame(chart_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="年龄分布图", command=self.show_age_chart).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="分数分布图", command=self.show_score_chart).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="城市统计图", command=self.show_city_chart).pack(side=tk.LEFT, padx=5)
        
        # 图表显示区域
        self.chart_frame = tk.Frame(chart_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
    def add_student(self):
        """添加学生信息"""
        try:
            name = self.name_entry.get().strip()
            age = int(self.age_entry.get())
            grade = self.grade_entry.get().strip()
            score = float(self.score_entry.get())
            city = self.city_entry.get().strip()
            
            if not name:
                messagebox.showerror("错误", "姓名不能为空")
                return
                
            self.cursor.execute('''
                INSERT INTO students (name, age, grade, score, city)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, age, grade, score, city))
            
            self.conn.commit()
            messagebox.showinfo("成功", "学生信息添加成功")
            self.clear_input()
            self.refresh_data()
            
        except ValueError:
            messagebox.showerror("错误", "请输入正确的数值格式")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")
            
    def clear_input(self):
        """清空输入框"""
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.score_entry.delete(0, tk.END)
        self.city_entry.delete(0, tk.END)
        
    def refresh_data(self):
        """刷新数据显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 从数据库获取数据
        self.cursor.execute('SELECT * FROM students')
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", "end", values=row)
            
    def delete_student(self):
        """删除选中的学生"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要删除的学生")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的学生吗？"):
            for item in selected:
                student_id = self.tree.item(item)['values'][0]
                self.cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
                
            self.conn.commit()
            self.refresh_data()
            messagebox.showinfo("成功", "删除成功")
            
    def export_data(self):
        """导出数据到JSON文件"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                self.cursor.execute('SELECT * FROM students')
                rows = self.cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append({
                        "id": row[0],
                        "name": row[1],
                        "age": row[2],
                        "grade": row[3],
                        "score": row[4],
                        "city": row[5]
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"数据已导出到 {file_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
            
    def get_weather(self):
        """获取天气数据（模拟网络请求）"""
        city = self.weather_city_entry.get().strip()
        
        try:
            # 这里使用一个免费的天气API（需要替换为实际的API key）
            # 如果没有API，这里提供一个模拟响应
            weather_info = f"城市: {city}\n温度: 22°C\n天气: 晴朗\n湿度: 65%\n风速: 5 km/h\n\n（这是模拟数据，实际使用需要接入真实天气API）"
            
            self.weather_text.delete(1.0, tk.END)
            self.weather_text.insert(1.0, weather_info)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取天气数据失败: {str(e)}")
            
    def show_age_chart(self):
        """显示年龄分布图"""
        self.cursor.execute('SELECT age FROM students')
        ages = [row[0] for row in self.cursor.fetchall()]
        
        if not ages:
            messagebox.showwarning("警告", "没有数据可显示")
            return
            
        # 清空现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(ages, bins=10, edgecolor='black', alpha=0.7)
        ax.set_title('学生年龄分布图')
        ax.set_xlabel('年龄')
        ax.set_ylabel('人数')
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def show_score_chart(self):
        """显示分数分布图"""
        self.cursor.execute('SELECT score FROM students')
        scores = [row[0] for row in self.cursor.fetchall()]
        
        if not scores:
            messagebox.showwarning("警告", "没有数据可显示")
            return
            
        # 清空现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(scores, bins=10, edgecolor='black', alpha=0.7, color='green')
        ax.set_title('学生分数分布图')
        ax.set_xlabel('分数')
        ax.set_ylabel('人数')
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def show_city_chart(self):
        """显示城市统计图"""
        self.cursor.execute('SELECT city, COUNT(*) FROM students GROUP BY city')
        data = self.cursor.fetchall()
        
        if not data:
            messagebox.showwarning("警告", "没有数据可显示")
            return
            
        cities = [row[0] for row in data]
        counts = [row[1] for row in data]
        
        # 清空现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(counts, labels=cities, autopct='%1.1f%%')
        ax.set_title('学生城市分布图')
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def __del__(self):
        """析构函数，关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()