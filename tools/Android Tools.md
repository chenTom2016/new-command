# Android Tools (desktop module)

This module provides a small, **desktop-only** helper for interacting with Android devices via `adb` and `fastboot`.

**Important:**
- These tools **can be destructive**. Unlocking bootloader will almost always erase user data.
- Use only on devices you own and after backing up data.
- This module **requires** Android platform-tools (`adb`, `fastboot`) to be installed and added to your PATH.

## Files
- `android_tools.py` - main module with CLI `run()` entrypoint.
- `__init__.py` - package initializer.

## Usage
From the root of your project (where `tools` is a package), run from Python:

```python
from tools.android_tools import run_android_tools
run_android_tools()
