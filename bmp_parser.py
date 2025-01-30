# import tkinter as tk
# import tkinter.filedialog

# def browse_file():
#     filepath = tk.filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
#     file_path_entry.delete(0, tk.END)
#     file_path_entry.insert(0, filepath)
#     open_file(filepath)  # Automatically process file after selection

# def open_file(filepath):
#     try:
#         with open(filepath, "rb") as f:
#             bmp_header = f.read(54)  # Read BMP header (first 54 bytes)

#         # Check if file is a valid BMP
#         if bmp_header[0:2] == b'BM':
#             file_size = int.from_bytes(bmp_header[2:6], byteorder='little')
#             width_no_padding = int.from_bytes(bmp_header[18:22], byteorder='little')
#             height = int.from_bytes(bmp_header[22:26], byteorder='little')
#             bits_per_pixel = int.from_bytes(bmp_header[28:30], byteorder='little')

#             width_padding = width_no_padding + (4 - width_no_padding % 4) % 4

#             # Update labels with extracted values
#             file_size_label.config(text=f"File Size: {file_size} bytes")
#             width_label.config(text=f"Width: {width_padding} pixels")
#             height_label.config(text=f"Height: {height} pixels")
#             bpp_label.config(text=f"Bits Per Pixel: {bits_per_pixel}")
#         else:
#             file_size_label.config(text="Invalid BMP file")
#     except Exception as e:
#         file_size_label.config(text="Error reading file")

# # GUI Setup
# root = tk.Tk()
# root.title("BMP Info Viewer")

# # File selection row
# tk.Label(root, text="File Path").grid(row=0, column=0)
# file_path_entry = tk.Entry(root, width=50)
# file_path_entry.grid(row=0, column=1)
# tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

# # Labels for displaying BMP info
# file_size_label = tk.Label(root, text="File Size: ")
# file_size_label.grid(row=1, column=0, columnspan=3, sticky="w")

# width_label = tk.Label(root, text="Width: ")
# width_label.grid(row=2, column=0, columnspan=3, sticky="w")

# height_label = tk.Label(root, text="Height: ")
# height_label.grid(row=3, column=0, columnspan=3, sticky="w")

# bpp_label = tk.Label(root, text="Bits Per Pixel: ")
# bpp_label.grid(row=4, column=0, columnspan=3, sticky="w")

# root.mainloop()

import tkinter as tk
import tkinter.filedialog

# Global variables to store image data and settings
original_rgb = []
original_width = 0
original_height = 0
current_photo = None
r_enabled = True
g_enabled = True
b_enabled = True

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
        row_order = reversed(range(abs_height)) if height > 0 else range(abs_height)
        
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
                elif bits_per_pixel == 32:
                    pixel_start = x * 4
                    b, g, r, _ = row_bytes[pixel_start], row_bytes[pixel_start+1], row_bytes[pixel_start+2], row_bytes[pixel_start+3]
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
        width_label.config(text=f"Width: {width} pixels")
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
        scaled_width = max(1, int(original_width * scale))
        scaled_height = max(1, int(original_height * scale))

        # Create new photo image
        current_photo = tk.PhotoImage(width=scaled_width, height=scaled_height)
        
        # Process each pixel
        for y_new in range(scaled_height):
            y_old = min(int(y_new / scaled_height * original_height), original_height - 1)
            for x_new in range(scaled_width):
                x_old = min(int(x_new / scaled_width * original_width), original_width - 1)
                
                # Get original color
                r, g, b = original_rgb[y_old][x_old]
                
                # Apply brightness
                r = int(r * brightness)
                g = int(g * brightness)
                b = int(b * brightness)
                
                # Apply channel toggles
                if not r_enabled: r = 0
                if not g_enabled: g = 0
                if not b_enabled: b = 0
                
                # Clamp values
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                current_photo.put(hex_color, (x_new, y_new))

        image_label.config(image=current_photo)
        image_label.image = current_photo

    except Exception as e:
        file_size_label.config(text=f"Render Error: {str(e)}")

def toggle_channel(channel):
    global r_enabled, g_enabled, b_enabled
    if channel == 'R':
        r_enabled = not r_enabled
    elif channel == 'G':
        g_enabled = not g_enabled
    elif channel == 'B':
        b_enabled = not b_enabled
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
tk.Label(root, text="Brightness:").grid(row=5, column=0)
brightness_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_image)
brightness_slider.set(100)
brightness_slider.grid(row=5, column=1, sticky='ew')

