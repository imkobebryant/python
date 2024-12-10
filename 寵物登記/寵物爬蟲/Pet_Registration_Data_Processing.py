import pandas as pd

def process_pet_data(filename):
    """
    處理寵物登記資料CSV檔案
    
    參數:
    filename (str): CSV檔案名稱
    
    回傳:
    pandas.DataFrame: 處理後的資料表，包含合併後的狗貓資料及重新計算的絕育率
    """
    # 讀取CSV檔案，使用utf-8-sig編碼以正確處理中文
    df = pd.read_csv(filename, encoding='utf-8-sig')
    
    # 依年月分組並加總相關欄位
    grouped = df.groupby(['年', '月']).agg({
        '登記數': 'sum',     # 加總登記數
        '除戶數': 'sum',     # 加總除戶數
        '絕育數': 'sum',     # 加總絕育數
        '絕育除戶數': 'sum'  # 加總絕育除戶數
    }).reset_index()
    
    # 計算新的絕育率
    # 公式：(絕育數 - 絕育除戶數) / (登記數 - 除戶數) × 100
    grouped['絕育率'] = ((grouped['絕育數'] - grouped['絕育除戶數']) / 
                      (grouped['登記數'] - grouped['除戶數']) * 100).round(2)
    
    # 依年月降序排列
    grouped = grouped.sort_values(['年', '月'], ascending=[False, False])
    
    return grouped

def main():
    """
    主程式：處理兩個城市的寵物登記資料並儲存結果
    """
    try:
        # 處理台北市資料
        taipei_data = process_pet_data('pet_registration_tai北.csv')
        # 處理新北市資料
        xinbei_data = process_pet_data('pet_registration_新北.csv')
        
        # 將處理後的資料儲存為新的CSV檔案，使用utf-8-sig編碼
        taipei_data.to_csv('processed_taipei_pet_data.csv', index=False, encoding='utf-8-sig')
        xinbei_data.to_csv('processed_xinpei_pet_data.csv', index=False, encoding='utf-8-sig')
        
        print("處理完成！新檔案已儲存為：")
        print("- processed_taipei_pet_data.csv")
        print("- processed_xinpei_pet_data.csv")
        
    except Exception as e:
        print(f"處理過程中發生錯誤：{str(e)}")

if __name__ == "__main__":
    main()