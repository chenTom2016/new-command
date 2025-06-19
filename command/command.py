import subprocess
from tkinter import ttk, messagebox, filedialog, scrolledtext
from colorama import Fore, init
import os
from configparser import ConfigParser
import re
import tkinter as tk
from tkinter import font
import math
from time import strftime
from PIL import ImageGrab, ImageTk, ImageDraw, Image
import qrcode
import json
from datetime import datetime


init(autoreset=True)

DATE_FOLDER = "Date"
CONFIG_PATH = os.path.join(DATE_FOLDER, "color_config.ini")

def create_default_config():
    config = ConfigParser()
    config["help_command"] = {"fg": "blue", "bg": "black"}
    config["error_message"] = {"fg": "red", "bg": ""}
    config["prompt"] = {"fg": "green", "bg": ""}
    os.makedirs(DATE_FOLDER, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)
    return config

def load_color_config():
    config = ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        return create_default_config()
    config.read(CONFIG_PATH, encoding="utf-8")
    return config

color_config = load_color_config()

def color(fg_color=None, bg_color=None):
    color_code = ""
    fg_map = {
        "black": Fore.BLACK, "red": Fore.RED, "green": Fore.GREEN,
        "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN, "white": Fore.WHITE
    }
    if fg_color and fg_color.lower() in fg_map:
        color_code += fg_map[fg_color.lower()]
    return color_code

def help():
    try:
        with open("help.txt", "r", encoding="utf-8") as f:
            msg = f.read()
            cfg = color_config["help_command"]
            print(color(cfg["fg"], cfg["bg"]) + msg)
    except FileNotFoundError:
        cfg = color_config["error_message"]
        print(color(cfg["fg"], cfg["bg"]) + "Error: help.txt does not exist")

def date():

    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted)

class ScreenshotTool:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Tool")
        self.btn_full = tk.Button(root, text="Full Screen", command=self.capture_fullscreen)
        self.btn_full.pack(pady=10)
        self.btn_area = tk.Button(root, text="Select Area", command=self.start_area_selection)
        self.btn_area.pack(pady=10)
        self.preview_label = tk.Label(root)
        self.preview_label.pack()
        self.start_x = self.start_y = self.rect = None

    def capture_fullscreen(self):
        img = ImageGrab.grab()
        img.save("full_screenshot.png")
        self.show_preview(img)

    def start_area_selection(self):
        self.root.withdraw()
        self.area_window = tk.Toplevel()
        self.area_window.attributes('-fullscreen', True)
        self.area_window.attributes('-alpha', 0.3)
        self.area_window.bind("<ButtonPress-1>", self.on_press)
        self.area_window.bind("<B1-Motion>", self.on_drag)
        self.area_window.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x, self.start_y = event.x_root, event.y_root
        self.rect = tk.Canvas(self.area_window, cursor="cross")
        self.rect.pack(fill="both", expand=True)

    def on_drag(self, event):
        if self.rect:
            self.rect.delete("rectangle")
            x, y = min(self.start_x, event.x_root), min(self.start_y, event.y_root)
            w, h = abs(self.start_x - event.x_root), abs(self.start_y - event.y_root)
            self.rect.create_rectangle(x, y, x+w, y+h, outline="red", width=2, tag="rectangle")

    def on_release(self, event):
        self.area_window.destroy()
        self.root.deiconify()
        x0, y0 = min(self.start_x, event.x_root), min(self.start_y, event.y_root)
        x1, y1 = max(self.start_x, event.x_root), max(self.start_y, event.y_root)
        img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        img.save("area_screenshot.png")
        self.show_preview(img)

    def show_preview(self, img):
        img.thumbnail((300, 300))
        tk_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=tk_img)
        self.preview_label.image = tk_img

class AdvancedQRGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced QR Code Tool")
        self.root.geometry("800x600")
        
        self.current_image = None
        self.history = []
        self.load_config()
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        input_group = ttk.LabelFrame(control_frame, text="Input Content")
        input_group.pack(fill=tk.X, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(input_group, height=6, wrap=tk.WORD)
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        
        param_group = ttk.LabelFrame(control_frame, text="Advanced Parameters")
        param_group.pack(fill=tk.X, pady=5)
        
        ttk.Label(param_group, text="Error Correction:").grid(row=0, column=0, sticky="w")
        self.error_correction = ttk.Combobox(param_group, 
            values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"], 
            state="readonly")
        self.error_correction.current(1)
        self.error_correction.grid(row=0, column=1, sticky="e")
        
        ttk.Label(param_group, text="QR Version:").grid(row=1, column=0, sticky="w")
        self.version = ttk.Spinbox(param_group, from_=1, to=40, width=5)
        self.version.set("6")
        self.version.grid(row=1, column=1, sticky="e")
        
        style_group = ttk.LabelFrame(control_frame, text="Style Settings")
        style_group.pack(fill=tk.X, pady=5)
        
        ttk.Label(style_group, text="Foreground:").grid(row=0, column=0, sticky="w")
        self.fg_color = ttk.Combobox(style_group, 
            values=["#000000", "#FF0000", "#00FF00", "#0000FF", "#800080"])
        self.fg_color.current(0)
        self.fg_color.grid(row=0, column=1, sticky="e")
        
        ttk.Label(style_group, text="Background:").grid(row=1, column=0, sticky="w")
        self.bg_color = ttk.Combobox(style_group, 
            values=["#FFFFFF", "#FFFF00", "#FFC0CB", "#C0C0C0"])
        self.bg_color.current(0)
        self.bg_color.grid(row=1, column=1, sticky="e")
        
        logo_group = ttk.LabelFrame(control_frame, text="LOGO Settings")
        logo_group.pack(fill=tk.X, pady=5)
        
        self.logo_path = tk.StringVar()
        ttk.Entry(logo_group, textvariable=self.logo_path, state="readonly").pack(fill=tk.X, padx=5)
        ttk.Button(logo_group, text="Select LOGO", command=self.select_logo).pack(pady=5)
        self.logo_size = ttk.Scale(logo_group, from_=0.1, to=0.3, orient=tk.HORIZONTAL)
        self.logo_size.set(0.2)
        self.logo_size.pack(fill=tk.X, padx=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Generate QR", command=self.generate_qr).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Batch Generate", command=self.batch_generate).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save Config", command=self.save_config).pack(side=tk.RIGHT, padx=2)
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(expand=True)
        
        history_group = ttk.LabelFrame(preview_frame, text="Generation History")
        history_group.pack(fill=tk.BOTH, expand=True)
        
        self.history_list = tk.Listbox(history_group)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        self.history_list.bind("<<ListboxSelect>>", self.show_history_item)
        
    def select_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.logo_path.set(path)
            
    def generate_qr(self, data=None, save=False):
        try:
            content = data or self.text_input.get("1.0", tk.END).strip()
            if not content:
                raise ValueError("Content cannot be empty")
                
            qr = qrcode.QRCode(
                version=int(self.version.get()),
                error_correction=self.get_error_level(),
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            
            img = qr.make_image(
                fill_color=self.fg_color.get(),
                back_color=self.bg_color.get()
            ).convert("RGB")
            
            if self.logo_path.get():
                img = self.add_logo(img)
                
            self.current_image = img
            self.add_to_history(content)
            self.show_preview(img)
            
            if save:
                return img
                
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))
    
    def add_logo(self, img):
        logo = Image.open(self.logo_path.get())
        base_width = int(img.size[0] * self.logo_size.get())
        wpercent = (base_width / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((base_width, hsize), Image.LANCZOS)
        
        mask = Image.new("L", logo.size, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)
        
        pos = (
            (img.size[0] - logo.size[0]) // 2,
            (img.size[1] - logo.size[1]) // 2
        )
        img.paste(logo, pos, mask)
        return img
        
    def batch_generate(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not path:
            return
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                
            save_dir = filedialog.askdirectory()
            if not save_dir:
                return
                
            for i, text in enumerate(lines):
                img = self.generate_qr(text, save=True)
                img.save(os.path.join(save_dir, f"qrcode_{i+1}.png"))
                
            messagebox.showinfo("Complete", f"Generated {len(lines)} QR codes")
            
        except Exception as e:
            messagebox.showerror("Batch Error", str(e))
    
    def add_to_history(self, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "time": timestamp,
            "content": content[:50] + "..." if len(content) > 50 else content,
            "image": self.current_image
        }
        self.history.insert(0, entry)
        self.history_list.insert(0, f"{timestamp} - {entry['content']}")
    
    def show_history_item(self, event):
        selection = self.history_list.curselection()
        if selection:
            entry = self.history[selection[0]]
            self.show_preview(entry["image"])
    
    def show_preview(self, img):
        img.thumbnail((400, 400))
        tk_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=tk_img)
        self.preview_label.image = tk_img
        
    def get_error_level(self):
        levels = {
            "L (7%)": qrcode.constants.ERROR_CORRECT_L,
            "M (15%)": qrcode.constants.ERROR_CORRECT_M,
            "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
            "H (30%)": qrcode.constants.ERROR_CORRECT_H
        }
        return levels[self.error_correction.get()]
    
    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.fg_color.set(config.get("fg_color", "#000000"))
                self.bg_color.set(config.get("bg_color", "#FFFFFF"))
                self.version.set(config.get("version", 6))
                self.error_correction.current(config.get("error_level", 1))
        except FileNotFoundError:
            pass
            
    def save_config(self):
        config = {
            "fg_color": self.fg_color.get(),
            "bg_color": self.bg_color.get(),
            "version": self.version.get(),
            "error_level": self.error_correction.current()
        }
        with open("config.json", "w") as f:
            json.dump(config, f)
        messagebox.showinfo("Info", "Configuration saved")






class EnhancedCalculator:
    
    
    def __init__(self, master):
        self.master = master
        master.title("calculator")
        master.geometry("500x650")
        master.configure(bg="#f3f3f3")

            
        self.display_font = font.Font(family="Segoe UI", size=24)
        self.btn_font = font.Font(family="Segoe UI", size=12)
        self.sci_btn_font = font.Font(family="Segoe UI", size=10)

            
        self.current_input = "0"
        self.history = []
        self.memory = 0
        self.last_operation = None
        self.special_triggered = False

        
        self.create_widgets()

        
        master.bind("<Key>", self.handle_keyboard)

    def create_widgets(self):
      
        main_frame = tk.Frame(self.master, bg="#f3f3f3")
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

      
        self.display = tk.Entry(
            main_frame,
            font=self.display_font,
            justify='right',
            bd=2,
            relief='flat',
            bg="white",
            fg="black",
            insertwidth=0
        )
        self.display.grid(row=0, column=0, columnspan=5, sticky="nsew", pady=5)
        self.display.insert(0, "0")
        self.display.config(state='readonly')

       
        self.history_label = tk.Label(
            main_frame,
            text="History",
            font=self.sci_btn_font,
            bg="#f3f3f3",
            anchor='w'
        )
        self.history_label.grid(row=1, column=0, columnspan=5, sticky="w")

        self.history_text = tk.Text(
            main_frame,
            height=4,
            width=40,
            font=self.sci_btn_font,
            bg="white",
            relief='flat'
        )
        self.history_text.grid(row=2, column=0, columnspan=5, sticky="nsew", pady=5)

       
        buttons = [
            
            ('√', 3, 0, 1, '#e9ecef', self.sqrt),
            ('x²', 3, 1, 1, '#e9ecef', self.square),
            ('1/x', 3, 2, 1, '#e9ecef', self.reciprocal),
            ('n!', 3, 3, 1, '#e9ecef', self.factorial),
            ('CE', 3, 4, 1, '#ffd8a8', self.clear_entry),

           
            ('sin', 4, 0, 1, '#e9ecef', lambda: self.trig_func('sin')),
            ('cos', 4, 1, 1, '#e9ecef', lambda: self.trig_func('cos')),
            ('tan', 4, 2, 1, '#e9ecef', lambda: self.trig_func('tan')),
            ('π', 4, 3, 1, '#e9ecef', self.pi),
            ('C', 4, 4, 1, '#ffaba8', self.clear),

            
            ('7', 5, 0, 1, '#ffffff', lambda: self.number('7')),
            ('8', 5, 1, 1, '#ffffff', lambda: self.number('8')),
            ('9', 5, 2, 1, '#ffffff', lambda: self.number('9')),
            ('÷', 5, 3, 1, '#4dabf7', lambda: self.operation('÷')),
            ('%', 5, 4, 1, '#4dabf7', lambda: self.operation('%')),

           
            ('4', 6, 0, 1, '#ffffff', lambda: self.number('4')),
            ('5', 6, 1, 1, '#ffffff', lambda: self.number('5')),
            ('6', 6, 2, 1, '#ffffff', lambda: self.number('6')),
            ('×', 6, 3, 1, '#4dabf7', lambda: self.operation('×')),
            ('MS', 6, 4, 1, '#4dabf7', self.memory_store),

           
            ('1', 7, 0, 1, '#ffffff', lambda: self.number('1')),
            ('2', 7, 1, 1, '#ffffff', lambda: self.number('2')),
            ('3', 7, 2, 1, '#ffffff', lambda: self.number('3')),
            ('-', 7, 3, 1, '#4dabf7', lambda: self.operation('-')),
            ('MR', 7, 4, 1, '#4dabf7', self.memory_recall),

           
            ('0', 8, 0, 2, '#ffffff', lambda: self.number('0'), 10),
            ('.', 8, 2, 1, '#ffffff', lambda: self.number('.')),
            ('+', 8, 3, 1, '#4dabf7', lambda: self.operation('+')),
            ('=', 8, 4, 1, '#4dabf7', self.calculate)
        ]

        
        for btn_def in buttons:
            text, row, col, colspan, color, command = btn_def[:6]
            btn = tk.Button(
                main_frame,
                text=text,
                font=self.sci_btn_font if row < 5 else self.btn_font,
                bg=color,
                fg='black',
                activebackground='#dee2e6',
                bd=0,
                padx=8,
                pady=8,
                command=command
            )
            if colspan > 1:
                btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=1, pady=1)
            else:
                btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

        
        for i in range(9):
            main_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            main_frame.grid_columnconfigure(i, weight=1)

    def update_display(self):
        self.display.config(state='normal')
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_input)
        self.display.config(state='readonly')

    def number(self, num):
        if self.current_input == "0" or self.special_triggered:
            self.current_input = num
            self.special_triggered = False
        else:
            if num == '.':
                if '.' not in self.current_input:
                    self.current_input += num
            else:
                self.current_input += num
        self.update_display()

    def operation(self, op):
        try:
            self.history.append(float(self.current_input))
            self.history.append(op)
            self.current_input = "0"
            self.update_display()
            self.update_history()
        except:
            self.show_error()

    def calculate(self):
        try:
            if len(self.history) >= 2:
                self.history.append(float(self.current_input))

                
                if self.check_special():
                    self.trigger_special()
                    return

                expression = ' '.join(map(str, self.history))
                expression = expression.replace('×', '*').replace('÷', '/')
                result = eval(expression)

              
                formatted_result = "{:.10f}".format(result).rstrip('0').rstrip('.')
                self.current_input = formatted_result if '.' in formatted_result else str(int(result))
                self.update_display()

                
                self.history_text.insert(tk.END, f"{expression} = {self.current_input}\n")
                self.history_text.see(tk.END)

               
                self.history = []
                self.last_operation = None
        except Exception as e:
            self.show_error()

    def check_special(self):
       
        if len(self.history) == 3:
            num1, op, num2 = self.history
            return (
                    math.isclose(num1, 2016.0, rel_tol=1e-9) and
                    op == '÷' and
                    math.isclose(num2, 13.0, rel_tol=1e-9)
            )
        return False

    def trigger_special(self):
        self.special_triggered = True
        self.show_message("🎉 The hidden function has been triggered!",'2016 ÷ 13 = 155.076923077\n''This is a classic easter egg of the Windows Calculator!\n''A hidden feature from the Windows 95 era.')
        self.current_input = "155.076923077"
        self.update_display()
        self.history = []

        
        colors = ["#e6f3ff", "#cce7ff", "#99cfff"]
        for i, color in enumerate(colors + colors[-2::-1]):
            self.master.after(100 * i, lambda c=color: self.master.configure(bg=c))
        self.master.after(600, lambda: self.master.configure(bg="#f3f3f3"))

    
    def sqrt(self):
        try:
            num = float(self.current_input)
            self.current_input = str(math.sqrt(num))
            self.update_display()
        except:
            self.show_error()

    def square(self):
        try:
            num = float(self.current_input)
            self.current_input = str(num ** 2)
            self.update_display()
        except:
            self.show_error()

    def reciprocal(self):
        try:
            num = float(self.current_input)
            self.current_input = str(1 / num)
            self.update_display()
        except:
            self.show_error()

    def factorial(self):
        try:
            num = int(float(self.current_input))
            if num < 0:
                raise ValueError
            self.current_input = str(math.factorial(num))
            self.update_display()
        except:
            self.show_error()

    def trig_func(self, func):
        try:
            num = float(self.current_input)
            if func == 'sin':
                res = math.sin(math.radians(num))
            elif func == 'cos':
                res = math.cos(math.radians(num))
            elif func == 'tan':
                res = math.tan(math.radians(num))
            self.current_input = "{:.10f}".format(res).rstrip('0').rstrip('.')
            self.update_display()
        except:
            self.show_error()

   
    def clear(self):
        self.current_input = "0"
        self.history = []
        self.update_display()
        self.update_history()

    def clear_entry(self):
        self.current_input = "0"
        self.update_display()

    def update_history(self):
        self.history_label.config(text=f"Operation history：{' '.join(map(str, self.history))}")

    def handle_keyboard(self, event):
        key = event.char.lower()
        key_mappings = {
            'c': self.clear,
            'r': self.sqrt,
            's': lambda: self.trig_func('sin'),
            't': lambda: self.trig_func('tan'),
            'q': self.square,
            'm': self.memory_store,
            'v': self.memory_recall
        }

        if key in key_mappings:
            key_mappings[key]()
        elif key in '0123456789':
            self.number(key)
        elif key == '.':
            self.number('.')
        elif event.keysym in {'Return', 'equal'}:
            self.calculate()
        elif event.char in {'+', '-', '*', '/'}:
            op_map = {'+': '+', '-': '-', '*': '×', '/': '÷'}
            self.operation(op_map[event.char])

    def memory_store(self):
        try:
            self.memory = float(self.current_input)
        except:
            self.show_error()

    def memory_recall(self):
        self.current_input = str(self.memory)
        self.update_display()

    def pi(self):
        self.current_input = str(math.pi)
        self.update_display()

    def show_error(self):
        self.current_input = "mistake"
        self.update_display()
        self.master.after(1000, self.clear_entry)

    def show_message(self, title, message):
        messagebox.showinfo(title, message)




