import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt

def prepare_taipei_data(df):
    # 篩選台北市數據
    taipei_data = df[df['County'] == '臺北市'].copy()
    
    # 將年份轉換為數值特徵(2009=0, 2010=1, ...)
    taipei_data['Year_Num'] = taipei_data['Year'] - 2009
    
    # 準備特徵(X)和目標變數(y)
    X = taipei_data[['Year_Num', 'Neutering Rate']]
    y = taipei_data['Registrations']
    
    return X, y, taipei_data

def train_model(X, y):
    # 分割訓練和測試數據 - 調整為70/30
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 訓練線性迴歸模型
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 評估模型
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    
    return model, train_r2, test_r2, test_rmse, X_test, y_test

def plot_results(model, taipei_data, X_test, y_test):
    plt.figure(figsize=(12, 6))
    
    # 實際值
    plt.scatter(taipei_data['Neutering Rate'], taipei_data['Registrations'], 
                color='blue', label='實際登記數', alpha=0.6)
    
    # 測試集預測值
    test_pred = model.predict(X_test)
    plt.scatter(X_test['Neutering Rate'], test_pred, 
                color='red', label='預測登記數', alpha=0.6)
    
    plt.xlabel('絕育率 (%)')
    plt.ylabel('登記數')
    plt.title('台北市寵物登記數與絕育率關係')
    plt.legend()
    
    return plt

def predict_registration(model, year_num, neutering_rate):
    """預測特定絕育率下的登記數"""
    prediction = model.predict([[year_num, neutering_rate]])
    return prediction[0]

# 讀取數據
df = pd.read_csv('2023-2009pet_data.csv')

# 準備數據
X, y, taipei_data = prepare_taipei_data(df)

# 訓練模型
model, train_r2, test_r2, test_rmse, X_test, y_test = train_model(X, y)

# 顯示模型結果
print(f"訓練集 R² 分數: {train_r2:.4f}")
print(f"測試集 R² 分數: {test_r2:.4f}")
print(f"測試集 RMSE: {test_rmse:.2f}")
print("\n模型係數:")
print(f"年份係數: {model.coef_[0]:.2f}")
print(f"絕育率係數: {model.coef_[1]:.2f}")
print(f"截距: {model.intercept_:.2f}")

# 預測2024年，絕育率50%的情況
future_year_num = 2024 - 2009  # 將2024轉換為相對年份數值
predicted_registration = predict_registration(model, future_year_num, 50.0)
print(f"\n預測2024年，在絕育率50%的情況下:")
print(f"預測的寵物登記數為: {predicted_registration:.0f}")

# 計算95%預測區間
# 使用訓練數據的標準差來估算預測區間
y_pred = model.predict(X)
prediction_std = np.std(y - y_pred)
confidence_interval = 1.96 * prediction_std  # 95% 信賴區間

print(f"預測區間: {predicted_registration - confidence_interval:.0f} 到 {predicted_registration + confidence_interval:.0f}")

# 繪製結果圖
plot = plot_results(model, taipei_data, X_test, y_test)