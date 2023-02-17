from tkinter import *
from tkinter import filedialog
from moviepy.video.io.VideoFileClip import VideoFileClip
import whisper
from whisper.utils import get_writer
import subprocess
import os
import pytube as pt
import re
from tkinter import messagebox
import winsound
import datetime


FOLDER_SOUNDS = "./sounds/"

idiomas = [
    ('es', 'español'),
    ('en', 'inglés'),
    ('pt', 'portugués'),
    ('ar', 'árabe'),
    ('zh', 'chino'),
    ('hi', 'hindi')
]

def reproducir_sonido():
    winsound.PlaySound("sonido.wav", winsound.SND_ASYNC)

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


def verbose_callback(language,start, end, result, text):
    concat_current_line(f"[{start} --> {end}]")

def concat_current_line(line):
    current_line.set(f"{line} | Time {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \n {current_line.get()}")
    root.update()

def enviar_formulario():
    language_video = next(idioma for idioma in idiomas if idioma[1] == opcion_seleccionada.get())

    if yt_url.get() != "":
        if yt_url.get().find("youtu") == -1:
            messagebox.showinfo("Error con video", "Debes ingresar una url de youtube")
            return
        
        yt = pt.YouTube(yt_url.get())
        clear_name = clearName(yt.title)
        duration = yt.length
        video_time.set(f"Duración del video: {duration} segundos")
        nameMp3 = nameToMp3(yt.title)
        audio_route = f"{FOLDER_SOUNDS}{nameMp3}"
        if os.path.exists(nameMp3):
            os.remove(nameMp3)
        
        if os.path.exists(f"{FOLDER_SOUNDS}{yt.title}.mp4"):
            os.remove(f"{FOLDER_SOUNDS}{yt.title}.mp4")
        concat_current_line(f"Descargando video de youtube...")
        t = yt.streams.filter(only_audio=True)
        t[0].download()
        concat_current_line(f"Renombrando video a audio...")
        rename_videos()
        #remove al characteres title
        video_name.set(yt.title.replace("/","-")[:50])
        root.update()
    if yt_url.get() == "" and not video_route.get():
        messagebox.showinfo("Error con video", "Debes seleccionar un video")
        return

    if video_route.get() and yt_url.get() == "":
        concat_current_line(f"Convirtiendo video a audio...")
        convert_video_to_audio_ffmpeg(video_route.get())
        concat_current_line(f"fin de conversión de video a audio")
        audio_route = video_route.get().replace('.mp4','.mp3')
        clear_name = video_name.get()
    
    concat_current_line("Cargando modelo...")
    modelTranscribe = whisper.load_model("tiny",None,'./models/')
    concat_current_line("Modelo cargado")


    #transcribe
    concat_current_line(f"Transcribiendo audio...")
    decode_options = dict(language=language_video[0])
    result = modelTranscribe.transcribe(audio_route,verbose=True,verbose_callback=verbose_callback, fp16=False,**decode_options)

    if yt_url.get() != "":
        writer = get_writer("vtt", f"{FOLDER_SOUNDS}")
    else:
        writer = get_writer("vtt",os.path.dirname(video_route.get()))

    concat_current_line("Transcripción completa")

    writer(result, nameToMp3(clear_name).replace('.mp3','').replace('.mp4','')) 

    concat_current_line("Transcripción guardada")

    concat_current_line("cargando modelo de traducción...")
    model = whisper.load_model("large-v2",None,'./models/')
    concat_current_line("Modelo cargado")

    decode_options = dict(language=language_video[0])
    transcribe_options = dict(task="translate", **decode_options)
    concat_current_line("Traduciendo...")
    result = model.transcribe(audio_route,verbose=True,verbose_callback=verbose_callback,fp16=False,**transcribe_options)
    writer = get_writer("vtt", video_route.get().replace(clear_name,''))  
    writer(result, f"{clear_name.replace('.mp4','')}-en")
    concat_current_line("Traducción guardada")
    reproducir_sonido()

# Define una función para seleccionar un archivo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi;*.mov")])

    if(archivo == ""):
        return
    print("Archivo seleccionado:", archivo)
    ##get name video
    name = archivo.split("/")[-1]
    #duración del video
    clip = VideoFileClip(archivo)
    #minutes
    video_name.set(name)
    video_route.set(archivo)
    minutes = int(clip.duration/60)
    if(minutes>1):
        duration = f"{minutes} minutos"
    else:
        duration = f"{clip.duration} segundos"
    video_time.set(duration)

nombres_idiomas = [idioma[1] for idioma in idiomas]

# Code tkinder window
root = Tk()
root.resizable(0,0)
root.title("Transcribe audio to text")
opcion_seleccionada = StringVar(value="español")

video_name = StringVar()
yt_url = StringVar()
video_route = StringVar()
video_time = StringVar()
list_result = StringVar()
current_line = StringVar()
# labels entry forms
etiqueta_nombre = Label(root, textvariable=video_name)
label_video_time = Label(root, textvariable=video_time)
label_list_result = Label(root, textvariable=list_result)
label_current_line = Label(root, textvariable=current_line)

#entry text video youtube
ytInput = Entry(root, width=30, textvariable=yt_url)


label_languages = Label(root, text="Seleccionar Idiomas:")

boton = Button(root, text="Seleccionar archivo", command=seleccionar_archivo)
select_idioma = OptionMenu(root, opcion_seleccionada, *nombres_idiomas)

# scrolling start
frame = Frame(root)
frame.grid(row=10, column=0, sticky="nsew")

canvas = Canvas(frame)
canvas.grid(row=10, column=0, sticky="nsew")

scrollbar = Scrollbar(frame, command=canvas.yview,width=15)
scrollbar.grid(row=10, column=1, sticky="ns")

canvas.configure(yscrollcommand=scrollbar.set)

label = Label(canvas,textvariable=current_line)

canvas.create_window((0, 0), window=label, anchor="nw")

label.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))
# scrolling end

#add grid layout
ytInput.grid(row=0, column=0)
etiqueta_nombre.grid(row=1, column=0)
label_video_time.grid(row=2, column=0)
boton.grid(row=3, column=0)
label_languages.grid(row=4, column=0)
select_idioma.grid(row=5, column=0)
label_list_result.grid(row=6, column=0)
boton_enviar = Button(root, text="Crear Traducciones", command=enviar_formulario)
boton_enviar.grid(row=7, column=0)

root.mainloop()