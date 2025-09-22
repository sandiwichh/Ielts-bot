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
import tempfile
import shutil
import time # Import time for potential delays

# Uncomment the following lines if you want to use webdriver_manager
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service

class IeltsTestfinder:

  def __init__(self, driver, city, day, month, year, receiver_emails, screenshot_filename):
    self.driver = driver
    self.wait = WebDriverWait(self.driver, 30) # Increased wait time for robustness
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
     # Dynamically create the city_button XPath based on self.city
     "city_button": (By.XPATH, f"//div[@aria-labelledby='cityDropDown']//button[normalize-space()='{self.city}']"),
     "select_date_button": (By.XPATH, "/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-type/div/div/div/div[2]/button"),
     "date_button": (By.XPATH,f"//div[@role='gridcell' and not(contains(@class, 'disabled')) and @aria-label='{day}-{month}-{year}']"),
     "find_session_button": (By.XPATH,"/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-date/div/div/div[2]/div[3]/button")
    }
  
  def click_element(self, button_key):
    try: 
      # Wait for any potential loader to disappear
      loader_locator = (By.CLASS_NAME, "loader")
      # Check if loader elements are present before waiting for invisibility
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
    except TimeoutError:
      print(f"Failed to find or click '{button_key}'. The element was not clickable within the timeout period.")
      return False
    except Exception as e:
      print(f"An unexpected error occurred while clicking '{button_key}': {e}")
      # Optional: Take a screenshot on error for debugging
      self.driver.save_screenshot(f"error_{button_key}.png")
      return False
  
  def find_test(self):
    print("Starting IELTS test finder workflow...")
    self.driver.get("https://bxsearch.ielts.idp.com/wizard")
    
    # Add a small delay after page load to allow elements to render
    time.sleep(2)

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
    # You might need to add a small delay here if the date picker takes time to load
    time.sleep(1) 
    if not self.click_element("select_date_button"): return False
    if not self.click_element("date_button"): return False
    if not self.click_element("find_session_button"): return False
    
    print("IELTS test finder workflow completed up to session finding.")
    return True
  
  def take_screenshot(self):
        """Takes a screenshot and returns True if successful."""
        print("Attempting to take screenshot...")
        try:
            # Wait for any potential loader to disappear before taking a screenshot
            loader_locator = (By.CLASS_NAME, "loader")
            if self.driver.find_elements(*loader_locator):
                print("Loader found before screenshot. Waiting...")
                self.wait.until(EC.invisibility_of_element_located(loader_locator))
            
            self.driver.save_screenshot(self.screenshot_filename)
            print(f"Screenshot saved as {self.screenshot_filename}")
            return True
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return False
  
  def send_email(self):
     smtp_server = "smtp.gmail.com"
     smtp_port = 587
     sender_email = "shahrestaniali133@gmail.com" # Replace with your sender email
     sender_password = os.environ.get("SENDER_PASSWORD")
     
     if not sender_password:
         print("Error: SENDER_PASSWORD environment variable not set.")
         return False

     for email in self.receiver_emails:
        msg = MIMEMultipart()
        msg["Subject"] = "IELTS Test Date is Available"
        msg["From"] = sender_email
        msg["To"] = email
        msg.attach(MIMEText("Available IELTS test sessions list."))

        # Attach the screenshot
        try:
            with open(self.screenshot_filename, "rb") as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(self.screenshot_filename))
            msg.attach(image)
        except FileNotFoundError:
            print(f"Error: Screenshot file '{self.screenshot_filename}' not found. Cannot attach to email.")
            return False
        except Exception as e:
            print(f"Error attaching screenshot to email: {e}")
            return False

        try:
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Email sent successfully to {email}!") 
            # After sending the email, you might want to delete the screenshot if it's no longer needed
            # os.remove(self.screenshot_filename) 
            return True
        except smtplib.SMTPAuthenticationError:
            print(f"Failed to send email to {email}: Authentication error. Check sender email and password.")
            return False
        except smtplib.SMTPRecipientsRefused:
            print(f"Failed to send email to {email}: Recipient refused. Check recipient email address.")
            return False
        except Exception as e:
            print(f"Failed to send email to {email}. Error: {e}")
            return False
     return True # Return True if all emails were attempted to be sent

def main():
   # Use a context manager for the temporary directory to ensure cleanup
   with tempfile.TemporaryDirectory(prefix="chrome-profile-") as profile_dir:
       print(f"Using temporary Chrome profile directory: {profile_dir}")
       options = Options()
       # options.add_argument("--headless") # Uncomment if you want to run in headless mode
       options.add_argument("--no-sandbox") # Recommended for Docker/CI environments
       options.add_argument("--disable-dev-shm-usage") # Recommended for Docker/CI environments
       options.add_argument(f"--user-data-dir={profile_dir}")
       options.add_argument("--no-first-run")
       options.add_argument("--no-default-browser-check")
       options.add_argument("--disable-gpu") # Often needed for headless
       options.add_argument("--window-size=1920,1080") # Ensure a good window size for screenshots

       driver = None # Initialize driver to None
       try:
           # Uncomment the following lines if you want to use webdriver_manager
           # service = Service(ChromeDriverManager().install())
           # driver = webdriver.Chrome(service=service, options=options)
           driver = webdriver.Chrome(options=options)
           driver.maximize_window() # Maximize window for better screenshots in non-headless mode

           city = "Mashhad"
           # It's better to pass the date components as strings if the XPath expects a string format
           day = 30
           month = "September" # Use full month name as per aria-label format
           year = 2025
           receiver_emails = ["shahrestaniali3@gmail.com"] # Ensure this is a valid email for testing
           screenshot_filename = os.path.join(profile_dir, "ielts_test_sessions.png") # Save screenshot in temp dir
           
           finder = IeltsTestfinder(driver, city, day, month, year, receiver_emails, screenshot_filename)
           
           if finder.find_test():
              if finder.take_screenshot():
                 if finder.send_email():
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
           # Optional: Take a screenshot if an unexpected error occurs before driver.quit()
           if driver:
               try:
                   driver.save_screenshot("final_error_state.png")
                   print("Screenshot of final error state saved as final_error_state.png")
               except Exception as scr_e:
                   print(f"Could not save error screenshot: {scr_e}")
       finally:
           if driver:
               driver.quit()
               print("WebDriver session closed.")
           # The TemporaryDirectory context manager will handle cleaning up profile_dir

if __name__ == "__main__":
   main()
