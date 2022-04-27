# -- coding: utf-8 -

import re
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome(executable_path='C:\Program Files\chromedriver.exe')

def chrome(mode='h'):
    '''A function to instantiate chrome driver

        :arguments: 
            mode: representing either headless (preferred) or browser mode.

        :returns: 
            driver: the driver instantiated.
    '''
    chrome_options = Options()
    # bypass OS security
    chrome_options.add_argument('--no-sandbox')
    # overcome limited resources
    chrome_options.add_argument('--disable-dev-shm-usage')
    # don't tell chrome that it is automated
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # disable images
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)

    if mode == 'h':
        #  Headless mode
        # adding the user-agent argument opens a previously blocked offerup by cloudflare
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

    elif mode == 'b':
        # Browser mode
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        driver = webdriver.Chrome(options=chrome_options)

    else:
        print("Mode is invalid")
        exit(0)

    return driver

    print("Driver Returned")


def iit_madras(driver):
    '''
        Function to scrape professors of IIT Madras

        :arguments:
            driver - a instantiated chrome driver object
        
        :returns:
            arr - an array of arrays in the form [[Institution, name, designation, 
                  phone number, email, specialisation and interest]]
    '''

    arr = []

    # driver.get('http://www.cse.iitm.ac.in/listpeople.php?arg=RmFjdWx0eSExJDAkJA==')
    driver.get('http://www.cse.iitm.ac.in/listpeople.php')
    driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/p/select').click()
    driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/p/select/option[@value="0"]').click()
    driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/p/select[2]').click()
    driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/p/select[2]/option[@value="Faculty!1"]').click()
    time.sleep(5)
    lecturers = driver.find_elements(By.XPATH, '/html/body/div[3]/div[1]/div/table/tbody/tr')[1:]
    for lecturer in lecturers:
        for i in [2,4]:
            details = lecturer.find_element(By.XPATH, f'td[{i}]/span').text
            name = re.findall('.+\n', details)[0]
            email = re.findall('Email.+\n', details)[0]
            phone = re.findall('Phone.+\n', details)[0]
            interest = re.findall('Research Interests.+', details)[0]
            name = name[:-12].strip()
            phone = phone[-5:].strip()
            email = email.replace(' [dot] ', '.').strip()[8:]
            email = email.replace(' [at] ', '@').strip()
            interest = interest[21:].strip()
            arr += [['IIT Madras', name, 'Professor', email, phone, interest]]

    print(arr)
    return arr


def scrape_professors(driver, link, university):
    '''
        A function to scrape professors from a couple of universities

        :arguments:
            driver - an instantiated chrome driver object
        
        :returns:
            arr - an array in the form [[Institution, name, designation, 
                  phone number, email, specialisation and interest]]
    '''

    arr = []
    driver.get(link)
    lecturers = driver.find_elements(By.XPATH, '//div[@id="grid-container"]/div/div')

    # No phone number for lecturers here
    for lecturer in lecturers:
        # /html/body/div[1]/div[2]/div[2]/div/div/div/div[1]/div[1]/div/div/div/h3
        name = lecturer.find_element(By.XPATH, 'div/div/div/h3').text
        if name.strip() == '':
            continue
        interest = lecturer.find_element(By.XPATH, 'div/div/div/span[2]').text[:-5]
        email = f"Profile : {lecturer.find_element(By.XPATH, 'div/div/div/a').get_attribute('href')}"
        arr += [[f'IIT {university}', name, 'Professor', email, '', interest]]
    
    print(arr)
    return arr


def main():
    '''
        The main method
    '''
    # instantiate a chrome driver object
    driver = chrome('h')

    # scrape for iit madras
    arr = iit_madras(driver)

    # define links for universities with professors on same website
    links = [\
        ['https://iitd.irins.org/faculty/index/Department+of+Computer+Science+and+Engineering', 'Delhi'],
        ['https://iitb.irins.org/faculty/index/Department+of+Computer+Science+and+Engineering', 'Boombay'],
        ['https://iitk.irins.org/faculty/index/Department+of+Computer+Science+and+Engineering', 'Kanpur'],
        ['https://iitkgp.irins.org/faculty/index/Department+of+Computer+Science+and+Engineering', 'Kharagpur']
    ]

    for array in links:
        arr += scrape_professors(driver, array[0], array[1])
    
    df = pd.DataFrame(arr, columns=['Institution','Name','Designation','Email','PhoneNo','Specialisation'])
    df.to_excel('cs_professors.xlsx', index=False, encoding='utf-8', )
    

if __name__=="__main__":
    main()