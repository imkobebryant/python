from ttkthemes import ThemedTk
from tkinter import ttk

class Window(ThemedTk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title('呂安杰的lesson4作業')
        style = ttk.Style(self)        

        topFrame = ttk.Frame(self,borderwidth=1,relief='solid')
        btn1 = ttk.Button(topFrame,text="。")
        btn1.pack(side='left',expand=True,fill='x',padx=(10,30))
        btn2 = ttk.Button(topFrame,text="。")
        btn2.pack(side='left',expand=True,fill='x',padx=1)
        btn3 = ttk.Button(topFrame,text="。")
        btn3.pack(side='left',expand=True,fill='x',padx=(30,10))
        topFrame.pack(padx=10,pady=10,ipadx=10,ipady=10,expand=True,fill='x')     

        bottomFrame = ttk.Frame(self,borderwidth=1,relief='solid')
        btn1 = ttk.Button(bottomFrame,text="。")
        btn1.pack(side='top',expand=True,fill='x',padx=10,ipady=30,pady=(5,0))
        btn2 = ttk.Button(bottomFrame,text="。")
        btn2.pack(side='top',expand=True,fill='x',padx=10,ipady=15)
        btn3 = ttk.Button(bottomFrame,text="。")
        btn3.pack(side='top',expand=True,fill='x',padx=10,ipady=15,pady=(0,5))
        bottomFrame.pack(side='left',padx=10,pady=(0,10),ipadx=10,ipady=15,expand=True,fill='x')

        bottomFrame = ttk.Frame(self,borderwidth=1,relief='solid')
        btn1 = ttk.Button(bottomFrame,text="。")
        btn1.pack(side='top',expand=True,fill='x',padx=10,ipady=25,pady=(5,0))
        btn2 = ttk.Button(bottomFrame,text="。")
        btn2.pack(side='top',expand=True,fill='x',padx=10,ipady=10)
        btn3 = ttk.Button(bottomFrame,text="。")
        btn3.pack(side='top',expand=True,fill='x',padx=10,ipady=25,pady=(0,5))
        bottomFrame.pack(side='left',pady=(0,10),ipadx=10,ipady=15,expand=True,fill='x')

        bottomFrame = ttk.Frame(self,borderwidth=1,relief='solid')
        btn1 = ttk.Button(bottomFrame,text="。")
        btn1.pack(side='top',expand=True,fill='x',padx=10,ipady=20,pady=(5,0))
        btn2 = ttk.Button(bottomFrame,text="。")
        btn2.pack(side='top',expand=True,fill='x',padx=10,ipady=20)
        btn3 = ttk.Button(bottomFrame,text="。")
        btn3.pack(side='top',expand=True,fill='x',padx=10,ipady=20,pady=(0,5))
        bottomFrame.pack(side='left',padx=10,pady=(0,10),ipadx=10,ipady=15,expand=True,fill='x')

def main():
    window = Window(theme='awlight')
    window.mainloop()

if __name__ == '__main__':
    main()