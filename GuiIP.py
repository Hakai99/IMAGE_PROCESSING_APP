import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

# ---------------- MAIN WINDOW ---------------- #
root = tk.Tk()
root.title("Image Processing Studio")
root.geometry("1350x750")
root.configure(bg="#1e1e1e")

# ---------------- STYLE ---------------- #
style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                font=("Segoe UI", 11),
                padding=6,
                background="#3c3f41",
                foreground="white")

style.map("TButton",
          background=[("active", "#5a5a5a")])

# ---------------- GLOBAL VARIABLES ---------------- #
original_img = None
processed_img = None

brightness_value = 0
contrast_value = 1.0
gamma_value = 1.0

# ---------------- DISPLAY FUNCTION ---------------- #
def display_image(img, panel):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil = img_pil.resize((450, 450))
    img_tk = ImageTk.PhotoImage(img_pil)
    panel.config(image=img_tk)
    panel.image = img_tk

# ---------------- SAFETY CHECK ---------------- #
def check_image_loaded():
    if original_img is None:
        messagebox.showwarning("Warning", "Please load an image first!")
        return False
    return True

# ---------------- LOAD IMAGE ---------------- #
def load_image():
    global original_img, processed_img
    path = filedialog.askopenfilename()
    if path:
        original_img = cv2.imread(path)
        processed_img = original_img.copy()
        display_image(original_img, original_panel)
        display_image(processed_img, processed_panel)
        status_label.config(text="Image Loaded Successfully")

# ---------------- SAVE IMAGE ---------------- #
def save_image():
    if processed_img is not None:
        path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if path:
            cv2.imwrite(path, processed_img)
            status_label.config(text="Image Saved Successfully")

# ---------------- RESET ---------------- #
def reset():
    global processed_img, brightness_value, contrast_value, gamma_value

    if not check_image_loaded():
        return

    # Reset adjustment values
    brightness_value = 0
    contrast_value = 1.0
    gamma_value = 1.0

    brightness_slider.set(0)
    contrast_slider.set(1.0)
    gamma_slider.set(1.0)

    # Restore original image
    processed_img = original_img.copy()
    display_image(processed_img, processed_panel)

    status_label.config(text="Image Reset to Original")

# ---------------- BASIC OPERATIONS ---------------- #
def grayscale():
    global processed_img
    if check_image_loaded():
        img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        display_image(processed_img, processed_panel)
        status_label.config(text="Grayscale Applied")

def negative():
    global processed_img
    if check_image_loaded():
        processed_img = 255 - original_img
        display_image(processed_img, processed_panel)
        status_label.config(text="Negative Applied")

def log_transform():
    global processed_img
    if check_image_loaded():
        img = original_img.astype(np.float32)
        c = 255 / np.log(1 + np.max(img))
        log_img = c * np.log(1 + img)
        processed_img = np.array(log_img, dtype=np.uint8)
        display_image(processed_img, processed_panel)
        status_label.config(text="Log Transformation Applied")

# ---------------- SLIDER ADJUSTMENTS ---------------- #
def adjust_brightness(val):
    global brightness_value
    brightness_value = int(val)
    apply_adjustments()

def adjust_contrast(val):
    global contrast_value
    contrast_value = float(val)
    apply_adjustments()

def gamma_correction(val):
    global gamma_value
    gamma_value = float(val)
    apply_adjustments()

def apply_adjustments():
    global processed_img

    if not check_image_loaded():
        return

    img = original_img.astype(np.float32)

    # Gamma
    img = img / 255.0
    img = np.power(img, gamma_value)
    img = img * 255.0

    # Contrast (centered)
    img = (img - 127.5) * contrast_value + 127.5

    # Brightness
    img = img + brightness_value

    img = np.clip(img, 0, 255).astype(np.uint8)

    processed_img = img
    display_image(processed_img, processed_panel)

# ---------------- HEADER ---------------- #
header = tk.Label(root,
                  text="IMAGE PROCESSING STUDIO",
                  bg="#121212",
                  fg="white",
                  font=("Segoe UI", 22, "bold"),
                  pady=12)
header.pack(fill="x")

# ---------------- MAIN FRAME ---------------- #
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True)

# ---------------- SIDEBAR ---------------- #
sidebar = tk.Frame(main_frame, bg="#252526", width=260)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(sidebar, text="TOOLS",
         bg="#252526", fg="white",
         font=("Segoe UI", 14, "bold")).pack(pady=20)

ttk.Button(sidebar, text="Load Image", command=load_image).pack(pady=5, fill="x", padx=25)
ttk.Button(sidebar, text="Grayscale", command=grayscale).pack(pady=5, fill="x", padx=25)
ttk.Button(sidebar, text="Negative", command=negative).pack(pady=5, fill="x", padx=25)
ttk.Button(sidebar, text="Log Transform", command=log_transform).pack(pady=5, fill="x", padx=25)
ttk.Button(sidebar, text="Reset", command=reset).pack(pady=10, fill="x", padx=25)
ttk.Button(sidebar, text="Save Image", command=save_image).pack(pady=5, fill="x", padx=25)

# Sliders
tk.Label(sidebar, text="Brightness", bg="#252526", fg="white").pack(pady=(20,5))
brightness_slider = tk.Scale(sidebar, from_=-100, to=100,
                             orient="horizontal",
                             command=adjust_brightness,
                             bg="#252526", fg="white",
                             highlightthickness=0)
brightness_slider.pack(padx=20)

tk.Label(sidebar, text="Contrast", bg="#252526", fg="white").pack(pady=(15,5))
contrast_slider = tk.Scale(sidebar, from_=0.5, to=3,
                           resolution=0.1,
                           orient="horizontal",
                           command=adjust_contrast,
                           bg="#252526", fg="white",
                           highlightthickness=0)
contrast_slider.pack(padx=20)

tk.Label(sidebar, text="Gamma", bg="#252526", fg="white").pack(pady=(15,5))
gamma_slider = tk.Scale(sidebar, from_=0.1, to=3,
                        resolution=0.1,
                        orient="horizontal",
                        command=gamma_correction,
                        bg="#252526", fg="white",
                        highlightthickness=0)
gamma_slider.set(1)
gamma_slider.pack(padx=20)

# ---------------- IMAGE AREA ---------------- #
image_frame = tk.Frame(main_frame, bg="#1e1e1e")
image_frame.pack(side="right", expand=True)

original_box = tk.LabelFrame(image_frame,
                             text=" Original Image ",
                             bg="#2d2d2d",
                             fg="white",
                             font=("Segoe UI", 13),
                             bd=3,
                             relief="groove")
original_box.grid(row=0, column=0, padx=40, pady=40)

processed_box = tk.LabelFrame(image_frame,
                              text=" Processed Image ",
                              bg="#2d2d2d",
                              fg="white",
                              font=("Segoe UI", 13),
                              bd=3,
                              relief="groove")
processed_box.grid(row=0, column=1, padx=40, pady=40)

original_panel = tk.Label(original_box, bg="#2d2d2d")
original_panel.pack(padx=15, pady=15)

processed_panel = tk.Label(processed_box, bg="#2d2d2d")
processed_panel.pack(padx=15, pady=15)

# ---------------- STATUS BAR ---------------- #
status_label = tk.Label(root,
                        text="Ready",
                        bg="#121212",
                        fg="white",
                        anchor="w",
                        padx=10)
status_label.pack(fill="x")

root.mainloop()
