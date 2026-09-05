import platform
import psutil

def system_info():

    return {
        "OS": platform.system(),
        "CPU": psutil.cpu_percent(),
        "Memory": psutil.virtual_memory().percent
    }