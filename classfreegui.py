import tkinter as tk
import time
import sys
from subprocess import run
import os
import threading

def get_wait_time():
    # 第一个窗口，用来获取等待时间
    root_input = tk.Tk()
    root_input.title("Class Free GUI 课堂脱管工具图形界面版")
    root_input.geometry("460x150")

    result = {"value": 2}  # 默认值：2分钟

    label = tk.Label(
        root_input,
        text="输入发作前等待时间（分钟），20秒内无输入默认2分钟",
        font=("微软雅黑", 10)
    )
    label.pack(pady=12)

    entry = tk.Entry(root_input, font=("微软雅黑",11))
    entry.pack(pady=4, padx=40, fill=tk.X)

    def on_ok():
        s = entry.get().strip()
        try:
            num = float(s)
            if num >= 0:
                result["value"] = num
        except ValueError:
            pass
        root_input.destroy()

    tk.Button(root_input, text="确认", command=on_ok, padx=175).pack(pady=20)

    # 20秒超时，自动关闭，使用默认2分钟
    root_input.after(20000, root_input.destroy)

    root_input.mainloop()
    return result["value"]

# 第二步：主窗口（现接收 stop_event 参数）
def main(stop_event):
    window = tk.Tk()
    window.title("Class Free GUI 课堂脱管工具图形界面版")
    window.geometry("800x300")

    # 定义布尔变量，记录是否要退出
    should_exit = tk.BooleanVar(value=False)

    # 定义窗口关闭时的回调函数
    def on_closing():
        should_exit.set(True)    # 告诉主循环，用户想退出了
        window.destroy()         # 销毁窗口并结束 mainloop

    # 绑定窗口的“X”按钮到自定义的 on_closing 函数
    window.protocol("WM_DELETE_WINDOW", on_closing)

    text1 = tk.Label(window, text="Class Free GUI\n\n作者：范荐\n\n声明：本软件公益开发，完全免费，不得随意更改内容并传播", font=("微软雅黑", 12))
    text1.pack(pady=(40,0))
    
    text2 = tk.Label(window, text="\n警告：此软件及其附件可能造成系统损坏或功能异常，对于此类情况概不负责", font=("微软雅黑", 8))
    text2.pack()

    frame_button = tk.Frame(window)
    frame_button.pack(pady=20)

    button_restart = tk.Button(frame_button, text="启动桌面", font=("微软雅黑", 10), padx=20, command=restart)
    button_restart.pack(side=tk.LEFT, padx=10)

    button_browser = tk.Button(frame_button, text="启动浏览器", font=("微软雅黑", 10), padx=12, command=browser)
    button_browser.pack(side=tk.LEFT, padx=10)

    # ★ 修改：用闭包包装按钮命令，同时执行 kill() 和停止线程 ★
    def kill_action():
        if kill():  # 执行一次性的查杀守护进程操作
            print("一次性的查杀执行成功！正在停止后台循环杀进程线程...")
            stop_event.set()  # ★ 核心：触发事件，通知后台循环杀进程线程停止 ★
        else:
            print("一次性查杀执行失败！")

    button_kill = tk.Button(frame_button, text="杀死守护进程", font=("微软雅黑",10), padx=6, command=kill_action)
    button_kill.pack(side=tk.LEFT, padx=10)

    button_drvkillller = tk.Button(frame_button, text="禁用驱动", font=("微软雅黑", 10), padx=20, command=drvkillller)
    button_drvkillller.pack(side=tk.LEFT, padx=10)

    button_error = tk.Button(frame_button, text="重启自动查杀", font=("微软雅黑", 10), padx=6, command=error)
    button_error.pack(side=tk.LEFT, padx=10)

    window.mainloop()

    # 窗口销毁后，把变量值返回给外部
    return should_exit.get()



def restart():
    os.system('schtasks /delete /tn "RestartExplorer1" /f')
    time.sleep(0.5)
    os.system('schtasks /delete /tn "RestartExplorer2" /f')
    time.sleep(0.5)
    cmd_restart1 = r'schtasks /create /tn "RestartExplorer1" /tr "cmd /c \"taskkill /f /im explorer.exe\"" /sc once /st 23:59 /ru SYSTEM /f'
    cmd_restart2 = r'schtasks /create /tn "RestartExplorer2" /tr "cmd /c \"start explorer.exe\"" /sc once /st 23:59 /ru SYSTEM /f'
    if os.system(cmd_restart1) == 0 and os.system(cmd_restart2) == 0:
        os.system('schtasks /run /tn "RestartExplorer1"')
        time.sleep(0.5)
        os.system('schtasks /run /tn "RestartExplorer2"')
        time.sleep(0.5)
        os.system('schtasks /delete /tn "RestartExplorer1" /f')
        time.sleep(0.5)
        os.system('schtasks /delete /tn "RestartExplorer2" /f')
        print("桌面环境已重启")
    else:
        print("重启桌面任务创建失败")

