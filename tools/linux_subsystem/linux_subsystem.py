# tools/linux_subsystem/linux_subsystem.py
"""
Linux Subsystem helper for Windows (WSL-first).
Provides:
 - detect_wsl()
 - install_wsl()
 - list_wsl_distros()
 - run_in_wsl(cmd_list, distro=None)
 - run_elf_with_wsl(local_elf_path, args=[], distro=None)
 - fallback_info()
"""
import subprocess
import shutil
import os
import sys
import time

def _which(exe):
    return shutil.which(exe) is not None

# ---------------- detection ----------------
def detect_wsl():
    """
    Return a dict with basic WSL availability info:
      { 'available': bool, 'wsl_exe': bool, 'wsl_version': 'WSL1/WSL2/unknown', 'error': None or str }
    """
    info = {'available': False, 'wsl_exe': False, 'wsl_version': None, 'error': None}
    if not _which("wsl") and not _which("wsl.exe"):
        info['error'] = "wsl executable not found in PATH"
        return info
    info['wsl_exe'] = True
    try:
        proc = subprocess.run(["wsl", "-l", "-v"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
        out = proc.stdout
        if proc.returncode == 0 and out:
            info['available'] = True
            # try to detect v2 mention
            if "WSL 2" in out or "VERSION" in out or "Running" in out:
                info['wsl_version'] = "WSL2 or WSL with versions available"
            else:
                info['wsl_version'] = "WSL (unknown version)"
        else:
            info['available'] = True
            info['wsl_version'] = "WSL (unknown)"
    except subprocess.SubprocessError as e:
        info['error'] = f"Error running wsl: {e}"
    except Exception as e:
        info['error'] = str(e)
    return info

# ---------------- install helper ----------------
def install_wsl():
    """
    Attempt to run 'wsl --install'. This requires admin privileges and recent Windows.
    Returns (rc, output).
    NOTE: This will likely prompt for a reboot; caller must handle that.
    """
    if os.name != "nt":
        return -1, "Not Windows"
    try:
        proc = subprocess.run(["wsl", "--install"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return proc.returncode, proc.stdout
    except Exception as e:
        return -1, f"Failed to run 'wsl --install': {e}"

# ---------------- list distros ----------------
def list_wsl_distros():
    """Return list of installed distro names, or empty list."""
    try:
        proc = subprocess.run(["wsl", "-l", "-q"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=10)
        out = proc.stdout.strip()
        if not out:
            return []
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []

# ---------------- run command in WSL ----------------
def run_in_wsl(cmd_list, distro=None, capture_output=True, timeout=300):
    """
    Run a command inside WSL.
    cmd_list: list of strings for the Linux command (e.g. ['ls', '-la', '/home'])
    distro: optional distro name (e.g. 'Ubuntu-22.04'). If None, default distro used.
    Returns (returncode, stdout).
    """
    if os.name != "nt":
        # if not Windows, run locally
        try:
            p = subprocess.run(cmd_list, stdout=(subprocess.PIPE if capture_output else None),
                               stderr=subprocess.STDOUT, text=True, timeout=timeout)
            return p.returncode, p.stdout if capture_output else None
        except Exception as e:
            return -1, str(e)
    prefix = ["wsl"]
    if distro:
        prefix = ["wsl", "-d", distro, "--"]
    full_cmd = prefix + cmd_list
    try:
        p = subprocess.run(full_cmd, stdout=(subprocess.PIPE if capture_output else None),
                           stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return p.returncode, p.stdout if capture_output else None
    except Exception as e:
        return -1, str(e)

# ---------------- run ELF in WSL ----------------
def run_elf_with_wsl(local_elf_path, args=None, distro=None, timeout=300):
    """
    Execute a local Linux ELF binary inside WSL:
      - local_elf_path: Windows path to the ELF file (e.g. C:\\Users\\you\\bin\\app)
    This copies the file into the selected distro's filesystem (under /tmp) and runs it with args.
    Returns (returncode, stdout).
    """
    args = args or []
    if not os.path.exists(local_elf_path):
        return -1, f"File not found: {local_elf_path}"

    try:
        # create temporary directory inside WSL
        if distro:
            rc, out = run_in_wsl(["mktemp", "-d"], distro=distro)
        else:
            rc, out = run_in_wsl(["mktemp", "-d"])
        if rc != 0:
            return rc, out
        wtmp = out.strip()
        remote_name = os.path.basename(local_elf_path)
        remote_path = f"{wtmp}/{remote_name}"

        # push binary into WSL via stdin of bash -c "cat > remote_path"
        if distro:
            proc = subprocess.run(["wsl", "-d", distro, "--", "bash", "-c", f"cat > {remote_path}"],
                                  input=open(local_elf_path, "rb").read(),
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            proc = subprocess.run(["wsl", "--", "bash", "-c", f"cat > {remote_path}"],
                                  input=open(local_elf_path, "rb").read(),
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # set exec permission
        run_in_wsl(["chmod", "+x", remote_path], distro=distro)
        # run it
        return run_in_wsl([remote_path] + args, distro=distro, timeout=timeout)
    except Exception as e:
        return -1, f"Error pushing file into WSL: {e}"

# ---------------- fallback recommendations ----------------
def fallback_info():
    """
    Return text suggesting alternatives if WSL not available.
    """
    txt = []
    txt.append("WSL not available. Alternatives:")
    txt.append(" - Install WSL (recommended). See Microsoft docs: run 'wsl --install' (requires admin).")
    txt.append(" - Use a full VM (QEMU/VirtualBox) and a Linux ISO (heavier but isolated).")
    txt.append(" - Use MSYS2 / Cygwin for many GNU tools (not full native ELF support).")
    return "\n".join(txt)
