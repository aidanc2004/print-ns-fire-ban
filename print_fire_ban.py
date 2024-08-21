#!/usr/bin/env python3

# Download the current nova scotia fire ban at 2pm everyday
# Aidan Carey, June 8th - August 20st, 2024

import os
import time
import math
import win32api
import win32print
import schedule
import datetime
import threading
from selenium import webdriver
import PIL.Image
from io import BytesIO

# GUI imports
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

window = Tk()
window.title("Print Fire Ban")
window.iconbitmap("icon.ico")
window.wm_state("iconic") # Open minimized
window.resizable(False, False)

frame = ttk.Frame(window, padding=5)
frame.grid()

logs = scrolledtext.ScrolledText(frame, width=70, height=16, state=DISABLED, wrap=WORD)
logs.grid(column=1, rowspan=100, padx=(5,0))

### About button ###

def about():
    messagebox.showinfo("About", "Aidan Carey 2024")
ttk.Button(frame, text="About", command=about).grid(row=99)

### Help button ###

# Open the help window
def open_help():
  # Open new window and configure it
  help_window = Toplevel()
  help_window.title("Help")
  help_window.iconbitmap("icon.ico")
  help_window.focus()
  help_window.geometry("500x400")
  help_window.resizable(False, False)
  
  # Where the help information is shown
  help_text = scrolledtext.ScrolledText(help_window, width=60, height=24, wrap=WORD)
  # Load help information from file
  with open("help.txt", "r") as help_file:
    help_text.insert(INSERT, help_file.read())
  # Disable typing    
  help_text.config(state=DISABLED)
  help_text.pack()

ttk.Button(frame, text="Help", command=open_help).grid(row=98)

### Choose printer ###

# Get formatted printer names in a list
def get_printers():
  # All local printers
  printers_tuple = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
  
  # Get formatted printer names from the tuples
  printers = []
  for printer in printers_tuple:
    printer_name = printer[1]
    
    # Because of how the printer name is formatted, we get rid of everything
    # after the comma in the printer name
    comma = printer_name.find(",")
    if comma != -1:
      printer_name = printer_name[:comma]
    
    printers.append(printer_name)
  
  return printers

# Default printer selection, read from "config.txt"
default_printer = ""
with open('config.txt', 'r') as config:
  default_printer = config.read()

ttk.Label(frame, text="Printer:").grid(row=5)

printers = get_printers()

printer_combobox = ttk.Combobox(frame, values=printers)
printer_combobox.grid(row=9)

# Select the default printer if it's there
if default_printer in printers:
  printer_combobox.set(default_printer)

def update_default_printer(printer_name):
  with open("config.txt", "w") as config:
    config.write(printer_name)

### Main Script ###

# Print with date and time
def log(msg):
  dt = datetime.datetime.now().strftime("[%Y-%m-%d, %H:%M:%S]")
  dt_msg = f"{dt} {msg}"
  
  # Log to GUI
  logs.config(state=NORMAL)
  logs.insert(INSERT, dt_msg + "\n")
  logs.config(state=DISABLED)
  
  # Log to STDOUT
  print(dt_msg)
  
  # Log to file
  log_file = open("log.txt", "a")
  log_file.write(dt_msg + "\n")
  log_file.close()

# Set the Firefox window size to get all content on the page
def set_window_size(driver):
  window_width = driver.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
  window_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
  driver.set_window_size(window_width, window_height)

# Crop image to only needed information  
def crop_img(driver, img, size):
  # Section to get, from legend (included) to the county after Annapolis (not included)
  table_legend = driver.find_element("class name", "table-legend")
  antigonish_county = driver.find_element("id", "Antigonish-County")
  
  table_location = table_legend.location
  county_location = antigonish_county.location

  # Location of needed info
  left = table_location["x"] - 30
  top = table_location["y"]
  right = table_location["x"] + size["width"]
  bottom = county_location["y"]
  
  img = img.crop((left, top, right, bottom))

  return img

# Take a screenshot of the fire ban website
def fireban_png(file):
  # Start Firefox in headless mode
  options = webdriver.firefox.options.Options()
  options.add_argument("--headless")
  driver = webdriver.Firefox(options=options)
  
  # Open website
  url = "https://novascotia.ca/burnsafe/"
  try:
    driver.get(url)
  except:
    log(f"Couldn't get {url}.")
    return -1

  # Page might not have loaded fast enough
  id_name = "burn-data-content"
  try:
    page = driver.find_element("id", id_name)
  except:
    log(f"Couldn't find {id_name}.")
    return -1
  
  set_window_size(driver) # Set Firefox size

  # Get PNG of website and crop to only needed information
  png = driver.get_screenshot_as_png()
  img = PIL.Image.open(BytesIO(png))
  img = crop_img(driver, img, page.size)

  driver.quit() # Exit Firefox
  
  # New image for printer paper (A4 at 150dpi)
  paper = PIL.Image.new(mode="RGB", size=(1240, 1754), color=(255, 255, 255))

  # Paste image into the middle of the paper
  img_width, img_height = img.size
  new_width = 1240
  # Maintain aspect ratio
  new_height = math.floor(new_width * img_width / img_height)

  img = img.resize((new_width, new_height), PIL.Image.LANCZOS)
  paper.paste(img, (0, (math.floor(1754/2)) - (math.floor(new_height/2))))
  
  paper.save(file)

  return 0

# Get the fire ban and print it to the default printer
def print_fireban():
  # Save NS fire ban website as a png
  file = "fireban.png"
  err = fireban_png(file)
  if (err < 0):
    return
  
  # Print PDF to printer (Windows specific)
  printer_name = printers[printer_combobox.current()]
  update_default_printer(printer_name)
  err = win32api.ShellExecute(0, "printto", file, f'"{printer_name}"', ".", 0)
  if (err <= 32):
    log(f"Failed to print to f{printer_name}.")
    return
  log(f"Printing to {printer_name}.")

# Call print_fireban from a thread for use with ttk.Button
def print_fireban_threading():
    threading.Thread(target=print_fireban).start()

ttk.Label(frame, text="Immediately Print:").grid(row=0)
ttk.Button(frame, text="Print", command=print_fireban_threading).grid(row=1)

# Run print_fireban everyday at 2pm
def start_fire_ban():
  log("Started fire ban printing script.")
  schedule.every().day.at("14:00").do(print_fireban)
  while True:
    # Wait until the next time we need to run it
    t = schedule.idle_seconds()
    if t > 0:
      time.sleep(t)
    # Get and print ban
    schedule.run_pending()

# Start fire ban printing thread
print_thread = threading.Thread(target=start_fire_ban)
print_thread.daemon = True # Close on exit
print_thread.start()

# Start GUI main loop
window.mainloop()