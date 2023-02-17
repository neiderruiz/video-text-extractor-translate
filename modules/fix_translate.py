import shutil

shutil.copy2("./fix/transcribe_fix.py","./fix/transcribe.py")
shutil.move("./fix/transcribe.py", "./env/Lib/site-packages/whisper/transcribe.py")