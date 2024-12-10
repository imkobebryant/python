import time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import os
import random

class PetRegistrationScraper:
    def __init__(self):
        self.base_url = "https://www.pet.gov.tw/Web/O302.aspx"
        self.cities = ['新北市', '臺北市']
        self.wait_time = (3, 5)  # 隨機等待時間範圍（秒）
        
        # 設置 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 初始化 WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # 初始化每個城市的數據字典
        self.city_data = {city: [] for city in self.cities}

    def random_wait(self):
        """隨機等待一段時間"""
        time.sleep(random.uniform(*self.wait_time))

    def process_month_data(self, year, month, animal_type, max_retries=3):
        """處理特定月份和動物類型的數據，包含重試機制"""
        for retry in range(max_retries):
            try:
                start_date = f"{year}/{month:02d}/01"
                if month == 12:
                    next_year, next_month = year + 1, 1
                else:
                    next_year, next_month = year, month + 1
                end_date = (datetime(next_year, next_month, 1) - timedelta(days=1)).strftime("%Y/%m/%d")

                # 設置日期
                print(f"Setting dates for {year}/{month} (Attempt {retry + 1}/{max_retries})...")
                self.driver.execute_script(f'document.getElementById("txtSDATE").value = "{start_date}";')
                self.random_wait()
                self.driver.execute_script(f'document.getElementById("txtEDATE").value = "{end_date}";')
                self.random_wait()

                # 選擇動物類型
                radio_id = "animal_dog" if animal_type == 0 else "animal_cat"
                print(f"Selecting animal type: {radio_id}")
                radio = self.wait.until(EC.presence_of_element_located((By.ID, radio_id)))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                self.random_wait()
                self.driver.execute_script("arguments[0].click();", radio)

                # 點擊查詢按鈕
                print("Clicking search button...")
                search_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-main[data-event='前台_O302_查詢']"))
                )
                self.driver.execute_script("arguments[0].click();", search_button)
                time.sleep(5)  # 確保數據加載完成

                # 獲取表格數據
                print("Getting table data...")
                table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                
                data = {}
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    city = cells[0].text
                    if city in self.cities:
                        record = {
                            '動物類型': '狗' if animal_type == 0 else '貓',
                            '年': year,
                            '月': month,
                            '登記數': int(cells[2].text or 0),
                            '除戶數': int(cells[3].text or 0),
                            '絕育數': int(cells[6].text or 0),
                            '絕育除戶數': int(cells[7].text or 0),
                            '絕育率': cells[10].text
                        }
                        data[city] = record
                
                if data:
                    return data
                
            except Exception as e:
                print(f"Error on attempt {retry + 1}: {str(e)}")
                if retry < max_retries - 1:
                    print(f"Retrying... ({retry + 2}/{max_retries})")
                    time.sleep(5)  # 錯誤後等待更長時間
                    self.driver.get(self.base_url)
                    time.sleep(3)
                else:
                    print(f"Failed after {max_retries} attempts")
                    return {}

        return {}

    def get_monthly_data(self, year, month):
        """獲取指定月份的數據"""
        print(f"\nProcessing data for {year}/{month}")
        
        try:
            # 重新載入頁面以確保清潔狀態
            self.driver.get(self.base_url)
            time.sleep(3)

            # 分別處理狗和貓的數據
            for animal_type in [0, 1]:  # 0: 狗, 1: 貓
                print(f"Processing {'dog' if animal_type == 0 else 'cat'} data...")
                current_data = self.process_month_data(year, month, animal_type)
                
                # 將數據添加到對應城市的列表中
                for city, data in current_data.items():
                    self.city_data[city].append(data)

                self.random_wait()  # 在處理不同動物類型之間添加隨機等待

        except Exception as e:
            print(f"Error in get_monthly_data: {str(e)}")

    def save_city_data_to_csv(self, city):
        """將指定城市的數據保存到CSV"""
        if not self.city_data[city]:
            return

        # 建立檔名（移除城市名稱中的特殊字符）
        filename = f"pet_registration_{city.replace('臺', 'tai').replace('市', '')}.csv"
        
        df = pd.DataFrame(self.city_data[city])
        # 設置列的順序
        columns = ['動物類型', '年', '月', '登記數', '除戶數', '絕育數', '絕育除戶數', '絕育率']
        df = df[columns]
        
        # 按年份和月份排序
        df = df.sort_values(['年', '月'], ascending=[False, False])
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Saved data for {city} to {filename}")

    def scrape_all_months(self):
        """抓取所有月份的數據"""
        print("Starting data collection process...")
        
        try:
            for year in range(2024, 2014, -1):  # 從2024年往回抓到2015年
                for month in range(12, 0, -1):  # 從12月往回抓到1月
                    if year == 2024 and month > datetime.now().month:
                        continue
                    
                    print(f"\nProcessing {year}/{month}...")
                    try:
                        self.get_monthly_data(year, month)
                        print(f"Successfully processed {year}/{month}")
                    except Exception as e:
                        print(f"Error processing {year}/{month}: {str(e)}")
                    
                    time.sleep(5)  # 每個月份之間添加固定等待時間
            
            # 保存每個城市的數據到獨立的CSV文件
            for city in self.cities:
                self.save_city_data_to_csv(city)
            
            print("\nData collection completed successfully!")
            
        except Exception as e:
            print(f"Error during data collection: {str(e)}")
        
        finally:
            self.driver.quit()

# 主程式執行
if __name__ == "__main__":
    scraper = PetRegistrationScraper()
    scraper.scrape_all_months()