import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

class PetRegistrationPredictor:
    def __init__(self, data_path):
        """初始化預測器"""
        self.df = pd.read_csv(data_path)
        # 選擇要預測的地區
        self.target_regions = ['全臺', '臺北市', '新北市', '桃園市', '臺中市', 
                             '臺南市', '高雄市', '新竹市', '新竹縣', '嘉義市', 
                             '嘉義縣', '基隆市', '彰化縣', '南投縣']
        self.models = {}
        self.metrics = {}
        
    def prepare_data(self, region):
        """準備特定地區的訓練數據"""
        region_data = self.df[self.df['County'] == region].copy()
        region_data['Year_Num'] = region_data['Year'] - 2009  # 2009年為基準年
        
        X = region_data[['Year_Num', 'Neutering Rate']]
        y = region_data['Registrations']
        
        return X, y

    def train_model(self, region):
        """訓練特定地區的模型"""
        X, y = self.prepare_data(region)
        
        # 分割訓練集和測試集 (70/30)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        # 訓練模型
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # 計算模型指標
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        metrics = {
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred))
        }
        
        return model, metrics

    def train_all_models(self):
        """訓練所有地區的模型"""
        for region in self.target_regions:
            model, metrics = self.train_model(region)
            self.models[region] = model
            self.metrics[region] = metrics
            print(f"完成 {region} 模型訓練")

    def predict(self, region, neutering_rate):
        """預測2024年的登記數"""
        if region not in self.models:
            return None, "此地區無可用模型"
        
        # 2024年對應的相對年份數值
        year_num = 2024 - 2009
        
        # 進行預測
        prediction = self.models[region].predict([[year_num, neutering_rate]])[0]
        
        # 計算預測區間
        X, y = self.prepare_data(region)
        y_pred = self.models[region].predict(X)
        prediction_std = np.std(y - y_pred)
        confidence_interval = 1.96 * prediction_std
        
        result = {
            'region': region,
            'predicted_value': int(prediction),
            'confidence_interval': (
                int(prediction - confidence_interval),
                int(prediction + confidence_interval)
            ),
            'metrics': self.metrics[region]
        }
        
        return result

# 主程式執行部分
def main():
    # 初始化預測器
    predictor = PetRegistrationPredictor('2023-2009pet_data.csv')
    
    # 訓練所有模型
    print("開始訓練模型...")
    predictor.train_all_models()
    print("\n模型訓練完成！")
    
    while True:
        # 顯示可用地區
        print("\n可選擇的地區：")
        for i, region in enumerate(predictor.target_regions, 1):
            print(f"{i}. {region}")
        
        # 使用者輸入
        try:
            region_idx = int(input("\n請選擇地區 (輸入編號，0退出)： ")) - 1
            if region_idx == -1:
                break
            if region_idx < 0 or region_idx >= len(predictor.target_regions):
                print("無效的選擇，請重試")
                continue
                
            neutering_rate = float(input("請輸入預期絕育率 (%)： "))
            if not (0 <= neutering_rate <= 100):
                print("絕育率必須在0-100之間")
                continue
            
            # 獲取預測結果
            region = predictor.target_regions[region_idx]
            result = predictor.predict(region, neutering_rate)
            
            # 顯示結果
            print(f"\n{region} 2024年預測結果：")
            print("=" * 50)
            print(f"預測登記數：{result['predicted_value']:,}")
            print(f"95% 預測區間：{result['confidence_interval'][0]:,} 到 {result['confidence_interval'][1]:,}")
            print("\n模型評估指標：")
            print(f"訓練集 R² 分數：{result['metrics']['train_r2']:.4f}")
            print(f"測試集 R² 分數：{result['metrics']['test_r2']:.4f}")
            print(f"訓練集 RMSE：{result['metrics']['train_rmse']:.2f}")
            print(f"測試集 RMSE：{result['metrics']['test_rmse']:.2f}")
            
        except ValueError:
            print("輸入格式錯誤，請重試")
        except Exception as e:
            print(f"發生錯誤：{str(e)}")

if __name__ == "__main__":
    main()