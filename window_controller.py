import win32gui
from win32gui import GetWindowText, GetForegroundWindow



winlist = [] 
def winEnumHandler( hwnd, ctx ):
    global winlist
    if win32gui.IsWindowVisible( hwnd ):
        title = win32gui.GetWindowText( hwnd )
        process = hex( hwnd )
        winlist.append( ( process,title  ) )
    
    
    
    
win32gui.EnumWindows( winEnumHandler, None )
winlist = [i for i in winlist if i[1] != '']
for i in winlist:
    print(i)

def isSlideShowActive():
    return 'PowerPoint Slide Show' in GetWindowText(GetForegroundWindow())

import time
for i in  range(10):
    print(isSlideShowActive())
    time.sleep(1)