import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from src.ui.analysis_view import AnalysisView
from src.data.data_source import PetDataManager

class MainWindow(ThemedTk):
    """主視窗類別"""
    def __init__(self):
        """初始化主視窗"""
        super().__init__(theme="arc")
        self.title('寵物登記與絕育分析')
        self.geometry('1300x720')
        
        # 初始化資料管理器
        self.data_manager = PetDataManager()
        
        # 建立主視圖
        self.view = AnalysisView(self, self.data_manager)
        self.view.pack(fill='both', expand=True)
        
        # 設定關閉視窗事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """處理視窗關閉事件"""
        # 停止所有地圖更新
        if hasattr(self.view.map_renderer.map_widget, "after_id"):
            self.after_cancel(self.view.map_renderer.map_widget.after_id)
            
        # 清理資源
        self.view.map_renderer.map_widget.destroy()
        
        # 關閉視窗
        self.quit()
        self.destroy()

def main():
    """程式進入點"""
    app = MainWindow()
    app.mainloop()

if __name__ == '__main__':
    main()