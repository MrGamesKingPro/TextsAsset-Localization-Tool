# Based on Requirements

[UABEA](https://github.com/nesrak1/UABEA)

**Description**

This GUI tool extracts and imports localized texts from Unity-exported JSON TextAsset files. It supports two `m_Script` formats (XML-like entries or embedded JSON strings), converts texts to/from editable TXT files, and handles newlines and special characters for easy translation workflows.

## Download tool

[TextAsset-Localization-Tool](https://github.com/MrGamesKingPro/TextsAsset-Localization-Tool/releases/tag/TextsAsset-Localization-Tool.V.1.0)

# TextAsset Localization Tool

This Python-based GUI tool simplifies the process of localizing text found within Unity's `TextsAsset` JSON files. It allows you to extract translatable strings into clean text files for editing and then import those translated texts back into new JSON files, maintaining the original structure.

<img width="716" height="600" alt="Screenshot_2025-08-27_21-07-09" src="https://github.com/user-attachments/assets/a979e93e-ef3d-499b-a437-6c7f3bba8fc1" />

An updated and more accurate description based on the Python script provided:

## Features

*   **Multi-Format Text Extraction:** Extracts text from the `m_Script` field within JSON files, supporting three distinct formats:
    *   **Method 1 (XML-like):** Handles `<entry name="...">...</entry>` structures. It correctly processes HTML entities and ignores commented-out entries (those starting with `//`).
    *   **Method 2 (Embedded JSON):** Parses `m_Script` content that is formatted as an escaped JSON string (e.g., `"{\"key\": \"value\"}"`).
    *   **Method 3 (CSV-like):** Processes `m_Script` content formatted as a CSV string. It specifically reads the "English" column by default, making it suitable for localization sheets stored as CSV text.
*   **Translation-Friendly Output:** Exports extracted text into `.txt` files. Each string is placed on a new line and enclosed in double quotes. Newline characters are preserved as `\\n` for easy editing in text editors. Empty entries are clearly marked with a `---` placeholder.
*   **Seamless Re-Import:** Imports translated text from the `.txt` files, intelligently rebuilding the original JSON structure. It creates new, localized JSON files ready for use.
*   **User-Friendly Interface:** A simple and intuitive graphical user interface (GUI) built with Tkinter, allowing for easy operation without command-line interaction.
*   **Logging and Feedback:** A log area provides real-time progress updates, error messages, and clear instructions, ensuring the user is always informed of the tool's status.

## Python Requirements

This tool uses standard Python libraries and does not require any external packages to be installed.

*   Python 3.x
*   `tkinter` (typically included with Python)
*   `json`
*   `re`
*   `html`
*   `os`
*   `threading`
*   `csv`
*   `io`

## How to Use

The application provides detailed instructions in its log window upon startup.

1.  **Prepare Files:**
    *   Create a folder named `Original_TextsAsset` in the same directory as the script.
    *   Place all your original Unity TextAsset JSON files into the `Original_TextsAsset` folder.

2.  **Export Texts for Translation:**
    *   Run the Python script.
    *   From the dropdown menu in the GUI, **select the correct extraction method** that matches your JSON file's structure:
        *   **USE METHOD 1:** For files where `m_Script` contains XML-like tags (`<entry name="...">...</entry>`).
        *   **USE METHOD 2:** For files where `m_Script` contains an escaped JSON string (`{"key": "value"}`).
        *   **USE METHOD 3:** For files where `m_Script` contains CSV-formatted text with a header row that includes an "English" column.
    *   Click the **"Export Texts to TXT"** button.
    *   A new folder, `Output_Clean_Text`, will be created containing the exported `.txt` files.

3.  **Translate the Text:**
    *   Open the `.txt` files in the `Output_Clean_Text` folder.
    *   Translate the text inside the double quotes on each line.
    *   **Important Rules:**
        *   Do **not** remove the surrounding double quotes.
        *   Preserve the `\\n` characters to maintain line breaks.
        *   If an entry should be empty, keep the `---` placeholder exactly as is.

4.  **Import Translated Texts:**
    *   Once you have saved your translated `.txt` files, return to the application.
    *   Ensure the **same method** you used for exporting is still selected in the dropdown.
    *   Click the **"Import Texts from TXT"** button.
    *   A final folder, `Output_TextsAsset`, will be created. It will contain the newly generated JSON files with your translations integrated, ready to be used in your project.
