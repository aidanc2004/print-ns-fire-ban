# Nova Scotia Fire Ban Automation

<img width="944" height="386" alt="Fire Ban GUI" src="https://github.com/user-attachments/assets/1866293a-e334-492c-85d8-c3e1e020380d" />

Python automation tool using web scraping, Tkinter, and the Win32 API to automatically retrieve and print the current fire ban status in Nova Scotia daily at 2 PM.

## Features

- Automatically fetches and prints out the daily fire ban information at 2 PM.
- Logs all activity, showing when the script starts, prints, or errors.
- Provices manual button for printing in-case of misprints or error.

## Requirements

- Python 3.x
- pywin32
- tkinter
- selenium
- pillow
- schedule

## Installation

1. Clone the repository: ```bash
git clone https://github.com/aidanc2004/print-ns-fire-ban```
2. Install requirements: ```bash
pip install tkinter win32 selenium pillow schedule```
3. Start manually ```bash
python print_fire_ban.py```
4. Optional: Follow help.txt to setup automatic startup.
