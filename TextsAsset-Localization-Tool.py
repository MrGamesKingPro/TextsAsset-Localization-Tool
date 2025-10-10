import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import json
import re
import html
import os
import csv
import io

# --- Directory Names ---
ORIGINAL_JSON_DIR = 'Original_TextsAsset'
CLEAN_TEXT_DIR = 'Output_Clean_Text'
MODIFIED_JSON_DIR = 'Output_TextsAsset'

# --- Placeholder for empty text entries ---
EMPTY_TEXT_PLACEHOLDER = '---'

# --- Constants for method selection ---
METHOD_XML_LIKE = "USE METHOD 1"
METHOD_JSON_STRING = "USE METHOD 2"
METHOD_CSV_STRING = "USE METHOD 3"

# --- Regex for XML-like entries ---
XML_ENTRY_PATTERN = re.compile(r'<entry name="(.*?)">(.*?)</entry>', re.DOTALL)

def is_comment_entry(entry_name):
    return entry_name.strip().startswith('//')

# =====================================================
# EXPORT FUNCTION
# =====================================================
def export_texts(log_function, selected_method):
    log_function("--- Starting Export Process ---")
    log_function(f"Selected method: {selected_method}")

    if not os.path.isdir(ORIGINAL_JSON_DIR):
        log_function(f"Error: Input directory '{ORIGINAL_JSON_DIR}' not found.")
        return

    os.makedirs(CLEAN_TEXT_DIR, exist_ok=True)
    json_files = [f for f in os.listdir(ORIGINAL_JSON_DIR) if f.endswith('.json')]

    if not json_files:
        log_function(f"No JSON files found in the directory '{ORIGINAL_JSON_DIR}'.")
        return

    total_files = len(json_files)
    processed_files = 0

    for filename in json_files:
        input_json_path = os.path.join(ORIGINAL_JSON_DIR, filename)
        output_txt_filename = os.path.splitext(filename)[0] + '.txt'
        output_txt_path = os.path.join(CLEAN_TEXT_DIR, output_txt_filename)

        try:
            with open(input_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            script_content = data.get('m_Script')
            if script_content is None:
                log_function(f"Warning: 'm_Script' not found in file {filename}. Skipping file.")
                continue

            clean_lines = []

            # --- METHOD 1: XML-LIKE ---
            if selected_method == METHOD_XML_LIKE:
                if not isinstance(script_content, str):
                    log_function(f"Warning: 'm_Script' in {filename} is not string. Skipping.")
                    continue
                matches = XML_ENTRY_PATTERN.findall(script_content)
                for entry_name, text_content in matches:
                    if is_comment_entry(entry_name):
                        continue
                    text = html.unescape(text_content).strip()
                    processed = EMPTY_TEXT_PLACEHOLDER if not text else text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')
                    clean_lines.append(f'"{processed}"')

            # --- METHOD 2: JSON STRING ---
            elif selected_method == METHOD_JSON_STRING:
                if not isinstance(script_content, str):
                    continue
                inner_data = json.loads(script_content)
                if not isinstance(inner_data, dict):
                    continue
                for _, value in inner_data.items():
                    text = str(value).strip()
                    processed = EMPTY_TEXT_PLACEHOLDER if not text else text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')
                    clean_lines.append(f'"{processed}"')

            # --- METHOD 3: CSV-LIKE INSIDE STRING ---
            elif selected_method == METHOD_CSV_STRING:
                if not isinstance(script_content, str):
                    log_function(f"Warning: 'm_Script' in {filename} is not a string. Skipping.")
                    continue

                reader = csv.reader(io.StringIO(script_content))
                rows = list(reader)

                if len(rows) < 2:
                    log_function(f"Warning: No valid CSV data in {filename}.")
                    continue

                headers = rows[0]
                try:
                    english_index = headers.index("English")
                except ValueError:
                    log_function(f"Warning: No 'English' column found in {filename}. Skipping.")
                    continue

                for row in rows[1:]:
                    if len(row) <= english_index:
                        clean_lines.append(EMPTY_TEXT_PLACEHOLDER)
                        continue
                    text = row[english_index].strip()
                    if not text:
                        clean_lines.append(EMPTY_TEXT_PLACEHOLDER)
                    else:
                        text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')
                        clean_lines.append(f'"{text}"')

            # --- Write TXT output ---
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(clean_lines))

            processed_files += 1
            log_function(f"[{processed_files}/{total_files}] Exported {len(clean_lines)} lines from {filename}")

        except Exception as e:
            log_function(f"Error processing {filename}: {e}")

    log_function(f"--- Export completed. Processed {processed_files}/{total_files} files. ---")

