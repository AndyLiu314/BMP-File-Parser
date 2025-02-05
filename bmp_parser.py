import tkinter as tk
import tkinter.filedialog
import numpy as np
from PIL import Image, ImageTk

# Global variables to store image data and settings
original_rgb = []
original_width = 0
original_height = 0
current_photo = None
r_enabled = True
g_enabled = True
b_enabled = True

# RGB_TO_YUV = np.array([
#     [0.299, 0.587, 0.114],
#     [-0.299, -0.587, 0.886],
#     [0.701, -0.587, -0.114]
# ])

RGB_TO_YUV = np.array([
    [0.299, 0.587, 0.114],
    [-0.147, -0.289, 0.436],
    [0.615, -0.515, -0.100]
])

YUV_TO_RGB = np.array([
    [1, 0, 1.13983],
    [1, -0.39465, -0.58060],
    [1, 2.03211, 0]
])

def browse_file():
    filepath = tk.filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)
    open_file(filepath)

def open_file(filepath):
    global original_rgb, original_width, original_height
    try:
        with open(filepath, "rb") as f:
            bmp_header = f.read(54)

        if bmp_header[0:2] != b'BM':
            file_size_label.config(text="Invalid BMP file")
            return

        file_size = int.from_bytes(bmp_header[2:6], 'little')
        width = int.from_bytes(bmp_header[18:22], 'little')
        height = int.from_bytes(bmp_header[22:26], 'little', signed=True)
        bits_per_pixel = int.from_bytes(bmp_header[28:30], 'little')
        data_offset = int.from_bytes(bmp_header[10:14], 'little')
        colors_used = int.from_bytes(bmp_header[46:50], 'little')

        width_padding = width + (4 - width % 4) % 4

        abs_height = abs(height)
        color_table = []

        # Read color table for 1/4/8 bpp
        if bits_per_pixel in [1, 4, 8]:
            num_colors = 2 ** bits_per_pixel if colors_used == 0 else colors_used
            with open(filepath, "rb") as f:
                f.seek(54)
                color_table_data = f.read(num_colors * 4)
                for i in range(num_colors):
                    entry = color_table_data[i*4 : (i+1)*4]
                    blue, green, red, _ = entry
                    color_table.append((red, green, blue))

        # Read pixel data
        with open(filepath, "rb") as f:
            f.seek(data_offset)
            pixel_data = f.read()

        # Calculate bytes per row
        bits_per_row = width * bits_per_pixel
        bytes_per_row = ((bits_per_row + 31) // 32) * 4

        # Convert to RGB array
        original_rgb = []
        row_order = reversed(range(abs_height))
        
        for y in row_order:
            row_start = y * bytes_per_row
            row_end = row_start + bytes_per_row
            row_bytes = pixel_data[row_start:row_end]
            rgb_row = []
            
            for x in range(width):
                if bits_per_pixel == 1:
                    byte_idx = x // 8
                    bit_idx = 7 - (x % 8)
                    index = (row_bytes[byte_idx] >> bit_idx) & 1 if byte_idx < len(row_bytes) else 0
                elif bits_per_pixel == 4:
                    nibble_idx = x % 2
                    byte_idx = x // 2
                    byte = row_bytes[byte_idx] if byte_idx < len(row_bytes) else 0
                    index = (byte >> (4 * (1 - nibble_idx))) & 0x0F
                elif bits_per_pixel == 8:
                    index = row_bytes[x] if x < len(row_bytes) else 0
                elif bits_per_pixel == 24:
                    pixel_start = x * 3
                    b, g, r = row_bytes[pixel_start], row_bytes[pixel_start+1], row_bytes[pixel_start+2]
                    rgb_row.append((r, g, b))
                    continue
                else:
                    rgb_row.append((0, 0, 0))
                    continue

                if bits_per_pixel in [1, 4, 8]:
                    if index < len(color_table):
                        r, g, b = color_table[index]
                        rgb_row.append((r, g, b))
                    else:
                        rgb_row.append((0, 0, 0))
                        
            original_rgb.append(rgb_row)

        original_width = width
        original_height = abs_height

        # Update labels and image
        file_size_label.config(text=f"File Size: {file_size} bytes")
        width_label.config(text=f"Width: {width_padding} pixels")
        height_label.config(text=f"Height: {abs_height} pixels")
        bpp_label.config(text=f"Bits Per Pixel: {bits_per_pixel}")
        
        update_image()

    except Exception as e:
        file_size_label.config(text=f"Error: {str(e)}")

def update_image(*args):
    global current_photo
    if not original_rgb:
        return

    try:
        # Get current settings
        brightness = brightness_slider.get() / 100.0
        scale = scale_slider.get() / 100.0
        
        # Calculate scaled dimensions
        scaled_width = int(original_width * scale)
        scaled_height = int(original_height * scale)

        original_array_np = np.array(original_rgb, dtype=np.uint8)

        # Calculate indices for scaling (nearest-neighbor interpolation)
        y_indices = np.floor(np.linspace(0, original_height, scaled_height, endpoint=False)).astype(int)
        y_indices = np.clip(y_indices, 0, original_height - 1)
        x_indices = np.floor(np.linspace(0, original_width, scaled_width, endpoint=False)).astype(int)
        x_indices = np.clip(x_indices, 0, original_width - 1)

        # Perform scaling using advanced indexing
        scaled_array = original_array_np[y_indices[:, None], x_indices]

        # # Apply YUV brightness adjustment
        # scaled_float = scaled_array.astype(np.float32)

        # # Convert RGB to YUV
        # h, w, c = scaled_float.shape
        # rgb_flat = scaled_float.reshape(-1, 3)
        # yuv_flat = np.dot(rgb_flat, RGB_TO_YUV.T)
        
        # # Apply brightness to Y component
        # yuv_flat[..., 0] *= brightness
        
        # # Convert back to RGB
        # rgb_processed_flat = np.dot(yuv_flat, YUV_TO_RGB.T)
        # scaled_float = rgb_processed_flat.reshape(h, w, 3)

        # Convert RGB to YUV
        yuv_array = np.dot(scaled_array, RGB_TO_YUV.T)

        # Apply brightness to the YUV
        yuv_array[..., 0] *= brightness
        yuv_array[..., 1] *= brightness
        yuv_array[..., 2] *= brightness

        # Convert back to RGB
        scaled_array = np.dot(yuv_array, YUV_TO_RGB.T)

        if not r_enabled:
            scaled_array[..., 0] = 0.0
        if not g_enabled:
            scaled_array[..., 1] = 0.0
        if not b_enabled:
            scaled_array[..., 2] = 0.0

        # Clamp values and convert back to uint8
        processed_array = np.clip(scaled_array, 0, 255).astype(np.uint8)

        # Convert to Pillow Image and then to PhotoImage
        image_pil = Image.fromarray(processed_array, mode='RGB')
        current_image = ImageTk.PhotoImage(image_pil)

        image_label.config(image=current_image)
        image_label.image = current_image

    except Exception as e:
        file_size_label.config(text=f"Render Error: {str(e)}")

def toggle_channel(channel):
    global r_enabled, g_enabled, b_enabled
    if channel == 'R':
        r_enabled = not r_enabled
        r_toggle.config(relief="raised" if r_enabled else "sunken")
    elif channel == 'G':
        g_enabled = not g_enabled
        g_toggle.config(relief="raised" if g_enabled else "sunken")
    elif channel == 'B':
        b_enabled = not b_enabled
        b_toggle.config(relief="raised" if b_enabled else "sunken")
    update_image()

# GUI Setup
root = tk.Tk()
root.title("BMP Viewer")

# File selection
tk.Label(root, text="File Path").grid(row=0, column=0)
file_path_entry = tk.Entry(root, width=50)
file_path_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

# Info labels
file_size_label = tk.Label(root, text="File Size: ", anchor='w')
file_size_label.grid(row=1, column=0, columnspan=3, sticky='ew')

width_label = tk.Label(root, text="Width: ", anchor='w')
width_label.grid(row=2, column=0, columnspan=3, sticky='ew')

height_label = tk.Label(root, text="Height: ", anchor='w')
height_label.grid(row=3, column=0, columnspan=3, sticky='ew')

bpp_label = tk.Label(root, text="Bits Per Pixel: ", anchor='w')
bpp_label.grid(row=4, column=0, columnspan=3, sticky='ew')

# Controls
tk.Label(root, text="Brightness:").grid(row=5, column=0, sticky="sw")
brightness_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
brightness_slider.bind("<ButtonRelease-1>", update_image)
brightness_slider.set(100)
brightness_slider.grid(row=5, column=1, sticky='ew')

tk.Label(root, text="Scale:").grid(row=6, column=0, sticky="sw")
scale_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
scale_slider.bind("<ButtonRelease-1>", update_image)
scale_slider.set(100)
scale_slider.grid(row=6, column=1, sticky='ew')

# Channel buttons
button_frame = tk.Frame(root)
button_frame.grid(row=7, column=0, columnspan=3)
r_toggle = tk.Button(button_frame, text="R", relief="raised", command=lambda: toggle_channel('R'))
r_toggle.pack(side=tk.LEFT)
g_toggle = tk.Button(button_frame, text="G", relief="raised", command=lambda: toggle_channel('G'))
g_toggle.pack(side=tk.LEFT)
b_toggle = tk.Button(button_frame, text="B", relief="raised", command=lambda: toggle_channel('B'))
b_toggle.pack(side=tk.LEFT)

# Image display
image_label = tk.Label(root)
image_label.grid(row=8, column=0, columnspan=3)

root.mainloop()
