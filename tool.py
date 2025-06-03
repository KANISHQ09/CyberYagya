# mobile_forensic_tool.py

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from fpdf import FPDF
import re
from datetime import datetime
import sqlite3
import tarfile

def run_adb_command(cmd_list):
    result = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    return result.stdout

class ForensicTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Mobile Forensic Triage Tool")
        self.root.geometry("800x600")

        self.device_connected = False

        self.call_logs_var = tk.BooleanVar()
        self.sms_var = tk.BooleanVar()
        self.photos_var = tk.BooleanVar()
        self.videos_var = tk.BooleanVar()
        self.whatsapp_var = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        ttk.Label(frame, text="Select Evidence to Extract:").grid(row=0, column=0, columnspan=3)

        ttk.Checkbutton(frame, text="Call Logs", variable=self.call_logs_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(frame, text="SMS", variable=self.sms_var).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(frame, text="Photos", variable=self.photos_var).grid(row=3, column=0, sticky=tk.W)
        ttk.Checkbutton(frame, text="Videos", variable=self.videos_var).grid(row=4, column=0, sticky=tk.W)
        ttk.Checkbutton(frame, text="WhatsApp Chats", variable=self.whatsapp_var).grid(row=5, column=0, sticky=tk.W)

        ttk.Label(frame, text="Keyword Filter (SMS):").grid(row=1, column=1, sticky=tk.E)
        self.keyword_entry = ttk.Entry(frame, width=20)
        self.keyword_entry.grid(row=1, column=2)

        ttk.Label(frame, text="From Date (YYYY-MM-DD):").grid(row=2, column=1, sticky=tk.E)
        self.from_date = ttk.Entry(frame, width=20)
        self.from_date.grid(row=2, column=2)

        ttk.Label(frame, text="To Date (YYYY-MM-DD):").grid(row=3, column=1, sticky=tk.E)
        self.to_date = ttk.Entry(frame, width=20)
        self.to_date.grid(row=3, column=2)

        self.preview_btn = ttk.Button(frame, text="Preview Data", command=self.preview_data)
        self.preview_btn.grid(row=6, column=0, pady=10)

        self.export_btn = ttk.Button(frame, text="Export to PDF/CSV", command=self.export_data)
        self.export_btn.grid(row=6, column=1, pady=10)

        self.connect_btn = ttk.Button(frame, text="Connect Mobile", command=self.connect_device)
        self.connect_btn.grid(row=6, column=2, pady=10)

        self.text = tk.Text(self.root, height=20)
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def connect_device(self):
        output = run_adb_command(["adb", "devices"])
        lines = output.strip().split("\n")
        connected = any("device" in line and not line.startswith("List") for line in lines)
        if connected:
            self.device_connected = True
            messagebox.showinfo("Success", "Device connected successfully!")
        else:
            messagebox.showerror("Error", "No device connected. Make sure ADB is enabled.")

    def get_files_preview(self, folder, extensions):
        file_list = []
        for root_dir, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(extensions):
                    file_list.append(os.path.join(root_dir, file))
        return file_list

    def preview_data(self):
        if not self.device_connected:
            messagebox.showwarning("Warning", "Connect a mobile device first.")
            return

        self.text.delete(1.0, tk.END)
        keyword = self.keyword_entry.get().lower()

        if self.call_logs_var.get():
            calls = run_adb_command(["adb", "shell", "content", "query", "--uri", "content://call_log/calls"])
            filtered_calls = self.filter_by_date(calls)
            self.text.insert(tk.END, "--- Call Logs ---\n" + filtered_calls + "\n\n")

        if self.sms_var.get():
            sms_output = run_adb_command(["adb", "shell", "content", "query", "--uri", "content://sms/inbox"])
            filtered_sms = self.filter_by_keyword_and_date(sms_output, keyword)
            self.text.insert(tk.END, "--- Filtered SMS ---\n" + filtered_sms + "\n\n")

        if self.photos_var.get():
            self.text.insert(tk.END, "--- Extracting Photos ---\n")
            run_adb_command(["adb", "pull", "/sdcard/DCIM", "./photos"])
            run_adb_command(["adb", "pull", "/sdcard/Pictures", "./photos"])
            self.text.insert(tk.END, "Photos saved to ./photos\n")
            photos_list = self.get_files_preview("./photos", ('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
            if photos_list:
                self.text.insert(tk.END, "--- Photos Preview (filenames) ---\n")
                for p in photos_list[:20]:
                    filename = os.path.basename(p)
                    self.text.insert(tk.END, filename + "\n")
            else:
                self.text.insert(tk.END, "No photos found.\n")
            self.text.insert(tk.END, "\n")

        if self.videos_var.get():
            self.text.insert(tk.END, "--- Extracting Videos ---\n")
            run_adb_command(["adb", "pull", "/sdcard/Movies", "./videos"])
            run_adb_command(["adb", "pull", "/sdcard/DCIM", "./videos"])
            self.text.insert(tk.END, "Videos saved to ./videos\n")
            videos_list = self.get_files_preview("./videos", ('.mp4', '.avi', '.mov', '.mkv', '.3gp'))
            if videos_list:
                self.text.insert(tk.END, "--- Videos Preview (filenames) ---\n")
                for v in videos_list[:20]:
                    filename = os.path.basename(v)
                    self.text.insert(tk.END, filename + "\n")
            else:
                self.text.insert(tk.END, "No videos found.\n")
            self.text.insert(tk.END, "\n")

        if self.whatsapp_var.get():
            self.text.insert(tk.END, "--- Extracting WhatsApp Backup ---\n")
            run_adb_command(["adb", "backup", "-f", "whatsapp.ab", "-apk", "com.whatsapp"])
            os.system("dd if=whatsapp.ab bs=24 skip=1 | openssl zlib -d > whatsapp.tar")
            with tarfile.open("whatsapp.tar") as tar:
                tar.extractall("./whatsapp")
            db_path = os.path.join("whatsapp", "apps", "com.whatsapp", "db", "msgstore.db")
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT datetime(timestamp / 1000, 'unixepoch'), key_remote_jid, data FROM messages LIMIT 50")
                    rows = cursor.fetchall()
                    self.text.insert(tk.END, "--- WhatsApp Messages ---\n")
                    for row in rows:
                        self.text.insert(tk.END, f"[{row[0]}] {row[1]}: {row[2]}\n")
                except Exception as e:
                    self.text.insert(tk.END, f"WhatsApp DB Error: {e}\n")

    def filter_by_keyword_and_date(self, sms_data, keyword):
        filtered = []
        lines = sms_data.split('\n')
        from_dt = self.get_date(self.from_date.get())
        to_dt = self.get_date(self.to_date.get())

        for line in lines:
            if (not keyword or keyword in line.lower()):
                ts_match = re.search(r"date=(\d+)", line)
                if ts_match:
                    timestamp = int(ts_match.group(1)) / 1000
                    dt = datetime.fromtimestamp(timestamp)
                    if from_dt and dt < from_dt:
                        continue
                    if to_dt and dt > to_dt:
                        continue
                filtered.append(line)
        return '\n'.join(filtered)

    def filter_by_date(self, call_data):
        filtered = []
        lines = call_data.split('\n')
        from_dt = self.get_date(self.from_date.get())
        to_dt = self.get_date(self.to_date.get())

        for line in lines:
            ts_match = re.search(r"date=(\d+)", line)
            if ts_match:
                timestamp = int(ts_match.group(1)) / 1000
                dt = datetime.fromtimestamp(timestamp)
                if from_dt and dt < from_dt:
                    continue
                if to_dt and dt > to_dt:
                    continue
            filtered.append(line)
        return '\n'.join(filtered)

    def get_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d") if date_str else None
        except:
            return None

    def export_data(self):
        if not self.device_connected:
            messagebox.showwarning("Warning", "Connect a mobile device first.")
            return

        export_dir = filedialog.askdirectory()
        if not export_dir:
            return

        data = self.text.get(1.0, tk.END)

        with open(os.path.join(export_dir, "extracted_data.txt"), "w", encoding="utf-8") as f:
            f.write(data)

        rows = [line for line in data.strip().split('\n') if line.strip()]
        pd.DataFrame(rows).to_csv(os.path.join(export_dir, "extracted_data.csv"), index=False, header=False)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in rows:
            try:
                pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            except:
                pdf.cell(200, 10, txt="[Encoding Error Line]", ln=True)
        pdf.output(os.path.join(export_dir, "extracted_data.pdf"))

        messagebox.showinfo("Export", f"Data exported to {export_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ForensicTool(root)
    root.mainloop()
