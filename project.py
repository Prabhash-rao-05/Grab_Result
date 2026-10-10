import os
import sys
import time
import shutil
import requests
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from pytesseract import pytesseract
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import (
    NoAlertPresentException,
    InvalidSessionIdException,
    UnexpectedAlertPresentException
)

# find the link of capcha from source code


def find_src(source_code):
    HtmlCodeInListForm = source_code.split(" ")

    for i in HtmlCodeInListForm:
        if 'src="CaptchaImage.axd?guid=' in i:
            return i[5:-1]

    return None

#  after getting link of captcha image this function download the captcha image


def download_image(url, image_name):
    file_name = image_name
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        return True
    else:
        pass

# read text from image


def read_text(captcha_image):
    # path of tesseract.exe
    path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # image_path = r"./{captcha_image}"
    image_path = captcha_image
    img = Image.open(image_path)
    pytesseract.tesseract_cmd = path_to_tesseract

    # fetch text from image
    text = pytesseract.image_to_string(img)

    # covert text into upper format
    captcha = text.upper()

    # remove spaces
    captcha = captcha.replace(" ", "")

    # delete image
    os.remove(captcha_image)
    return captcha
def get_next_enrollment(filename, prefix, start_number):
    """
    Find the next enrollment number that should be scraped.
    """
    if not os.path.exists(filename):
        return start_number

    highest = start_number - 1

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = line.split(',')

            if not parts:
                continue

            enrollment = parts[0].strip()

            if enrollment.startswith(prefix):
                try:
                    number = int(enrollment[len(prefix):])

                    if number > highest:
                        highest = number

                except ValueError:
                    pass

    return highest + 1

def main():

    i = 1001 # starting rollnumber
    start_enrollment = 1001
    end_enrollment = 1500
    k = 0  # To close the program when all results are found
    print("1. AIML")
    print("2. AIDS")
    print("3. CSE")
    print("4. Civil")
    print("5. Electrical")
    print("6. Mechanical")
    print("7. Electronics")
    branch = input("Enter Branch Number: ")

    # sem = input("Enter semester: ")
    sem = "6"
    print("Semester is:6")

    # When user enter a wrong branch number
    try:
        j = int(branch)
    except ValueError:
        # when branch is wrong
        sys.exit("Values don't match")
    j = int(branch)

    # set roll number
    # Check user's input and set roll number accordingly
    if j == 1:
        en_num = "0103CE23"
        print("Your Starting Roll Number: ", en_num+str(i))
        input("Press Enter")
        filename = f'CE_{sem}thsem_result.csv'
    elif j == 2:
        en_num = "0103CS24"
        print("Your Starting Roll Number: ", en_num+str(i))
        input("Press Enter")
        filename = f'ME_{sem}thsem_result.csv'
    elif j == 3:
        en_num = "0103AD24"
        print("Your Starting Roll Number: ", en_num+str(i))
        input("Press Enter")
        filename = f'CE_{sem}thsem_result.csv'
    elif j == 4:
        en_num = "0103EX24"
        print("Your Starting Roll Number: ", en_num+str(i))
        input("Press Enter")
        filename = f'EX_{sem}thsem_result.csv'
    else:
        # when branch is wrong
        sys.exit("branch do not match")
    # Resume automatically
    i = get_next_enrollment(filename, en_num, i)

    print("Resuming from enrollment:", en_num + str(i))

    # open drive
    # path of chromedriver.exe
    # edge_driver_path = "msedgedriver.exe"
    edge_driver_path = os.path.abspath("msedgedriver.exe")

# Create a Microsoft Edge WebDriver instance
    driver = webdriver.Edge(executable_path=edge_driver_path)

