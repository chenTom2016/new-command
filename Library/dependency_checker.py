# dependency_checker.py
import importlib
import sys
import subprocess

def check_and_install(packages):
    missing = []
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing modules detected: {', '.join(missing)}")
        print("Installing required modules...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("Installation complete. Please restart the program if necessary.")

def run():
    required_packages = [
        "colorama",
        "PIL",          # Pillow
        "cryptography",
        "googletrans",
        "requests",
        "qrcode"
    ]
    check_and_install(required_packages)
