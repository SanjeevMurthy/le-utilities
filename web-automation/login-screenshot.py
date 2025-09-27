import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
# IMPORTANT: Replace these placeholder values with the actual values for your website.
WEBSITE_URL = "https://ticket.nagaraholetigerreserve.com/"  # The URL of the login page
USERNAME = "sanjeevmurthy01@gmail.com"
PASSWORD = "Sanju@10"

# --- Main Script ---

def automate_website_interaction():
    """
    This function opens a website, logs in, selects a dropdown value,
    and takes a timestamped screenshot.
    """
    # 1. Initialize the WebDriver
    # This will open a new Chrome window.
    # Make sure you have chromedriver installed and in your PATH.
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        # 2. Open the website
        print(f"Opening website: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)

        # Use WebDriverWait to ensure the page elements are loaded before interacting
        wait = WebDriverWait(driver, 10) # Wait for up to 10 seconds

        # 3. Login to the website
        print("Attempting to log in...")
        # Find the username field and enter the username
        # NOTE: You might need to change By.ID to By.NAME, By.XPATH, etc.
        # Use your browser's developer tools (F12) to inspect the elements and find the correct locator.
        username_field = wait.until(EC.presence_of_element_located((By.ID, "id_email"))) # Replace "username" with the actual ID/Name
        username_field.send_keys(USERNAME)

        # Find the password field and enter the password
        password_field = driver.find_element(By.ID, "id_password") # Replace "password" with the actual ID/Name
        password_field.send_keys(PASSWORD)

        # Find the login button and click it
        login_button = driver.find_element(By.TAG_NAME, "button") # Example: Find button by its tag
        login_button.click()

        print("Login successful. Navigating to the next page.")

        # Wait for the next page to load after login. Look for an element that
        # only appears *after* a successful login.
        wait.until(EC.presence_of_element_located((By.ID, "dashboard-element"))) # Replace with a real element ID from the post-login page

        # 4. Select a value from a dropdown menu
        print("Selecting value from dropdown...")
        # Find the dropdown element
        dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "id_landscape"))) # Replace with the dropdown's actual ID
        
        # Create a Select object to interact with the dropdown
        select = Select(dropdown_element)

        # You can select an option in three ways (uncomment the one you want to use):
        
        # a) By its visible text
        select.select_by_visible_text("Kakanakote (Kabini)") # e.g., "Category 2"
        
        # b) By its value attribute
        # select.select_by_value("option_value_here") # e.g., "cat_2"
        
        # c) By its index (0-based)
        # select.select_by_index(1) # Selects the second option

        print("Value selected.")
        time.sleep(2) # Add a small delay to ensure the page updates after selection

        # 5. Take a screenshot with a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_filename = f"website_screenshot_{timestamp}.png"
        
        driver.save_screenshot(screenshot_filename)
        print(f"Screenshot saved successfully as: {screenshot_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, take a screenshot on error to help debug
        driver.save_screenshot("error_screenshot.png")

    finally:
        # 6. Close the browser
        # This is in a 'finally' block to ensure it runs even if an error occurs.
        print("Closing the browser.")
        driver.quit()

if __name__ == "__main__":
    automate_website_interaction()