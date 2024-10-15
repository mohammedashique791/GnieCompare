import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging
import time
import os
import re
# from mongodbfile import connect_to_mongodb, log_mongodb 
import datetime

if not os.path.exists('application_logs'):
    os.makedirs('application_logs')
if not os.path.exists('meter_logs'):
    os.makedirs('meter_logs')

app_logger = logging.getLogger('applicationLogger')
app_handler = logging.FileHandler('application_logs/application.log')
app_handler.setLevel(logging.DEBUG)
app_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_handler.setFormatter(app_formatter)
app_logger.addHandler(app_handler)
app_logger.setLevel(logging.DEBUG)

# collection = connect_to_mongodb()

def log_performance_metrics(url, time_taken, operation_type):
    try:
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        formatted_time_taken = f"{time_taken:.3f}"
        with open('meter_logs/performance_metrics.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"{timestamp},{url},{operation_type},{formatted_time_taken}\n")
    except Exception as e:
        app_logger.error(f"Error logging performance metrics: {e}")

def log_meter(operation_name, time_taken, category):
    try:
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        formatted_time_taken = f"{time_taken:.3f}"
        with open('meter_logs/meter.log', 'a', encoding='utf-8') as meter_file:
            meter_file.write(f"{timestamp},{operation_name},{category},{formatted_time_taken}\n")
    except Exception as e:
        app_logger.error(f"Error logging meter data: {e}")

def is_dynamic(content):
    return "<script" in content or "ng-" in content or "data-ng-" in content

def retry_request(url, headers, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            app_logger.debug(f"Attempt {attempt + 1} failed with status code {response.status_code}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            app_logger.error(f"Error during request attempt {attempt + 1}: {e}")
            time.sleep(delay)
    return None

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = list(dict.fromkeys(text.split('.')))
    clean_body_text = '. '.join(sentences) + '.' if sentences else ''
    return clean_body_text

def scrape_static_website(url, initiator, find_me):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-popup-blocking') 
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument("--window-position=-2400,-2400")
        print('in static')
        
        app_logger.debug(f"Starting static scraping for {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = retry_request(url, headers)
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            if "Access Denied" in soup.get_text():
                app_logger.error(f"Access denied for {url}")
                return None
            
            start_time = time.time()
            title = soup.title.string if soup.title else 'No Title'
            body_text = clean_text(soup.get_text(separator=' ', strip=True))
            if find_me == None:
                images = [img['src'] for img in soup.find_all('img') if img.get('src')]
                links = [a['href'] for a in soup.find_all('a') if a.get('href')]
                images = [img if img is not None else ' ' for img in images]
                links = [link if link is not None else ' ' for link in links]
            else:
                images, links, images, links = [], [], [], []
            end_time = time.time()
            time_taken = end_time - start_time

            # log_mongodb(collection, initiator, 'static_scraping', url, {
            #     'url': url,
            #     'title': title,
            #     'body_text': body_text,
            #     'images': images,
            #     'links': links
            # }, time_taken, start_time)

            log_meter('static_scraping', time_taken, 'static')

            app_logger.debug(f"Static scraping completed for {url}")

            return {
                'url': url,
                'title': title,
                'body_text': body_text,
                'images': images,
                'links': links
            }
        else:
            app_logger.error(f"Failed to retrieve page at {url}, Status code: {response.status_code}")
            return None
    except Exception as e:
        app_logger.error(f"Error scraping static site {url}: {e}")
        return None

def scrape_dynamic_website(url, chromedriver_path, initiator, find_me):
    try:
        app_logger.debug(f"Starting dynamic scraping for {url}")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-popup-blocking') 
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument("--window-position=-2400,-2400")
        chrome_options.add_argument('--disable-extensions')  # Disable extensions to prevent popups
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        print('in dynamic')
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        start_time = time.time()

        driver.get(url)
        wait = WebDriverWait(driver, 50)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        title = driver.title
        body_text = clean_text(driver.find_element(By.TAG_NAME, 'body').text)

        if find_me == None:
            images = [img.get_attribute('src') for img in driver.find_elements(By.TAG_NAME, 'img')]
            links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a')]
            images = [img if img is not None else ' ' for img in images]
            links = [link if link is not None else ' ' for link in links]
        else:
            images, links, images, links = [], [], [], []

        driver.quit()
        end_time = time.time()
        time_taken = end_time - start_time

        # log_mongodb(collection, initiator, 'dynamic_scraping', url, {
        #     'url': url,
        #     'title': title,
        #     'body_text': body_text,
        #     'images': images,
        #     'links': links
        # }, time_taken, start_time)

        log_meter('dynamic_scraping', time_taken, 'dynamic')

        app_logger.debug(f"Dynamic scraping completed for {url}")

        return {
            'url': url,
            'title': title,
            'body_text': body_text,
            'images': images,
            'links': links
        }
    except Exception as e:
        app_logger.error(f"Error scraping dynamic site {url}: {e}")
        return None

def write_to_json(data, json_filename):
    try:
        with open(json_filename, 'a', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
            jsonfile.write('\n')
        app_logger.debug(f"Data written to {json_filename}")
    except Exception as e:
        app_logger.error(f"Error writing to JSON file: {e}")
        

def scrape_links(links, chromedriver_path, json_filename, initiator, find_me):
    all_data = []
    combined_data = {
        'urls': set(),
        'titles': set(),
        'body_texts': set(),
        'images': set(),
        'links': set()
    }

    for link in links:
        app_logger.debug(f"Starting scraping for {link}")
        start_time = time.time()

        static_result = scrape_static_website(link, initiator, find_me)
        dynamic_result = scrape_dynamic_website(link, chromedriver_path, initiator, find_me)
        print('scrape link executed for static and dynamic.')

        if static_result:
            all_data.append({'static_result': static_result})
            combined_data['urls'].add(static_result['url'])
            combined_data['titles'].add(static_result['title'])
            combined_data['body_texts'].add(static_result['body_text'])
            combined_data['images'].update(static_result['images'])
            combined_data['links'].update(static_result['links'])

        if dynamic_result:
            all_data.append({'dynamic_result': dynamic_result})
            combined_data['urls'].add(dynamic_result['url'])
            combined_data['titles'].add(dynamic_result['title'])
            combined_data['body_texts'].add(dynamic_result['body_text'])
            combined_data['images'].update(dynamic_result['images'])
            combined_data['links'].update(dynamic_result['links'])

        end_time = time.time()
        time_taken = end_time - start_time
        log_meter('combined_scraping', time_taken, 'combined')


    combined_data = {key: list(value) for key, value in combined_data.items()}

    write_to_json(all_data, json_filename)
    write_to_json(combined_data, 'combined_data.json')
    
    return combined_data
    
    
    
    # log_mongodb(collection, initiator, 'combined_scraping', 'combined_data', combined_data, time_taken, start_time)

def scrapping_execution(link, parameters=None, find_me=None):
    user_input = link
    initiator = ''
    links = [url.strip() for url in user_input.split(',')]
    if parameters == None:
        initiator = input("Enter your name: ")

    chromedriver_path = r"C:\Users\MohammedAshiqueVT\Downloads\chromedriver-win64\chromedriver.exe"
    json_filename = 'scraped_data.json'

    data = scrape_links(links, chromedriver_path, json_filename, initiator, find_me)    
    return data
