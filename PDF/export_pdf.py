import os
import fitz  # PyMuPDF
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Progressbar

def extract_xmp_metadata(file_path):
    try:
        doc = fitz.open(file_path)

        for xref in range(1, doc.xref_length()):
            stream = doc.xref_stream(xref)
            if stream and b"<x:xmpmeta" in stream:
                return stream.decode("utf-8", errors="ignore")
        return None
    except Exception as e:
        return f"Chyba při extrakci metadat: {str(e)}"

def check_pdf_a_compliance_xmp(file_path):
    try:
        xmp_metadata = extract_xmp_metadata(file_path)

        if not xmp_metadata or isinstance(xmp_metadata, str) and "Chyba" in xmp_metadata:
            return "XMP metadata nenalezena. Není kompatibilní s PDF/A."

        pdfa_pattern = re.compile(r"http://www.aiim.org/pdfa/ns/id/")
        pdfa_compliance = re.search(pdfa_pattern, xmp_metadata)

        if pdfa_compliance:
            part_pattern = re.compile(r"<pdfaid:part>(\d+)</pdfaid:part>")
            conformance_pattern = re.compile(r"<pdfaid:conformance>([A-Z])</pdfaid:conformance>")

            part_match = re.search(part_pattern, xmp_metadata)
            conformance_match = re.search(conformance_pattern, xmp_metadata)

            part = part_match.group(1) if part_match else "Neznámé"
            conformance = conformance_match.group(1) if conformance_match else "Neznámé"

            return f"PDF/A-{part}{conformance}"
        else:
            return "Není kompatibilní s PDF/A"
    except Exception as e:
        return f"Chyba při kontrole: {str(e)}"

def check_folder_for_pdf_a(folder_path, progress_callback=None):
    results = []
    if not os.path.exists(folder_path):
        return results

    pdf_files = [os.path.join(root, file) for root, _, files in os.walk(folder_path) for file in files if file.lower().endswith('.pdf')]
    total_files = len(pdf_files)

    for index, file_path in enumerate(pdf_files, start=1):
        compliance_result = check_pdf_a_compliance_xmp(file_path)
        results.append((os.path.basename(file_path), compliance_result))
        if progress_callback:
            progress_callback(index, total_files)

    return results

def select_folder():
    folder_path = filedialog.askdirectory(title="Vyberte složku")
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

def run_check():
    folder_path = folder_entry.get()
    if not folder_path or not os.path.exists(folder_path):
        messagebox.showerror("Chyba", "Vyberte prosím platnou složku.")
        return

    results_table.delete(*results_table.get_children())

    progress_bar["value"] = 0
    progress_label.config(text="Zahajuji analýzu...")

    def update_progress(current, total):
        progress = (current / total) * 100
        progress_bar["value"] = progress
        progress_label.config(text=f"Zpracovávám soubor {current} z {total}...")
        root.update_idletasks()

    results = check_folder_for_pdf_a(folder_path, update_progress)

    for file_name, result in results:
        results_table.insert("", tk.END, values=(file_name, result))

    progress_label.config(text="Analýza dokončena.")

# Vytvoření hlavního okna
root = tk.Tk()
root.title("Kontrola kompatibility PDF/A")

# Výběr složky
folder_frame = tk.Frame(root)
folder_frame.pack(pady=10, padx=10, fill=tk.X)

folder_label = tk.Label(folder_frame, text="Složka:")
folder_label.pack(side=tk.LEFT, padx=5)

folder_entry = tk.Entry(folder_frame, width=50)
folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

browse_button = tk.Button(folder_frame, text="Procházet", command=select_folder)
browse_button.pack(side=tk.LEFT, padx=5)

# Tlačítko pro spuštění kontroly
run_button = tk.Button(root, text="Spustit kontrolu", command=run_check)
run_button.pack(pady=5)

# Indikátor průběhu a popisek
progress_bar = Progressbar(root, mode="determinate")
progress_bar.pack(pady=5, fill=tk.X, padx=10)

progress_label = tk.Label(root, text="")
progress_label.pack(pady=5)

# Tabulka výsledků
columns = ("Název souboru", "Výsledek kontroly")
results_table = ttk.Treeview(root, columns=columns, show="headings")
results_table.heading("Název souboru", text="Název souboru")
results_table.heading("Výsledek kontroly", text="Výsledek kontroly")
results_table.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Spuštění hlavní smyčky
root.mainloop()
