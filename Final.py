import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from pdfminer.high_level import extract_text
from docx import Document
import edge_tts
import os
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime


class FileToMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("File to MP3 Converter")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.config(bg="lightgray")

        self.canvas = tk.Canvas(root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.canvas.pack(fill="both", expand=True)

        self.bg_image = Image.open("/home/parthieshwar/Development/College Project/wp4269239-370390428.jpg")
        self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        self.label = tk.Label(root, text="Convert files into MP3", bg="white", fg="black", font=("Times New Roman", 36, "bold"))
        self.label.place(y=30, x=700)

        self.label = tk.Label(root, text="1.Select a file to convert:", bg="white", fg="black", font=("Times New Roman", 24))
        self.label.place(y=230, x=120)

        self.file_path_entry = tk.Entry(root, width=60, bg="white", fg="black", font=("Times New Roman", 16))
        self.file_path_entry.place(y=240, x=600)

        self.label = tk.Label(root, text="Eg: .docx, .pdf, .txt files", bg="white", fg="black", font=("Times New Roman", 24, "bold"))
        self.label.place(y=235, x=1450)

        self.output_file_name_label = tk.Label(root, text="2.Output file name:", bg="white", fg="black", font=("Times New Roman", 24))
        self.output_file_name_label.place(y=340, x=120)

        self.output_file_name_entry = tk.Entry(root, width=60, bg="white", fg="black", font=("Times New Roman", 16))
        self.output_file_name_entry.place(y=350, x=600)

        self.label = tk.Label(root, text="Eg: Result File, Audio File", bg="white", fg="black", font=("Times New Roman", 24, "bold"))
        self.label.place(y=345, x=1450)

        self.save_location_label = tk.Label(root, text="3.Output File Location:", bg="white", fg="black", font=("Times New Roman", 24))
        self.save_location_label.place(y=450, x=120)

        self.save_location_entry = tk.Entry(root, width=60, bg="white", fg="black", font=("Times New Roman", 16))
        self.save_location_entry.place(y=460, x=600)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file, bg="white", fg="black", font=("Times New Roman", 24))
        self.browse_button.place(y=230, x=1300)

        self.save_location_browse_button = tk.Button(root, text="Browse", command=self.browse_save_location, bg="white", fg="black", font=("Times New Roman", 24))
        self.save_location_browse_button.place(y=450, x=1300)

        self.process_button = tk.Button(root, text="Process", command=self.process_file, bg="white", fg="black", font=("Times New Roman", 24))
        self.process_button.place(y=600, x=750)

        self.exit_button = tk.Button(root, text="Exit", command=self.root.destroy, bg="white", fg="black", font=("Times New Roman", 24))
        self.exit_button.place(y=600, x=1000)

        self.label = tk.Label(root, text="To view the previous MP3 Files click this button -->", bg="white", fg="black", font=("Times New Roman", 24))
        self.label.place(y=750, x=600)

        self.new_window_button = tk.Button(root, text="History", command=self.open_new_window, bg="white", fg="black", font=("Times New Roman", 24))
        self.new_window_button.place(y=745, x=1300)

        self.file_path = None
        self.output_file_name = None
        self.save_location = None

        self.init_db()


    def init_db(self):
        self.conn = sqlite3.connect("converted_files.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT,file_name TEXT,mp3_data BLOB,timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()


    def save_to_db(self, file_name, mp3_file_path):
        try:
            conn = sqlite3.connect("converted_files.db")
            cursor = conn.cursor()
            
            with open(mp3_file_path, "rb") as f:
                mp3_data = f.read()
        
            cursor.execute("INSERT INTO files (file_name, mp3_data) VALUES (?, ?)", (file_name, mp3_data))
            conn.commit()
        
        except Exception as e:
            print(f"Error saving to database: {e}")
        finally:
            conn.close()


    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf"), ("Word Files", "*.docx")])
        if file_path:
            self.file_path = file_path
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)


    def browse_save_location(self):
        save_location = filedialog.askdirectory(title="Select Save Location")
        if save_location:
            self.save_location = save_location
            self.save_location_entry.delete(0, tk.END)
            self.save_location_entry.insert(0, save_location)


    def open_new_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Converted Files History")
        new_window.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        new_window.config(bg="lightgray")

        canvas = tk.Canvas(new_window, width=new_window.winfo_screenwidth(), height=new_window.winfo_screenheight())
        canvas.pack(fill="both", expand=True)

        bg_image = Image.open("/home/parthieshwar/Development/College Project/wp4269239-370390428.jpg")
        bg_image = bg_image.resize((new_window.winfo_screenwidth(), new_window.winfo_screenheight()), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, anchor="nw", image=bg_photo)
        new_window.bg_photo = bg_photo

        label = tk.Label(new_window, text="History Window!", font=("Times New Roman", 36, "bold"), bg="white", fg="black")
        label.place(y=30, x=750)

        self.cursor.execute("SELECT id, file_name, timestamp FROM files")
        records = self.cursor.fetchall()

        new_window.text_widget = tk.Text(new_window, height=25, width=100)
        new_window.text_widget.place(y=150, x=450)

        for record in records:
            file_id, file_name, timestamp = record
            new_window.text_widget.insert(tk.END, f"Id:{file_id},File: {file_name} | Time: {timestamp}\n")

        records_frame = tk.Frame(new_window, bg="white")
        records_frame.place(y=150, x=450, width=1000, height=600)

        for index, record in enumerate(records):
            file_id, file_name, timestamp = record
            label = tk.Label(records_frame, text=f"Id:{file_id},File: {file_name} | Time: {timestamp}", font=("Times New Roman", 16), bg="white")
            label.grid(row=index, column=0, sticky="w", padx=10, pady=5)

            download_button = tk.Button(records_frame, text="Download", command=lambda file_id=file_id: self.download_file(file_id, new_window), bg="white", fg="black", font=("Times New Roman", 16))
            download_button.grid(row=index, column=1, padx=10, pady=5)

        clear_button = tk.Button(new_window, text="Clear History", command=lambda: self.confirm_action("clear", new_window=new_window), bg="white", fg="black", font=("Times New Roman", 24))
        clear_button.place(x=750, y=800)

        self.exit_button = tk.Button(new_window, text="Exit", command=new_window.destroy, bg="white", fg="black", font=("Times New Roman", 24))
        self.exit_button.place(y=800, x=1000)

        self.new_window = new_window


    def confirm_action(self, action_type, new_window=None):
        if action_type == "download":
            response = messagebox.askyesno("Confirm Download", "Are you sure you want to download this file?")
            if response:
                self.download_file(new_window)

        elif action_type == "clear":
            response = messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the history and delete all records from the database?")
            if response:
                    self.clear_history(new_window.text_widget) 

        elif action_type == "exit":
            response = messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?")
            if response:
                new_window.destroy()


    def download_file(self, file_id, new_window):
        self.cursor.execute("SELECT mp3_data, file_name FROM files WHERE id=?", (file_id,))
        result = self.cursor.fetchone()

        if result:
            mp3_data, file_name = result
            if isinstance(mp3_data, str):
                mp3_data = bytes(mp3_data, 'utf-8')
            save_location = filedialog.askdirectory(title="Select Save Location")
            
            if not save_location:
                return

            mp3_file_path = os.path.join(save_location, f"{file_name}.mp3")

            with open(mp3_file_path, "wb") as f:
                f.write(mp3_data)
            messagebox.showinfo("Success", f"File downloaded as {file_name}.mp3")
        else:
            messagebox.showerror("Error", "Selected file not found in the database.")


    def clear_history(self, text_widget):
        self.cursor.execute("DELETE FROM files")
        self.conn.commit()
        text_widget.delete(1.0, tk.END)
        messagebox.showinfo("Success", "History cleared successfully.")


    def process_file(self):
        file_path = self.file_path_entry.get()
        output_file_name = self.output_file_name_entry.get()
        save_location = self.save_location_entry.get()

        if not file_path or not output_file_name or not save_location:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
            
        text_content = None

        if file_path.endswith(".pdf"):
            text_content = extract_text(file_path)

        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            text_content = "\n".join([para.text for para in doc.paragraphs])

        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding='utf-8') as f:
                text_content = f.read()

        if text_content:
            self.convert_to_mp3(text_content, output_file_name, save_location)


    def convert_to_mp3(self, text_content, output_file_name, save_location):
        async def main():
            try:
                communicate = edge_tts.Communicate(text_content, voice="en-US-AriaNeural", rate="+0%", volume="+100%")
                mp3_file_path = os.path.join(save_location, f"{output_file_name}.mp3")
                await communicate.save(mp3_file_path)
                self.save_to_db(output_file_name, mp3_file_path)
                messagebox.showinfo("Success", f"File saved as {output_file_name}.mp3")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert: {e}")


        asyncio.run(main())


if __name__ == "__main__":
    root = tk.Tk()
    app = FileToMP3Converter(root)
    root.mainloop()
