import tkinter as tk
import pytchat
import threading
import time
import string
import pyautogui
import pydirectinput
import re

global option
option = ['shift', 'ctrl', 'alt', 'up', 'down', 'left', 'right', 'space']
for s in string.ascii_lowercase:
    option.append(s)


def main():
    global root, topFrame, modeSwitchFrame, modeFrame
    global chat, chatThreadControl
    global mode, modeStartControl, mode1IsReading

    mode = 0
    modeStartControl = False
    mode1IsReading = False

    root = tk.Tk()
    topFrame = CreateTopFrame(root)
    modeSwitchFrame = CreateModeSwitchFrame(root)
    modeFrame = tk.Frame(root)

    root.title('Youtube聊天室擷取')
    root.geometry('800x600')
    root.resizable(1, 1)

    root.mainloop()

# 建立主畫面


def CreateTopFrame(root):
    global InfoLabel
    global chatRoomWindow, chatRoomInput, chatRoomConnectButton, chatRoomDisconnectButton

    topFrame = tk.Frame(root)
    InfoLabel = tk.Label(topFrame, width=100)
    chatRoomLabel = tk.Label(topFrame, text='影片ID:', width=20)
    chatRoomInput = tk.Entry(topFrame, width=60)
    chatRoomConnectButton = tk.Button(
        topFrame, text="開始擷取", command=ConnectToChat, width=10)
    chatRoomDisconnectButton = tk.Button(
        topFrame, text="停止擷取", command=DisconnectToChat, width=10, state=tk.DISABLED)
    chatRoomWindow = tk.Listbox(topFrame, width=100)

    topFrame.pack(pady=25)
    InfoLabel.grid(row=0, columnspan=4)
    chatRoomLabel.grid(row=1, column=0)
    chatRoomInput.grid(row=1, column=1)
    chatRoomConnectButton.grid(row=1, column=2)
    chatRoomDisconnectButton.grid(row=1, column=3)
    chatRoomWindow.grid(row=2, columnspan=4)

    testInput = tk.Entry(topFrame, width=60)
    testInput.grid(row=3, column=1)
    tk.Button(topFrame, text="測試", command=lambda: KeywordToKeyboard(
        testInput.get()), width=10).grid(row=3, column=2)

    return topFrame

# 建立模式切換畫面


def CreateModeSwitchFrame(root):
    global modeLabel, mode1Button
    modeSwitchFrame = tk.Frame(root)
    modeLabel = tk.Label(modeSwitchFrame, text='請選擇模式:', width=100)
    mode1Button = tk.Button(modeSwitchFrame, text="鍵盤被控制了!",
                            command=lambda: ChangeMode(1), width=10, state=tk.DISABLED)

    modeSwitchFrame.pack()
    modeLabel.grid(row=0, columnspan=4)
    mode1Button.grid(row=1, column=0)

    return modeSwitchFrame


def ConnectToChat():
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


def DisconnectToChat():
    global chatThreadControl, modeStartControl, modeFrame, mode
    mode = 0
    chatThreadControl = False
    modeStartControl = False
    mode1Button.config(state=tk.DISABLED)
    chatRoomDisconnectButton.config(state=tk.DISABLED)
    chatRoomInput.config(state=tk.NORMAL)
    chatRoomConnectButton.config(state=tk.NORMAL)

    modeFrame.pack_forget()
    modeFrame = tk.Frame(root)


def AutoCatchChat():
    global chat, chatThreadControl
    while chat.is_alive() and chatThreadControl:
        for c in chat.get().sync_items():
            chatRoomWindow.insert(
                0, f"{c.datetime} [{c.author.name}]- {c.message}")
            if chatRoomWindow.size() > 100:
                chatRoomWindow.delete(100)

            if modeStartControl:
                match mode:
                    case 1:
                        KeywordToKeyboard(c.message)
                    case _:
                        return


def InfoLabelDisplay(message, color, autoReset=True):
    global infoThread
    InfoLabel.config(text=message, fg=color)
    if autoReset:
        infoThread = threading.Thread(target=InfoLabelReset)
        infoThread.daemon = True
        infoThread.start()


