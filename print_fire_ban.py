#!/usr/bin/env python3

# Download the current nova scotia fire ban at 2pm everyday
# Orchard Queen Motel and RV Park, Aidan Carey, June 8th 2024

import os
import time
import win32api
import win32print
import schedule
from selenium import webdriver
from PIL import Image
from io import BytesIO

def fireban_png(file):
  url = "https://novascotia.ca/burnsafe/"
  # Start Firefox in headless mode
  options = webdriver.firefox.options.Options()
  options.add_argument("--headless")
  driver = webdriver.Firefox(options=options)
  
  # Open firefox and set window width/height
  driver.get(url)
  page = driver.find_element("id", "burn-data-content")
  size = page.size

  window_width = driver.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
  window_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
  driver.set_window_size(window_width, window_height)
  
  # Get content as a png
  png = driver.get_screenshot_as_png()
  
  table_legend = driver.find_element("class name", "table-legend")
  # Not showing Antigonish County
  antigonish_county = driver.find_element("id", "Antigonish-County")
  
  table_location = table_legend.location
  county_location = antigonish_county.location

  # Crop then save to file  
  img = Image.open(BytesIO(png))

  left = table_location["x"] - 30
  top = table_location["y"]
  right = table_location["x"] + size["width"]
  bottom = county_location["y"]
  img = img.crop((left, top, right, bottom))
  
  img = img.resize((595, 842)) # A4 at 72dpi
  
  #img.show()
  img.save(file)
  
  # Exit Firefox
  driver.quit()

# Get the fire ban and print it to the default printer
def print_fireban():
  # Save NS fire ban website as a png
  file = "fireban.png"
  fireban_png(file)
  print(f"Saved to {file}")
  
  # Print PDF to printer (Windows specific)
  printer_name = "Brother MFC-L2740DW series Printer"
  win32api.ShellExecute(0, "printto", file, f'"{printer_name}"', ".", 0)
  print(f"Printing to {printer_name}")

# Run print_fireban() everyday at 2pm
print_fireban() # Test
"""
schedule.every().day.at("14:00").do(print_fireban)
while True:
  schedule.run_pending()
  time.sleep(60)
"""
