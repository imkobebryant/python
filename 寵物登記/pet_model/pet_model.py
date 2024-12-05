import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class MultiCityPetPredictor:
    def __init__(self, csv_file: str):
        """初始化預測器"""
        self.df = pd.read_csv(csv_file)
        self.scaler = StandardScaler()
        self.results_df = pd.DataFrame()
        
        # 設置matplotlib中文字體
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        
    def prepare_features(self, county_data):
        """增強特徵工程"""
        features = county_data.copy()
        
        # 添加lag特徵
        features['prev_year_registrations'] = features.groupby('County')['Registrations'].shift(1)
        features['prev_year_neutering_rate'] = features.groupby('County')['Neutering Rate'].shift(1)
        
        # 添加趨勢特徵
        features['registration_growth'] = features.groupby('County')['Registrations'].pct_change()
        features['neutering_rate_growth'] = features.groupby('County')['Neutering Rate'].pct_change()
        
        # 添加移動平均
        features['registration_ma'] = features.groupby('County')['Registrations'].rolling(window=3).mean().reset_index(0, drop=True)
        
        # 移除NaN值
        features = features.dropna()
        
        # 選擇特徵
        X = features[['Year', 'Neutering Rate', 'prev_year_registrations', 
                     'prev_year_neutering_rate', 'registration_growth', 
                     'neutering_rate_growth', 'registration_ma']]
        y = features['Registrations']
        
        return X, y, features

    def analyze_county(self, county: str, future_year: int, future_rate: float):
        """分析單一縣市"""
        print(f"\n分析 {county} 的數據...")
        
        # 準備數據
        county_data = self.df[self.df['County'] == county].copy()
        X, y, features = self.prepare_features(county_data)
        
        # 標準化特徵
        X_scaled = self.scaler.fit_transform(X)
        
        # 分割數據
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # 初始化模型
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(random_state=42),
            'XGBoost': XGBRegressor(random_state=42),
            'SVR': SVR(kernel='rbf')
        }
        
        best_model = None
        best_score = -np.inf
        model_results = {}
        
        # 訓練和評估所有模型
        for name, model in models.items():
            # 訓練模型
            model.fit(X_train, y_train)
            
            # 預測
            y_pred = model.predict(X_test)
            
            # 計算指標
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            cv_score = cross_val_score(model, X_scaled, y, cv=5, scoring='r2').mean()
            
            model_results[name] = {
                'r2': r2,
                'rmse': rmse,
                'cv_score': cv_score
            }
            
            # 更新最佳模型
            if cv_score > best_score:
                best_score = cv_score
                best_model = (name, model)
        
        # 使用最佳模型進行未來預測
        best_model_name, best_model_obj = best_model
        future_pred = self._predict_future(
            best_model_obj, county, future_year, future_rate, features
        )
        
        # 保存結果
        result = {
            'County': county,
            'Best Model': best_model_name,
            'Best CV Score': best_score,
            'Future Year': future_year,
            'Future Rate': future_rate,
            'Predicted Registration': future_pred,
            'Current Registration': county_data.iloc[-1]['Registrations'],
            'Prediction Change %': ((future_pred - county_data.iloc[-1]['Registrations']) / 
                                  county_data.iloc[-1]['Registrations'] * 100)
        }
        
        return result, model_results

    def _predict_future(self, model, county, future_year, future_rate, features):
        """預測未來登記數"""
        latest_data = features.sort_values('Year').tail(1)
        
        pred_features = pd.DataFrame({
            'Year': [future_year],
            'Neutering Rate': [future_rate],
            'prev_year_registrations': [latest_data['Registrations'].values[0]],
            'prev_year_neutering_rate': [latest_data['Neutering Rate'].values[0]],
            'registration_growth': [0],
            'neutering_rate_growth': [0],
            'registration_ma': [latest_data['Registrations'].values[0]]
        })
        
        pred_features_scaled = self.scaler.transform(pred_features)
        return model.predict(pred_features_scaled)[0]

    def analyze_all_cities(self, future_year: int, future_rate: float):
        """分析所有指定的縣市"""
        # 選擇要分析的縣市
        target_cities = ['全臺', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', 
                        '高雄市', '新竹市', '新竹縣', '南投縣', '嘉義市', 
                        '嘉義縣', '宜蘭縣', '花蓮縣']
        
        results = []
        all_model_results = {}
        
        for city in target_cities:
            if city in self.df['County'].unique():
                try:
                    result, model_results = self.analyze_county(city, future_year, future_rate)
                    results.append(result)
                    all_model_results[city] = model_results
                    print(f"{city} 分析完成")
                except Exception as e:
                    print(f"分析 {city} 時發生錯誤: {str(e)}")
        
        # 轉換為DataFrame
        self.results_df = pd.DataFrame(results)
        
        # 保存結果 - 使用 utf-8-sig 編碼以正確處理中文
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_df.to_csv(f'prediction_results_{timestamp}.csv', 
                              index=False, 
                              encoding='utf-8-sig')
        
        return self.results_df, all_model_results

    def plot_results(self):
        """繪製預測結果視覺化"""
        if self.results_df.empty:
            print("沒有可用的結果來繪製圖表")
            return
        
        # 創建圖表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        # 預測變化百分比條形圖
        sns.barplot(data=self.results_df, x='County', y='Prediction Change %', ax=ax1)
        ax1.set_title('各縣市預測登記數變化百分比')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
        
        # 當前vs預測登記數對比圖
        width = 0.35
        x = np.arange(len(self.results_df))
        ax2.bar(x - width/2, self.results_df['Current Registration'], width, label='當前登記數')
        ax2.bar(x + width/2, self.results_df['Predicted Registration'], width, label='預測登記數')
        ax2.set_xticks(x)
        ax2.set_xticklabels(self.results_df['County'], rotation=45)
        ax2.set_title('當前vs預測登記數對比')
        ax2.legend()
        
        plt.tight_layout()
        
        # 保存圖表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f'prediction_visualization_{timestamp}.png', 
                   dpi=300, 
                   bbox_inches='tight',
                   encoding='utf-8')
        plt.close()

def main():
    # 初始化預測器
    predictor = MultiCityPetPredictor('2023-2009pet_data.csv')
    
    # 設定預測參數
    FUTURE_YEAR = 2024
    FUTURE_RATE = 50.0  # 假設絕育率為50%
    
    # 執行分析
    print(f"開始分析... 預測{FUTURE_YEAR}年，絕育率{FUTURE_RATE}%的情況")
    results_df, model_results = predictor.analyze_all_cities(FUTURE_YEAR, FUTURE_RATE)
    
    # 輸出結果摘要
    print("\n分析結果摘要:")
    print("=" * 80)
    print(results_df[['County', 'Best Model', 'Best CV Score', 
                     'Predicted Registration', 'Prediction Change %']]
          .to_string(index=False))
    
    # 繪製視覺化結果
    predictor.plot_results()
    
    print("\n分析完成！結果已保存到CSV文件和圖表中。")

if __name__ == "__main__":
    main()