def InfoLabelReset():
    time.sleep(3)
    InfoLabel.config(text="", fg='#000000')


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


def SetUpMode1():
    global startButton, stopButton
    modeFrame.pack()

    modeLabel.config(text="當前模式:我的鍵盤被控制了!", padx=2)
    mode1Button.config(state=tk.DISABLED)
    startButton = tk.Button(modeFrame, text="開始",
                            command=OnMode1Start, width=10)
    stopButton = tk.Button(modeFrame, text="結束",
                           command=OnModel1Stop, width=10, state=tk.DISABLED)
    
    text = tk.Text(modeFrame, height=10, width=100)
    rule = """使用方法:
1.輸入指令必須以驚嘆號 "!" 開頭。
2.感嘆號後面可以包含一個或多個指令，這些指令必須使用逗號 "," 來分隔。 如:"!左0.5,右0.3"
3.指令的關鍵字為："跳", "左", "右","左跳", "右跳"。
4.在每個關鍵字之後，須加上一個數字(可用小數點)，表示按住指定按鍵的時間（秒）。 如:"!左0.5"
5.在指令讀取與執行期間，不會讀取其他指令。                
"""
    text.insert(tk.END, rule)     
    text.config(state=tk.DISABLED)
    startButton.grid(row=0, column=0)
    stopButton.grid(row=0, column=1)
    text.grid(row=1, columnspan=2, pady=5)


def OnMode1Start():
    global modeStartControl
    startButton.config(state=tk.DISABLED)
    stopButton.config(state=tk.NORMAL)
    modeStartControl = True


def OnModel1Stop():
    global modeStartControl
    modeStartControl = False
    startButton.config(state=tk.NORMAL)
    stopButton.config(state=tk.DISABLED)


def KeywordToKeyboard(message):
    global mode1IsReading
    if not mode1IsReading:
        if message.startswith("!"):
            mode1IsReading = True
            keywordString = message.replace("!", "")
            keywordList = keywordString.split(",")
            actionList = []
            actionDict = {
                "左跳": ("左跳", 4),
                "右跳": ("右跳", 5),
                "跳": ("跳", 1),
                "左": ("左", 2),
                "右": ("右", 3)
            }
            errorMessage = '錯誤的指令，已取消讀取:' + message
            successMessage = '當前執行指令:' + message

            for keyword in keywordList:
                isMatch = re.search(r"左跳|右跳|跳|左|右", keyword)
                if isMatch:
                    actionKey = isMatch.group()
                else:
                    InfoLabelDisplay(errorMessage, '#FF3333')
                    mode1IsReading = False
                    return

                try:
                    pressTime = float(keyword.replace(actionKey, ""))
                except:
                    InfoLabelDisplay(errorMessage, '#FF3333')
                    mode1IsReading = False

                actionType = actionDict.get(actionKey)[1]
                actionList.append([actionType, pressTime])

            InfoLabelDisplay(successMessage, '#28a745', False)
            thread = threading.Thread(target=KeywordToKeyboardThread, args=(actionList, message))
            thread.daemon = True
            thread.start()


def KeywordToKeyboardThread(actionList, message):
    global mode1IsReading
    for actionType, pressTime in actionList:
        match actionType:
            case 1:
                pydirectinput.keyDown("space")
            case 2:
                pydirectinput.keyDown('left')
            case 3:
                pydirectinput.keyDown('right')
            case 4:
                pydirectinput.keyDown('space')
                pydirectinput.keyDown('left')
            case 5:
                pydirectinput.keyDown('space')
                pydirectinput.keyDown('right')

        time.sleep(0.1 if pressTime <= 0 else pressTime)

        match actionType:
            case 1:
                pydirectinput.keyUp("space")
            case 2:
                pydirectinput.keyUp('left')
            case 3:
                pydirectinput.keyUp('right')
            case 4:
                pydirectinput.keyUp('space')
                pydirectinput.keyUp('left')
            case 5:
                pydirectinput.keyUp('space')
                pydirectinput.keyUp('right')

    InfoLabelDisplay('執行指令完成:' + message, '#FF3333')
    time.sleep(0.1)
    mode1IsReading = False
                            
if __name__ == '__main__':
    main()