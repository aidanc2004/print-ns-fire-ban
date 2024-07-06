#!/usr/bin/env python3

# Download the current nova scotia fire ban at 2pm everyday
# Aidan Carey, June 8th - July 2nd, 2024

import os
import time
import math
import win32api
import win32print
import schedule
import datetime
from selenium import webdriver
from PIL import Image
from io import BytesIO

# Print with date and time
def log(msg):
  dt = datetime.datetime.now().strftime("[%Y-%m-%d, %H:%M:%S]")
  dt_msg = f"{dt} {msg}"
  
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
  img = Image.open(BytesIO(png))
  img = crop_img(driver, img, page.size)

  driver.quit() # Exit Firefox
  
  # New image for printer paper (A4 at 150dpi)
  paper = Image.new(mode="RGB", size=(1240, 1754), color=(255, 255, 255))

  # Paste image into the middle of the paper
  img_width, img_height = img.size
  new_width = 1240
  # Maintain aspect ratio
  new_height = math.floor(new_width * img_width / img_height)

  img = img.resize((new_width, new_height), Image.LANCZOS)
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
  printer_name = "Brother MFC-L2740DW series Printer"
  err = win32api.ShellExecute(0, "printto", file, f'"{printer_name}"', ".", 0)
  if (err <= 32):
    log(f"Failed to print to f{printer_name}.")
    return
  log(f"Printing to {printer_name}.")

# Run print_fireban everyday at 2pm
log("Started fire ban printing script.")
schedule.every().day.at("14:00").do(print_fireban)
while True:
  # Wait until the next time we need to run it
  t = schedule.idle_seconds()
  if t > 0:
    time.sleep(t)
  # Get and print ban
  schedule.run_pending()
