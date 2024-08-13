"""! @file log_viewer.py
@brief A script to generate an HTML viewer for log files and open it with xdg-open.

This script uses a GUI to select a log file, generates an HTML viewer with syntax highlighting
for different log levels, and attempts to open it with xdg-open, even when run with sudo.

@author Iskandar Putra
@date August 13, 2024
@version 1.8
"""

import re
import tkinter as tk
from tkinter import filedialog
from html import escape
import os
import subprocess
import time

def parse_log_entry(line):
    """! Parse a single log entry line.
    
    @param line The log entry line to parse.
    @return A tuple containing (time, prefix, message) if parsing is successful, None otherwise.
    """
    line = re.sub(r'<(?!(?:inf|wrn|err))[^>]+>', '', line)
    
    match = re.match(r'^(\d{2}:\d{2}:\d{2})(?:,\s*"?\[(\d+)\])?\s*(.*)$', line.strip())
    if match:
        time, prefix, message = match.groups()
        prefix = prefix or ""
        return time, prefix, message
    return None

def generate_html(log_file, output_file):
    """! Generate an HTML viewer for the log file.
    
    @param log_file Path to the input log file.
    @param output_file Path to the output HTML file.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Log Viewer</title>
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Fira Code', monospace;
                background-color: #000000;
                color: #ffffff;
                padding: 20px;
                font-size: 15px;
                line-height: 2.0;
            }
            .log-entry {
                margin-bottom: 3px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .time { color: #00ffff; font-weight: bold; }
            .prefix { color: #f300e5; font-weight: bold; }
            .error { color: #ff2c1f; }
            .warning { color: #f1ff00; }
            .info { color: #ffffff; }
            .highlight-err {
                background-color: #ff2c1f;
                color: #000000;
                padding: 2px 4px;
                border-radius: 3px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
    """
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_log_entry(line)
            if parsed:
                time, prefix, message = parsed
                
                line_class = "info"
                if "<err>" in message.lower():
                    line_class = "error"
                elif "<wrn>" in message.lower():
                    line_class = "warning"
                
                html_content += f'<div class="log-entry {line_class}">'
                html_content += f'<span class="time">{escape(time)}</span> '
                if prefix:
                    html_content += f'<span class="prefix">[{escape(prefix)}]</span> '
                
                html_content += f'{escape(message.strip("\"\n"))}'
                html_content += '</div>\n'
            else:
                html_content += f'<div class="log-entry info">{escape(line.strip("\"\n"))}</div>\n'
    html_content += """
    </body>
    </html>
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def select_file():
    """! Open a file dialog for selecting the input log file.
    
    @return The selected file path, or None if no file was selected.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.txt"), ("All Files", "*.*")])
    return file_path

def open_file(filename):
    """! Attempt to open the file using xdg-open, even when run as root.
    
    @param filename Name of the file to be opened.
    """
    print(f"Waiting for 1 second before attempting to open the file...")
    time.sleep(1)  # Sleep for 1 second

    try:
        print(f"Attempting to open {filename} using xdg-open...")
        # Use sudo -u to run xdg-open as the real user, not root
        real_user = os.environ.get('SUDO_USER')
        if real_user:
            subprocess.run(['sudo', '-u', real_user, 'xdg-open', filename], check=True)
        else:
            subprocess.run(['xdg-open', filename], check=True)
        print(f"File opened successfully using xdg-open")
    except subprocess.CalledProcessError as e:
        print(f"Error opening file with xdg-open: {e}")
        print(f"Please open the file manually: {filename}")

def main():
    """! Main function to execute the log viewer generation process."""
    input_file = select_file()
    if not input_file:
        print("No file selected. Exiting.")
        return
    
    output_filename = "log_viewer.html"
    
    generate_html(input_file, output_filename)
    print(f"HTML log viewer generated: {output_filename}")
    
    open_file(output_filename)
    
    print("Script execution completed.")

if __name__ == "__main__":
    main()