# =====================================================
# IMPORT FUNCTION
# =====================================================
def import_texts(log_function, selected_method):
    log_function("--- Starting Import Process ---")
    log_function(f"Selected method: {selected_method}")

    if not os.path.isdir(CLEAN_TEXT_DIR) or not os.path.isdir(ORIGINAL_JSON_DIR):
        log_function(f"Error: Required directories not found.")
        return

    os.makedirs(MODIFIED_JSON_DIR, exist_ok=True)
    json_files = [f for f in os.listdir(ORIGINAL_JSON_DIR) if f.endswith('.json')]
    total_files = len(json_files)
    processed_files = 0
    skipped_files = 0

    for json_filename in json_files:
        original_json_path = os.path.join(ORIGINAL_JSON_DIR, json_filename)
        txt_filename = os.path.splitext(json_filename)[0] + '.txt'
        clean_text_path = os.path.join(CLEAN_TEXT_DIR, txt_filename)
        modified_json_path = os.path.join(MODIFIED_JSON_DIR, json_filename)

        if not os.path.exists(clean_text_path):
            log_function(f"Skipping {json_filename}: No matching TXT file found.")
            skipped_files += 1
            continue

        try:
            with open(clean_text_path, 'r', encoding='utf-8') as f:
                lines = [line.strip().strip('"') for line in f if line.strip()]

            with open(original_json_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            script_content = original_data.get('m_Script')
            if script_content is None:
                skipped_files += 1
                continue

            # --- METHOD 1: XML-LIKE ---
            if selected_method == METHOD_XML_LIKE:
                matches = XML_ENTRY_PATTERN.findall(script_content)
                real_count = sum(1 for name, _ in matches if not is_comment_entry(name))
                if len(lines) != real_count:
                    log_function(f"Line mismatch in {json_filename}. Skipping.")
                    skipped_files += 1
                    continue

                it = iter(lines)

                def replacer(match):
                    name = match.group(1)
                    if is_comment_entry(name):
                        return match.group(0)
                    new_line = next(it)
                    new_line = "" if new_line == EMPTY_TEXT_PLACEHOLDER else html.escape(new_line.replace('\\n', '\n'))
                    return f'<entry name="{name}">{new_line}</entry>'

                modified_script = XML_ENTRY_PATTERN.sub(replacer, script_content)
                original_data['m_Script'] = modified_script

            # --- METHOD 2: JSON STRING ---
            elif selected_method == METHOD_JSON_STRING:
                inner = json.loads(script_content)
                if not isinstance(inner, dict) or len(lines) != len(inner):
                    log_function(f"Mismatch in {json_filename}. Skipping.")
                    skipped_files += 1
                    continue
                it = iter(lines)
                for key in inner.keys():
                    val = next(it)
                    inner[key] = "" if val == EMPTY_TEXT_PLACEHOLDER else val.replace('\\n', '\n')
                original_data['m_Script'] = json.dumps(inner, ensure_ascii=False, separators=(',', ':'))

            # --- METHOD 3: CSV-LIKE INSIDE STRING ---
            elif selected_method == METHOD_CSV_STRING:
                reader = csv.reader(io.StringIO(script_content))
                rows = list(reader)
                headers = rows[0]
                english_index = headers.index("English")

                if len(lines) != len(rows) - 1:
                    log_function(f"Mismatch in {json_filename} line count. Skipping.")
                    skipped_files += 1
                    continue

                for i, row in enumerate(rows[1:]):
                    new_text = lines[i].replace('\\n', '\n')
                    row[english_index] = "" if new_text == EMPTY_TEXT_PLACEHOLDER else new_text

                output_stream = io.StringIO()
                writer = csv.writer(output_stream, lineterminator="\n")
                writer.writerows(rows)
                original_data['m_Script'] = output_stream.getvalue()

            with open(modified_json_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, ensure_ascii=False, indent=2)

            processed_files += 1
            log_function(f"Imported and saved: {json_filename}")

        except Exception as e:
            log_function(f"Error importing {json_filename}: {e}")
            skipped_files += 1

    log_function(f"--- Import completed ---")
    log_function(f"Processed: {processed_files} | Skipped: {skipped_files}")

# =====================================================
# GUI APPLICATION
# =====================================================
class TextToolApp:
    def __init__(self, root):
        self.root = root
        root.title("TextsAsset Localization Tool By (MrGamesKingPro)")
        root.geometry("700x550")

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Method Selection ---
        method_frame = tk.LabelFrame(main_frame, text="Select Text Extraction Method", padx=5, pady=5)
        method_frame.pack(fill=tk.X, pady=5)

        self.method_var = tk.StringVar()
        self.method_dropdown = ttk.Combobox(method_frame, textvariable=self.method_var,
                                            values=[METHOD_XML_LIKE, METHOD_JSON_STRING, METHOD_CSV_STRING], state="readonly")
        self.method_dropdown.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.method_dropdown.set(METHOD_XML_LIKE)

        # --- Buttons ---
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.export_button = tk.Button(button_frame, text="Export Texts to TXT", command=self.run_export_thread, height=2, bg="#DDF0DD")
        self.export_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.import_button = tk.Button(button_frame, text="Import Texts from TXT", command=self.run_import_thread, height=2, bg="#DDEBF0")
        self.import_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state='disabled', font=("Courier New", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

        self.display_initial_instructions()

    def log(self, msg):
        self.root.after(0, self._log_main, msg)

    def _log_main(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + '\n')
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def display_initial_instructions(self):
        lines = [
            "--- How to Use ---",
            "1. Place original JSON files in 'Original_TextsAsset/'",
            "2. Choose the correct method:",
            "   • USE METHOD 1 → XML-like (<entry name=...>)",
            "   • USE METHOD 2 → Inner JSON string (escaped JSON)",
            "   • USE METHOD 3 → CSV text (Key,Korean,English,... in m_Script)",
            "3. Click Export to generate TXT files in 'Output_Clean_Text'.",
            "4. Edit and translate them.",
            "5. Click Import to rebuild localized JSONs in 'Output_TextsAsset'."
        ]
        for l in lines: self._log_main(l)

    def set_buttons_state(self, state):
        s = tk.DISABLED if state == 'disabled' else tk.NORMAL
        self.export_button.config(state=s)
        self.import_button.config(state=s)
        self.method_dropdown.config(state="readonly" if state == 'normal' else tk.DISABLED)

    def run_export_thread(self):
        self._clear_log()
        method = self.method_var.get()
        if not method:
            self.log("Please select a method.")
            return
        self.set_buttons_state('disabled')
        threading.Thread(target=self._export_worker, args=(method,)).start()

    def _export_worker(self, method):
        try:
            export_texts(self.log, method)
        finally:
            self.root.after(0, self.set_buttons_state, 'normal')

    def run_import_thread(self):
        self._clear_log()
        method = self.method_var.get()
        if not method:
            self.log("Please select a method.")
            return
        self.set_buttons_state('disabled')
        threading.Thread(target=self._import_worker, args=(method,)).start()

    def _import_worker(self, method):
        try:
            import_texts(self.log, method)
        finally:
            self.root.after(0, self.set_buttons_state, 'normal')

    def _clear_log(self):
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToolApp(root)
    root.mainloop()
