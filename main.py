from fastapi import FastAPI, HTTPException, Response
import json
from selenium import webdriver
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.responses import JSONResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

app = FastAPI()


def scrape_nvidia(): #basic logic :first hit the url and then in the div of general-container there was a div for title which contained name and div for price

    url = "https://www.nvidia.com/en-in/geforce/buy/"
    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 1500)#i have set the timeout to be high because i tried out with low,it was showing error so it might be due to low connectivity
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "general-container")))
    product_containers = driver.find_elements(By.CLASS_NAME, "general-container")

    gpu_names = []
    starting_prices = []

    for container in product_containers:
        try:
            gpu_name = container.find_element(By.CLASS_NAME, "title").text
            gpu_names.append(gpu_name)
            try:
                starting_price = container.find_element(By.CLASS_NAME, "startingprice").text
                numerical_value = re.sub(r'[^\d]', '', starting_price)  # basically manupilating the string to just get the numerical value
                starting_prices.append(int(numerical_value)) #converting to int 
            except Exception:
                starting_prices.append("N/A")
            
        except Exception as e:
            print(f"Error processing product: {e}")

    indices_to_delete = [0, 1, 11, 12, 13, 14, 15, 16, 17]  # i have to just include the gpus only so doing this otherwise there were manyh products
    gpu_names_updated = [gpu_names[i] for i in range(len(gpu_names)) if i not in indices_to_delete]
    prices_updates = [starting_prices[i] for i in range(len(starting_prices)) if i not in indices_to_delete]

    gpu_dict = dict(zip(gpu_names_updated, prices_updates))
    gpu_list = json.dumps(gpu_dict)
    driver.quit()
    return gpu_list

@app.get("/scrape")
def get_nvidia_data(response: Response):
    data = json.loads(scrape_nvidia())
    response = JSONResponse(content=data)
    response.headers["Access-Control-Allow-Origin"] = "*" # below the code , i am basically operating to reolve the cors error by modifying the headers that i am getting from the request(frontend)
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response
