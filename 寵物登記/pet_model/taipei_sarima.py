import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import matplotlib.pyplot as plt
import matplotlib as mpl

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示負號

# 可調參數
PARAMS = {
    'train_size': 0.7,  # 訓練集比例
    'order': (1, 1, 1),  # SARIMA參數 (p,d,q) - 可調整
    'seasonal_order': (1, 1, 1, 12),  # 季節性參數 (P,D,Q,s) - 可調整
    'enforce_stationarity': False,  # 是否強制平穩性 - 可調整
    'enforce_invertibility': False  # 是否強制可逆性 - 可調整
}

def prepare_data():
    # 讀取數據，使用適當的編碼
    try:
        # 嘗試不同的編碼方式
        encodings = ['utf-8', 'big5', 'cp950', 'gb18030']
        taipei_df = None
        budget_df = None
        
        for encoding in encodings:
            try:
                taipei_df = pd.read_csv('processed_taipei_pet_data.csv', encoding=encoding)
                budget_df = pd.read_csv('絕育補助預算表.csv', encoding=encoding)
                print(f"成功使用 {encoding} 編碼讀取檔案")
                break
            except UnicodeDecodeError:
                continue
            
        if taipei_df is None or budget_df is None:
            raise Exception("無法以任何編碼方式讀取檔案")
        
        # 處理預算數據
        budget_df['預算'] = budget_df['台北市預算'].str.replace(',', '').astype(float)
        
        # 轉換日期
        taipei_df['date'] = pd.to_datetime(taipei_df['年'].astype(str) + '-' + 
                                         taipei_df['月'].astype(str) + '-01')
        
        # 按日期排序
        taipei_df = taipei_df.sort_values('date')
        
        return taipei_df, budget_df
        
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {str(e)}")
        raise

def train_model(data):
    # 分割訓練集和測試集
    split_idx = int(len(data) * PARAMS['train_size'])
    train_data = data.iloc[:split_idx]
    test_data = data.iloc[split_idx:]
    
    # 訓練SARIMA模型
    model = SARIMAX(train_data['登記數'],
                    order=PARAMS['order'],
                    seasonal_order=PARAMS['seasonal_order'],
                    enforce_stationarity=PARAMS['enforce_stationarity'],
                    enforce_invertibility=PARAMS['enforce_invertibility'])
    
    results = model.fit()
    
    # 預測測試集
    forecast = results.get_forecast(steps=len(test_data))
    predicted_mean = forecast.predicted_mean
    
    # 計算準確度指標
    mape = mean_absolute_percentage_error(test_data['登記數'], predicted_mean)
    rmse = np.sqrt(mean_squared_error(test_data['登記數'], predicted_mean))
    
    return results, predicted_mean, test_data['登記數'], mape, rmse

def predict_2025(model):
    # 預測2025年12個月
    forecast_2025 = model.get_forecast(steps=12)
    predictions = forecast_2025.predicted_mean
    conf_int = forecast_2025.conf_int()
    
    return predictions, conf_int

def plot_results(actual, predicted, title):
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(actual)), actual, label='實際值', color='blue')
    plt.plot(range(len(predicted)), predicted, label='預測值', color='orange')
    plt.title(title, fontsize=12)
    plt.xlabel('時間', fontsize=10)
    plt.ylabel('寵物登記數', fontsize=10)
    plt.legend(prop={'size': 10})
    plt.grid(True)
    
    # 設定更大的字體大小
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    
    # 調整圖表邊距
    plt.tight_layout()
    
    plt.show()

def main():
    print("開始分析台北市寵物登記數據...")
    
    # 準備數據
    taipei_df, budget_df = prepare_data()
    
    # 訓練模型
    model, predictions, actual, mape, rmse = train_model(taipei_df)
    
    # 顯示模型性能
    print("\n模型性能指標：")
    print(f"MAPE (平均絕對百分比誤差): {mape:.2%}")
    print(f"RMSE (均方根誤差): {rmse:.2f}")
    print(f"平均每月預測誤差範圍: ±{rmse:.0f}個登記數")
    
    # 預測2025年數據
    predictions_2025, conf_int = predict_2025(model)
    
    print("\n2025年預測結果：")
    for month, pred in enumerate(predictions_2025, 1):
        print(f"2025年{month}月預測登記數: {pred:.0f}")
    
    # 繪製結果圖表
    plot_results(actual, predictions, "台北市寵物登記數預測結果")
    
    # 顯示模型摘要
    print("\n模型詳細資訊：")
    print(model.summary())

if __name__ == "__main__":
    main()