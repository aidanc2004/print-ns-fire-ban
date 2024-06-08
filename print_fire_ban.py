#!/usr/bin/env python3

# Download the current nova scotia fire ban at 2pm everyday
# Orchard Queen Motel and RV Park, Aidan Carey, June 8th 2024

import os
import time
import math
import win32api
import win32print
import schedule
from selenium import webdriver
from PIL import Image
from io import BytesIO

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

  #return (img, (new_width, new_height))
  return img

def fireban_png(file):
  url = "https://novascotia.ca/burnsafe/"
  
  # Start Firefox in headless mode
  options = webdriver.firefox.options.Options()
  options.add_argument("--headless")
  driver = webdriver.Firefox(options=options)
  
  # Open firefox and set window width/height
  driver.get(url)
  page = driver.find_element("id", "burn-data-content")
  set_window_size(driver)
  
  # Get content as a png
  png = driver.get_screenshot_as_png()

  # Crop PNG to only needed information
  img = Image.open(BytesIO(png))
  img = crop_img(driver, img, page.size)

  # New image for printer paper (A4 at 150dpi)
  paper = Image.new(mode="RGB", size=(1240, 1754), color=(255, 255, 255))

  # Paste image into the middle of the paper
  img_width, img_height = img.size
  new_width = 1240
  new_height = math.floor(new_width * img_width / img_height)

  img = img.resize((new_width, new_height), Image.LANCZOS)
  paper.paste(img, (0, (math.floor(1754/2)) - (math.floor(new_height/2))))
  
  #paper.show()
  paper.save(file)
  
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
