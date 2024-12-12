import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.preprocessing import RobustScaler

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False

# 讀取數據
df = pd.read_csv('processed_taipei_pet_data.csv')
budget_df = pd.read_csv('絕育補助預算表.csv')

# 基本數據預處理
df['ds'] = pd.to_datetime(df.apply(lambda x: f"{int(x['年'])}-{int(x['月']):02d}-01", axis=1))
df['y'] = df['登記數'] 
df['month'] = df['ds'].dt.month
df['year'] = df['ds'].dt.year

# 合併預算數據  
budget_df['台北市預算'] = budget_df['台北市預算'].str.replace(',', '').astype(float)
df = pd.merge(df, budget_df[['西元年分', '台北市預算']], 
              left_on='year', right_on='西元年分', how='left')

# 計算每月預算
df['monthly_budget'] = df['台北市預算'] / 12

# 基本特徵
df['MA3'] = df['y'].rolling(window=3, min_periods=1).mean()  
df['month_avg'] = df.groupby('month')['y'].transform('mean')

# 使用 RobustScaler 進行特徵縮放（對異常值更穩健）
scaler = RobustScaler()
features_to_scale = ['monthly_budget', 'MA3', 'month_avg', '絕育率']

scaled_features = scaler.fit_transform(df[features_to_scale])
scaled_df = pd.DataFrame(scaled_features, columns=[f'{col}_scaled' for col in features_to_scale])  
df = pd.concat([df, scaled_df], axis=1)

# 處理缺失值
df = df.ffill().bfill()

# 分割訓練集和測試集（70/30） 
train_size = int(len(df) * 0.7)
train_df = df[:train_size]
test_df = df[train_size:]

# 選擇特徵
selected_features = [f'{col}_scaled' for col in features_to_scale]

# Prophet 模型設置
model = Prophet(
    changepoint_prior_scale=0.005,  # 降低變化點敏感度
    seasonality_prior_scale=5,      # 適度的季節性強度
    holidays_prior_scale=0.01,  
    seasonality_mode='multiplicative',
    yearly_seasonality=8,           # 簡化年度季節性
    weekly_seasonality=False,
    daily_seasonality=False, 
    changepoint_range=0.9
)

# 添加月度季節性
model.add_seasonality(
    name='monthly',
    period=30.5,
    fourier_order=8
)

# 添加特徵
for feature in selected_features:
    model.add_regressor(feature, mode='additive')

# 準備訓練數據    
train_prophet = train_df[['ds', 'y'] + selected_features].copy()

# 訓練模型
model.fit(train_prophet)

# 準備測試數據和預測
test_prophet = test_df[['ds'] + selected_features].copy()
test_forecast = model.predict(test_prophet)

# 生成歷史預測值
historical_forecast = model.predict(df[['ds'] + selected_features]) 

# 準備未來預測日期
future_dates = pd.DataFrame({
    'ds': pd.date_range(start='2024-12-01', end='2025-12-31', freq='MS')  
})

# 為未來日期添加特徵
for feature in selected_features:
    future_dates[feature] = df[feature].iloc[-1]

# 預測未來值  
future_forecast = model.predict(future_dates)

# 合併歷史預測和未來預測
all_forecast = pd.concat([historical_forecast, future_forecast]) 

# 計算評估指標
y_true = test_df['y'].values
y_pred = test_forecast['yhat'].values

rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
r2 = r2_score(y_true, y_pred) 
mean_error = np.mean(np.abs(y_true - y_pred))

# 繪製圖表
plt.figure(figsize=(15, 7))

# 繪製實際值
plt.plot(df['ds'], df['y'], label='實際值', color='blue', linewidth=2)

# 繪製預測值  
plt.plot(all_forecast['ds'], all_forecast['yhat'], 
         label='預測值', color='orange', linewidth=2)

plt.title('臺北市寵物登記數預測結果 (2015-2025)', fontsize=14, pad=15)  
plt.xlabel('年份', fontsize=12)
plt.ylabel('登記數量', fontsize=12)
plt.legend(prop={'size': 12}, loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)

# 設置x軸刻度
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y')) 
plt.gcf().autofmt_xdate()

# 設置y軸數值格式 
plt.gca().yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: format(int(x), ','))
)

plt.tight_layout()
plt.show()

# 輸出評估指標  
print(f"\n模型評估指標:")
print(f"RMSE: {rmse:.2f}") 
print(f"MAPE: {mape:.2f}%")
print(f"R平方: {r2:.4f}")
print(f"平均每月預測誤差範圍: ±{mean_error:.2f}")

# 輸出未來預測值
print("\n2024年12月~2025年12月預測值:")
future_predictions = future_forecast[['ds', 'yhat']]  
for _, row in future_predictions.iterrows():
    print(f"{row['ds'].strftime('%Y年%m月')}: {int(row['yhat'])}")

# 分析特徵重要性    
from sklearn.linear_model import LinearRegression
reg = LinearRegression()
reg.fit(df[selected_features], df['y'])

importance = pd.DataFrame({
    'feature': features_to_scale,
    'importance': np.abs(reg.coef_),  
    'correlation': df[features_to_scale].corrwith(df['y'])
})
importance = importance.sort_values('importance', ascending=False)

print("\n特徵重要性分析:")  
print(importance)