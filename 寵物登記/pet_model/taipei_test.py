import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.preprocessing import MinMaxScaler

def setup_style():
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

def load_data():
    df = pd.read_csv('processed_taipei_pet_data.csv')
    budget_df = pd.read_csv('絕育補助預算表.csv')
    
    df['ds'] = pd.to_datetime(df.apply(lambda x: f"{int(x['年'])}-{int(x['月']):02d}-01", axis=1))
    df['y'] = df['登記數']
    df['month'] = df['ds'].dt.month
    
    budget_df['台北市預算'] = budget_df['台北市預算'].str.replace(',', '').astype(float)
    df = pd.merge(df, budget_df[['西元年分', '台北市預算']], 
                  left_on='年', right_on='西元年分', how='left')
    
    return df

def create_features(df):
    df['monthly_budget'] = df['台北市預算'] / 12
    df['spay_ratio'] = df['絕育率'] / 100
    
    # 優化特徵處理
    df['ma3'] = df['y'].rolling(window=3, center=True, min_periods=1).mean()
    df['month_avg'] = df.groupby('month')['y'].transform('mean')
    
    # 加入年度趨勢
    df['year_trend'] = (df['ds'] - df['ds'].min()).dt.days / 365.25
    
    return df.fillna(method='ffill')

def scale_features(df, features):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[features])
    
    for i, col in enumerate(features):
        df[f'{col}_scaled'] = scaled_data[:, i]
    
    return df, scaler

def split_data(df, train_ratio=0.7):
    train_size = int(len(df) * train_ratio)
    return df[:train_size], df[train_size:]

def create_prophet_model():
    return Prophet(
        changepoint_prior_scale=0.001,
        seasonality_prior_scale=1.0,
        holidays_prior_scale=0.01,
        seasonality_mode='additive',
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_range=0.85
    )

def train_model(model, train_df, features):
    for feature in features:
        model.add_regressor(feature, mode='additive')
    model.fit(train_df[['ds', 'y'] + features])
    return model

def generate_predictions(model, df, test_df, features):
    test_forecast = model.predict(test_df[['ds'] + features])
    historical_forecast = model.predict(df[['ds'] + features])
    
    future_dates = pd.DataFrame({
        'ds': pd.date_range(start='2024-12-01', end='2025-12-31', freq='MS')
    })
    
    # 使用最後12個月的中位數
    recent_data = df.tail(12)
    for feature in features:
        future_dates[feature] = recent_data[feature].median()
    
    future_forecast = model.predict(future_dates)
    
    return test_forecast, historical_forecast, future_forecast

def plot_results(df, historical_forecast, future_forecast):
    plt.figure(figsize=(15, 7))
    plt.plot(df['ds'], df['y'], label='實際值', color='blue', linewidth=2)
    
    all_forecast = pd.concat([historical_forecast, future_forecast])
    plt.plot(all_forecast['ds'], all_forecast['yhat'], label='預測值', color='orange', linewidth=2)
    
    plt.title('臺北市寵物登記數預測結果 (2015-2025)', fontsize=14, pad=15)
    plt.xlabel('年份', fontsize=12)
    plt.ylabel('登記數量', fontsize=12)
    plt.legend(prop={'size': 12})
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate()
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    
    plt.tight_layout()
    plt.show()

def main():
    setup_style()
    df = load_data()
    df = create_features(df)
    
    features_to_scale = [
        'monthly_budget', 'spay_ratio', 'ma3', 'month_avg', 'year_trend'
    ]
    
    df, scaler = scale_features(df, features_to_scale)
    scaled_features = [f'{col}_scaled' for col in features_to_scale]
    
    train_df, test_df = split_data(df)
    
    model = create_prophet_model()
    model = train_model(model, train_df, scaled_features)
    
    test_forecast, historical_forecast, future_forecast = generate_predictions(
        model, df, test_df, scaled_features
    )
    
    y_true = test_df['y'].values
    y_pred = test_forecast['yhat'].values
    
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    mean_error = np.mean(np.abs(y_true - y_pred))
    
    print("\n模型評估指標:")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"R平方: {r2:.4f}")
    print(f"平均每月預測誤差範圍: ±{mean_error:.2f}")
    
    print("\n2024年12月~2025年12月預測值:")
    for _, row in future_forecast[['ds', 'yhat']].iterrows():
        print(f"{row['ds'].strftime('%Y年%m月')}: {int(row['yhat'])}")
    
    plot_results(df, historical_forecast, future_forecast)

if __name__ == "__main__":
    main()