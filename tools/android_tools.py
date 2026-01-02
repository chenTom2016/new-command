# tools/android_tools/android_tools.py
"""
Android Tools module for desktop (adb/fastboot helper).
This module provides a safe CLI menu to:
  - attempt 'adb root' (rarely works on retail devices)
  - attempt to unlock bootloader via fastboot (will likely wipe device)
This module requires adb and fastboot (Android platform-tools) to be installed and available in PATH.

WARNING: These operations can wipe data, void warranty, or brick devices.
This module forces multiple explicit confirmations before proceeding.
"""

import subprocess
import shutil
import time

# ----- utilities -----
def check_tool_exists(tool_name: str) -> bool:
    """Return True if tool_name (adb/fastboot) is on PATH."""
    return shutil.which(tool_name) is not None

def run_cmd(cmd_list, timeout=120):
    """Run a command and return (returncode, stdout)."""
    try:
        proc = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return proc.returncode, proc.stdout
    except subprocess.TimeoutExpired:
        return -1, "Command timed out"
    except Exception as e:
        return -1, f"Failed to run command: {e}"

# ----- adb / fastboot helpers -----
def list_adb_devices():
    """List adb-connected devices (returns list of serials)."""
    if not check_tool_exists("adb"):
        return []
    rc, out = run_cmd(["adb", "devices"])
    if rc != 0:
        return []
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    devices = []
    for l in lines:
        # skip header like "List of devices attached"
        if "\tdevice" in l:
            devices.append(l.split("\t")[0])
    return devices

def list_fastboot_devices():
    """List fastboot devices (returns list of serials)."""
    if not check_tool_exists("fastboot"):
        return []
    rc, out = run_cmd(["fastboot", "devices"])
    if rc != 0:
        return []
    devices = []
    for l in out.splitlines():
        if l.strip():
            parts = l.split()
            if parts:
                devices.append(parts[0].strip())
    return devices

def choose_from_list(items, label="device"):
    """Simple selection helper; returns selected item or None."""
    if not items:
        return None
    if len(items) == 1:
        return items[0]
    print(f"Multiple {label}s found:")
    for i, it in enumerate(items):
        print(f"  [{i}] {it}")
    while True:
        choice = input("Select index (or 'q' to cancel): ").strip().lower()
        if choice == "q":
            return None
        try:
            idx = int(choice)
            if 0 <= idx < len(items):
                return items[idx]
        except Exception:
            pass
        print("Invalid selection.")

# ----- confirmations (force explicit tokens) -----
def require_confirm_token(purpose: str):
    """
    Print heavy warning and require a token:
      - purpose == "ROOT" -> token: I_AGREE_ROOT
      - purpose == "UNLOCK" -> token: I_AGREE_UNLOCK
    Returns True if token matched, False otherwise.
    """
    print("\n" + "="*70)
    if purpose == "ROOT":
        print("!!! DANGEROUS OPERATION: ANDROID ONE-CLICK ROOT !!!")
        print("This may fail, may void warranty, and may brick the device.")
        print("If you understand and accept the risk, type EXACTLY: I_AGREE_ROOT")
    elif purpose == "UNLOCK":
        print("!!! DANGEROUS OPERATION: ANDROID UNLOCK-BOOTLOADER (WILL WIPE DATA) !!!")
        print("Unlocking bootloader will MOST LIKELY ERASE USER DATA and may void warranty.")
        print("If you understand and accept the risk, type EXACTLY: I_AGREE_UNLOCK")
    else:
        print("!!! DANGEROUS OPERATION !!!")
        print("Type EXACT confirmation token to proceed.")
    print("="*70 + "\n")
    token = input("Enter confirmation token (or 'q' to cancel): ").strip()
    if purpose == "ROOT" and token == "I_AGREE_ROOT":
        return True
    if purpose == "UNLOCK" and token == "I_AGREE_UNLOCK":
        return True
    print("Confirmation failed or cancelled.")
    return False

