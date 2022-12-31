import customtkinter
import ppt_gesture
from threading import Thread
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gesture Control System")
        self.minsize(500,300)
        self.headFont = customtkinter.CTkFont(family="Arail", size=24)

        self.contentFont = customtkinter.CTkFont(family="Arail", size=16)

        self.appTitle = customtkinter.CTkLabel(master=self,text="Gesture Controlled System",font=self.headFont)
        self.appTitle.pack(padx=10,pady=20)
        self.lanuchBtn = customtkinter.CTkButton(master=self,text="Lanuch",command=self.btn_launch,
        font=self.contentFont)

        self.settingBtn = customtkinter.CTkButton(master=self,text="Settings",command=self.button_callback,font=self.contentFont)

        self.helpBtn = customtkinter.CTkButton(master=self,text="Help",command=self.button_callback,font=self.contentFont)

        self.aboutBtn = customtkinter.CTkButton(master=self,text="About",command=self.button_callback,font=self.contentFont)
    


        self.lanuchBtn.pack(pady=10)
        self.settingBtn.pack(pady=10)
        self.helpBtn.pack(pady=10)
        self.aboutBtn.pack(pady=10)
    def btn_launch(self):
        Thread(target=self.cameraThread).start()
        
    def cameraThread(self):
        for i in ppt_gesture.launchGestureControl():
            print(i)
            self.lanuchBtn.configure(text=i)
            
    def button_callback(self):
        print("BTN Pressed")

if __name__=="__main__":
    app = App()
    app.mainloop()