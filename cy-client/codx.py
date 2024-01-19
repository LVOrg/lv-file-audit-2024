# This is a sample Python script.
# how to build
# pyinstaller --onefile E:\long\python\codx.py --icon=E:\long\python\icon\WP.ico --noconsole
import pathlib
import threading
import time
import uuid
import extract_icon


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.





# Press the green button in the gutter to run the script.
import asyncio
import websockets
import win32com.client
import requests
import os
import pystray
import pefile
import io
import traceback

codx_dir= os.path.join(os.environ.get("USERPROFILE"),"AppData","Roaming","codx")
os.makedirs(codx_dir,exist_ok=True)
def set_auto_start_up():
    import winreg
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
    winreg.SetValueEx(key, "Codx-Office-Client-Comunication", 0, winreg.REG_SZ, __file__)
if pathlib.Path(__file__).suffix==".exe":
    set_auto_start_up()
def download(url):
    response = requests.get(url,verify=False)
    download_path= os.path.join(codx_dir,str(uuid.uuid4()))
    with open(download_path, "wb") as f:
        f.write(response.content)
    return download_path
stop_server = False
async def hello_world(websocket, path:str):
    url=path.split("=")[1]
    doc_path=download(url)
    word = win32com.client.Dispatch("Word.Application")

    word.Visible = True  # Make Word window visible

    doc = word.Documents.Open(doc_path)
    word.Activate()  # This brings Word to the foreground

    await websocket.send("helloworld")

import pystray
from PIL import Image
import sys
verion = 'p.0.1'
app_dir=pathlib.Path(__file__).parent.__str__()
def get_icon():
    icon_extractor = extract_icon.ExtractIcon(sys.executable)
    raw = icon_extractor.get_raw_windows_preferred_icon()
    icon_io = io.BytesIO(raw)
    app_icon = Image.open(icon_io)
    return app_icon
server=None
start_server= None

async def handler(websocket):
    while not stop_server:
        await websocket.recv()


async def server_async():
    async with websockets.serve(hello_world, "localhost", 8765):
        await asyncio.Future()  # Run forever until stopped


def start_socket():
    asyncio.run(server_async())
def create_tray_icon(icon):
    def show_window():
        # Code to display your application's main window
        pass
    def exit_app():
        try:
            # start_server.ws_server.server.close()
            icon.stop()  # Stop the tray icon
            sys.exit()  # Exit the application
        except Exception as e:
            print(e)
            pass
        finally:
            sys.exit(0)
     # Load your icon
    menu = pystray.Menu(
        pystray.MenuItem("Show Window", show_window),
        pystray.MenuItem("Exit", exit_app),
    )
    icon = pystray.Icon("Codx Office interact", icon, menu=menu)
    return icon.run


try:
# In your main script, call this function to create the tray icon
    app_icon= get_icon()
    tray_icon_run=create_tray_icon(app_icon)
    th1=threading.Thread(target=start_socket)
    th1.name="Socket"
    th2=threading.Thread(target=tray_icon_run)
    th2.name="Tray"
    th2.start()
    # th1.start()


    # th1.join()
    start_socket()
    th2.join()
    # threading.Thread(target=tray_icon_run).start()
    #
    # start_socket()
except Exception as e:
    txt = traceback.print_exc()
    print(__file__)
    print(txt)
    # time.sleep(10000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
