import subprocess
import os
from colorama import Fore, Style

def open_vim(filename):
   
    try:
        if not os.path.exists(filename):
            
            open(filename, "w").close()

        print(Fore.CYAN + f"📝 打开 Vim 编辑器: {filename}" + Style.RESET_ALL)
        subprocess.run(["vim", filename])

        print(Fore.GREEN + f"✅ 文件编辑完成: {filename}" + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + "❌ 未找到 vim，请确认系统已安装。" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ 启动失败: {e}" + Style.RESET_ALL)
