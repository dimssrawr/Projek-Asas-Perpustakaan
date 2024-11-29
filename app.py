import sqlite3
from tkinter import Tk, Label, Entry, Button, ttk, messagebox


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Perpustakaan")
        self.root.geometry("800x500")

        # Database
        self.conn = sqlite3.connect("library.db")
        self.create_table()

        # Inisialisasi atribut
        self.selected_id = None

        # GUI Components
        self.create_widgets()

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    year INTEGER,
                    category TEXT
                )"""
            )

    def create_widgets(self):
        # Labels and Entries
        Label(self.root, text="Judul").grid(row=0, column=0, padx=10, pady=10)
        Label(self.root, text="Penulis").grid(row=1, column=0, padx=10, pady=10)
        Label(self.root, text="Tahun").grid(row=0, column=2, padx=10, pady=10)
        Label(self.root, text="Kategori").grid(row=1, column=2, padx=10, pady=10)

        self.title_entry = Entry(self.root, width=30)
        self.author_entry = Entry(self.root, width=30)
        self.year_entry = Entry(self.root, width=30)
        self.category_entry = Entry(self.root, width=30)

        self.title_entry.grid(row=0, column=1, padx=10, pady=10)
        self.author_entry.grid(row=1, column=1, padx=10, pady=10)
        self.year_entry.grid(row=0, column=3, padx=10, pady=10)
        self.category_entry.grid(row=1, column=3, padx=10, pady=10)

        # Buttons
        Button(self.root, text="Tambah", command=self.add_book).grid(row=2, column=0, padx=10, pady=10)
        Button(self.root, text="Ubah", command=self.update_book).grid(row=2, column=1, padx=10, pady=10)
        Button(self.root, text="Hapus", command=self.delete_book).grid(row=2, column=2, padx=10, pady=10)
        Button(self.root, text="Cari", command=self.search_books).grid(row=2, column=3, padx=10, pady=10)

        # Treeview for displaying books
        self.tree = ttk.Treeview(self.root, columns=("id", "title", "author", "year", "category"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Judul")
        self.tree.heading("author", text="Penulis")
        self.tree.heading("year", text="Tahun")
        self.tree.heading("category", text="Kategori")
        self.tree.column("id", width=30)
        self.tree.bind("<Double-1>", self.fill_form)

        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.load_books()

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        year = self.year_entry.get()
        category = self.category_entry.get()

        if title and author and year and category:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO books (title, author, year, category) VALUES (?, ?, ?, ?)",
                    (title, author, year, category),
                )
            self.clear_form()
            self.load_books()
        else:
            messagebox.showwarning("Input Error", "Semua field harus diisi!")

    def load_books(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books")
        for book in cursor.fetchall():
            self.tree.insert("", "end", values=book)

    def fill_form(self, event):
        try:
            # Ambil item yang dipilih
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Error", "Tidak ada data yang dipilih!")
                return

            values = self.tree.item(selected[0], "values")

            # Masukkan data ke form input
            self.title_entry.delete(0, "end")
            self.author_entry.delete(0, "end")
            self.year_entry.delete(0, "end")
            self.category_entry.delete(0, "end")

            self.title_entry.insert(0, values[1])
            self.author_entry.insert(0, values[2])
            self.year_entry.insert(0, values[3])
            self.category_entry.insert(0, values[4])

            # Simpan ID buku yang dipilih
            self.selected_id = int(values[0])  # Pastikan ID diubah menjadi integer
        except IndexError:
            messagebox.showwarning("Selection Error", "Pilih data untuk diisi ke form!")

    def update_book(self):
        try:
            if not self.selected_id:
                messagebox.showwarning("Update Error", "Pilih data yang ingin diperbarui!")
                return

            title = self.title_entry.get()
            author = self.author_entry.get()
            year = self.year_entry.get()
            category = self.category_entry.get()

            if title and author and year and category:
                with self.conn:
                    self.conn.execute(
                        "UPDATE books SET title = ?, author = ?, year = ?, category = ? WHERE id = ?",
                        (title, author, year, category, self.selected_id),
                    )

                messagebox.showinfo("Berhasil", "Data berhasil diperbarui!")
                self.clear_form()
                self.load_books()
            else:
                messagebox.showwarning("Input Error", "Semua field harus diisi!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

    def delete_book(self):
        if not self.selected_id:
            messagebox.showwarning("Delete Error", "Pilih data yang ingin dihapus!")
            return

        with self.conn:
            self.conn.execute("DELETE FROM books WHERE id = ?", (self.selected_id,))
        messagebox.showinfo("Berhasil", "Data berhasil dihapus!")
        self.clear_form()
        self.load_books()

    def search_books(self):
        query = self.title_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )
        for book in cursor.fetchall():
            self.tree.insert("", "end", values=book)

    def clear_form(self):
        self.title_entry.delete(0, "end")
        self.author_entry.delete(0, "end")
        self.year_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.selected_id = None


if __name__ == "__main__":
    root = Tk()
    app = LibraryApp(root)
    root.mainloop()