tk.Label(root, text="Scale:").grid(row=6, column=0)
scale_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, command=update_image)
scale_slider.set(100)
scale_slider.grid(row=6, column=1, sticky='ew')

# Channel buttons
button_frame = tk.Frame(root)
button_frame.grid(row=7, column=0, columnspan=3)
tk.Button(button_frame, text="R", command=lambda: toggle_channel('R')).pack(side=tk.LEFT)
tk.Button(button_frame, text="G", command=lambda: toggle_channel('G')).pack(side=tk.LEFT)
tk.Button(button_frame, text="B", command=lambda: toggle_channel('B')).pack(side=tk.LEFT)

# Image display
image_label = tk.Label(root)
image_label.grid(row=8, column=0, columnspan=3)

root.mainloop()


# import tkinter as tk
# import tkinter.filedialog
# import numpy as np

# # Global variables
# original_rgb_np = np.zeros((0, 0, 3), dtype=np.uint8)
# original_height = 0
# original_width = 0
# current_photo = None
# r_enabled = True
# g_enabled = True
# b_enabled = True

# # YUV conversion matrices
# forward_matrix = np.array([
#     [0.299, 0.587, 0.114],
#     [-0.299, -0.587, 0.886],
#     [0.701, -0.587, -0.114]
# ], dtype=np.float32)

# inverse_matrix = np.linalg.inv(forward_matrix)

# def browse_file():
#     filepath = tk.filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
#     file_path_entry.delete(0, tk.END)
#     file_path_entry.insert(0, filepath)
#     open_file(filepath)

# def open_file(filepath):
#     global original_rgb_np, original_width, original_height
#     try:
#         with open(filepath, "rb") as f:
#             bmp_header = f.read(54)

#         if bmp_header[0:2] != b'BM':
#             file_size_label.config(text="Invalid BMP file")
#             return

#         width = int.from_bytes(bmp_header[18:22], 'little')
#         height = int.from_bytes(bmp_header[22:26], 'little', signed=True)
#         bits_per_pixel = int.from_bytes(bmp_header[28:30], 'little')
#         data_offset = int.from_bytes(bmp_header[10:14], 'little')
#         colors_used = int.from_bytes(bmp_header[46:50], 'little')

#         abs_height = abs(height)
#         color_table = []

#         if bits_per_pixel in [1, 4, 8]:
#             num_colors = 2 ** bits_per_pixel if colors_used == 0 else colors_used
#             with open(filepath, "rb") as f:
#                 f.seek(54)
#                 color_table_data = f.read(num_colors * 4)
#                 color_table = [(entry[2], entry[1], entry[0]) 
#                              for entry in (color_table_data[i*4:(i+1)*4] 
#                                          for i in range(num_colors))]

#         with open(filepath, "rb") as f:
#             f.seek(data_offset)
#             pixel_data = f.read()

#         bits_per_row = width * bits_per_pixel
#         bytes_per_row = ((bits_per_row + 31) // 32) * 4
#         original_rgb = []
#         row_order = reversed(range(abs_height)) if height > 0 else range(abs_height)

#         for y in row_order:
#             row_start = y * bytes_per_row
#             row_bytes = pixel_data[row_start:row_start+bytes_per_row]
#             rgb_row = []
            
#             for x in range(width):
#                 if bits_per_pixel == 1:
#                     byte_idx, bit_idx = x//8, 7-(x%8)
#                     index = (row_bytes[byte_idx] >> bit_idx) & 1 if byte_idx < len(row_bytes) else 0
#                 elif bits_per_pixel == 4:
#                     byte_idx, nibble_idx = x//2, x%2
#                     byte = row_bytes[byte_idx] if byte_idx < len(row_bytes) else 0
#                     index = (byte >> (4*(1-nibble_idx))) & 0x0F
#                 elif bits_per_pixel == 8:
#                     index = row_bytes[x] if x < len(row_bytes) else 0
#                 elif bits_per_pixel == 24:
#                     b, g, r = row_bytes[x*3:x*3+3]
#                     rgb_row.append((r, g, b))
#                     continue
#                 elif bits_per_pixel == 32:
#                     b, g, r, _ = row_bytes[x*4:x*4+4]
#                     rgb_row.append((r, g, b))
#                     continue
#                 else:
#                     rgb_row.append((0, 0, 0))
#                     continue

#                 if index < len(color_table):
#                     rgb_row.append(color_table[index])
#                 else:
#                     rgb_row.append((0, 0, 0))

#             original_rgb.append(rgb_row)

#         original_rgb_np = np.array(original_rgb, dtype=np.uint8)
#         original_width = width
#         original_height = abs_height

