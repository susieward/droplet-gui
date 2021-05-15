import tkinter as tk
from tkinter.font import Font
from tkinter import N, S, E, W
from widgets.console import Console

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Droplet Desktop')
        self.root.geometry('1300x900')
        self.bg_color = '#121212'

        self._frame = tk.Frame(self.root)
        tk.Grid.rowconfigure(self.root, 0, weight=1)
        tk.Grid.columnconfigure(self.root, 0, weight=1)
        self._frame.grid(row=0, column=0, sticky=N+S+E+W)
        self._frame.config(bg=self.bg_color)

        self.frame = tk.Frame(self._frame)
        tk.Grid.rowconfigure(self._frame, 0, weight=1)
        tk.Grid.columnconfigure(self._frame, 0, weight=1)

        self.frame.grid(row=0, column=0, sticky=N+S+E+W)
        self.frame.config(bg=self.bg_color)

        tk.Grid.rowconfigure(self.frame, 0, weight=1)
        tk.Grid.rowconfigure(self.frame, 1, weight=1)
        tk.Grid.rowconfigure(self.frame, 2, weight=1)
        tk.Grid.columnconfigure(self.frame, 0, weight=1)

        self.console = Console(self.frame)
        self.init_buttons()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)

    def init_buttons(self):
        self.btn_container = tk.Frame(self.frame)
        self.btn_container.grid(row=0, column=0, sticky=N+W, padx=10, pady=10)
        self.btn_container.config(bg=self.bg_color)
        tk.Grid.rowconfigure(self.btn_container, 0, weight=1)

        btns = [
            { 'text': 'xfiles-generator status', 'command': self.console.check_status },
            { 'text': 'gunicorn logs', 'command': self.console.get_logs },
            { 'text': 'nginx access logs', 'command': self.console.access_logs },
            { 'text': 'quit', 'command': self.quit },
        ]
        for i in range(len(btns)):
            config = btns[i]
            btn = tk.Button(self.btn_container, text=config['text'], highlightbackground=self.bg_color, bg=self.bg_color, command=config['command'])
            btn.grid(row=0, column=i)

        for i in range(len(btns)):
            tk.Grid.columnconfigure(self.btn_container, i, weight=1)

    def quit(self):
        self.console.logout()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.root.mainloop()
