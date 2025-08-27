

**Description**

This GUI tool extracts and imports localized texts from Unity-exported JSON TextAsset files. It supports two `m_Script` formats (XML-like entries or embedded JSON strings), converts texts to/from editable TXT files, and handles newlines and special characters for easy translation workflows.

## Download tool

[TextAsset-Localization-Tool](https://github.com/MrGamesKingPro/TextsAsset-Localization-Tool/releases/tag/TextsAsset-Localization-Tool.V.1.0)

# TextAsset Localization Tool

This Python-based GUI tool simplifies the process of localizing text found within Unity's `TextsAsset` JSON files. It allows you to extract translatable strings into clean text files for editing and then import those translated texts back into new JSON files, maintaining the original structure.

<img width="716" height="600" alt="Screenshot_2025-08-27_21-07-09" src="https://github.com/user-attachments/assets/a979e93e-ef3d-499b-a437-6c7f3bba8fc1" />

## Features

*   **Text Extraction:** Extracts text content from the `m_Script` field within JSON files, supporting two distinct formats:
    *   **XML-like Structure (`<entry name="...">...</entry>`):** Ideal for JSONs where the `m_Script` contains XML-like elements. It correctly handles HTML entities and skips comment entries.
    *   **Embedded JSON String (`{"key": "value"}`):** Designed for JSONs where the `m_Script` field holds an escaped JSON string.
*   **Translation-Friendly Output:** Exports texts into `.txt` files, with each translatable string on a new line and newlines (`\n`) represented as `\\n` for easier editing. Empty entries are marked with `---`.
*   **Seamless Import:** Imports translated texts from `.txt` files, re-inserting them into the original JSON structure to create new, localized JSON files.
*   **User-Friendly Interface:** A Tkinter-based graphical user interface for intuitive operation.
*   **Error Handling & Logging:** Provides real-time feedback and error messages within the GUI.

## Python Requirements

This tool uses standard Python libraries and does not require any external packages to be installed via `pip`.

*   Python 3.x
*   `tkinter` (usually included with Python installations)
*   `json`
*   `re`
*   `html`
*   `os`
*   `threading`

## How to Use

The application provides detailed instructions directly within its log area upon startup. Follow these general steps:

1.  **Prepare Original Files:**
    *   Create a folder named `Original_TextsAsset` in the same directory as the script.
    *   Place all your original Unity TextAsset JSON files (e.g., `en-CAB-....json`, `EN_UI-resources.assets-3194.json`) into this `Original_TextsAsset` folder.

2.  **Export Texts for Translation:**
    *   Run the script (`python your_script_name.py`).
    *   In the GUI, carefully **select the correct "Text Extraction Method"** from the dropdown menu:
        *   Choose **"USE METHOD 1"** for JSON files where `m_Script` contains XML-like `<entry name="...">...</entry>` tags (e.g., `EN_UI-resources.assets-3194.json`).
        *   Choose **"USE METHOD 2"** for JSON files where `m_Script` contains an escaped JSON string like `{"key": "value"}` (e.g., `en-CAB-....json`).
    *   Click the **"Export Texts to TXT"** button.
    *   A new folder named `Output_Clean_Text` will be created, containing `.txt` files for each processed JSON.

3.  **Translate the Text Files:**
    *   Open the `.txt` files located in the `Output_Clean_Text` folder using a text editor.
    *   Translate the text content within the double quotes.
    *   **Important:**
        *   Do **not** change the double quotes.
        *   Maintain `\\n` for newlines if you want them in the final output.
        *   Keep the placeholder `---` (three hyphens) exactly as is for any text entry that you wish to remain empty.

4.  **Import Translated Texts:**
    *   After saving all your translated `.txt` files, return to the GUI.
    *   Ensure the **same "Text Extraction Method"** used for export is still selected.
    *   Click the **"Import Texts from TXT"** button.
    *   A new folder named `Output_TextsAsset` will be created, containing the new JSON files with your translations merged in. These are ready for use in your game.
