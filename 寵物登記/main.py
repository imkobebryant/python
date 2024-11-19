import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pet_datasource import PetDataSource

class PetAnalysisWindow(ThemedTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('寵物登記與絕育分析')
        self.geometry('1400x900')  # 增加視窗大小以容納更多資訊
        self.datasource = PetDataSource()
        
        # 設定中文字型
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # Style configuration
        style = ttk.Style(self)
        style.configure('TopFrame.TLabel', font=('Microsoft JhengHei', 20))

        # 設定關閉視窗事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._create_widgets()

    def on_closing(self):
        """處理視窗關閉事件"""
        plt.close('all')  # 關閉所有matplotlib圖表
        self.quit()  # 結束mainloop
        self.destroy()  # 銷毀視窗
        
    def _create_widgets(self):
        # Top Frame
        top_frame = ttk.Frame(self)
        ttk.Label(top_frame, text='寵物登記與絕育統計分析', style='TopFrame.TLabel').pack()
        top_frame.pack(padx=20, pady=20)
        
        # Main Content Frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left Frame for Controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='y', padx=10)
        
        # Selector Frame
        selector_frame = ttk.LabelFrame(left_frame, text="資料選擇", padding=10)
        selector_frame.pack(fill='x', pady=5)
        
        # Year Combobox
        years = self.datasource.get_years()
        self.selected_year = tk.StringVar()
        year_frame = ttk.Frame(selector_frame)
        year_frame.pack(fill='x', pady=5)
        ttk.Label(year_frame, text="年份:").pack(side='left')
        year_cb = ttk.Combobox(year_frame, textvariable=self.selected_year, values=years, state='readonly')
        self.selected_year.set(years[0])
        year_cb.pack(side='left', padx=5)
        year_cb.bind('<<ComboboxSelected>>', self.update_data)
        
        # County Combobox
        counties = self.datasource.get_counties()
        self.selected_county = tk.StringVar()
        county_frame = ttk.Frame(selector_frame)
        county_frame.pack(fill='x', pady=5)
        ttk.Label(county_frame, text="縣市:").pack(side='left')
        county_cb = ttk.Combobox(county_frame, textvariable=self.selected_county, values=counties, state='readonly')
        self.selected_county.set(counties[0])
        county_cb.pack(side='left', padx=5)
        county_cb.bind('<<ComboboxSelected>>', self.update_data)
        
        # Right Frame for Data Display
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Tree View
        tree_frame = ttk.LabelFrame(right_frame, text="詳細資料", padding=10)
        tree_frame.pack(fill='x', pady=5)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')
        
        columns = ('year', 'county', 'registrations', 'deregistrations', 'neutered', 'rate')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)
        
        self.tree.heading('year', text='年份')
        self.tree.heading('county', text='縣市')
        self.tree.heading('registrations', text='登記數')
        self.tree.heading('deregistrations', text='註銷數')
        self.tree.heading('neutered', text='絕育數')
        self.tree.heading('rate', text='絕育率(%)')
        
        for col in columns:
            self.tree.column(col, width=100, anchor='center')
        
        self.tree.pack(fill='x')
        
        # Chart Frame
        self.chart_frame = ttk.LabelFrame(right_frame, text="圖表分析", padding=10)
        self.chart_frame.pack(fill='both', expand=True, pady=5)
        
        self.update_data()
        
    def update_data(self, event=None):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update tree view based on selected county
        county_data = self.datasource.get_county_data(self.selected_county.get())
        for record in county_data:
            self.tree.insert('', 'end', values=record)
        
        # Update chart
        self.update_chart()
        
    def update_chart(self):
        try:
            # Clear existing chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # 創建新圖表，調整大小和內邊距
            fig = plt.figure(figsize=(14, 10))  # 加大圖表高度
            
            # 創建子圖，調整間距
            gs = plt.GridSpec(2, 2, height_ratios=[1.5, 1])
            gs.update(hspace=0.8, wspace=0.3)  # 增加子圖之間的垂直間距
            
            # Get data for selected county
            county_data = self.datasource.get_county_data(self.selected_county.get())
            years = [str(record[0]) for record in reversed(county_data)]
            registrations = [record[2] for record in reversed(county_data)]
            deregistrations = [record[3] for record in reversed(county_data)]
            neutered = [record[4] for record in reversed(county_data)]
            rates = [record[5] for record in reversed(county_data)]
            
            # 1. Registration and Deregistration Trend
            ax1 = fig.add_subplot(gs[0, :])
            ax1.plot(years, registrations, marker='o', color='blue', linewidth=2, label='登記數')
            ax1.plot(years, deregistrations, marker='s', color='red', linewidth=2, label='註銷數')
            ax1.set_title(f'{self.selected_county.get()} 寵物登記與註銷趨勢', fontsize=12, pad=15)
            ax1.set_xlabel('年份', fontsize=10, labelpad=10)
            ax1.set_ylabel('數量', fontsize=10, labelpad=10)
            ax1.grid(True, linestyle='--', alpha=0.7)
            ax1.legend(loc='upper right')
            
            # 調整x軸標籤角度和位置
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 2. Neutering Rate Trend
            ax2 = fig.add_subplot(gs[1, 0])
            ax2.plot(years, rates, marker='o', color='green', linewidth=2)
            ax2.set_title(f'{self.selected_county.get()} 絕育率趨勢', fontsize=12, pad=15)
            ax2.set_xlabel('年份', fontsize=10, labelpad=10)
            ax2.set_ylabel('絕育率 (%)', fontsize=10, labelpad=10)
            ax2.grid(True, linestyle='--', alpha=0.7)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 3. Neutering vs Registration Ratio
            ax3 = fig.add_subplot(gs[1, 1])
            ratio = [n/r*100 for n, r in zip(neutered, registrations)]
            ax3.plot(years, ratio, marker='o', color='purple', linewidth=2)
            ax3.set_title(f'{self.selected_county.get()} 絕育數與登記數比率', fontsize=12, pad=15)
            ax3.set_xlabel('年份', fontsize=10, labelpad=10)
            ax3.set_ylabel('比率 (%)', fontsize=10, labelpad=10)
            ax3.grid(True, linestyle='--', alpha=0.7)
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 調整整體布局，給標題和x軸標籤預留更多空間
            fig.subplots_adjust(left=0.1, right=0.95, bottom=0.2, top=0.95)
            
            # Embed chart in window
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            print(f"Error updating chart: {e}")

def main():
    window = PetAnalysisWindow(theme="arc")
    window.mainloop()

if __name__ == '__main__':
    main()