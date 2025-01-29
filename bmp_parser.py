import tkinter as tk
import tkinter.filedialog

def browse_file():
    filepath = tk.filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)
    open_file(filepath)  # Automatically process file after selection

def open_file(filepath):
    try:
        with open(filepath, "rb") as f:
            bmp_header = f.read(54)  # Read BMP header (first 54 bytes)

        # Check if file is a valid BMP
        if bmp_header[0:2] == b'BM':
            file_size = int.from_bytes(bmp_header[2:6], byteorder='little')
            width_no_padding = int.from_bytes(bmp_header[18:22], byteorder='little')
            height = int.from_bytes(bmp_header[22:26], byteorder='little')
            bits_per_pixel = int.from_bytes(bmp_header[28:30], byteorder='little')

            width_padding = width_no_padding + (4 - width_no_padding % 4) % 4

            # Update labels with extracted values
            file_size_label.config(text=f"File Size: {file_size} bytes")
            width_label.config(text=f"Width: {width_padding} pixels")
            height_label.config(text=f"Height: {height} pixels")
            bpp_label.config(text=f"Bits Per Pixel: {bits_per_pixel}")
        else:
            file_size_label.config(text="Invalid BMP file")
    except Exception as e:
        file_size_label.config(text="Error reading file")

# GUI Setup
root = tk.Tk()
root.title("BMP Info Viewer")

# File selection row
tk.Label(root, text="File Path").grid(row=0, column=0)
file_path_entry = tk.Entry(root, width=50)
file_path_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

# Labels for displaying BMP info
file_size_label = tk.Label(root, text="File Size: ")
file_size_label.grid(row=1, column=0, columnspan=3, sticky="w")

width_label = tk.Label(root, text="Width: ")
width_label.grid(row=2, column=0, columnspan=3, sticky="w")

height_label = tk.Label(root, text="Height: ")
height_label.grid(row=3, column=0, columnspan=3, sticky="w")

bpp_label = tk.Label(root, text="Bits Per Pixel: ")
bpp_label.grid(row=4, column=0, columnspan=3, sticky="w")

root.mainloop()
