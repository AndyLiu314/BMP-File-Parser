import tkinter as tk
import tkinter.filedialog
from time import sleep
from threading import Thread


def browse_file():
    filepath = tk.filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)

root = tk.Tk()

tk.Label(root, text="File Path").grid(row=0, column=0)

file_path_entry = tk.Entry(root, width=50)
file_path_entry.grid(row=0, column=1)

tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

root.mainloop()