# Set an implicit wait time (in seconds) for element locating
    driver.implicitly_wait(0.5)
    # driver = webdriver.Chrome("chromedriver.exe")
    # driver.implicitly_wait(0.5)
    # link of collage page
    driver.get("http://result.rgpv.ac.in/Result/ProgramSelect.aspx")
    radio = driver.find_element_by_id("radlstProgram_1")
    radio.click()
    print("Current URL:", driver.current_url)

    captcha_elements = driver.find_elements(
    "xpath",
    "//img[contains(@src, 'Captcha')]"
    )

    print("Captcha images found:", len(captcha_elements))

    for element in captcha_elements:
         print("CAPTCHA SRC:", element.get_attribute("src"))
    while i<=end_enrollment:
        # set rollnumber

        en_num_format = en_num+str(i)
        # when roll number limit is reached
        if k > 9:
            break
        print(en_num+str(i))

        # file name of captcha image
        image = en_num_format+'.jpg'

        # get page source
        s = driver.page_source
        print("Current URL:", driver.current_url)

        with open("page_source.html", "w", encoding="utf-8") as f:
           f.write(s)

        print("Page source saved to page_source.html")

        # functions
        link = find_src(s)

        if link is None:
          print("CAPTCHA not found. Refreshing page...")
          driver.refresh()
          time.sleep(1)
          continue

        url = f'http://result.rgpv.ac.in/result/{link}'
        download_image(url, image)
        captcha = read_text(image)

        # fill data like enrollment number, semester, captcha.
        Select(driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_drpSemester"]')).select_by_value(sem)  # select 4th sem
        time.sleep(2)
        driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]').send_keys(captcha)  # type captcha
        time.sleep(1)
        driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_txtrollno"]').send_keys(en_num_format)  # type roll number
        time.sleep(2)
        driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]').send_keys(Keys.ENTER)  # press enter

        # handel alert, when captcha is wrong and enrollment number is not found
        time.sleep(2)
        alerttext = ""

        try:
           alert = driver.switch_to.alert
           alerttext = alert.text
           print("RGPV Alert:", alerttext)
           alert.accept()
           time.sleep(0.5)

        except NoAlertPresentException:
            pass

        except UnexpectedAlertPresentException:
            try:
              alert = driver.switch_to.alert
              alerttext = alert.text
              print("RGPV Alert:", alerttext)
              alert.accept()
            except NoAlertPresentException:
              pass
        s = driver.page_source

        # when captcha is correct featch from result page
        if "Total Credit" in s:
            soup = BeautifulSoup(s, 'html.parser')
            roll_nu = soup.find(
                'span', id='ctl00_ContentPlaceHolder1_lblRollNoGrading').get_text()
            name = soup.find(
                'span', id='ctl00_ContentPlaceHolder1_lblNameGrading').get_text()
            sgpa = soup.find(
                'span', id='ctl00_ContentPlaceHolder1_lblSGPA').get_text()
            cgpa = soup.find(
                'span', id='ctl00_ContentPlaceHolder1_lblcgpa').get_text()
            result = soup.find(
                'span', id='ctl00_ContentPlaceHolder1_lblResultNewGrading').get_text()
            name = name.replace(" ", "")
            name = name.replace("\n", " ")
            information = [roll_nu, ",", name,
                           ",", sgpa, ",", cgpa, ",", result, "\n"]

            # write result in CSV file
            # Check whether this enrollment already exists
            duplicate = False

            if os.path.exists(filename):
                with open(filename, 'r') as f:
                  for line in f:
                     if line.startswith(roll_nu + ","):
                        duplicate = True
                        break

            if not duplicate:
                with open(filename, 'a') as f:
                    f.writelines(information)

                print("Successful - saved:", roll_nu)
            else:
                 print("Duplicate skipped:", roll_nu)
            print("succesful")
            # Press reset information button
            driver.find_element_by_xpath(
                '//*[@id="ctl00_ContentPlaceHolder1_btnReset"]').send_keys(Keys.ENTER)
            i = i+1  # increment in enrollment number
            k = 0
        # when captcha is wrong and enrollment number is not found
        else:
            if "Result" in alerttext:  # enrollment number is not found
                driver.find_element_by_xpath(
                    '//*[@id="ctl00_ContentPlaceHolder1_btnReset"]').send_keys(Keys.ENTER)  # press reset button
                i = i+1  # increment in enrollment number
                k = k+1
                print("enrollment number is not found")
            else:  # when captcha is wrong clear input field
                driver.find_element_by_xpath(
                    '//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]').clear()  # clear captcha
                driver.find_element_by_xpath(
                    '//*[@id="ctl00_ContentPlaceHolder1_txtrollno"]').clear()  # clear roll number
                print("captcha is wrong")
            continue


# main function
if __name__ == "__main__":
    main()
