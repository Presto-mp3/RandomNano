import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from Random_Album_Selector import run_random_album_selector
import importlib.util
import json
import os

class App:
    def __init__(self, root):
        self.root = root
        root.title("RandomNano")
        root.resizable(False, False)
        
        # Setup config file path
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.script_dir, "gui_config.json")
        self.config = self.load_config()

        # --- Top image (optional) ---
        self.logo_image = None
        logo_path = os.path.join(self.script_dir, "logo.png")
        if os.path.exists(logo_path):
            try:
                self.logo_image = tk.PhotoImage(file=logo_path).subsample(3, 3)  # Adjust size if needed
                tk.Label(root, image=self.logo_image).grid(row=0, column=0, columnspan=3, pady=(10, 5))
            except Exception:
                self.logo_image = None

        # --- Source directory ---
        tk.Label(root, text="Source directory:").grid(row=2, column=0, sticky="w")
        self.src_var = tk.StringVar(value=self.config.get("source", ""))
        tk.Entry(root, textvariable=self.src_var, width=40).grid(row=2,columnspan=3, column=0)
        tk.Button(root, text="Browse", command=self.pick_src).grid(row=2,columnspan=3, column=2)

        # --- Destination directory ---
        tk.Label(root, text="Destination directory:").grid(row=3, column=0, sticky="w")
        self.dst_var = tk.StringVar(value=self.config.get("destination", ""))
        tk.Entry(root, textvariable=self.dst_var, width=40).grid(row=3, columnspan=3, column=0)
        tk.Button(root, text="Browse", command=self.pick_dst).grid(row=3, column=2)

        #Horizontal separators

        ttk.Separator(root, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Separator(root, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Separator(root, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Separator(root, orient="horizontal").grid(row=8, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Separator(root, orient="horizontal").grid(row=10, column=0, columnspan=3, sticky="ew", pady=5)

        # --- Selection mode ---
        self.selection_mode = tk.StringVar(value=self.config.get("selection_mode", "gb"))
        tk.Label(root, text="Selection mode:").grid(row=7, column=0, sticky="w")
        GB_count_button = tk.Radiobutton(root, text="By GB", variable=self.selection_mode, value="gb", command=self.update_amount_label)
        GB_count_button.place(x=250, y=207)
        album_count_button = tk.Radiobutton(root, text="By album count", variable=self.selection_mode, value="count", command=self.update_amount_label)
        album_count_button.place(x=310, y=207)


        # --- GB of music ---
        self.amount_label = tk.Label(root, text="GB of music:")
        self.amount_label.grid(row=5, column=0, sticky="w")
        self.gb_var = tk.StringVar(value=self.config.get("amount", ""))
        tk.Entry(root, textvariable=self.gb_var, width=10).grid(row=5, columnspan=3, column=0)

        # --- Convert to MP3 checkbox ---
        self.convert_mp3_var = tk.BooleanVar(value=self.config.get("convert_mp3", False))
        tk.Checkbutton(root, text="Convert files to MP3 in destination directory", variable=self.convert_mp3_var).grid(row=9, column=0, columnspan=2, sticky="w",)

        # --- Fix Rockbox artwork checkbox ---
        self.fix_artwork_var = tk.BooleanVar(value=self.config.get("fix_artwork", False))
        tk.Checkbutton(root, text="Optimise embedded artwork for Rockbox in destination directory", variable=self.fix_artwork_var).grid(row=9, column=2, sticky="w")

        # --- Run button ---
        tk.Button(root, text="Run", command=self.run).grid(row=11, column=0, columnspan=3, pady=20)

        # --- Status ---
        self.status = tk.Label(root, text="", fg="blue")
        self.status.grid(row=13, column=0, columnspan=3, sticky="w")
        
        # Handle window close
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        config = {
            "source": self.src_var.get(),
            "destination": self.dst_var.get(),
            "selection_mode": self.selection_mode.get(),
            "amount": self.gb_var.get(),
            "convert_mp3": self.convert_mp3_var.get(),
            "fix_artwork": self.fix_artwork_var.get()
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def on_closing(self):
        self.save_config()
        self.root.destroy()

    def pick_src(self):
        path = filedialog.askdirectory()
        if path:
            self.src_var.set(path)

    def pick_dst(self):
        path = filedialog.askdirectory()
        if path:
            self.dst_var.set(path)

    def update_amount_label(self):
        if self.selection_mode.get() == "count":
            self.amount_label.config(text="Album count:")
        else:
            self.amount_label.config(text="GB of music:")

    def update_progress(self, current, total, filename):
        """Callback for MP3 conversion progress."""
        self.status.config(text=f"Converting MP3: {current}/{total} - {filename}")
        self.root.update()  # Process all pending GUI events

    def run(self):
        src = self.src_var.get().strip()
        dst = self.dst_var.get().strip()
        amount_text = self.gb_var.get().strip()
        mode = self.selection_mode.get()

        if not src:
            messagebox.showerror("Error", "Please select a source directory.")
            return
        if not dst:
            messagebox.showerror("Error", "Please select a destination directory.")
            return
        if not amount_text:
            messagebox.showerror("Error", "Please enter a value for the selected mode.")
            return

        max_bytes = None
        max_albums = None
        if mode == "count":
            try:
                count = int(amount_text)
                if count <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid whole number greater than zero for album count.")
                return
            max_albums = count
        else:
            try:
                gb = float(amount_text)
                if gb <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number greater than zero for GB.")
                return
            max_bytes = int(gb * 1024 * 1024 * 1024)

        try:
            progress_callback = self.update_progress if self.convert_mp3_var.get() else None
            selected, used_space = run_random_album_selector(src, dst, max_bytes=max_bytes, max_albums=max_albums, convert_mp3=self.convert_mp3_var.get(), progress_callback=progress_callback)
            self.status.config(text=f"Copied {len(selected)} albums ({used_space / (1024**3):.2f} GB)")
            # Optionally fix artwork in the destination
            if self.fix_artwork_var.get():
                self.status.config(text="Fixing artwork in destination...")
                self.root.update()
                # Dynamically load the artwork fixer module by path
                fixer_path = os.path.join(self.script_dir, "Rockbox_Artwork_Fixer.py")
                try:
                    spec = importlib.util.spec_from_file_location("artfixer", fixer_path)
                    artfixer = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(artfixer)
                    artfixer.process_folder(dst)
                    self.status.config(text="Done")
                except Exception as e:
                    messagebox.showerror("Artwork Fix Error", f"Failed to fix artwork:\n{e}")
                    self.status.config(text="Artwork fix failed")
            self.save_config()
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to copy albums:\n{exc}")
            self.status.config(text="Error")

root = tk.Tk()
app = App(root)
root.mainloop()
