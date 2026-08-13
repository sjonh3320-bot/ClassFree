import sys
import subprocess

def run_ps_silent(ps_cmd: str) -> tuple[int, str]:
    """静默执行PowerShell，不弹出窗口，返回(退出码,输出文本)"""
    try:
        proc = subprocess.run(
            ["powershell", "-ExecutionPolicy", "RemoteSigned", "-Command", ps_cmd],
            creationflags=0x08000000,  # CREATE_NO_WINDOW 隐藏黑框
            capture_output=True,
            text=True
        )
        return proc.returncode, proc.stdout + proc.stderr
    except Exception as e:
        return -1, str(e)

def is_admin() -> bool:
    """校验程序是否管理员运行"""
    try:
        subprocess.check_output(
            ["fltmc", "filters"],
            creationflags=0x08000000,
            stderr=subprocess.STDOUT
        )
        return True
    except:
        return False

def check_install_ntmodule():
    print("[*] 正在检测依赖模块 NtObjectManager ...")
    # PowerShell脚本：存在模块输出1，不存在输出0
    check_ps = r'Get-Module -ListAvailable NtObjectManager | Out-Null; if ($?) {Write-Host 1} else {Write-Host 0}'
    code, out = run_ps_silent(check_ps)
    if out.strip() != "1":
        print("[!] 未检测到模块，开始自动在线安装")
        install_ps = r'Install-Module -Name NtObjectManager -Force -Scope CurrentUser -Confirm:$false -AllowClobber'
        install_code, install_out = run_ps_silent(install_ps)
        # 判断安装失败场景：断网、组策略拦截
        if "Unable to reach" in install_out or "repository" in install_out or install_code != 0:
            print("[×] 模块安装失败！")
            print("    机房断网/组策略屏蔽PS模块仓库，无法使用TrustedInstaller提权功能")
            input("按回车键退出程序")
            sys.exit(1)
        print("[√] NtObjectManager 模块安装完成")
    else:
        print("[√] NtObjectManager 模块已存在，跳过安装")

def disable_oydrv():
    print("\n[*] 准备以TrustedInstaller权限停止并禁用OyDrv内核驱动")
    print("[!] 仅修改服务启动项，不会删除OyDrv.sys，无蓝屏风险\n")

    ps_core = r'''
    # 判断TrustedInstaller服务状态，避免重复启动报错
    sc query TrustedInstaller | Out-Null
    if ($LASTEXITCODE -ne 0) {
        sc start TrustedInstaller
        Start-Sleep -Milliseconds 300  # 等待进程完全拉起
    }
    Import-Module NtObjectManager
    Set-NtTokenPrivilege SeDebugPrivilege
    $ti_proc = Get-NtProcess -Name TrustedInstaller.exe
    if (-not $ti_proc) {
        Write-Host "[错误] 无法捕获TrustedInstaller进程，操作终止"
        pause
        exit 1
    }
    $cmd_str = 'sc stop OyDrv && sc config OyDrv start=disabled && echo =========操作完成========= && echo OyDrv驱动已停用，重启电脑自动恢复 && echo 手动恢复命令：sc config OyDrv start=system && sc start OyDrv && pause'
    New-Win32Process cmd.exe -CreationFlags NewConsole -CommandLine $cmd_str -ParentProcess $ti_proc
    '''
    code, output = run_ps_silent(ps_core)
    if code != 0:
        print(f"[!] 执行异常，PowerShell输出：{output}")
    print("[√] TrustedInstaller权限CMD窗口已弹出，请等待执行完成再关闭窗口")

if __name__ == "__main__":
    print("===== OyDrv 机房管控内核驱动禁用工具 =====")
    # 前置校验：必须管理员运行
    if not is_admin():
        print("[×] 权限错误！程序未以管理员身份运行")
        print("打包命令必须携带 --uac-admin 参数，否则无法操作内核驱动服务")
        input("回车关闭程序")
        sys.exit(1)
    # 检测/安装依赖模块
    check_install_ntmodule()
    # 执行禁用驱动逻辑
    disable_oydrv()
    input("\n全部流程执行完毕，按回车键关闭程序")