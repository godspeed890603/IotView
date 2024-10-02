import os
import sys
import atexit

pidfile = 'C:\\UserData\\my_program.pid'

def remove_pidfile():
    """程式退出時刪除 PID 文件"""
    if os.path.exists(pidfile):
        os.remove(pidfile)
        print("PID 文件已刪除")

# 註冊退出時刪除 PID 文件的回調
atexit.register(remove_pidfile)

if os.path.exists(pidfile):
    with open(pidfile, 'r') as f:
        pid = int(f.read().strip())
    try:
        # 檢查進程是否存在
        os.kill(pid, 0)  # 傳遞信號 0，檢查進程是否有效
        print(f"程式已經在運行，PID: {pid}")
        sys.exit(0)
    except OSError:
        print("檢測到舊 PID 文件，但對應進程不存在，刪除舊 PID 文件")
        os.remove(pidfile)

# 創建新的 PID 文件，記錄當前進程 ID
with open(pidfile, 'w') as f:
    f.write(str(os.getpid()))
    print(f"PID 文件已創建，PID: {os.getpid()}，程式開始執行")

try:
    # 程式的邏輯
    print("程式正在運行...")
    input("按 Enter 鍵退出程式...")

finally:
    # 確保即使程式異常退出也會刪除 PID 文件
    remove_pidfile()
