import sys
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    # Side Note: the chrome options below were added so that the window doesn't close by itself
    chrome_options = Options()
    # stop Chrome window from closing after finishing running the code
    chrome_options.add_experimental_option("detach", True)

    # stop the message that appears under the URL stating that Chrome is being run by a bot
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # remove the 'Save Password' popup when logging in to an account
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    chrome_options.add_experimental_option("prefs", prefs)

    chrome_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.maximize_window()
    driver.get("https://recreationcenter.ca/login")
    print("=================The 'setup_driver' function was executed=================")
    driver.implicitly_wait(15)
    return driver


def login(driver):
    # input email
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "account-login-email")))
    email_input = driver.find_element(By.ID, "account-login-email")
    email_input.send_keys("example@hotmail.com")

    # input password
    password_input = driver.find_element(By.ID, "account-login-password")
    password_input.send_keys("Qwerty123456")
    password_input.send_keys(Keys.RETURN)
    print("=================The 'login' function was executed=================")


def click_drop_ins_button(driver):
    drop_ins_button = driver.find_element(By.XPATH, "//span[text()='Drop in Bookings']")
    drop_ins_button.click()
    print("=================The 'click_drop_ins_button' function was executed=================")


def view_timetable(driver):
    select_rec_center = driver.find_element(By.XPATH, "//input[@class='select2-search__field']")
    select_rec_center.click()

    # select Facility input (i.e. Recreation Centre)
    driver.find_element(By.XPATH, "//li[text()='Recreation Centre']").click()

    # select Category input (i.e. Lane Swim)
    driver.find_element(By.XPATH, "//label[text()='Lane Swim']").click()

    # select Activities input (i.e. RC Lane Swim)
    driver.find_element(By.XPATH, "//label[text()='RC Lane Swim']").click()

    # select View Timetable button
    driver.find_element(By.XPATH, "//span[text()='View Timetable']").click()
    print("=================The 'view_timetable' function was executed=================")


def select_next_week_date_fn(driver, number_of_days_from_today):
    # click the date icon to pull up calendar
    date_picker_icon = driver.find_element(By.XPATH, "//button[@class='Zebra_DatePicker_Icon']")
    date_picker_icon.click()

    # get current month
    current_month = driver.find_element(By.XPATH, "//td[@class='dp_caption']").get_attribute("innerHTML")

    # get today's date as a string then convert it to int and add 7 to it to get next week's date
    current_date_str = driver.find_element(By.XPATH, "//td[contains(@class, 'dp_current dp_selected')]").get_attribute("innerHTML")
    current_date = int(current_date_str)
    next_week_date = str(current_date + number_of_days_from_today)

    if is_month_thirty_days(current_month) and current_date >= 24:  # for Months that are 30 days in length
        move_to_next_month_then_select_date(driver, next_week_date)
    elif is_february(current_month) and current_date >= 22:  # for February that is 28 days in length
        move_to_next_month_then_select_date(driver, next_week_date)
    else:  # for Months that are 31 days in length
        if current_date >= 25:
            move_to_next_month_then_select_date(driver, next_week_date)
        else:
            clickable_dates = driver.find_elements(By.XPATH, f"//td[text()='{next_week_date}']")
            for date in clickable_dates:
                is_date_clickable = "dp_disabled" not in date.get_attribute("class")
                if is_date_clickable:
                    date.click()
    print("=================The 'select_next_week_date_fn' function was executed=================")


def is_month_thirty_days(current_month):
    if "April" or "June" or "September" or "November" in current_month:
        return True
    else:
        return False


def is_february(current_month):
    if "February" in current_month:
        return True
    else:
        return False


def move_to_next_month_then_select_date(driver, next_week_date):
    # move to next month by clicking the Next button
    driver.find_element(By.XPATH, "//td[@class='dp_next']")
    # then click next week's date
    clickable_dates = driver.find_elements(By.XPATH, f"//td[text()='{next_week_date}']")
    for date in clickable_dates:
        if "dp_disabled" not in date.get_attribute("class"):
            date.click()