#         file_size_label.config(text=f"File Size: {int.from_bytes(bmp_header[2:6], 'little')} bytes")
#         width_label.config(text=f"Width: {width} pixels")
#         height_label.config(text=f"Height: {abs_height} pixels")
#         bpp_label.config(text=f"Bits Per Pixel: {bits_per_pixel}")
#         update_image()

#     except Exception as e:
#         file_size_label.config(text=f"Error: {str(e)}")

# def update_image(*args):
#     global current_photo
#     if original_rgb_np.size == 0:
#         return

#     try:
#         brightness = brightness_slider.get() / 100.0
#         scale = scale_slider.get() / 100.0
#         new_width = max(1, int(original_width * scale))
#         new_height = max(1, int(original_height * scale))

#         # Convert to YUV and adjust brightness
#         rgb_normalized = original_rgb_np.astype(np.float32) / 255.0
#         yuv = np.dot(rgb_normalized.reshape(-1, 3), forward_matrix.T)
#         yuv[:, 0] *= brightness
#         rgb_modified = np.dot(yuv, inverse_matrix.T)
#         rgb_modified = np.clip(rgb_modified, 0.0, 1.0).reshape(original_height, original_width, 3)
#         rgb_modified = (rgb_modified * 255).astype(np.uint8)

#         # Apply channel toggles
#         if not r_enabled: rgb_modified[..., 0] = 0
#         if not g_enabled: rgb_modified[..., 1] = 0
#         if not b_enabled: rgb_modified[..., 2] = 0

#         # Scale using nearest neighbor
#         if scale != 1.0:
#             y_idx = np.clip((np.arange(new_height) * (original_height / new_height)).astype(int), 0, original_height-1)
#             x_idx = np.clip((np.arange(new_width) * (original_width / new_width)).astype(int), 0, original_width-1)
#             scaled_rgb = rgb_modified[y_idx[:, None], x_idx]
#         else:
#             scaled_rgb = rgb_modified

#         # Create and display image
#         photo = tk.PhotoImage(width=new_width, height=new_height)
#         hex_data = ["#%02x%02x%02x" % tuple(pixel) for pixel in scaled_rgb.reshape(-1, 3)]
#         photo.put(" ".join(hex_data), (0, 0, new_width-1, new_height-1))
        
#         image_label.config(image=photo)
#         image_label.image = photo

#     except Exception as e:
#         file_size_label.config(text=f"Render Error: {str(e)}")

# def toggle_channel(channel):
#     global r_enabled, g_enabled, b_enabled
#     if channel == 'R': r_enabled = not r_enabled
#     elif channel == 'G': g_enabled = not g_enabled
#     elif channel == 'B': b_enabled = not b_enabled
#     update_image()

# # GUI Setup
# root = tk.Tk()
# root.title("BMP Viewer")

# # File selection
# tk.Label(root, text="File Path").grid(row=0, column=0)
# file_path_entry = tk.Entry(root, width=50)
# file_path_entry.grid(row=0, column=1)
# tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

# # Info labels
# file_size_label = tk.Label(root, anchor='w')
# file_size_label.grid(row=1, column=0, columnspan=3, sticky='ew')

# width_label = tk.Label(root, anchor='w')
# width_label.grid(row=2, column=0, columnspan=3, sticky='ew')

# height_label = tk.Label(root, anchor='w')
# height_label.grid(row=3, column=0, columnspan=3, sticky='ew')

# bpp_label = tk.Label(root, anchor='w')
# bpp_label.grid(row=4, column=0, columnspan=3, sticky='ew')

# # Controls
# tk.Label(root, text="Brightness:").grid(row=5, column=0)
# brightness_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_image)
# brightness_slider.set(100)
# brightness_slider.grid(row=5, column=1, sticky='ew')

# tk.Label(root, text="Scale:").grid(row=6, column=0)
# scale_slider = tk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, command=update_image)
# scale_slider.set(100)
# scale_slider.grid(row=6, column=1, sticky='ew')

# # Channel buttons
# button_frame = tk.Frame(root)
# button_frame.grid(row=7, column=0, columnspan=3)
# tk.Button(button_frame, text="R", command=lambda: toggle_channel('R')).pack(side=tk.LEFT)
# tk.Button(button_frame, text="G", command=lambda: toggle_channel('G')).pack(side=tk.LEFT)
# tk.Button(button_frame, text="B", command=lambda: toggle_channel('B')).pack(side=tk.LEFT)

# # Image display
# image_label = tk.Label(root)
# image_label.grid(row=8, column=0, columnspan=3)

# root.mainloop()