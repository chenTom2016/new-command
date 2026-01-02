import time
import threading
import builtins

class Sandbox:
    def __init__(self, time_limit=3):
        self.time_limit = time_limit
        self.safe_globals = {
            "__builtins__": self.safe_builtins(),
        }

    def safe_builtins(self):
        
        SAFE = {
            "print": print,
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "abs": abs,
            "min": min,
            "max": max,
        }

        BLOCKED = [
            "open", "exec", "eval", "__import__", "compile",
            "globals", "locals", "vars", "dir",
        ]

        for f in BLOCKED:
            SAFE[f] = lambda *args, **kw: (_ for _ in ()).throw(
                PermissionError(f"Sandbox Blocked: {f}")
            )
        return SAFE

    def run(self, code):
        
        result = {"timeout": False, "error": None}

        def target():
            try:
                exec(code, self.safe_globals)
            except Exception as e:
                result["error"] = e

        t = threading.Thread(target=target)
        t.start()
        t.join(self.time_limit)

        if t.is_alive():
            return "⏳ Sandbox: Time Limit Exceeded"

        if result["error"]:
            return f"❌ Sandbox Error: {result['error']}"

        return "✅ Sandbox executed successfully"
