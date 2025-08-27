import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import json
import re
import html
import os

# --- Directory Names ---
# The folder containing the original JSON files
ORIGINAL_JSON_DIR = 'Original_TextsAsset'
# The folder where clean text files will be saved
CLEAN_TEXT_DIR = 'Output_Clean_Text'
# The folder where modified JSON files will be saved after import
MODIFIED_JSON_DIR = 'Output_TextsAsset'

# --- Placeholder for empty text entries ---
EMPTY_TEXT_PLACEHOLDER = '---'

# --- Constants for method selection ---
METHOD_XML_LIKE = "USE METHOD 1"
METHOD_JSON_STRING = "USE METHOD 2"

# --- Method 1: XML-like 'm_Script' (e.g., EN_UI-resources.assets-3194.json) ---
# Regex to find <entry name="NAME">CONTENT</entry>
XML_ENTRY_PATTERN = re.compile(r'<entry name="(.*?)">(.*?)</entry>', re.DOTALL)

def is_comment_entry(entry_name):
    """
    Helper function for XML-like method to determine if an entry is a comment.
    Entries starting with '//' are considered comments and are skipped during extraction/import.
    """
    return entry_name.strip().startswith('//')

# --- Function 1: Export texts from JSON to TXT ---
def export_texts(log_function, selected_method):
    """
    Reads all JSON files, extracts translatable texts based on the selected method,
    and saves them as TXT files.
    Args:
        log_function (function): A function to log messages to the GUI.
        selected_method (str): The method to use for text extraction (XML_LIKE or JSON_STRING).
    """
    log_function("--- Starting Export Process ---")
    log_function(f"Selected method: {selected_method}")

    if not os.path.isdir(ORIGINAL_JSON_DIR):
        log_function(f"Error: Input directory '{ORIGINAL_JSON_DIR}' not found.")
        return

    os.makedirs(CLEAN_TEXT_DIR, exist_ok=True)
    
    json_files = [f for f in os.listdir(ORIGINAL_JSON_DIR) if f.endswith('.json')]
    
    if not json_files:
        log_function(f"No JSON files found in the directory '{ORIG_JSON_DIR}'.")
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
            
            if selected_method == METHOD_XML_LIKE:
                if not isinstance(script_content, str):
                    log_function(f"Warning: 'm_Script' in {filename} is not a string, expected for XML_LIKE method. Skipping.")
                    continue
                matches = XML_ENTRY_PATTERN.findall(script_content)
                for entry_name, text_content in matches:
                    if is_comment_entry(entry_name):
                        continue

                    unescaped_text = html.unescape(text_content)
                    stripped_text = unescaped_text.strip()
                    
                    if not stripped_text:
                        processed_text = EMPTY_TEXT_PLACEHOLDER
                    else:
                        # Normalize all newlines to '\n', then escape them to literal '\\n' for TXT file
                        normalized_newlines = stripped_text.replace('\r\n', '\n').replace('\r', '\n')
                        processed_text = normalized_newlines.replace('\n', '\\n')
                    
                    quoted_text = f'"{processed_text}"'
                    clean_lines.append(quoted_text)
            
            elif selected_method == METHOD_JSON_STRING:
                if not isinstance(script_content, str):
                    log_function(f"Warning: 'm_Script' in {filename} is not a string, expected for JSON_STRING method. Skipping.")
                    continue
                inner_data = json.loads(script_content) # Parse the inner JSON string
                
                # Check if inner_data is a dictionary, as expected for key-value pairs
                if not isinstance(inner_data, dict):
                    log_function(f"Warning: 'm_Script' in {filename} does not contain a JSON object, expected for JSON_STRING method. Skipping.")
                    continue

                # Iterate through key-value pairs to extract text, preserving order
                for key, value in inner_data.items():
                    # Ensure value is treated as a string for consistent processing
                    unescaped_text = str(value) 
                    stripped_text = unescaped_text.strip()
                    
                    if not stripped_text:
                        processed_text = EMPTY_TEXT_PLACEHOLDER
                    else:
                        # Normalize all newlines to '\n', then escape them to literal '\\n' for TXT file
                        normalized_newlines = stripped_text.replace('\r\n', '\n').replace('\r', '\n')
                        processed_text = normalized_newlines.replace('\n', '\\n')
                    
                    quoted_text = f'"{processed_text}"'
                    clean_lines.append(quoted_text)

            # Write the extracted lines to the TXT file
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(clean_lines))
            
            processed_files += 1
            progress_msg = f"[{processed_files}/{total_files}] Extracted texts from {filename} to {output_txt_filename} ({len(clean_lines)} lines)"
            log_function(progress_msg)

        except json.JSONDecodeError as jde:
            log_function(f"JSON parsing error in {filename} for m_Script content: {jde}. This might be due to an incorrect method selection or malformed JSON.")
            continue
        except Exception as e:
            log_function(f"An unexpected error occurred while processing {filename}: {e}")

    log_function(f"\n--- Export process completed. Successfully processed {processed_files} files. ---")

