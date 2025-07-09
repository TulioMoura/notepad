import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog,PhotoImage
import tkinter.font as tkFont
import json
import os
import platform

CONFIG_FILE = "config.json"

COMMON_FONTS = [
    "Consolas", "Courier New", "Arial", "Helvetica", "Verdana",  # sans-serif
    "Times New Roman", "Georgia", "Garamond", "Palatino", "Serif"  # serif
]

class SimpleNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Bloco de Notas")
        self.filename = None
        self.config = self.load_config()
        w = self.config.get("width", 800)
        h = self.config.get("height", 600)
        self.root.geometry(f"{w}x{h}")

        self.font_size = self.config.get("font_size", 12)
        self.font_family = self.config.get("font_family", "Consolas")
        self.theme = self.config.get("theme", "system")
        self.font = tkFont.Font(family=self.font_family, size=self.font_size)

        self.root.iconphoto(False, PhotoImage(file="icon.ico"))
        

        self.create_widgets()
        self.create_menus()
        self.apply_theme()
        self.bind_shortcuts()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)



        self.line_numbers = tk.Text(self.main_frame, width=4, padx=4, takefocus=0, border=0,
                                    background="#f0f0f0", state='disabled', font=self.font)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.separator = tk.Frame(self.main_frame, width=1, bg="#a0a0a0",)
        self.separator.pack(side=tk.LEFT, fill=tk.Y)

        self.text = tk.Text(self.main_frame, font=self.font, undo=True, wrap='word')
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text.bind("<KeyRelease>", self.update_line_numbers)
        self.text.bind("<MouseWheel>", self.sync_scroll)
        self.text.bind("<Button-4>", self.sync_scroll)  # Linux scroll up
        self.text.bind("<Button-5>", self.sync_scroll)  # Linux scroll down
        self.text.bind("<Configure>", self.update_line_numbers)

        self.text_scroll = tk.Scrollbar(self.text, command=self.sync_both)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=self.on_text_scroll)

    def on_text_scroll(self, *args):
        self.line_numbers.yview_moveto(args[0])
        self.text_scroll.set(*args)

    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.text.yview()[0])

    def sync_both(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        line_count = int(self.text.index('end-1c').split('.')[0])
        lines = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert(1.0, lines)
        self.line_numbers.config(state='disabled')

    def create_menus(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Abrir", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Salvar como", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        font_menu = tk.Menu(options_menu, tearoff=0)
        for f in COMMON_FONTS:
            font_menu.add_command(label=f, command=lambda ff=f: self.set_font(ff))
        options_menu.add_cascade(label="Fonte", menu=font_menu)

        theme_menu = tk.Menu(options_menu, tearoff=0)
        theme_menu.add_command(label="Claro", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Escuro", command=lambda: self.set_theme("dark"))
        theme_menu.add_command(label="Sistema", command=lambda: self.set_theme("system"))
        options_menu.add_cascade(label="Tema", menu=theme_menu)

        menu_bar.add_cascade(label="Opções", menu=options_menu)
        self.root.config(menu=menu_bar)

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_file_as())
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-plus>", self.increase_font)
        self.root.bind("<Control-minus>", self.decrease_font)
        self.root.bind("<Control-equal>", self.increase_font)

    def apply_theme(self):
        mode = self.theme
        if mode == "system":
            if platform.system() == "Windows":
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                        val = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
                        mode = "light" if val == 1 else "dark"
                except:
                    mode = "light"
            else:
                mode = "light"

        bg = "#ffffff" if mode == "light" else "#1e1e1e"
        fg = "#000000" if mode == "light" else "#d4d4d4"
        self.text.config(bg=bg, fg=fg, insertbackground=fg)
        self.line_numbers.config(bg="#f0f0f0" if mode == "light" else "#2a2a2a",
                                 fg="#000000" if mode == "light" else "#cccccc")

    def set_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    def open_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)
                self.filename = path
                self.root.title(f"Bloco de Notas - {os.path.basename(path)}")
                self.update_line_numbers()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def save_file(self):
        if not self.filename:
            self.save_file_as()
            return
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write(self.text.get(1.0, tk.END))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension="",
                                            initialfile="arquivo_texto",
                                            filetypes=[("Todos os arquivos", "*.*")])
        if not path:
            return
        self.filename = path
        self.save_file()
        self.root.title(f"Bloco de Notas - {os.path.basename(path)}")

    def new_file(self):
        if self.text.edit_modified():
            resp = messagebox.askyesnocancel("Salvar", "Deseja salvar o arquivo atual?")
            if resp is None:
                return
            if resp:
                self.save_file()
        self.text.delete(1.0, tk.END)
        self.filename = None
        self.root.title("Bloco de Notas")
        self.update_line_numbers()

    def increase_font(self, event=None):
        self.font_size += 1
        self.font.configure(size=self.font_size)
        self.update_line_numbers()

    def decrease_font(self, event=None):
        if self.font_size > 1:
            self.font_size -= 1
            self.font.configure(size=self.font_size)
            self.update_line_numbers()

    def set_font(self, family):
        self.font_family = family
        self.font.configure(family=family)
        self.update_line_numbers()

    def on_close(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        self.save_config({
            "width": width,
            "height": height,
            "font_size": self.font_size,
            "font_family": self.font_family,
            "theme": self.theme
        })
        self.root.destroy()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self, config):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleNotepad(root)
    root.mainloop()
