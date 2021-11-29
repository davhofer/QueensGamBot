import subprocess
import sys


import time
import datetime
import re


import getpass

from multiprocessing import Process
subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 



# make sure to download the right version of chromedriver for your version of Google Chrome, and place it in the same location as the script

def get_driver(args):

    chrome_options = Options()
    if '--demo' not in args:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")

    try:
        if '--raspbian' in args:
            subprocess.check_call(['sudo','apt-get','install','chromium-chromedriver'])
            driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options, executable_path="./chromedriver")
    except Exception as e:
        raise Exception("Please make sure that your chromedriver file is the right version for your browser, and is either in the same folder as the python script or specified in PATH.")
        
    return driver

def driver_explicitWait(driver,xpath,condition="clickable",timeout=30):
    # case: condition == "clickable"
    func = EC.element_to_be_clickable
    if condition == "present":
        func = EC.presence_of_element_located
        
    return WebDriverWait(driver, timeout).until(func((By.XPATH, xpath)))


def get_signup_time(lesson_num,driver):

    weekdays = {
        'Mo': 'mon',
        'Di': 'tue',
        'Mi': 'wed',
        'Do': 'thu',
        'Fr': 'fri',
        'Sa': 'sat',
        'So': 'sun'
    }
    
    link = "https://schalter.asvz.ch/tn/lessons/<number>"
    link = link.replace("<number>", lesson_num)

    # goto main lesson page
    driver.get(link)
    
    try:
        elem = driver_explicitWait(driver,"//button[@class='btn btn-default ng-star-inserted']",condition="present")
    except:
        raise Exception("Timeout exception when waiting for lesson page")
        
    # get time when enrollment opens
    html = driver.page_source
    r = "Datum/Zeit.*\n.*"

    ans0 = re.search(r, html)[0]
    weekday = ans0.split(',')[0].split('>')[-1]
    ans = ans0.split(", ")[1].split(" -")[0]

    d = int(ans.split(".")[0]) - 1
    mo = int(ans.split(".")[1])
    y = int(ans.split(".")[2].split(" ")[0])
    h = int(ans.split(".")[2].split(" ")[1].split(":")[0])
    mi = int(ans.split(".")[2].split(" ")[1].split(":")[1])

    t = datetime.datetime(
        year=y, month=mo, day=d, hour=h, minute=mi
    )

    return f'{t.minute} {t.hour} {t.day} {t.month} {t.year} {weekdays[weekday]}'


def asvz_signup(args,lesson_num,username,password):
    if "--help" in args:
        print("---- Help ----")
        print()
        print(
            "use: 'python3 asvz-insc-bot.py' to run the program, after that the user will be prompted to enter the lesson number and his credentials."
        )
        print()
        print("optional arguments:")
        print("--demo               use this argument to display the automated webbrowser while the programm is running.")
        print("--raspbian           to run in production environment on raspberry pi.")
        print("--help               for help.")
        print()
        return


    if (username==None or password==None):
        if ('-u' in args and '-p' in args):
            username = args[args.index('-u')+1]
            username = args[args.index('-p')+1]
        else:
            raise Exception('Username and password must be specified!')


    
    driver = get_driver(args)

    


    def explicitWait(xpath,condition="clickable",timeout=30):
        return driver_explicitWait(driver,xpath,condition,timeout)


    print("Setting up...")
    print()

    link = "https://schalter.asvz.ch/tn/lessons/<number>"
    link = link.replace("<number>", lesson_num)

    # goto main lesson page
    driver.get(link)
    
    try:

        elem = explicitWait("//button[@class='btn btn-default ng-star-inserted']")
    except:
        raise Exception("Timeout exception when waiting for lesson page")
        
    # get time when enrollment opens
    html = driver.page_source
    r = "Datum/Zeit.*\n.*"

    ans = re.search(r, html)[0].split(", ")[1].split(" -")[0]
    d = int(ans.split(".")[0]) - 1
    mo = int(ans.split(".")[1])
    y = int(ans.split(".")[2].split(" ")[0])
    h = int(ans.split(".")[2].split(" ")[1].split(":")[0])
    mi = int(ans.split(".")[2].split(" ")[1].split(":")[1])

    t = datetime.datetime(
        year=y, month=mo, day=d, hour=h, minute=mi, microsecond=200000
    )

    # login
    
    elem.click()

    # SWITCH AAI
    try:
        elem = explicitWait("//button[@name='provider']")
    except:
        raise Exception("Timeout exception when waiting for SWITCH AAI")
        

    elem.click()

    # select institution
    try:
        elem = explicitWait("//input[@id='userIdPSelection_iddtext']")
    except:
        raise Exception("Timeout exception waiting for institution")
        
    elem.click()
    elem.send_keys("ETH Zürich")
    elem.send_keys(Keys.ENTER)

    # enter accoutn data
    try:
        elem = explicitWait("//input[@id='username']")
    except:
        raise Exception("Timeout exception waiting for username input field")
        
    elem.click()
    elem.send_keys(username)

    try:
        elem = explicitWait("//input[@id='password']")
    except:
        raise Exception("Timeout exception waiting for password input field")
        
    elem.click()
    elem.send_keys(password)

    elem.send_keys(Keys.ENTER)




    def f1():
        try:
            explicitWait("//button[@id='btnRegister']",condition="present",timeout=30)
        except:
            raise Exception("Timeout exception: waiting for register button")

    def f2():
        try:
            explicitWait("//button[@name='_eventId_proceed']",condition="present",timeout=30)
        except:
            raise Exception("Timeout exception: waiting for accept button")

    def wait_then_signup(t):
        if datetime.datetime.now() < t:
            print("Waiting for enrollment to open...")
        while datetime.datetime.now() < t:
            time.sleep(0.5)

        elem = explicitWait("//button[@id='btnRegister']")
        elem.click()
        print("Completed successfully, but please check manually if you got a spot.")


    p1 = Process(target=f1)
    p2 = Process(target=f2)

    p1.start()
    p2.start()


    for i in range(20):

        # check if either process has finished, react accordingly
        if not p1.is_alive():
            p1.join()
            p2.terminate()
            p2.join()

            wait_then_signup(t)
            return

        if not p2.is_alive():
            p2.join()
            p1.terminate()
            p1.join()

            elem = explicitWait("//button[@name='_eventId_proceed']")
            elem.click()

            wait_then_signup(t)

        time.sleep(1)
    
    raise Exception("Error: Did not reach signup page!")

            



if __name__ == '__main__':
    # driver code
    args = sys.argv
    lesson_num = input("ASVZ lesson number: ")
    username = input("NETHZ username: ")
    password = getpass.getpass("Password: ")

    asvz_signup(args,lesson_num,username,password)

