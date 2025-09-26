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
import argparse


def check_loader():
    loader_locator = (By.CLASS_NAME, "loader")
    loader_elements = driver.find_elements(*loader_locator)
    if len(loader_elements) > 0:
        print("Loader found. Waiting for it to disappear...")
        wait.until(EC.invisibility_of_element_located(loader_locator))
        print("Loader has disappeared.")


def click_element(button_key):
    try:
        check_loader()
        button = wait.until(EC.element_to_be_clickable(buttons[button_key]))
        button.click()
        print(f"Successfully clicked '{button_key}'.")
        return True
    except TimeoutError:
        print(
            f"Failed to find or click '{button_key}'. The element was not clickable within the timeout period."
        )
        return False
    except Exception as e:
        print(f"An unexpected error occurred while clicking '{button_key}': {e}")
        return False


def search_month():
    check_loader()
    target_month_locator = (
        By.XPATH,
        f"//div[contains(@class, 'ngb-dp-month-name') and normalize-space()='{month_text} 2025']",
    )
    found_elements = driver.find_elements(*target_month_locator)

    if found_elements:
        print("Success! The target month header was found.")
        return True
    else:
        # This block runs if find_elements returned an empty list []
        print("The target month is not yet visible. Clicking 'Next'.")
        next_month_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next month']"))
        )
        next_month_button.click()
        print(f"Successfully clicked next_month.")
        return False


def search_date():
    try:

        for i in range(31):
            print(i + 1)
            day_it = i + 1
            all_days_locator = (
                By.XPATH,
                f"//div[@role='gridcell' and not(contains(@class, 'disabled')) and @aria-label='{day_it}-{month}-{year}']",
            )
            find_element = driver.find_elements(*all_days_locator)
            if find_element:
                day_range.append(i + 1)
                print("Availble dau Found")
            else:
                print("No available days were found in the current month view.")
        print(day_range)
        if day in day_range:
            print("Desire date available!")
            check_loader()
            # if not self.click_element("desire_day_button"): return False
            desire_button = (
                By.XPATH,
                f"//div[@role='gridcell' and not(contains(@class, 'disabled')) and @aria-label='{day}-{month}-{year}']",
            )
            button = wait.until(EC.element_to_be_clickable(desire_button))
            button.click()
            if not click_element("find_session_button"):
                return False
            global screenshot_filename
            screenshot_filename = "ielts_test_sessions.png"
            return True
        elif len(day_range) != 0:
            screenshot_filename = ""
            print("Desire date not available!")
            return True

        else:
            return False

    except Exception as e:
        print(f"An error occurred while trying to find an available day: {e}")
        return False


def find_test():
    driver.get("https://bxsearch.ielts.idp.com/wizard")
    if not click_element("accept_cookies"):
        return False
    if not click_element("find_element"):
        return False
    if not click_element("academic_button"):
        return False
    if not click_element("on_computer_button"):
        return False

    # Sequence for country and city selection
    if not click_element("country_dropdown_button"):
        return False
    if not click_element("iran_button"):
        return False
    if not click_element("city_dropdown_button"):
        return False
    if not click_element("city_button"):
        return False

    # Sequence for date selection
    if not click_element("select_date_button"):
        return False

    for _ in range(3):
        if search_month():
            if not search_date():
                print(f"No available days in the {month_text}")
                return False
            else:
                return True
        else:
            print("Retrying...")
            pass


# twfzlbwpkcjnsbou
def take_screenshot():
    try:
        check_loader()
        if screenshot_filename != "":
            driver.save_screenshot(screenshot_filename)
            print(f"Screenshot saved as {screenshot_filename}")
            return True
        else:
            return True
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return False


def send_email(sender_password, receiver_emails):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "shahrestaniali133@gmail.com"

    if not sender_password:
        print("Error: Password was not provided.")
        return False

    for email in receiver_emails:
        msg = MIMEMultipart()
        msg["Subject"] = "IELTS Test Date is Available"
        msg["From"] = sender_email
        msg["To"] = email
        msg.attach(MIMEText(f"IELTS test sessions are available.\n"))

        try:
            if screenshot_filename != "":
                with open(screenshot_filename, "rb") as f:
                    img_data = f.read()
                image = MIMEImage(img_data, name=os.path.basename(screenshot_filename))
                msg.attach(image)
            else:
                for day in day_range:
                    msg.attach(MIMEText(f"{day} {month_text} is available.\n"))
        except FileNotFoundError:
            print(f"Error: Screenshot file '{screenshot_filename}' not found.")
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
    parser = argparse.ArgumentParser(description="IELTS Test Finder Bot")
    parser.add_argument(
        "--password", required=True, help="The sender's email app password."
    )
    args = parser.parse_args()
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    service = Service(ChromeDriverManager().install())
    global driver
    driver = webdriver.Chrome(service=service, options=options)
    print("WebDriver session created successfully in headless mode.")
    global wait
    wait = WebDriverWait(driver, 30)
    city = "Mashhad"
    global day
    day = 14
    global day_range
    day_range = []
    global month
    month = 11
    global month_text
    month_text = "November"
    global year
    year = 2025
    receiver_emails = ["shahrestaniali3@gmail.com"]
    global buttons
    buttons = {
        "accept_cookies": (By.ID, "onetrust-accept-btn-handler"),
        "find_element": (By.CSS_SELECTOR, ".option > a:nth-child(1)"),
        "academic_button": (
            By.XPATH,
            "//li[@datatracking-id='wizard-card-IELTS_Academic']/a",
        ),
        "on_computer_button": (
            By.XPATH,
            "//li[@datatracking-id='wizard-card-IELTS_on_Computer']/a",
        ),
        "country_dropdown_button": (By.XPATH, "//*[@id='countryDropDown']"),
        "iran_button": (
            By.XPATH,
            "//button[normalize-space()='Iran (Islamic Republic of)']",
        ),
        "city_dropdown_button": (By.XPATH, "//*[@id='cityDropDown']"),
        "city_button": (
            By.XPATH,
            f"//div[@aria-labelledby='cityDropDown']//button[normalize-space()='{city}']",
        ),
        "select_date_button": (
            By.XPATH,
            "/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-type/div/div/div/div[2]/button",
        ),
        "desire_day_button": (
            By.XPATH,
            f"//div[@role='gridcell' and not(contains(@class, 'disabled')) and @aria-label='{day}-{month}-{year}']",
        ),
        "find_session_button": (
            By.XPATH,
            "/html/body/app-root/main/app-new-manage-booking/div/div[1]/app-new-test-date/div/div/div[2]/div[3]/button",
        ),
    }

    if find_test():
        if take_screenshot():
            if send_email(args.password, receiver_emails):
                print("Email workflow completed successfully.")
            else:
                print("Email workflow failed.")
        else:
            print("Screenshot failed, skipping email.")
        print("Workflow completed successfully.")
    else:
        print("Workflow failed. Check logs for details.")

    driver.quit()
    print("WebDriver session closed.")


if __name__ == "__main__":
    main()