def browser():
    os.startfile("www.cn.bing.com")

def kill():
    os.system('schtasks /delete /tn "KillTarget1" /f')
    time.sleep(0.5)
    os.system('schtasks /delete /tn "KillTarget2" /f')
    time.sleep(0.5)
    cmd1 = r'schtasks /create /tn "KillTarget1" /tr "cmd /c \"taskkill /f /t /im MMPC.exe\"" /sc once /st 23:59 /ru SYSTEM /f'
    cmd2 = r'schtasks /create /tn "KillTarget2" /tr "cmd /c \"taskkill /f /t /im MultiClient.exe\"" /sc once /st 23:59 /ru SYSTEM /f'
    cmd3 = r'schtasks /create /tn "KillTarget3" /tr "cmd /c \"taskkill /f /t /im student.exe\"" /sc once /st 23:59 /ru SYSTEM /f'
    ret1 = os.system(cmd1)
    ret2 = os.system(cmd2)
    ret3 = os.system(cmd3)
    if ret1 == 0 and ret2 == 0 and ret3 == 0:
        print("创建计划任务成功")
    else:
        print("创建计划任务失败")
        return False
    os.system('schtasks /run /tn "KillTarget1"')
    time.sleep(0.5)
    os.system('schtasks /run /tn "KillTarget2"')
    time.sleep(0.5)
    os.system('schtasks /run /tn "KillTarget3"')
    print("SYSTEM权限进程查杀已执行")
    os.system('schtasks /delete /tn "KillTarget1" /f')
    time.sleep(0.5)
    os.system('schtasks /delete /tn "KillTarget2" /f')
    time.sleep(0.5)
    os.system('schtasks /delete /tn "KillTarget3" /f')
    print("临时计划任务清理完成")
    return True

def drvkillller():
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        exe_path = os.path.join(desktop, "DrvKillller.exe")
        os.startfile(exe_path)
    except FileNotFoundError:
        print("文件不存在")

def error():
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        exe_path = os.path.join(desktop, "ClassFreeGUI.exe")
        os.startfile(exe_path)
    except FileNotFoundError:
        print("文件不存在")

# ===== 入口与线程控制 =====

def loop_kill_student(stop_event):
    """
    后台线程：只要 stop_event 没有被设置，就一直循环杀 student.exe
    """
    print("后台杀进程线程已启动")
    while not stop_event.is_set():
        run(["taskkill", "/f", "/im", "student.exe"])
        time.sleep(0.3)
    print("后台杀进程线程已停止")

if __name__ == "__main__":
    try:
        wait_minute = get_wait_time()
        print(f"等待时间 {wait_minute} 分钟")
        wait_sec = wait_minute * 60
        time.sleep(wait_sec)

        # 1. 先做第一次清理并重启桌面（按你的需求）
        print("正在执行首次清理与重启桌面...")
        run(["taskkill", "/f", "/im", "student.exe"])
        restart()
        time.sleep(2)  # 给桌面重启一点缓冲时间

        # 2. 创建一个线程控制事件
        stop_event = threading.Event()

        # 3. 启动后台杀进程线程（设为守护线程，防止主线程退出时不干净）
        killer_thread = threading.Thread(target=loop_kill_student, args=(stop_event,))
        killer_thread.daemon = True
        killer_thread.start()

        # 4. 进入主循环（菜单显示）
        while True:
            # 主界面现在和后台杀进程是完全分开的线程喵！
            user_exit = main(stop_event)
            if user_exit:
                # 如果用户想彻底退出，先通知后台线程停止，再退出
                print("用户关闭菜单，正在清理后台线程...")
                stop_event.set()
                break

    except Exception as e:
        print(f"发生错误: {e}")
    except KeyboardInterrupt:
        if 'stop_event' in locals():
            stop_event.set()
        sys.exit()