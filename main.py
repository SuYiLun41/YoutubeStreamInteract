import tkinter as tk
import pytchat
import threading
import time
import string
import pyautogui
import pydirectinput

global option
option = ['shift', 'ctrl', 'alt', 'up','down','left', 'right', 'space']
for s in string.ascii_lowercase:
    option.append(s)

def main ():
    global root, topFrame, modeSwitchFrame, modeFrame
    global InfoLabel
    global chatRoomLabel, chatRoomInput, chatRoomConnectButton, chatRoomDisconnectButton, chatRoomWindow
    global chat, chatThreadControl
    global mode, modeLabel, mode1Button, modeStartControl
    
    mode = 0
    modeStartControl = False
    
    root = tk.Tk()
    topFrame = tk.Frame(root)
    modeSwitchFrame = tk.Frame(root)
    modeFrame = tk.Frame(root)
    
    InfoLabel = tk.Label(topFrame, width=20)
    
    chatRoomLabel = tk.Label(topFrame, text='影片ID:', width=20)
    chatRoomInput = tk.Entry(topFrame, width=60)
    chatRoomConnectButton = tk.Button(topFrame, text="開始擷取", command=ConnectToChat, width=10)
    chatRoomDisconnectButton = tk.Button(topFrame, text="停止擷取", command=DisconnectToChat, width=10, state=tk.DISABLED)
    chatRoomWindow = tk.Listbox(topFrame, width=100)

    modeLabel = tk.Label(modeSwitchFrame, text='請選擇模式:', width=100)
    mode1Button = tk.Button(modeSwitchFrame, text="鍵盤被控制了!", command=lambda:ChangeMode(1), width=10, state=tk.DISABLED)

    root.title('Youtube聊天室擷取')
    root.geometry('800x600')
    root.resizable(1, 1)

    # 主畫面
    topFrame.pack(pady=25)
    InfoLabel.grid(row=0, columnspan=4)
    chatRoomLabel.grid(row=1, column=0)
    chatRoomInput.grid(row=1, column=1)
    chatRoomConnectButton.grid(row=1, column=2)
    chatRoomDisconnectButton.grid(row=1, column=3)
    chatRoomWindow.grid(row=2, columnspan=4)
    
    # 模式切換
    modeSwitchFrame.pack()
    modeLabel.grid(row=0, columnspan=4)
    mode1Button.grid(row=1, column=0)
    
    
    root.mainloop()
    
def ConnectToChat ():
    global chat, chatThread, chatThreadControl
    if chatRoomInput.get() != "":
        try:
            chat = pytchat.create(video_id=chatRoomInput.get())
            if chat.is_alive():
                chatThreadControl = chat.is_alive
                chatRoomInput.config(state=tk.DISABLED)
                chatRoomConnectButton.config(state=tk.DISABLED)
                chatRoomDisconnectButton.config(state=tk.NORMAL)
                chatThread = threading.Thread(target=AutoCatchChat)
                chatThread.daemon = True
                chatThread.start()
                
                mode1Button.config(state=tk.NORMAL)
        except pytchat.exceptions.InvalidVideoIdException:
            InfoLabelDisplay("錯誤的影片ID", '#FF3333')
            
def DisconnectToChat ():
    global chatThreadControl, modeStartControl, modeFrame, mode
    mode = 0
    chatThreadControl = False
    modeStartControl = False
    mode1Button.config(state=tk.DISABLED)
    chatRoomDisconnectButton.config(state=tk.DISABLED)
    chatRoomInput.config(state=tk.NORMAL)
    chatRoomConnectButton.config(state=tk.NORMAL)
    
    for item in wordToKeyList:
        item[0].grid_forget()
        item[1].grid_forget()
        item[2].grid_forget()
        del item[3]
        
    modeFrame.pack_forget()
    modeFrame = tk.Frame(root)
    
            
def AutoCatchChat ():
    global chat, chatThreadControl
    while chat.is_alive() and chatThreadControl:
        for c in chat.get().sync_items():
            chatRoomWindow.insert(0, f"{c.datetime} [{c.author.name}]- {c.message}")
            if chatRoomWindow.size() > 100:
                chatRoomWindow.delete(100)
            
            if modeStartControl:
                match mode:
                    case 1:
                        KeywordToKeyboard(c.message)
                    case _:
                        return

def InfoLabelDisplay (message, color):
    global infoThread
    InfoLabel.config(text="錯誤的影片ID",fg='#FF3333')
    infoThread = threading.Thread(target=InfoLabelReset)
    infoThread.daemon = True
    infoThread.start()
        
def InfoLabelReset ():
    time.sleep(3)
    InfoLabel.config(text="",fg='#000000')

