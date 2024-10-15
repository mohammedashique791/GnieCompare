import os
import time
import json
import xlsxwriter
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_socketio import SocketIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import AzureOpenAI
from scraping import scrapping_execution
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from prompts import converting_to_correct_output, main_prompt
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
progress = 0

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
  

model = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

def ask_openai(prompt):
    try:
        response = model.chat.completions.create(
            model='gpt-4o',
            messages=[{"role":"user", "content":prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print("error in ask_openai", e)


# def write_to_excel(data):
#     print('in excel writing function')
#     try:
#         workbook = xlsxwriter.Workbook('comparison_my_new_one.xlsx')
#         worksheet = workbook.add_worksheet()
#         headers = list(data[0].keys())
#         for col, header in enumerate(headers):
#             worksheet.write(0, col, header)
            
#             row = 1
#             for comparison_item in data:
#                 for col, header in enumerate(headers):
#                     worksheet.write(row, col, comparison_item[header])
#                 row += 1
#         workbook.close()
#         print("Excel file comaprison_new(1) created successfully")
        
#     except Exception as e:
#         print("An error occured while creating the excel file", e)


def write_to_excel(data, filename='comparison_my_new_one.xlsx'):
    print('In excel writing function')
    try:
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        headers = list(data[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row, comparison_item in enumerate(data, start=1):
            for col, header in enumerate(headers):
                value = comparison_item.get(header, 'N/A')
                worksheet.write(row, col, value)

        print(f"Excel file '{filename}' created successfully")

    except Exception as e:
        print("An error occurred while creating the Excel file:", e)

    finally:
        # Ensure the workbook is closed properly
        workbook.close()


def setup_driver():
    try:
        service = Service(executable_path=r"C:\Users\MohammedAshiqueVT\Downloads\chromedriver-win64\chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox') 
        options.add_argument('--disable-dev-shm-usage')  
        options.add_argument('--disable-gpu') 
        options.add_argument('--disable-popup-blocking') 
        options.add_argument("--window-position=-2400,-2400")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print("Error occured in setup driver function", e)

def convert_to_correct_output(scraped_data):
    ogAction = {}
    try:
        prompt = converting_to_correct_output(scraped_data)
        actions_response = ask_openai(prompt)
        print('this is the actions_response from convert_to_correct_ouput', actions_response)
        try:
            print('Parsing the actions:', actions_response)
            ogAction = json.loads(actions_response)
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            print("Failed at position:", e.pos)
            print("Error message:", e.msg)
            print("Partial JSON content:", actions_response[:e.pos+20]) 
            return
        except Exception as e:
            print("Error occurred while creating ogAction in perform actions:", e)
            return
    except Exception as e:
        print("Error occured in convert to correct output function", e)
    return ogAction

def scrape_pricing_urls(driver, items, query=None):
    scraped_data = {}
    global progress
    try:
        total_items = len(items)
        socketio.emit('number_of_tasks', {'number': total_items})
        for idx, item_name in enumerate(items):
            print('in scraping pricing urls function')
            progress = int((idx / total_items) * 100)
            socketio.emit('update_progress', {'progress': progress})
            driver.get("https://www.google.com")

            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(f"{item_name}")
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)

            try:
                first_result = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "(//h3)[1]"))
                )
                
                first_result.click()
                time.sleep(3)   

                current_url = driver.current_url
                socketio.emit('update_url', {'url': current_url})

                result = scrapping_execution(current_url, 2, 1)
                socketio.emit('add_to_list', {'url': current_url})
                scraped_data[item_name] = result

            except TimeoutException:
                print(f"Timeout: Could not retrieve URL for {item_name}.")
            except ElementClickInterceptedException as e:
                print(f"Element click intercepted for {item_name}: {str(e)}")
                time.sleep(1)
                try:
                    first_result.click()
                except Exception as e:
                    print(f"Retrying click failed for {item_name}: {str(e)}")
    except Exception as e:
        print("Error in scrape_pricing_urls:", e)
    socketio.emit('process_completed', {'url': current_url})
    return scraped_data

def perform_actions(driver, actions):
    try:
        print('this is the actions i got', actions)
        
        ogAction = {}
        user_query = ''
        if not actions or len(actions.strip()) == 0:
            print("No actions received from OpenAI. Exiting...")
            return

        scraped_data = {}
        try:
            print('Parsing the actions:', actions)
            ogAction = json.loads(actions)
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            print("Failed at position:", e.pos)
            print("Error message:", e.msg)
            print("Partial JSON content:", actions[:e.pos+20])  # Show some content around the error for debugging
            return
        except Exception as e:
            print("Error occurred while creating ogAction in perform actions:", e)
            return
            
        details = ogAction[0]["details"]
        print('this is the details', details)
        scraped_data = scrape_pricing_urls(driver, details)
        print('the scraped_data is', scraped_data)

        print('Processing comparison data...')
        
        llm_response = convert_to_correct_output(scraped_data)
        
        write_to_excel(llm_response)

    except Exception as e:
        print("An error occurred in perform_actions:", e)

def main(user_input, n_models):
    try:
        prompt = main_prompt(user_input, n_models)
        actions_response = ask_openai(prompt)
        driver = setup_driver()
        perform_actions(driver, actions_response)
        driver.quit()
    except Exception as e:
        print("Error in main:", e)

@app.route('/main', methods=['POST'])
def run_main():
    global progress
    progress = 0
    user_input = request.form.get('search')
    # n_models = int(request.form.get('n_models', 5))
    session['command'] = ''

    if "compare" in user_input.lower():
        session['command'] = 'compare'

    main(user_input, config["maximum"])
    return jsonify({"status": "success"})


@app.route('/')
def homePage():
    return render_template('home.html')

@app.route('/download')
def download_excel():
    excel_file_path = 'comparison_my_new_one.xlsx'
    if os.path.exists(excel_file_path):
        return send_file(excel_file_path, as_attachment=True, download_name=excel_file_path,  mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        return "Excel file not found.", 404

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True, port = os.getenv('PORT'))