# ----- main actions -----
def android_one_click_root():
    """Attempt 'adb root' on selected device (rare on retail devices)."""
    if not check_tool_exists("adb"):
        print("Error: 'adb' not found in PATH. Install Android platform-tools and retry.")
        return

    ok = require_confirm_token("ROOT")
    if not ok:
        return

    devices = list_adb_devices()
    if not devices:
        print("No adb devices found. Ensure USB debugging is enabled and device is connected.")
        return

    serial = choose_from_list(devices, label="adb device")
    if not serial:
        print("Cancelled.")
        return

    print(f"Attempting 'adb -s {serial} root' (may fail on retail devices)...")
    rc, out = run_cmd(["adb", "-s", serial, "root"], timeout=30)
    print(out)
    if rc == 0:
        # check shell id
        rc2, out2 = run_cmd(["adb", "-s", serial, "shell", "id"], timeout=10)
        print(out2)
        print("If the shell shows uid=0 then adbd is running as root.")
    else:
        print("adb root returned non-zero; on most retail devices this is expected. Rooting typically needs device-specific steps or flashing su binaries.")

def android_one_click_unlock_bl():
    """Attempt to unlock bootloader using fastboot."""
    if not (check_tool_exists("adb") and check_tool_exists("fastboot")):
        print("Error: 'adb' and/or 'fastboot' not found in PATH. Install platform-tools first.")
        return

    ok = require_confirm_token("UNLOCK")
    if not ok:
        return

    # try to pick device via adb -> reboot bootloader
    devices = list_adb_devices()
    serial = None
    if devices:
        serial = choose_from_list(devices, label="adb device")
        if not serial:
            print("Cancelled.")
            return
        print(f"Rebooting {serial} to bootloader...")
        rc, out = run_cmd(["adb", "-s", serial, "reboot", "bootloader"], timeout=30)
        print(out)
        print("Waiting a few seconds...")
        time.sleep(4)

    # list fastboot devices
    fast_devices = list_fastboot_devices()
    if not fast_devices:
        print("No fastboot devices found. Make sure the device is in bootloader/fastboot mode and drivers are installed.")
        return

    fast_serial = choose_from_list(fast_devices, label="fastboot device")
    if not fast_serial:
        print("Cancelled.")
        return

    print(f"Attempting to unlock bootloader on {fast_serial}. This will likely wipe userdata.")
    print("Running: fastboot -s <device> flashing unlock")
    rc, out = run_cmd(["fastboot", "-s", fast_serial, "flashing", "unlock"], timeout=180)
    print(out)
    if rc != 0:
        print("The 'flashing unlock' command failed; trying legacy 'oem unlock'...")
        rc2, out2 = run_cmd(["fastboot", "-s", fast_serial, "oem", "unlock"], timeout=180)
        print(out2)
        if rc2 != 0:
            print("Both unlock attempts failed. The device may require OEM-specific process or additional drivers.")
            return

    print("Unlock command issued. Follow on-device prompts (if any). Device may perform factory reset.")
    run_cmd(["fastboot", "-s", fast_serial, "reboot"])
    print("Finished. Verify device state after reboot with 'adb devices'.")

# ----- CLI menu / entrypoint -----
def run():
    """Simple CLI menu to expose module functions."""
    print("\nAndroid Tools Module")
    print("====================")
    print("This module requires adb and fastboot (Android platform-tools) in PATH.")
    print("WARNING: Unlocking bootloader will wipe device and may void warranty.")
    print()
    while True:
        print("\nMenu:")
        print("  1) List adb devices")
        print("  2) List fastboot devices")
        print("  3) Attempt 'adb root' (one-click root, may not work)")
        print("  4) Attempt unlock bootloader (fastboot) - DANGEROUS, will wipe data")
        print("  5) Exit module")
        choice = input("Choose option: ").strip()
        if choice == "1":
            devs = list_adb_devices()
            print("adb devices:", devs or "None")
        elif choice == "2":
            fdevs = list_fastboot_devices()
            print("fastboot devices:", fdevs or "None")
        elif choice == "3":
            android_one_click_root()
        elif choice == "4":
            android_one_click_unlock_bl()
        elif choice == "5" or choice.lower() in ("q", "quit", "exit"):
            print("Exit Android Tools.")
            return
        else:
            print("Invalid choice.")