def ChangeMode(localMode):
    global mode
    mode = localMode
    modeFrame.pack_forget()
    match mode:
        case 1:
            # 模式1: 聊天室控制鍵盤
            SetUpMode1()
        case _:
            return

#  聊天室控制鍵盤
def SetUpMode1 ():
    global wordToKeyList
    global mode1ElementList
    global row
    global createButton, startButton, stopButton 
     
    row = 1
    mode1ElementList = []
    wordToKeyList = []
    modeFrame.pack()
        
    modeLabel.config(text="當前模式:我的鍵盤被控制了!", padx= 2)
    mode1Button.config(state=tk.DISABLED)
    tk.Label(modeFrame, text="關鍵字", width=20).grid(row=0,column=0)
    tk.Label(modeFrame, text="鍵盤位置", width=20).grid(row=0,column=1)
    tk.Label(modeFrame, text="秒數(單位:秒)", width=20).grid(row=0,column=2)
    createButton = tk.Button(modeFrame, text=f"+ ({21-row})", command=AddNewKeyword, width=10)
    startButton = tk.Button(modeFrame, text="開始", command=OnMode1Start, width=10)
    stopButton = tk.Button(modeFrame, text="結束", command=OnModel1Stop, width=10, state=tk.DISABLED)
    
    createButton.grid(row=0,column=3, padx=5)
    startButton.grid(row=0,column=4, padx=5)
    stopButton.grid(row=0,column=5, padx=5)

def AddNewKeyword ():
    global row ,createButton
    if row < 21:
        index = row-1
        
        keywordInput = tk.Entry(modeFrame)
        variable = tk.StringVar(modeFrame)
        variable.set('')
        keyboardInput = tk.OptionMenu(modeFrame, variable, *option)
        keyboardRemainInput =  tk.Entry(modeFrame)
        deleteButton = tk.Button(modeFrame, text="-", width=10, command=lambda: DeleteKeyword(index))
        keywordInput.grid(row=row, column=0)
        keyboardInput.grid(row=row, column=1)
        keyboardRemainInput.grid(row=row, column=2)
        deleteButton.grid(row=row, column=3)
        wordToKeyList.append([keywordInput, keyboardInput, keyboardRemainInput, deleteButton, variable])
        row+=1
        createButton.config(text=f"+ ({21-row})")
        if row == 21:
            createButton.config(state=tk.DISABLED)
    
def DeleteKeyword (index):
    item = wordToKeyList[index]
    item[0].grid_forget()
    item[1].grid_forget()
    item[2].grid_forget()
    item[3].grid_forget()
    del item[4]
    wordToKeyList.remove(item)
    
    ResetWordToKeyList()
    
def OnMode1Start ():
    global modeStartControl
    createButton.config(state=tk.DISABLED)
    startButton.config(state=tk.DISABLED)
    stopButton.config(state=tk.NORMAL)

    # 檢查空字串
    removeList = []
    for item in wordToKeyList:
        if len(item[0].get()) == 0 or len(item[4].get()) == 0  :
            removeList.insert(0, item)

    for item in removeList:
        item[0].grid_forget()
        item[1].grid_forget()
        item[2].grid_forget()
        item[3].grid_forget()
        del item[4]
        wordToKeyList.remove(item)
        
    ResetWordToKeyList()
    
    for item in wordToKeyList:
        item[0].config(state=tk.DISABLED)
        item[1].config(state=tk.DISABLED)
        item[2].config(state=tk.DISABLED)
        item[3].config(state=tk.DISABLED)
    
    modeStartControl = True
   
def OnModel1Stop ():
    global modeStartControl
    modeStartControl = False
    createButton.config(state=tk.NORMAL)
    startButton.config(state=tk.NORMAL)
    stopButton.config(state=tk.DISABLED) 
    
    for item in wordToKeyList:
        item[0].config(state=tk.NORMAL)
        item[1].config(state=tk.NORMAL)
        item[2].config(state=tk.NORMAL)
        item[3].config(state=tk.NORMAL)

def KeywordToKeyboard (message):
    for item in wordToKeyList:
        if item[0].get() in message:
            pydirectinput.keyDown(item[4].get())
            if len(item[2].get()) == 0 or item[2].get() == "0":
                time.sleep(0.05)
            else:
                time.sleep(float(item[2].get()))
            pydirectinput.keyUp(item[4].get())
    return
    
def ResetWordToKeyList ():
    global row
    row=1
    for item in wordToKeyList:
        index = row-1
        item[0].grid(row=row, column=0)
        item[1].grid(row=row, column=1)
        item[2].grid(row=row, column=2)
        item[3].config(command=lambda: DeleteKeyword(index))
        item[3].grid(row=row, column=3)
        row+=1
    createButton.config(text=f"+ ({21-row})")
if __name__ == '__main__':
    main()