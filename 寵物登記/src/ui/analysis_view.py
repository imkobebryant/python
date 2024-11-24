import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from .map_renderer import TaiwanMapRenderer
from concurrent.futures import ThreadPoolExecutor
import threading

class AnalysisView(ttk.Frame):
    """高效能分析視圖"""
    
    def __init__(self, master, data_manager):
        super().__init__(master)
        self.data_manager = data_manager
        self._update_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # 設定matplotlib
        self._setup_matplotlib()
        
        # 初始化UI
        self._initialize_ui()
        
        # 註冊定期更新任務
        self._schedule_updates()
        
    def _setup_matplotlib(self):
        """設定matplotlib配置"""
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 預建立圖表物件
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.figure.set_tight_layout(True)
        
        # 預建立子圖
        self.gs = self.figure.add_gridspec(2, 2, height_ratios=[1.5, 1])
        self.axes = {
            'trend': self.figure.add_subplot(self.gs[0, :]),
            'rate': self.figure.add_subplot(self.gs[1, 0]),
            'ratio': self.figure.add_subplot(self.gs[1, 1])
        }
        
    def _initialize_ui(self):
        """初始化UI元件"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 建立左側面板
        self._create_left_panel()
        
        # 建立右側面板
        self._create_right_panel()
        
        # 初始化快取
        self._chart_data = None
        self._current_county = None
        
        # 綁定事件
        self._bind_events()
        
    def _create_left_panel(self):
        """建立左側面板"""
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky='ns', padx=10)
        
        # 建立選擇器框架
        self._create_selector_frame(left_frame)
        
        # 建立地圖框架
        self._create_map_frame(left_frame)
        
    def _create_selector_frame(self, parent):
        """建立縣市選擇器"""
        selector_frame = ttk.LabelFrame(parent, text="選擇縣市", padding=5)
        selector_frame.pack(fill='x', pady=5)
        
        county_frame = ttk.Frame(selector_frame)
        county_frame.pack(fill='x', pady=5)
        
        ttk.Label(county_frame, text="縣市:").pack(side='left')
        
        # 使用資料管理器提供的已排序縣市列表
        self.selected_county = tk.StringVar()
        counties = self.data_manager.counties  # 這裡會自動使用正確的順序
        
        self.county_cb = ttk.Combobox(
            county_frame,
            textvariable=self.selected_county,
            values=counties,
            state='readonly',
            width=15
        )
        self.county_cb.pack(side='left', padx=5)
        
        # 設定預設選擇為第一個縣市
        self.selected_county.set(counties[0] if counties else "")
        
    def _create_map_frame(self, parent):
        """建立地圖框架"""
        map_frame = ttk.LabelFrame(parent, text="台灣地圖", padding=5)
        map_frame.pack(fill='both', expand=True, pady=5)
        
        self.map_renderer = TaiwanMapRenderer(map_frame, self.data_manager)
        self.map_renderer.pack(fill='both', expand=True)
        
    def _create_right_panel(self):
        """建立右側面板"""
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # 建立表格
        self._create_tree_view(right_frame)
        
        # 建立圖表
        self._create_chart_frame(right_frame)
        
    def _create_tree_view(self, parent):
        """建立表格視圖"""
        tree_frame = ttk.LabelFrame(parent, text="詳細資料", padding=10)
        tree_frame.grid(row=0, column=0, sticky='ew', pady=5)
        
        # 建立捲軸
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 建立表格
        columns = ('year', 'county', 'registrations', 'deregistrations', 
                  'neutered', 'rate')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=5,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # 設定表頭
        headers = ['年份', '縣市', '登記數', '註銷數', '絕育數', '絕育率(%)']
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=100, anchor='center')
        
        self.tree.pack(fill='x', expand=True)
        
    def _create_chart_frame(self, parent):
        """建立圖表框架"""
        self.chart_frame = ttk.LabelFrame(parent, text="圖表分析", padding=10)
        self.chart_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        
        # 建立畫布
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def _schedule_updates(self):
        """排程定期更新"""
        def update_task():
            if self._current_county != self.selected_county.get():
                self.update_data()
            self.after(1000, update_task)
            
        self.after(1000, update_task)
        
    def _bind_events(self):
        """綁定事件處理"""
        self.selected_county.trace('w', lambda *args: self.after(100, self._on_county_selected))
        self.map_renderer.on_county_select = self._on_map_county_selected
        
    def _on_county_selected(self):
        """處理縣市選擇事件"""
        with self._update_lock:
            selected = self.selected_county.get()
            if selected != self._current_county:
                self._current_county = selected
                self.map_renderer.select_county(selected)
                self._executor.submit(self.update_data)
                
    def _on_map_county_selected(self, county):
        """處理地圖選擇事件"""
        if county != self.selected_county.get():
            self.selected_county.set(county)
            
    def update_data(self):
        """更新資料顯示"""
        with self._update_lock:
            self._update_tree_view()
            self._update_charts()
            
    def _update_tree_view(self):
        """更新表格資料"""
        county = self.selected_county.get()
        if not county:
            return
            
        stats = self.data_manager.get_county_stats(county)
        if not stats:
            return
            
        self.tree.delete(*self.tree.get_children())
        for record in stats.records:
            self.tree.insert('', 'end', values=record)
            
    def _update_charts(self):
        """更新圖表"""
        county = self.selected_county.get()
        if not county:
            return
            
        stats = self.data_manager.get_county_stats(county)
        if not stats:
            return
            
        # 更新趨勢圖
        self._plot_trend_chart(stats)
        
        # 更新比率圖
        self._plot_rate_charts(stats)
        
        # 重繪圖表
        self.canvas.draw_idle()
        
    def _plot_trend_chart(self, stats):
        """繪製趨勢圖"""
        ax = self.axes['trend']
        ax.clear()
        
        # 反轉年份順序（從舊到新）
        years = [str(y) for y in reversed(stats.years)]
        registrations = stats.registrations[::-1]  # 反轉數據順序
        deregistrations = stats.deregistrations[::-1]  # 反轉數據順序
        
        ax.plot(years, registrations, 'bo-', label='登記數', linewidth=2)
        ax.plot(years, deregistrations, 'ro-', label='註銷數', linewidth=2)
        
        ax.set_title(f'{self.selected_county.get()} 寵物登記與註銷趨勢')
        ax.set_xlabel('年份')
        ax.set_ylabel('數量')
        ax.legend()
        ax.grid(True)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
    def _plot_rate_charts(self, stats):
        """繪製比率圖"""
        # 反轉年份和數據順序
        years = [str(y) for y in reversed(stats.years)]
        neutering_rates = stats.neutering_rates[::-1]
        neutered = stats.neutered[::-1]
        registrations = stats.registrations[::-1]
        
        # 絕育率趨勢
        ax_rate = self.axes['rate']
        ax_rate.clear()
        ax_rate.plot(years, neutering_rates, 'go-', linewidth=2)
        ax_rate.set_title(f'{self.selected_county.get()} 絕育率趨勢')
        ax_rate.set_xlabel('年份')
        ax_rate.set_ylabel('絕育率 (%)')
        ax_rate.grid(True)
        plt.setp(ax_rate.xaxis.get_majorticklabels(), rotation=45)
        
        # 絕育比率
        ax_ratio = self.axes['ratio']
        ax_ratio.clear()
        ratio = np.divide(neutered, registrations) * 100
        ax_ratio.plot(years, ratio, 'mo-', linewidth=2)
        ax_ratio.set_title(f'{self.selected_county.get()} 絕育數與登記數比率')
        ax_ratio.set_xlabel('年份')
        ax_ratio.set_ylabel('比率 (%)')
        ax_ratio.grid(True)
        plt.setp(ax_ratio.xaxis.get_majorticklabels(), rotation=45)
            
    def destroy(self):
        """清理資源"""
        # 停止執行緒池
        self._executor.shutdown(wait=True)
        
        # 清理matplotlib資源
        plt.close(self.figure)
        
        # 呼叫父類的destroy
        super().destroy()