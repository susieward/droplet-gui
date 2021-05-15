import subprocess
import queue
import threading
import tkinter as tk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from tkinter import N, S, E, W
from config import CommandsConfig

config = CommandsConfig()

class Console:
    def __init__(self, frame):
        self.frame = frame
        self.process = None
        self.cmd = tk.StringVar()
        self.queue = queue.Queue()
        self.thread = None
        self.font = Font(family='Courier New', name='outputFont', size=16, weight='normal')
        self.bg = '#121212'
        self.fg = '#32CD32'
        self.init_input()
        self.init_output()
        self.login()
        self.frame.after(100, self.get_output)

    def init_input(self):
        # input container grid
        self.input_container = tk.Frame(self.frame)
        self.input_container.grid(row=1, column=0, sticky=N+W, padx=20, pady=0)
        self.input_container.config(bg=self.bg)
        tk.Grid.rowconfigure(self.input_container, 0, weight=1)
        tk.Grid.rowconfigure(self.input_container, 1, weight=1)
        tk.Grid.columnconfigure(self.input_container, 0, weight=1)

        # input label text
        label = tk.Label(self.input_container, text='Input:', bg=self.bg, fg=self.fg, font=self.font)
        label.grid(row=0, column=0, sticky=N+W)

        # input entry
        self.entry = tk.Entry(self.input_container, bg=self.bg, fg=self.fg, font=self.font)
        self.entry.grid(row=1, column=0)
        self.entry["textvariable"] = self.cmd
        self.entry.bind('<Key-Return>', self.enter_command)

    def init_output(self):
        # output label frame
        self.window = tk.LabelFrame(self.frame, text='Output:', height="1300px", bg=self.bg, fg=self.fg, font=self.font)
        self.window.grid(row=2, column=0, sticky=N+S+E+W, padx=20, pady=20)
        tk.Grid.columnconfigure(self.window, 0, weight=1)
        tk.Grid.rowconfigure(self.window, 0, weight=1)
        tk.Grid.rowconfigure(self.window, 1, weight=2)

        # scrolled text output
        self.scrolled_text = ScrolledText(self.window, state='disabled', height=36)
        self.scrolled_text.grid(row=0, column=0, sticky=N+S+E+W, padx=15, pady=15)
        self.scrolled_text.configure(background='#121212', foreground='#32CD32', font=self.font, wrap='word')

    def login(self):
        # ssh into server via pre-configured executable script
        self.process = subprocess.Popen(['droplet'],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            start_new_session=True)
        t = threading.Thread(target=self.output_reader, args=(self.process,))
        t._stop_event = threading.Event()
        self.thread = t
        self.thread.start()

    def output_reader(self, proc):
        for line in iter(proc.stdout.readline, b''):
            self.queue.put(line.decode('utf-8'))

    def get_output(self):
        while True:
            try:
                record = self.queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.show_message(message=record)
        self.frame.after(100, self.get_output)

    def show_message(self, message):
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, message)
        self.scrolled_text.configure(state='disabled')
        #self.scrolled_text.yview(tk.END)

    def flush_output(self):
        self.process.stdout.flush()
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.delete(1.0, tk.END)
        self.scrolled_text.configure(state='disabled')
        return

    def enter_command(self, event):
        try:
            cmd = self.cmd.get()
            bytestr = bytes(f'{cmd}\n', encoding='utf-8')
            self.flush_output()
            self.process.stdin.write(bytestr)
            self.process.stdin.flush()
            self.frame.after(100, self.get_output)
            self.cmd.set('')
        except Exception as e:
            print(f'Caught exception: {e}')

    def check_status(self):
        self.flush_output()
        self.process.stdin.write(config.xgen_status)
        self.process.stdin.flush()
        self.frame.after(100, self.get_output)

    def get_logs(self):
        self.flush_output()
        self.process.stdin.write(config.xgen_gunicorn)
        self.process.stdin.write(config.pwd)
        self.process.stdin.flush()
        self.frame.after(100, self.get_output)

    def access_logs(self):
        self.flush_output()
        self.process.stdin.write(config.nginx_access)
        self.process.stdin.write(config.pwd)
        self.process.stdin.flush()
        self.frame.after(100, self.get_output)

    def logout(self):
        self.process.stdin.write(b'exit\n')
        self.process.stdin.flush()
        self.process.terminate()
        self.thread._stop_event.set()
