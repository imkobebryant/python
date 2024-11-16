import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

class PetRegistrationScraper:
    def __init__(self):
        self.url = "https://www.pet.gov.tw/web/O302.aspx"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.pet.gov.tw/web/O302.aspx',
            'Origin': 'https://www.pet.gov.tw',
            'Connection': 'keep-alive',
        }

    def get_viewstate_data(self, html_content):
        """獲取ASP.NET的表單驗證資料"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 印出所有form標籤和其內容，幫助調試
            print("\n找到的表單：")
            forms = soup.find_all('form')
            print(f"表單數量：{len(forms)}")
            for form in forms:
                print(f"Form ID: {form.get('id', 'N/A')}")
            
            # 印出所有hidden input標籤
            print("\n找到的表單欄位：")
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            print(f"隱藏欄位數量：{len(hidden_inputs)}")
            for input_tag in hidden_inputs:
                print(f"Name: {input_tag.get('name', 'N/A')}, Value: {input_tag.get('value', 'N/A')[:30]}...")
            
            # 獲取必要的表單數據
            form_data = {}
            for input_tag in hidden_inputs:
                name = input_tag.get('name')
                if name:
                    form_data[name] = input_tag.get('value', '')
            
            # 檢查表單欄位
            required_fields = ['__VIEWSTATE', '__VIEWSTATEGENERATOR']
            missing_fields = [field for field in required_fields if field not in form_data]
            
            if missing_fields:
                print(f"\n警告：缺少以下表單欄位：{', '.join(missing_fields)}")
            else:
                print("\n成功找到所有必要的表單欄位")
            
            return form_data
            
        except Exception as e:
            print(f"獲取表單驗證資料時發生錯誤：{str(e)}")
            return {}

    def parse_registration_data(self, soup):
        """解析寵物登記統計資料"""
        data = []
        try:
            # 嘗試找到所有表格
            print("\n正在尋找數據表格...")
            tables = soup.find_all('table')
            print(f"找到 {len(tables)} 個表格")
            
            # 檢查每個表格的結構
            for i, table in enumerate(tables):
                print(f"\n檢查表格 {i+1}:")
                print(f"Table ID: {table.get('id', 'N/A')}")
                print(f"Table Class: {table.get('class', 'N/A')}")
                
                # 嘗試獲取表格的行
                rows = table.find_all('tr')
                print(f"行數：{len(rows)}")
                
                # 如果表格有行，檢查第一行的列數
                if rows:
                    header_cells = rows[0].find_all(['th', 'td'])
                    print(f"列數：{len(header_cells)}")
                    print("列標題：", [cell.text.strip() for cell in header_cells])
                    
                    # 如果這是我們要找的表格（根據列數和內容判斷）
                    if len(header_cells) >= 10:
                        print("找到目標表格！")
                        # 解析除了表頭外的所有行
                        for row in rows[1:]:
                            cols = row.find_all('td')
                            if len(cols) >= 10:  # 確保有足夠的欄位
                                try:
                                    registration_data = {
                                        '縣市': cols[0].text.strip(),
                                        '登記單位數': self.parse_number(cols[1].text),
                                        '登記數(A)': self.parse_number(cols[2].text),
                                        '除戶數(B)': self.parse_number(cols[3].text),
                                        '轉讓數(C)': self.parse_number(cols[4].text),
                                        '變更數(D)': self.parse_number(cols[5].text),
                                        '絕育數(E)': self.parse_number(cols[6].text),
                                        '絕育除戶數(F)': self.parse_number(cols[7].text),
                                        '免絕育數(G)': self.parse_number(cols[8].text),
                                        '免絕育除戶數(H)': self.parse_number(cols[9].text),
                                    }
                                    
                                    # 計算比率
                                    a_minus_b = registration_data['登記數(A)'] - registration_data['除戶數(B)']
                                    if a_minus_b > 0:
                                        registration_data['絕育率'] = round((registration_data['絕育數(E)'] - 
                                                                    registration_data['絕育除戶數(F)']) / a_minus_b * 100, 2)
                                        registration_data['緊殺管理率'] = round(((registration_data['絕育數(E)'] - 
                                                                       registration_data['絕育除戶數(F)']) + 
                                                                      (registration_data['免絕育數(G)'] - 
                                                                       registration_data['免絕育除戶數(H)'])) / a_minus_b * 100, 2)
                                    else:
                                        registration_data['絕育率'] = 0
                                        registration_data['緊殺管理率'] = 0
                                    
                                    data.append(registration_data)
                                    print(f"已解析 {registration_data['縣市']} 的數據")
                                except Exception as e:
                                    print(f"解析行數據時發生錯誤：{str(e)}")
                                    continue

        except Exception as e:
            print(f"解析表格時發生錯誤：{str(e)}")
        
        if not data:
            print("警告：未能從任何表格中提取數據")
        
        return data

    # 其他方法（parse_number, scrape, save_to_csv）保持不變...
    
    def parse_number(self, text):
        """解析數字，移除逗號並轉換為整數"""
        try:
            return int(text.strip().replace(',', ''))
        except ValueError:
            return 0

    def scrape(self, date="2023/01/01"):
        """執行爬蟲"""
        try:
            session = requests.Session()
            print("正在獲取初始頁面...")
            response = session.get(self.url, headers=self.headers)
            response.raise_for_status()
            print(f"頁面大小：{len(response.text)} 字節")
            
            print("正在獲取表單驗證資料...")
            form_data = self.get_viewstate_data(response.text)
            
            if not form_data:
                print("無法獲取表單驗證資料，程式終止")
                return []
            
            form_data.update({
                'ContentPlaceHolder1_ddl_Animal_Kind': '狗',
                'ContentPlaceHolder1_txt_Adopt_StartDate': date,
                'ContentPlaceHolder1_ddl_Query_Type': '3',
                'ContentPlaceHolder1_btn_Search': '查詢'
            })
            
            print("\n將要發送的表單數據：")
            for key, value in form_data.items():
                print(f"{key}: {value[:30]}..." if len(str(value)) > 30 else f"{key}: {value}")
            
            print("\n正在發送查詢請求...")
            response = session.post(self.url, data=form_data, headers=self.headers)
            response.raise_for_status()
            
            with open('response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("已將響應內容保存到 response.html")
            
            print("正在解析數據...")
            soup = BeautifulSoup(response.text, 'html.parser')
            data = self.parse_registration_data(soup)
            
            if not data:
                print("警告：未獲取到任何數據")
                return []
            
            for item in data:
                item['查詢日期'] = date
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"網路請求錯誤：{str(e)}")
            return []
        except Exception as e:
            print(f"執行過程中發生錯誤：{str(e)}")
            raise

    def save_to_csv(self, data, filename):
        """將資料保存為CSV檔案並計算總計"""
        if not data:
            print("沒有數據可供保存")
            return
            
        try:
            df = pd.DataFrame(data)
            
            # 計算總和並添加到最後一行
            numeric_columns = ['登記單位數', '登記數(A)', '除戶數(B)', '轉讓數(C)', '變更數(D)', 
                             '絕育數(E)', '絕育除戶數(F)', '免絕育數(G)', '免絕育除戶數(H)']
            
            total_row = {'縣市': '總計'}
            for col in numeric_columns:
                total_row[col] = df[col].sum()
                
            # 計算總計的絕育率和緊殺管理率
            a_minus_b = total_row['登記數(A)'] - total_row['除戶數(B)']
            if a_minus_b > 0:
                total_row['絕育率'] = round((total_row['絕育數(E)'] - total_row['絕育除戶數(F)']) / a_minus_b * 100, 2)
                total_row['緊殺管理率'] = round(((total_row['絕育數(E)'] - total_row['絕育除戶數(F)']) + 
                                          (total_row['免絕育數(G)'] - total_row['免絕育除戶數(H)'])) / a_minus_b * 100, 2)
            else:
                total_row['絕育率'] = 0
                total_row['緊殺管理率'] = 0
                
            total_row['查詢日期'] = df['查詢日期'].iloc[0]
            
            # 添加總計行
            df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
            
            # 保存CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n資料已成功保存到 {filename}")
            
            # 顯示統計資訊
            print("\n資料統計:")
            print(f"總縣市數: {len(data)}")
            print(f"總登記數: {total_row['登記數(A)']:,}")
            print(f"全國絕育率: {total_row['絕育率']}%")
            print(f"全國緊殺管理率: {total_row['緊殺管理率']}%")
            
        except Exception as e:
            print(f"保存數據時發生錯誤：{str(e)}")

def main():
    try:
        scraper = PetRegistrationScraper()
        print("開始執行爬蟲...")
        data = scraper.scrape()
        if data:
            scraper.save_to_csv(data, "dog_registration_2023_detailed.csv")
        else:
            print("未獲取到數據，程式結束")
    except Exception as e:
        print(f"程式執行過程中發生錯誤：{str(e)}")

if __name__ == "__main__":
    main()