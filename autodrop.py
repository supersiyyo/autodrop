import os
import shutil
import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext
import json

CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'AutoDrop')
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, 'autodrop_config.json')


# Load saved config if it exists
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save current GUI values to config
def save_config():
    config_data = {
        'source': source_entry.get(),
        'destination': dest_entry.get(),
        'move': move_var.get()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f)

# Main transfer logic
def transfer_videos():
    source = source_entry.get()
    dest = dest_entry.get()
    move = move_var.get()

    if not os.path.exists(source):
        log_output(f"❌ Source folder not found: {source}")
        return
    if not os.path.exists(dest):
        log_output(f"❌ Destination folder not found: {dest}")
        return

    # Save config before running
    save_config()

    # Create dated folder
    today = datetime.date.today().strftime('%Y-%m-%d')
    dated_folder = os.path.join(dest, today)
    os.makedirs(dated_folder, exist_ok=True)
    log_output(f"📂 Created folder for today: {dated_folder}")

    # Optional: log file for transfer records
    log_file_path = os.path.join(dated_folder, 'log.txt')
    with open(log_file_path, 'w') as log_file:
        log_file.write(f"AutoDrop Log - {today}\n\n")

        moved_count = 0
        for file in os.listdir(source):
            src_path = os.path.join(source, file)
            dest_path = os.path.join(dated_folder, file)

            log_output(f"{'📥 Moving' if move else '📥 Copying'} {file}...")
            log_file.write(f"{'Moved' if move else 'Copied'}: {file}\n")

            try:
                if move:
                    shutil.move(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                moved_count += 1
            except Exception as e:
                log_output(f"❌ Error: {e}")
                log_file.write(f"❌ Error: {e}\n")

        if moved_count:
            log_output(f"\n✅ Transfer complete! {moved_count} file(s) saved to:\n{dated_folder}")
            log_file.write(f"\n✅ Transfer complete! {moved_count} file(s).\n")
        else:
            log_output("\n⚠️ No files found.")
            log_file.write("\n⚠️ No files found.\n")

# Output logs to the GUI console
def log_output(message):
    output_text.insert(tk.END, message + '\n')
    output_text.see(tk.END)

# Folder selection popups
def select_source():
    folder = filedialog.askdirectory()
    if folder:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, folder)

def select_dest():
    folder = filedialog.askdirectory()
    if folder:
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, folder)

# ✅ UI Setup
root = tk.Tk()
root.title("AutoDrop - Data Transfer Tool")
root.geometry("720x550")
root.resizable(False, False)

tk.Label(root, text="Source Folder:").pack(anchor='w', padx=10, pady=(10, 0))
source_frame = tk.Frame(root)
source_frame.pack(fill='x', padx=10)
source_entry = tk.Entry(source_frame, width=80)
source_entry.pack(side='left', padx=(0, 5))
tk.Button(source_frame, text="Browse", command=select_source).pack(side='right')

tk.Label(root, text="Destination Folder:").pack(anchor='w', padx=10, pady=(10, 0))
dest_frame = tk.Frame(root)
dest_frame.pack(fill='x', padx=10)
dest_entry = tk.Entry(dest_frame, width=80)
dest_entry.pack(side='left', padx=(0, 5))
tk.Button(dest_frame, text="Browse", command=select_dest).pack(side='right')

move_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Move instead of Copy", variable=move_var).pack(anchor='w', padx=10, pady=10)

tk.Button(root, text="Start Transfer", command=transfer_videos, bg="#4CAF50", fg="white", height=2).pack(pady=5)

output_text = scrolledtext.ScrolledText(root, width=90, height=20, bg="#222", fg="#EEE", font=("Courier", 10))
output_text.pack(padx=10, pady=10)

# Preload saved values into the GUI
config = load_config()
source_entry.insert(0, config.get('source', ''))
dest_entry.insert(0, config.get('destination', ''))
move_var.set(config.get('move', True))

root.mainloop()
