import platform
import shutil
import os

def copy_file(src, dst):
    try:
        if not os.path.exists(src):
            raise FileNotFoundError(f"{src} does not exist.")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"File copied from {src} to {dst}")
    except (FileNotFoundError, PermissionError, shutil.Error) as e:
        print(f"An error occurred: {e}")

source_file = "./fix/transcribe_fix.py"

os_name = platform.system()

if os_name == 'Windows':
    destination_file = "./env/Lib/site-packages/whisper/transcribe.py"
elif os_name == 'Darwin':  # macOS
    destination_file = "./env/Lib/python3.10/site-packages/whisper/transcribe.py"
else:
    print(f"Unsupported OS: {os_name}")
copy_file(source_file, destination_file)