def main():
    
    
    print("[Version 2.0]") 
    print('''_    ________     
    |\   ____\ |\   __  \ |\   _ \  _   \ |\   _ \  _   \ |\   __  \ |\   ___  \ |\   ___ \    
    \ \  \___| \ \  \|\  \\ \  \\\__\ \  \\ \  \\\__\ \  \\ \  \|\  \\ \  \\ \  \\ \  \_|\ \   
     \ \  \     \ \  \\\  \\ \  \\|__| \  \\ \  \\|__| \  \\ \   __  \\ \  \\ \  \\ \  \ \\ \  
      \ \  \____ \ \  \\\  \\ \  \    \ \  \\ \  \    \ \  \\ \  \ \  \\ \  \\ \  \\ \  \_\\ \ 
       \ \_______\\ \_______\\ \__\    \ \__\\ \__\    \ \__\\ \__\ \__\\ \__\\ \__\\ \_______\
        \|_______| \|_______| \|__|     \|__| \|__|     \|__| \|__|\|__| \|__| \|__| \|_______|
        ''')
                                                                                           
                                                                                          
    
   

    while True:
        user_input = input("C:\\Users\\GitHub\\Desktop> ").strip().lower()

        if user_input == "exit":
            print("Exit the command line")
            break

        elif user_input == "help":
            help()

        elif user_input == "dir":
            subprocess.run("dir", shell=True)

        elif re.match(r"^color\(\s*[a-zA-Z]+\s*,\s*[a-zA-Z]+\s*\)$", user_input):
            match = re.search(r"color\((.*),(.*)\)", user_input)

            fg_color = match.group(1).strip()
            bg_color = match.group(2).strip()
            print(color(fg_color, bg_color))

        elif user_input == "calculator":
            root = tk.Tk()
            EnhancedCalculator(root)
            root.mainloop()

        elif user_input == 'screenshot':
            root = tk.Tk()
            ScreenshotTool(root)
            root.mainloop()

        elif user_input == 'date':
            date()

        elif user_input == 'qrcode':
            root = tk.Tk()
            AdvancedQRGenerator(root)
            root.mainloop()

        else:
            print(f"Error: Unknown command {user_input}，Enter 'help' to see the supported commands")

if __name__ == "__main__":
    main()
