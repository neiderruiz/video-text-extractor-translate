import winsound
import re
import os
import subprocess
import datetime

from modules.declarations import FOLDER_SOUNDS
def reproducir_sonido():
    winsound.PlaySound(f"{FOLDER_SOUNDS}sound.wav", winsound.SND_ASYNC)

def clearName(name):
    clear_name = re.sub(r'[^\w\s]', '', name).strip()
    return clear_name

def nameToMp3(name):
    clear_name = clearName(name)
    nameMp3 = clear_name.replace(' ','-')+".mp3".lower()
    return nameMp3

def rename_videos():
    with os.scandir('./') as entries:
        for entry in entries:
            if entry.name.endswith(".mp4") and entry.is_file():
                name_video = entry.name.replace(".mp4","")
                nameMp3 = nameToMp3(name_video)
                #remove video
                os.rename(entry.name,nameMp3)
                #remove if exist
                if os.path.exists(f"{FOLDER_SOUNDS}{nameMp3}"):
                    os.remove(f"{FOLDER_SOUNDS}{nameMp3}")
                #move video to folder
                os.rename(nameMp3, f"{FOLDER_SOUNDS}{nameMp3}")

def convert_video_to_audio_ffmpeg(video_file, output_ext="mp3"):
    """Converts video to audio directly using `ffmpeg` command
    with the help of subprocess module"""
    filename, ext = os.path.splitext(video_file)
    subprocess.call(["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)

def concat_current_line(root,current_line,text):
    current_line.set(f"{text} | Time {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \n {current_line.get()}")
    root.update()