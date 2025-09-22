from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

class IeltsTestfinder:

  def __init__(self, driver, city, day, month, year, receiver_emails, screenshot_filename):
    self.driver = driver
    self.wait = WebDriverWait(self.driver, 20)
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
     "city_button": (By.XPATH,"//div[@aria-labelledby='cityDropDown']//button[normalize-space()='Mashhad']"),
     "select_date_button": (By.XPATH, "/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-type/div/div/div/div[2]/button"),
     "date_button": (By.XPATH,f"//div[@role='gridcell' and not(contains(@class, 'disabled')) and @aria-label='{day}-{month}-{year}']"),
     "find_session_button": (By.XPATH,"/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-date/div/div/div[2]/div[3]/button")
    }
  
  def click_element(self, button_key):
    try: 
      loader_locator = (By.CLASS_NAME, "loader")
      loader_elements = self.driver.find_elements(*loader_locator)
      if len(loader_elements) > 0:
        print("Loader found. Waiting for it to disappear...")
        self.wait.until(EC.invisibility_of_element_located(loader_locator))
        print("Loader has disappeared.")
      
      button = self.wait.until(
        EC.element_to_be_clickable(self.buttons[button_key])
       )
      button.click() 
      print(f"Successfully clicked '{button_key}'.") 
      return True
    except TimeoutError:
      print(f"Failed to find or click '{button_key}'. The element was not clickable within the timeout period.")
      return False
    except Exception as e:
      print(f"An unexpected error occurred while clicking '{button_key}': {e}")
      return False
  
  def find_test(self):

    self.driver.get("https://bxsearch.ielts.idp.com/wizard")
    if not self.click_element("accept_cookies"): return False
    if not self.click_element("find_element"): return False
    if not self.click_element("academic_button"): return False
    if not self.click_element("on_computer_button"): return False
        
     # Sequence for country and city selection
    if not self.click_element("country_dropdown_button"): return False
    if not self.click_element("iran_button"): return False
    if not self.click_element("city_dropdown_button"): return False
    if not self.click_element("city_button"): return False
        
    # Sequence for date selection
    if not self.click_element("select_date_button"): return False
    if not self.click_element("date_button"): return False
    if not self.click_element("find_session_button"): return False
    return True
  
  def take_screenshot(self):
        """Takes a screenshot and returns True if successful."""
        try:
            self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loader")))
            self.driver.save_screenshot(self.screenshot_filename)
            print(f"Screenshot saved as {self.screenshot_filename}")
            return True
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return False
  
  def send_email(self):
     smtp_server = "smtp.gmail.com"
     smtp_port = 587
     sender_email = "shahrestaniali133@gmail.com"
     sender_password = os.environ.get("SENDER_PASSWORD")
     receiver_emails = self.receiver_emails
     
     for email in receiver_emails:
        msg = MIMEMultipart()
        msg["Subject"] = "IELTS Test Date is Available"
        msg["From"] = sender_email
        msg["To"] = email
        msg.attach(MIMEText("Available IELTS test sessions list."))

        # Attach the screenshot
        with open(self.screenshot_filename, "rb") as f:
            img_data = f.read()
        image = MIMEImage(img_data, name=self.screenshot_filename)
        msg.attach(image)
        try:
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Email sent successfully {email} !") 
            return True
        except Exception as e:
            print(f"Failed to send email. Error: {e}")
            return False

def main():
   options = Options()
   options.add_argument("--window-size=1920,1080")
   options.add_experimental_option("detach", True)
   driver = webdriver.Chrome(options=options)
   driver.maximize_window()
   city = "Mashhad"
   day = 30
   month = 9
   year = 2025
   receiver_emails = ["shahrestaniali3@gmail.com"]
   screenshot_filename = "ielts_test_sessions.png"
   finder = IeltsTestfinder(driver, city, day, month, year, receiver_emails, screenshot_filename)
   
   if finder.find_test():
      finder.take_screenshot()
      if finder.send_email():
         print("Email workflow completed successfully.")
      else:
         print("Email workflow failed.")    
      print("Workflow completed successfully.")
   else:
      print("Workflow failed. Check logs for details.")
   driver.quit()
if __name__ == "__main__":
   main()