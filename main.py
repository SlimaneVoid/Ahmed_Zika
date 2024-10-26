import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Configuration
url = 'https://phoneauth.plaync.com/signup?ticket_id=phoneauth_session_cache_de623d69-704e-45ad-9d23-d256433818e2&return_url=https%253A%252F%252Fid.plaync.com%252Fsignup%252Fphoneauthwebproc%253Fagreement_session%253Dagreement_session_cache_cb30d089-3a4c-446f-a740-9a77e516c288%2526ticket_id%253Dphoneauth_session_cache_de623d69-704e-45ad-9d23-d256433818e2'
num_input_classname = "input-tel__input"
proxy = 'http://67.43.227.227:15117'
chrome_driver_path = 'C:\\Users\\Slimane\\Desktop\\chrome-win64\\chromedriver.exe'  # Path to your ChromeDriver


try:
    with open('phone_numbers.txt', 'r') as file:
        numbers = [line.strip() for line in file]
except FileNotFoundError:
    print("Error: The phone_numbers.txt file was not found.")
    numbers = []

# Function to interact with the page
def interact_with_page(number):
    try:
        options = webdriver.ChromeOptions()
        #options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Chrome()

        driver.get(url)
        print(f"Opened URL: {driver.current_url}")

        time.sleep(5)  # Wait for the page to load

        driver.execute_script("""
            var firstEl = document.querySelector('.input-country-selector');
            if (firstEl) {
                firstEl.classList.add("has-list-opened");
                firstEl.classList.add("is-focused");

                var secondEl = document.querySelector('.country-selector__list');
                if (secondEl) {
                    secondEl.classList.add("slide-enter-active");
                    secondEl.classList.add("slide-enter-to");
                    secondEl.style.display = "block";

                    var buttonToClick = Array.from(secondEl.querySelectorAll('.country-selector__list__item')).find(function(item) {
                        return item.querySelector('.country-selector__list__item__calling-code').textContent.trim() === "+373";
                    });
                    if (buttonToClick) {
                        secondEl.classList.replace("slide-enter-active", "slide-leave-active");
                        secondEl.classList.replace("slide-enter-to", "slide-leave-to");
                        secondEl.style.display = "none";
                        buttonToClick.click();
                    }
                }
            }
        """)
        
        number_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, num_input_classname))
        )
        number_input.send_keys(number)
        print("Phone number entered.")

 
        send_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Send Verification Code")]'))
        )
        
        send_button.click()
        print("Send Verification Code Button Clicked")

        # Confirm the action
        dialog_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Confirm")]'))
        )
        dialog_button.click()

        # Monitor the timer
        while True:
            try:
                timer_element = WebDriverWait(driver, 16).until(
                    EC.visibility_of_element_located((By.XPATH, '//div[@class="timer"]/p'))
                )
                timer_text = timer_element.text
                print(f"Timer text for browser {number} is: {timer_text}")

                if timer_text == "01:50":
                    second_button = WebDriverWait(driver, 18).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn-primary")]//span[text()="Resend"]'))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", second_button)
                    second_button.click()

                    dialog_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Confirm")]'))
                    )
                    dialog_button.click()
                    
                    
                    #break  # Exit after resend
            except TimeoutException:
                print("Timer element not found.")
                #break  # Exit loop if the timer cannot be found

    except Exception as e:
        print(f"Error interacting with page for number {number}: {e}")
    finally:
        #driver.quit()
        #print(f"Browser closed for number {number}.")
        pass

# Create and start a thread for each number
threads = []
for number in numbers:
    thread = threading.Thread(target=interact_with_page, args=(number,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("All browsers closed. Program finished.")
