import json
import psutil
import article
import win32con
import pyautogui
import win32clipboard
from time import sleep
from pywinauto.keyboard import send_keys
from pywinauto.application import Application

from win32con import IDC_HAND
from win32gui import LoadCursor, GetCursorInfo
DEFAULT_CURSORS = {
  LoadCursor(0, IDC_HAND): 'Hand'
}

# 获取光标信息
def get_cursor_info():
  cursor_info = GetCursorInfo()[1]
  return DEFAULT_CURSORS.get(cursor_info, 'None')

# 获取进程id
def get_pid(processName):
  for proc in psutil.process_iter():
    try:
      if (proc.name() == processName):
        return proc.pid
    except psutil.NoSuchProcess:
      pass
  return -1

# 获取剪切板内容
def get_clipboard():
  win32clipboard.OpenClipboard()
  text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
  win32clipboard.CloseClipboard()
  return text

# 读取公众号列表文件
def get_gzh():
  with open('accounts.json', encoding='utf-8') as accounts:
    result = json.load(accounts)
    return result

def get_body(procId): #微信主窗口
  # 利用进程ID初始化一下实例
  app = Application(backend='uia').connect(process=procId)
  # 快捷键Ctrl + Alt + W打开微信主窗口
  send_keys('^%w')
  # 微信主窗口
  main_Win = app.window(class_name='WeChatMainWndForPC')
  # main_Win.print_control_identifiers()
  # 切换到搜一搜
  search(app, main_Win)
def search(app, main_Win): # 搜一搜窗口
  accounts = get_gzh()
  for mp_account in accounts:
    print('当前公众号', mp_account)
    main_Win.set_focus()

    search_btn = main_Win.child_window(title="搜一搜", control_type="Button").wrapper_object()
    search_btn.draw_outline(colour='red')
    search_btn.click_input()

    search_Dlg = app.window(class_name='Search2Wnd')
    # 点击搜索框下面的公众号，只搜索公众号内容
    mp_btn = search_Dlg.child_window(title="公众号", control_type="Button").wrapper_object()
    mp_btn.click_input()
    search_Dlg.type_keys(mp_account) # 输入公众号
    sleep(2)
    send_keys("{ENTER}") # 按回车键
    # 搜索公众号，点击进入公众号消息列表
    selectItem = search_Dlg.child_window(title=mp_account, control_type="Text", found_index=0).wrapper_object()
    selectItem.click_input()
    # 抓取最近的推送文章
    get_articles(app)
    sleep(2)

def get_latest_article():
  pyautogui.moveTo(550/2, 15, duration=1)
  enterInner = False # 确保进去消息列表点击，避免点到视频号
  for i in range(1040):
    pyautogui.moveRel(0, 10, duration=0.1)
    x,y = pyautogui.position()
    matchColor = pyautogui.pixelMatchesColor(x, y, (243, 243, 243), tolerance=10)
    if matchColor:
      enterInner = True
    cursor = get_cursor_info()
    if enterInner and cursor == 'Hand':
      return x,y

def get_articles(app): # 公众号窗口
  # 抓取最近的推送文章
  profile_Dlg = app.window(class_name='H5SubscriptionProfileWnd')
  profile_Dlg.maximize() # 最大化公众号消息列表
  # 在1920*1080下的大小是，550x1040
  get_latest_article()
  pyautogui.click()
  sleep(5) # 等待打开页面
  view_Dlg = app.window(class_name='CefWebViewWnd')
  view_Dlg.wait('ready')
  copy_btn = view_Dlg.child_window(title='复制链接地址', control_type='Button').wrapper_object()
  copy_btn.draw_outline(colour='red')
  copy_btn.click_input() # 点击左上角复制链接
  link = get_clipboard()
  (tag,title,photoUrl,originUrl,textContent) = article.get_article(link)
  # todo 插入数据库即可
  print(tag,title)
  
if __name__ == '__main__':
  procId = get_pid("WeChat.exe")
  if (procId == -1):
    print("微信未运行")
    pyautogui.alert(text='微信未运行', title='提示', button='OK')
  else:
    get_body(procId)