# --- Function 2: Import texts from TXT to JSON ---
def import_texts(log_function, selected_method):
    """
    Reads modified texts from TXT files and merges them back into new JSON files
    based on the selected method.
    Args:
        log_function (function): A function to log messages to the GUI.
        selected_method (str): The method to use for text importation (XML_LIKE or JSON_STRING).
    """
    log_function("--- Starting Import Process ---")
    log_function(f"Selected method: {selected_method}")

    if not os.path.isdir(CLEAN_TEXT_DIR) or not os.path.isdir(ORIGINAL_JSON_DIR):
        log_function(f"Error: The directories '{CLEAN_TEXT_DIR}' and '{ORIGINAL_JSON_DIR}' must exist.")
        return

    os.makedirs(MODIFIED_JSON_DIR, exist_ok=True)

    json_files = [f for f in os.listdir(ORIGINAL_JSON_DIR) if f.endswith('.json')]

    if not json_files:
        log_function(f"No JSON files found in the source directory '{ORIGINAL_JSON_DIR}'.")
        return
        
    total_files = len(json_files)
    processed_files = 0
    skipped_files = 0
    
    for json_filename in json_files:
        original_json_path = os.path.join(ORIGINAL_JSON_DIR, json_filename)
        txt_filename = os.path.splitext(json_filename)[0] + '.txt'
        clean_text_path = os.path.join(CLEAN_TEXT_DIR, txt_filename)
        modified_json_path = os.path.join(MODIFIED_JSON_DIR, json_filename)

        progress_prefix = f"[{processed_files + skipped_files + 1}/{total_files}]"

        if not os.path.exists(clean_text_path):
            log_function(f"{progress_prefix} Skipping: No corresponding TXT file '{txt_filename}' found for '{json_filename}'.")
            skipped_files += 1
            continue

        try:
            with open(clean_text_path, 'r', encoding='utf-8') as f:
                # Read lines, removing quotes and surrounding whitespace.
                # This assumes export function ensured one quoted line per entry.
                modified_lines_raw = [line.strip() for line in f if line.strip()]
            
            modified_lines = []
            for line in modified_lines_raw:
                if line.startswith('"') and line.endswith('"'):
                    modified_lines.append(line[1:-1])
                else:
                    # Fallback for lines that might somehow not be quoted, though they should be
                    modified_lines.append(line)

            with open(original_json_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            script_content = original_data.get('m_Script')
            if script_content is None:
                log_function(f"{progress_prefix} Warning in {json_filename}: 'm_Script' not found. Skipping file.")
                skipped_files += 1
                continue
            
            actual_translatable_count = 0

            if selected_method == METHOD_XML_LIKE:
                if not isinstance(script_content, str):
                    log_function(f"Warning: 'm_Script' in {json_filename} is not a string, expected for XML_LIKE method. Skipping.")
                    skipped_files += 1
                    continue
                original_matches = XML_ENTRY_PATTERN.findall(script_content)
                actual_translatable_count = sum(1 for name, content in original_matches if not is_comment_entry(name))

                if len(modified_lines) != actual_translatable_count:
                    error_msg = f"{progress_prefix} Error in {txt_filename}: Number of lines ({len(modified_lines)}) does not match original translatable texts ({actual_translatable_count}). Skipping."
                    log_function(error_msg)
                    skipped_files += 1
                    continue

                line_iterator = iter(modified_lines)
                
                def replacer(match):
                    entry_name = match.group(1)
                    if is_comment_entry(entry_name):
                        return match.group(0) # If it's a comment, return it unchanged

                    try:
                        new_line = next(line_iterator)
                        if new_line == EMPTY_TEXT_PLACEHOLDER:
                            escaped_text = ""
                        else:
                            # Convert literal '\\n' back to actual newline '\n'
                            new_line_processed = new_line.replace('\\n', '\n')
                            # HTML escape for XML-like output
                            escaped_text = html.escape(new_line_processed)
                        return f'<entry name="{entry_name}">{escaped_text}</entry>'
                    except StopIteration:
                        log_function(f"Internal error: Ran out of lines for {json_filename} during XML replacement. Check TXT file integrity.")
                        return match.group(0) # Fallback to original content

                modified_script_content = XML_ENTRY_PATTERN.sub(replacer, script_content)
                original_data['m_Script'] = modified_script_content

            elif selected_method == METHOD_JSON_STRING:
                if not isinstance(script_content, str):
                    log_function(f"Warning: 'm_Script' in {json_filename} is not a string, expected for JSON_STRING method. Skipping.")
                    skipped_files += 1
                    continue
                original_inner_dict = json.loads(script_content)
                
                if not isinstance(original_inner_dict, dict):
                    log_function(f"Warning: 'm_Script' in {json_filename} does not contain a JSON object, expected for JSON_STRING method. Skipping.")
                    skipped_files += 1
                    continue

                actual_translatable_count = len(original_inner_dict) # All key-value pairs are translatable

                if len(modified_lines) != actual_translatable_count:
                    error_msg = f"{progress_prefix} Error in {txt_filename}: Number of lines ({len(modified_lines)}) does not match original translatable texts ({actual_translatable_count}). Skipping."
                    log_function(error_msg)
                    skipped_files += 1
                    continue

                new_inner_dict = original_inner_dict.copy() # Create a copy to modify
                line_iterator = iter(modified_lines)

                # Iterate through keys of the original dictionary to maintain order
                for key in original_inner_dict.keys():
                    new_value_raw = next(line_iterator)
                    
                    if new_value_raw == EMPTY_TEXT_PLACEHOLDER:
                        processed_value = ""
                    else:
                        # Convert literal '\\n' back to actual newline '\n' for JSON string
                        processed_value = new_value_raw.replace('\\n', '\n')
                    
                    new_inner_dict[key] = processed_value
                
                # Dump the modified inner dictionary back to a compact JSON string,
                # ensuring no extra whitespace or ASCII escaping to match original style.
                original_data['m_Script'] = json.dumps(new_inner_dict, ensure_ascii=False, separators=(',', ':'))

            with open(modified_json_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, ensure_ascii=False, indent=2)
            
            processed_files += 1
            log_function(f"{progress_prefix} Successfully merged texts from {txt_filename} into {json_filename}.")

        except json.JSONDecodeError as jde:
            log_function(f"JSON parsing error in {json_filename} for m_Script content: {jde}. This might be due to an incorrect method selection or malformed JSON.")
            skipped_files += 1
            continue
        except Exception as e:
            log_function(f"A fatal error occurred while processing {json_filename}: {e}")
            skipped_files += 1

    log_function("\n--- Import process completed ---")
    log_function(f"Total original files: {total_files}")
    log_function(f"Files successfully merged: {processed_files}")
    log_function(f"Files skipped: {skipped_files}")
    log_function(f"---------------------------------")


# --- GUI Application Class ---
class TextToolApp:
    def __init__(self, root):
        self.root = root
        root.title("TextsAsset Localization Tool By (MrGamesKingPro)")
        root.geometry("700x550") # Slightly taller for the new dropdown

        # --- Main Frame ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Method Selection Frame ---
        method_frame = tk.LabelFrame(main_frame, text="Select Text Extraction Method", padx=5, pady=5)
        method_frame.pack(fill=tk.X, pady=5)

        self.method_var = tk.StringVar()
        # Set initial value and available options for the dropdown
        self.method_dropdown = ttk.Combobox(method_frame, textvariable=self.method_var,
                                            values=[METHOD_XML_LIKE, METHOD_JSON_STRING], state="readonly")
        self.method_dropdown.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.method_dropdown.set(METHOD_XML_LIKE) # Default selection is XML_LIKE

        # --- Button Frame ---
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.export_button = tk.Button(button_frame, text="Export Texts to TXT", command=self.run_export_thread, height=2, bg="#DDF0DD")
        self.export_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.import_button = tk.Button(button_frame, text="Import Texts from TXT", command=self.run_import_thread, height=2, bg="#DDEBF0")
        self.import_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state='disabled', font=("Courier New", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # --- Display instructions on startup ---
        self.display_initial_instructions()

    def log(self, message):
        """ Thread-safe logging to the text area. """
        self.root.after(0, self._log_on_main_thread, message)

    def _log_on_main_thread(self, message):
        """ This method is executed by the main GUI thread. """
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.see(tk.END) # Auto-scroll to the end
        self.log_area.config(state='disabled')

    def display_initial_instructions(self):
        """Displays the 'How to Use' guide in the log area upon application start."""
        instructions = [
            "--- How to Use ---",
            "1. 'Original_TextsAsset' folder:",
            "   - Place your original JSON files in this folder.",
            "   - The script reads files from here to extract texts.",
            "   - Example: Place 'quests.json' inside 'Original_TextsAsset/'.",
            "",
            "2. 'Output_Clean_Text' folder:",
            "   - Select the correct method above (XML_LIKE or JSON_STRING).",
            "   - Click 'Export Texts to TXT'. The extracted texts will appear here as .txt files.",
            "   - Open these .txt files and translate the lines. Maintain the placeholder '---' for empty entries.",
            "   - Example: 'Output_Clean_Text/quests.txt' will be created for you to edit.",
            "",
            "3. 'Output_TextsAsset' folder:",
            "   - Ensure the correct method is still selected.",
            "   - After translating the .txt files, click 'Import Texts from TXT'.",
            "   - The script will create new, modified JSON files here with your translations.",
            "   - Example: The final translated file 'Output_TextsAsset/quests.json' is ready.",
            "",
            "--- Method Descriptions ---",
            f"'{METHOD_XML_LIKE}': For JSONs where 'm_Script' contains XML-like '<entry name=\"...\">...</entry>' tags. (e.g., EN_UI-resources.assets-3194.json)",
            f"'{METHOD_JSON_STRING}': For JSONs where 'm_Script' contains another JSON string itself (escaped). (e.g., en-CAB-....json)",
            "--------------------"
        ]
        for line in instructions:
            self._log_on_main_thread(line)

    def set_buttons_state(self, state):
        """ Enable or disable buttons and method dropdown. """
        if state == 'disabled':
            self.export_button.config(state=tk.DISABLED)
            self.import_button.config(state=tk.DISABLED)
            self.method_dropdown.config(state=tk.DISABLED)
        else: # 'normal'
            self.export_button.config(state=tk.NORMAL)
            self.import_button.config(state=tk.NORMAL)
            self.method_dropdown.config(state="readonly") # Allow selection when active

    def run_export_thread(self):
        """ Starts the export process in a new thread to avoid freezing the GUI. """
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END) # Clear log before new operation
        self.log_area.config(state='disabled')
        
        selected_method = self.method_var.get()
        if not selected_method:
            self.log("Please select an extraction method from the dropdown.")
            return

        self.set_buttons_state('disabled')
        thread = threading.Thread(target=self._export_worker, args=(selected_method,))
        thread.start()

    def _export_worker(self, selected_method):
        """ The actual work for the export thread. """
        try:
            export_texts(self.log, selected_method)
        except Exception as e:
            self.log(f"An unexpected error occurred during export: {e}")
        finally:
            self.root.after(0, self.set_buttons_state, 'normal')

    def run_import_thread(self):
        """ Starts the import process in a new thread. """
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END) # Clear log before new operation
        self.log_area.config(state='disabled')

        selected_method = self.method_var.get()
        if not selected_method:
            self.log("Please select an import method from the dropdown.")
            return

        self.set_buttons_state('disabled')
        thread = threading.Thread(target=self._import_worker, args=(selected_method,))
        thread.start()

    def _import_worker(self, selected_method):
        """ The actual work for the import thread. """
        try:
            import_texts(self.log, selected_method)
        except Exception as e:
            self.log(f"An unexpected error occurred during import: {e}")
        finally:
            self.root.after(0, self.set_buttons_state, 'normal')

# --- Main execution block ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToolApp(root)
    root.mainloop()
