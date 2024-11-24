import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import threading
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CountyStats:
    """縣市統計資料類別"""
    county: str
    years: np.ndarray
    registrations: np.ndarray
    deregistrations: np.ndarray
    neutered: np.ndarray
    neutering_rates: np.ndarray
    
    @property
    def records(self) -> List[Tuple]:
        """將資料轉換為記錄格式"""
        return [
            (year, self.county, reg, dereg, neu, rate)
            for year, reg, dereg, neu, rate in zip(
                self.years,
                self.registrations,
                self.deregistrations,
                self.neutered,
                self.neutering_rates
            )
        ]

class PetDataManager:
    """高效能寵物資料管理類別"""
    
    def __init__(self, csv_file: str = '2023-2009pet_data.csv'):
        """
        初始化資料管理器
        
        Args:
            csv_file: CSV 資料檔案路徑
        """
        # 定義縣市順序
        self._county_order = [
            "基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", 
            "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市",
            "嘉義縣", "臺南市", "高雄市", "屏東縣", "臺東縣", "花蓮縣",
            "宜蘭縣", "澎湖縣", "金門縣", "連江縣"
        ]
        
        self._lock = threading.Lock()
        self._stats_cache = {}
        self._initialize_data(csv_file)
        
    def _initialize_data(self, csv_file: str):
        """初始化並預處理資料"""
        # 使用最佳化的CSV讀取選項
        self.df = pd.read_csv(
            csv_file,
            dtype={
                'Year': np.int32,
                'Registrations': np.int32,
                'Deregistrations': np.int32,
                'Neutered': np.int32,
                'Neutering Rate': np.float32
            }
        )
        
        # 過濾並預處理資料
        mask = self.df['County'] != '全臺'
        self.df = self.df[mask].copy()
        
        # 預計算並儲存常用數據
        self._precompute_data()
        
    def _precompute_data(self):
        """預計算所有統計資料"""
        # 預先排序資料以提高效能
        self.df.sort_values(['County', 'Year'], ascending=[True, False], inplace=True)
        
        # 使用線程池進行並行計算
        with ThreadPoolExecutor() as executor:
            # 非同步預計算每個縣市的統計資料
            futures = []
            for county in self.df['County'].unique():
                futures.append(
                    executor.submit(self._compute_county_stats, county)
                )
            
            # 等待所有計算完成
            for future in futures:
                stats = future.result()
                self._stats_cache[stats.county] = stats
        
        # 預計算年度統計
        self._yearly_stats = defaultdict(dict)
        for year in self.df['Year'].unique():
            year_data = self.df[self.df['Year'] == year]
            self._yearly_stats[year] = {
                'total_reg': year_data['Registrations'].sum(),
                'total_dereg': year_data['Deregistrations'].sum(),
                'total_neutered': year_data['Neutered'].sum(),
                'avg_rate': year_data['Neutering Rate'].mean()
            }
            
        # 快取其他常用資料
        self._years = sorted(self.df['Year'].unique(), reverse=True)
        self._available_counties = set(self.df['County'].unique())
        
    def _compute_county_stats(self, county: str) -> CountyStats:
        """
        計算單一縣市的統計資料
        
        Args:
            county: 縣市名稱
            
        Returns:
            CountyStats: 縣市統計資料物件
        """
        county_data = self.df[self.df['County'] == county]
        
        # 轉換為 NumPy 陣列以提高效能
        return CountyStats(
            county=county,
            years=county_data['Year'].values,
            registrations=county_data['Registrations'].values,
            deregistrations=county_data['Deregistrations'].values,
            neutered=county_data['Neutered'].values,
            neutering_rates=county_data['Neutering Rate'].values
        )
    
    @property
    def years(self) -> List[int]:
        """
        取得年份列表
        
        Returns:
            List[int]: 排序後的年份列表
        """
        return self._years
    
    @property
    def counties(self) -> List[str]:
        """
        取得依照指定順序排序的縣市列表
        
        Returns:
            List[str]: 依照指定順序排序的縣市列表
        """
        return [county for county in self._county_order if county in self._available_counties]
    
    @lru_cache(maxsize=32)
    def get_county_data(self, county: str) -> List[Tuple]:
        """
        取得縣市資料
        
        Args:
            county: 縣市名稱
            
        Returns:
            List[Tuple]: 該縣市的所有年度資料
        """
        stats = self._stats_cache.get(county)
        return stats.records if stats else []
    
    @lru_cache(maxsize=32)
    def get_yearly_summary(self, year: int) -> Dict[str, float]:
        """
        取得年度統計
        
        Args:
            year: 年份
            
        Returns:
            Dict[str, float]: 包含該年度統計資料的字典
        """
        return self._yearly_stats.get(year, {})
    
    def get_county_stats(self, county: str) -> Optional[CountyStats]:
        """
        取得縣市統計資料
        
        Args:
            county: 縣市名稱
            
        Returns:
            Optional[CountyStats]: 縣市統計資料物件，如果縣市不存在則返回None
        """
        return self._stats_cache.get(county)
    
    def get_pet_data(self, county: str) -> List[Tuple]:
        """
        取得特定縣市的所有資料（相容性方法）
        
        Args:
            county: 縣市名稱
            
        Returns:
            List[Tuple]: 該縣市的所有年度資料
        """
        return self.get_county_data(county)
    
    def clear_cache(self):
        """清除所有快取資料"""
        with self._lock:
            self.get_county_data.cache_clear()
            self.get_yearly_summary.cache_clear()
            self._stats_cache.clear()
            
    def __del__(self):
        """解構時清理資源"""
        self.clear_cache()