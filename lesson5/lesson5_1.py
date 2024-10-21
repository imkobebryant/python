from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter as tk
from tkinter.messagebox import showinfo

class Window(ThemedTk):
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        #=======================style======================
        style=ttk.Style(self)
        style.configure('Topframe',font=('Helvetica',20))
        #===================End style======================

        #===================Top frame======================

        topframe=ttk.Frame(self)
        ttk.Label(topframe,text='個人資訊輸入:').pack()
        topframe.pack(padx=20,pady=20)

        #===================End Top frame==================
        #==================bottom frame====================

        bottomFrame=ttk.Frame(self)

        ttk.Label(bottomFrame,text='UserName:').grid(column=0,row=0,padx=(10,0),sticky='E')

        self.username=tk.StringVar()
        ttk.Entry(bottomFrame,textvariable=self.username).grid(column=1,row=0)#使用者名稱輸入

        ttk.Label(bottomFrame,text='Password:').grid(column=0,row=1,sticky='E')

        self.password=tk.StringVar()
        ttk.Entry(bottomFrame,textvariable=self.password,show='*').grid(column=1, row=1,pady=10,padx=10)#密碼輸入

        cancel_btn=ttk.Button(bottomFrame,text='取消',command=self.cancel_click)
        cancel_btn.grid(column=0,row=2,padx=10,pady=(30,0))

        ok_btn=ttk.Button(bottomFrame,text='確定',command=self.ok_click)
        ok_btn.grid(column=1,row=2,padx=0,pady=(30,0),sticky='E')

        bottomFrame.pack(expand=True,fill='x',padx=20,pady=(0,20))





        #==============End bottom frame====================

    def cancel_click(self):
        self.username.set("")
        self.password.set("")
    def ok_click(self):
        username = self.username.get()
        password = self.password.get()
        showinfo(title="使用者輸入",message=f'使用者名稱:{username}\n使用者密碼:{password}')






def main():
    window = Window(theme="awlight")
    
    # window.username.set('這裏放姓名')
    # window.password.set('這裏打password')

    window.mainloop()

if __name__ == '__main__':
    main()




