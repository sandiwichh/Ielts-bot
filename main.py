# main.py

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import time
import argparse # ADD THIS IMPORT for command-line arguments
import calendar # ADD THIS IMPORT to convert month number to name

class IeltsTestfinder:
  def __init__(self, driver, city, day, month, year, receiver_emails, screenshot_filename):
    self.driver = driver
    self.wait = WebDriverWait(self.driver, 30)
    self.city = city
    self.day = day
    self.month = month
    self.year = year
    self.screenshot_filename = screenshot_filename
    self.receiver_emails = receiver_emails
    self.buttons ={
     "accept_cookies" : (By.ID, "onetrust-accept-btn-handler"),
     "find_element": (By.CSS_SELECTOR, ".option > a:nth-child(1)"),
     "academic_button": (By.XPATH, "//li[@datatracking-id='wizard-card-IELTS_Academic']/a"),
     "on_computer_button": (By.XPATH, "//li[@datatracking-id='wizard-card-IELTS_on_Computer']/a"),
     "country_dropdown_button": (By.XPATH, "//*[@id='countryDropDown']"),
     "iran_button": (By.XPATH, "//button[normalize-space()='Iran (Islamic Republic of)']"),
     "city_dropdown_button": (By.XPATH, "//*[@id='cityDropDown']"),
     "city_button": (By.XPATH, f"//div[@aria-labelledby='cityDropDown']//button[normalize-space()='{self.city}']"),
     "select_date_button": (By.XPATH, "//div[contains(@class, 'primary-button-container')]//button[normalize-space()='Select test date']"),
     # MODIFIED: XPath is now more reliable using the month name
     "date_button": (By.XPATH,f"//div[@role='gridcell' and not(contains(@class, 'disabled')) and @aria-label='{self.day} {self.month} {self.year}']"),
     "find_session_button": (By.XPATH,"/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-date/div/div/div[2]/div[3]/button")
    }

  def click_element(self, button_key):
    try:
      loader_locator = (By.CLASS_NAME, "loader")
      if self.driver.find_elements(*loader_locator):
          print("Loader found. Waiting for it to disappear...")
          self.wait.until(EC.invisibility_of_element_located(loader_locator))
          print("Loader has disappeared.")

      button = self.wait.until(
        EC.element_to_be_clickable(self.buttons[button_key])
       )
      button.click()
      print(f"Successfully clicked '{button_key}'.")
      return True
    except Exception as e:
      print(f"Failed to find or click '{button_key}'. Error: {e}")
      self.driver.save_screenshot(f"error_clicking_{button_key}.png")
      return False

  def find_test(self):
    print("Starting IELTS test finder workflow...")
    self.driver.get("https://bxsearch.ielts.idp.com/wizard")
    time.sleep(2)

    if not self.click_element("accept_cookies"): return False
    if not self.click_element("find_element"): return False
    if not self.click_element("academic_button"): return False
    if not self.click_element("on_computer_button"): return False
    if not self.click_element("country_dropdown_button"): return False
    if not self.click_element("iran_button"): return False
    if not self.click_element("city_dropdown_button"): return False
    if not self.click_element("city_button"): return False
    time.sleep(1)
    if not self.click_element("select_date_button"): return False
    if not self.click_element("date_button"): return False
    if not self.click_element("find_session_button"): return False

    print("IELTS test finder workflow completed up to session finding.")
    return True

  def take_screenshot(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loader")))
            self.driver.save_screenshot(self.screenshot_filename)
            print(f"Screenshot saved as {self.screenshot_filename}")
            return True
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return False

  # MODIFIED: The method now accepts the password as an argument
  def send_email(self, sender_password):
     smtp_server = "smtp.gmail.com"
     smtp_port = 587
     sender_email = "shahrestaniali133@gmail.com"
     # REMOVED: No more hardcoded password here
     # sender_password = "twfz lbwp kcjn sbou"

     if not sender_password:
         print("Error: Password was not provided.")
         return False

     for email in self.receiver_emails:
        msg = MIMEMultipart()
        msg["Subject"] = "IELTS Test Date is Available"
        msg["From"] = sender_email
        msg["To"] = email
        msg.attach(MIMEText("An IELTS test session is available. See the attached screenshot for details."))

        try:
            with open(self.screenshot_filename, "rb") as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(self.screenshot_filename))
            msg.attach(image)
        except FileNotFoundError:
            print(f"Error: Screenshot file '{self.screenshot_filename}' not found.")
            return False

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Email sent successfully to {email}!")
            return True
        except Exception as e:
            print(f"Failed to send email to {email}. Error: {e}")
            return False
     return True

def main():
   # ADD THIS BLOCK to parse command-line arguments
   parser = argparse.ArgumentParser(description="IELTS Test Finder Bot")
   parser.add_argument("--password", required=True, help="The sender's email app password.")
   args = parser.parse_args()

   options = Options()
   options.add_argument("--headless=new")
   options.add_argument("--no-sandbox")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--disable-gpu")
   options.add_argument("--window-size=1920,1200")

   driver = None
   try:
       service = Service(ChromeDriverManager().install())
       driver = webdriver.Chrome(service=service, options=options)
       print("WebDriver session created successfully in headless mode.")

       city = "Mashhad"
       day = 30
       month = 9
       year = 2025
       receiver_emails = ["shahrestaniali3@gmail.com"]
       screenshot_filename = "ielts_test_sessions.png"

       finder = IeltsTestfinder(driver, city, day, month, year, receiver_emails, screenshot_filename)

       if finder.find_test():
          if finder.take_screenshot():
             # MODIFIED: Pass the password from the argument into the method
             if finder.send_email(args.password):
                print("Email workflow completed successfully.")
             else:
                print("Email workflow failed.")
          else:
              print("Screenshot failed, skipping email.")
          print("Workflow completed successfully.")
       else:
          print("Workflow failed. Check logs for details.")

   except Exception as e:
       print(f"An error occurred during the Selenium workflow: {e}")
       if driver:
           driver.save_screenshot("final_error_state.png")
   finally:
       if driver:
           driver.quit()
           print("WebDriver session closed.")

if __name__ == "__main__":
   try:
       from webdriver_manager.chrome import ChromeDriverManager
   except ImportError:
       print("Error: webdriver-manager is not installed.")
       print("Please install it using: pip install webdriver-manager")
       exit(1)
   main()
