from ttkthemes import ThemedTk
from tkinter import ttk

class Window(ThemedTk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title('呂安杰的lesson4作業')
        style = ttk.Style(self) 

#=============================== TopFrame =====================================
        topFrame = ttk.Frame(self,borderwidth=1,relief='solid')
        self.btn1 = ttk.Button(topFrame,text="Hello",command=self.user_click1
        )
        self.btn1.pack(side='left',expand=True,fill='x',padx=(10,30))
        btn2 = ttk.Button(topFrame,text="。")
        btn2.bind('<ButtonRelease>',self.button_click)
        btn2.pack(side='left',expand=True,fill='x',padx=1)
        btn3 = ttk.Button(topFrame,text="。")
        btn3.bind('<ButtonRelease>',self.button_click)
        btn3.pack(side='left',expand=True,fill='x',padx=(30,10))
        topFrame.pack(padx=10,pady=10,ipadx=10,ipady=10,expand=True,fill='x')     
#==============================End TopFrame ===================================

#============================= BottomFrame 1 ==================================
        bottomFrame1 = ttk.Frame(self,borderwidth=1,relief='solid')
        btn11 = ttk.Button(bottomFrame1,text="。")
        btn11.pack(side='top',expand=True,fill='x',padx=10,ipady=30,pady=(5,0))
        btn12 = ttk.Button(bottomFrame1,text="。")
        btn12.pack(side='top',expand=True,fill='x',padx=10,ipady=15)
        btn13 = ttk.Button(bottomFrame1,text="。")
        btn13.pack(side='top',expand=True,fill='x',padx=10,ipady=15,pady=(0,5))
        bottomFrame1.pack(side='left',padx=10,pady=(0,10),ipadx=10,ipady=15,expand=True,fill='x')
#==========================End BottomFrame 1 ==================================
#============================= BottomFrame 2 ==================================
        bottomFrame2 = ttk.Frame(self,borderwidth=1,relief='solid')
        btn21 = ttk.Button(bottomFrame2,text="。")
        btn21.pack(side='top',expand=True,fill='x',padx=10,ipady=25,pady=(5,0))
        btn22 = ttk.Button(bottomFrame2,text="。")
        btn22.pack(side='top',expand=True,fill='x',padx=10,ipady=10)
        btn23 = ttk.Button(bottomFrame2,text="。")
        btn23.pack(side='top',expand=True,fill='x',padx=10,ipady=25,pady=(0,5))
        bottomFrame2.pack(side='left',pady=(0,10),ipadx=10,ipady=15,expand=True,fill='x')
#==========================End BottomFrame 2 ==================================
#============================= BottomFrame 3 ==================================
        bottomFrame3 = ttk.Frame(self,borderwidth=1,relief='solid')
        btn31 = ttk.Button(bottomFrame3,text="。")
        btn31.pack(side='top',expand=True,fill='x',padx=10,ipady=20,pady=(5,0))
        btn32 = ttk.Button(bottomFrame3,text="。")
        btn32.pack(side='top',expand=True,fill='x',padx=10,ipady=20)
        btn33 = ttk.Button(bottomFrame3,text="。")
        btn33.pack(side='top',expand=True,fill='x',padx=10,ipady=20,pady=(0,5))
        bottomFrame3.pack(side='left',padx=10,pady=(0,10),ipadx=10,ipady=15,expand=True,fill='x')
#==========================End BottomFrame 3 ==================================

    def user_click1(self):
        self.btn1.configure(text="被按了")
        print('Hello!1')

    def button_click(self,event):
        print(type(event))
        print(event.x)
        print(event.y)
        print(event.width)
        event.widget.configure(text="被按了")

def main():
    window = Window(theme='awlight')
    window.mainloop()

if __name__ == '__main__':
    main()