def select_time(driver, swim_type, swim_time):
    try:
        # select the workout's time and type
        time_element = driver.find_element(By.XPATH, f"//div[@data-test-id='bookings-timetable-timetableitem-lane-swim---{swim_type}-pool---60min-{swim_time}']/div[1]/div[3]")
    except exceptions.NoSuchElementException as e:
        print(e.msg)
        print(f"Error: The combination of time and the type of activity selected (i.e. {swim_type} swim at {swim_time} o'clock) is not offered on the selected day.")
        driver.quit()
        sys.exit()

    time_element_children = time_element.find_elements(By.XPATH, "./child::*")
    for child in time_element_children:
        if child.is_displayed():
            displayed_icon_element = child

    # check if time selected is full, added to basket, or already enrolled in it
    is_full_space = False
    is_added_to_basket = False
    is_enrolled = False
    icon_class_attribute_value = displayed_icon_element.find_element(By.CSS_SELECTOR, "i").get_attribute("class")
    if "fas fa-user-plus fa-3x" in icon_class_attribute_value:
        is_full_space = True
    elif "fa fa-check fa-3x" == icon_class_attribute_value:
        is_added_to_basket = True
    elif "fa fa-clipboard-check fa-3x" == icon_class_attribute_value:
        is_enrolled = True

    # if time selected is available for booking, book it
    if not is_enrolled and not is_added_to_basket and not is_full_space:
        print("The time selected is available to book.\nBooking Now...")
        displayed_icon_element.click()  # book the time selected
    else:
        if is_enrolled:
            print("YOU ARE ALREADY ENROLLED IN THE TIME SELECTED!")
            driver.quit()
            sys.exit()
        elif is_added_to_basket:
            print("TIME SELECTED IS ALREADY ADDED TO CART!")
            driver.quit()
            sys.exit()
        elif is_full_space:
            print("TIME SELECTED IS FULLY BOOKED!")
            driver.quit()
            sys.exit()
        else:
            print("THERE'S SOMETHING WRONG!!!!")
            driver.quit()
            sys.exit()
    print("=================The 'select_time' function was executed=================")


def buy_now_button(driver):
    # click Buy now button
    buy_now = driver.find_element(By.XPATH, "//span[text()='Buy now']")
    buy_now.click()
    print("=================The 'buy_now_button' function was executed=================")


def continue_button(driver):
    # click Continue button
    continue_btn = driver.find_element(By.XPATH, "//span[text()='Continue']")
    continue_btn.click()
    print("=================The 'continue_button' function was executed=================")


def click_accept_terms_checkbox(driver):
    # accept terms and conditions
    accept_checkbox = driver.find_element(By.XPATH, "//span[text()='I accept the terms & conditions *']")
    accept_checkbox.click()
    print("=================The 'click_accept_terms_checkbox' function was executed=================")


def confirm_choice_button(driver):
    # click on the Confirm button
    confirm_btn = driver.find_element(By.XPATH, "//span[text()='Confirm']")
    confirm_btn.click()
    print("=================YOUR SPOT WAS SUCCESSFULLY BOOKED=================")
    print("=================The 'confirm_choice_button' function was executed=================")


def main():
    driver = setup_driver()  # setup appropriate driver for Chrome Website
    login(driver)  # login using username and password
    click_drop_ins_button(driver)  # click the Drop-ins button
    view_timetable(driver)  # select which rec center you want and then click the view timetable button
    select_next_week_date_fn(driver, 7)  # open calendar and retrieve current date
    select_time(driver, "competition", "1200")  # select the time you want to book
    buy_now_button(driver)  # click the Buy now button
    continue_button(driver)  # click the Continue button
    click_accept_terms_checkbox(driver)  # accept terms and conditions checkbox
    confirm_choice_button(driver)  # finally, click the Confirm button to finish
    driver.quit()


if __name__ == '__main__':
    main()
