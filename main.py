import modules.fix_translate
from tkinter import *
from tkinter import filedialog
from moviepy.video.io.VideoFileClip import VideoFileClip
import whisper
from whisper.utils import get_writer
import os
import pytube as pt
from tkinter import messagebox
from modules.declarations import languages, models, FOLDER_SOUNDS
from modules.utils import clearName, nameToMp3, rename_videos, convert_video_to_audio_ffmpeg, concat_current_line, reproducir_sonido
import threading

def verbose_callback(language,start, end, result, text):
    concat_current_line(root,current_line,f"[{start} --> {end}]")

def press_form():
    language_video = next(idioma for idioma in languages if idioma[1] == opcion_seleccionada.get())
    model_use = option_model.get()
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
        concat_current_line(root,current_line,f"Descargando video de youtube...")
        t = yt.streams.filter(only_audio=True)
        t[0].download()
        concat_current_line(root,current_line,f"Renombrando video a audio...")
        rename_videos()
        #remove al characteres title
        video_name.set(yt.title.replace("/","-")[:50])
        root.update()
    if yt_url.get() == "" and not video_route.get():
        messagebox.showinfo("Error con video", "Debes seleccionar un video")
        return

    if video_route.get() and yt_url.get() == "":
        concat_current_line(root,current_line,f"Convirtiendo video a audio...")
        convert_video_to_audio_ffmpeg(video_route.get())
        concat_current_line(root,current_line,f"fin de conversión de video a audio")
        audio_route = video_route.get().replace('.mp4','.mp3')
        clear_name = video_name.get()
    
    concat_current_line(root,current_line,"Cargando modelo...")
    modelTranscribe = whisper.load_model(model_use,None,'./models/')
    concat_current_line(root,current_line,"Modelo cargado")


    #transcribe
    concat_current_line(root,current_line,f"Transcribiendo audio...")
    decode_options = dict(language=language_video[0])
    result = modelTranscribe.transcribe(audio_route,verbose=True,verbose_callback=verbose_callback, fp16=False,**decode_options)

    if yt_url.get() != "":
        writer = get_writer("vtt", f"{FOLDER_SOUNDS}")
    else:
        writer = get_writer("vtt",os.path.dirname(video_route.get()))

    concat_current_line(root,current_line,"Transcripción completa")

    writer(result, nameToMp3(clear_name).replace('.mp3','').replace('.mp4','')) 

    concat_current_line(root,current_line,"Transcripción guardada")

    concat_current_line(root,current_line,"cargando modelo de traducción...")
    model = whisper.load_model(model_use,None,'./models/')
    concat_current_line(root,current_line,"Modelo cargado")

    decode_options = dict(language=language_video[0])
    transcribe_options = dict(task="translate", **decode_options)
    concat_current_line(root,current_line,"Traduciendo...")
    result = model.transcribe(audio_route,verbose=True,verbose_callback=verbose_callback,fp16=False,**transcribe_options)
    
    if yt_url.get() != "":
        writer = get_writer("vtt", f"{FOLDER_SOUNDS}")
    else:
        writer = get_writer("vtt",os.path.dirname(video_route.get()))
        
    writer(result, f"{clear_name.replace('.mp4','')}-en")
    concat_current_line(root,current_line,"Traducción guardada")
    reproducir_sonido()

# Define una función para seleccionar un archivo
def select_file():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi;*.mov")])
    if(archivo == ""):
        return
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

name_languages = [idioma[1] for idioma in languages]


def run_traslate():
    # Crea un hilo para ejecutar la tarea pesada
    t = threading.Thread(target=press_form)
    t.start()

# Code tkinder window
root = Tk()
root.resizable(0,0)
root.title("Transcribe audio to text")
opcion_seleccionada = StringVar(value="español")
option_model = StringVar(value="large-v2")

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
ytInput = Entry(root, width=30, textvariable=yt_url,fg='grey',show='')
ytInput.insert(0, "add url video Yt")


label_languages = Label(root, text="Seleccionar Idiomas:")

boton = Button(root, text="Seleccionar archivo", command=select_file)
select_idioma = OptionMenu(root, opcion_seleccionada, *name_languages)

select_model = OptionMenu(root, option_model,*models )

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
select_model.grid(row=3, column=0)
boton.grid(row=4, column=0)
label_languages.grid(row=5, column=0)
select_idioma.grid(row=6, column=0)
label_list_result.grid(row=7, column=0)
boton_enviar = Button(root, text="Crear Traducciones", command=run_traslate)
boton_enviar.grid(row=8, column=0)

root.mainloop()