import modules.fix_translate
import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox
import threading
from modules.declarations import languages, models, FOLDER_SOUNDS
import re
import pytube as pt
import os
from modules.utils import clearName, nameToMp3, rename_videos, convert_video_to_audio_ffmpeg, concat_current_line, run_sound_finish
from moviepy.editor import AudioFileClip
import whisper
from whisper.utils import get_writer

optionsWriter = {
    "max_line_width": 80,
    "max_line_count": 2,
    "highlight_words": True
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Extract Audio from Video')
        self.iconbitmap('./assets/icon.ico')

        self.frm = ttk.Frame(self, padding=10, width=300, height=400)
        self.frm.grid()

        self.setup_styles()
        self.setup_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure(
            'TEntry',
            padding=[5, 2],
            font=('Arial', 12),
            fieldbackground='white',
            foreground='black',
            borderwidth=2,
            relief='solid',
            bordercolor='#ccc'
        )
        self.style.configure(
            'TButton',
            padding=[5, 5],
            font=('Arial', 12),
            relief='raised',
            borderwidth=2,
        )
        self.style.configure(
            'TLabel',
            font=('Arial', 12),
        )
        self.style.configure(
            'TLabelFrame',
            font=('Arial', 12, 'bold'),
            borderwidth=2,
            relief='solid',
        )

    def setup_widgets(self):
        self.yt_url_var = tk.StringVar()  # Crear una nueva instancia de StringVar
        self.yt_url, _ = self.create_entry(
            self.frm, "Url Video Youtube", 0, 0, textvariable=self.yt_url_var)  # Pasar StringVar a create_entry
        self.yt_url_var.trace_add("write", self.check_youtube_url)  # Añadir un rastreador para cambios en la variable
             
        self.select_file_btn = self.create_button(
            self.frm, "Select File", self.select_file, 3, 0)

        self.reset_btn = self.create_button(
            self.frm, "Reset", self.reset, 3, 1)

        self.process_video_btn = self.create_button(
            self.frm, "Procesar Video", self.process_video, 3, 0)

        # Crear un LabelFrame para el grupo Miniatura
        self.miniature_frame = ttk.LabelFrame(
            self.frm, text="Parametros a procesar", padding=(10, 5))
        self.miniature_frame.grid(
            column=0, row=4, padx=10, pady=10, columnspan=4, sticky=(tk.W, tk.E))  # Ajuste en columnspan
        
        # Crear el widget OptionMenu para seleccionar idioma
        self.opcion_seleccionada = tk.StringVar(value="español")
        self.name_languages = [idioma[1] for idioma in languages]  # Ejemplo de lista de idiomas
        self.select_idioma_label = ttk.Label(self.miniature_frame, text="Seleccionar Idioma:")
        self.select_idioma_label.grid(column=0, row=4)
        self.select_idioma = tk.OptionMenu(self.miniature_frame, self.opcion_seleccionada, *self.name_languages)
        self.select_idioma.grid(column=0, row=5, sticky=tk.W)

        # Crear el widget OptionMenu para seleccionar modelo
        self.option_model = tk.StringVar(value="large-v2")
        self.models = [modelo for modelo in models]  # Lista de modelos
        self.select_model_label = ttk.Label(self.miniature_frame, text="Seleccionar Modelo:")
        self.select_model_label.grid(column=1, row=4)  # Puedes ajustar la columna y la fila según lo necesites
        self.select_model = tk.OptionMenu(self.miniature_frame, self.option_model, *self.models)
        self.select_model.grid(column=1, row=5, sticky=tk.W)  # Puedes ajustar la columna y la fila según lo necesites

        self.hide_miniature_frame_and_button()

        # button save
        self.save_directory_var = tk.StringVar()
        self.select_directory_btn = self.create_button(
        self.frm, "Select Directory Save", self.select_directory, 3, 1)  

        self.save_directory_label = ttk.Label(self.frm, text="")
        self.save_directory_label.grid(column=0, row=6, columnspan=2, sticky=tk.W)  # Ajustar row y column según sea necesario


    def select_directory(self):
        directory = fd.askdirectory()
        if directory:  
            self.save_directory_var.set(directory)  
            self.save_directory_label.config(text=f"Save Directory: {directory}") 


    def check_youtube_url(self, *args):
        yt_url = self.yt_url_var.get()
        if self.is_valid_youtube_url(yt_url):
            self.show_miniature_frame_and_button()
            self.select_file_btn.grid_remove()
        else:
            self.hide_miniature_frame_and_button()

    def create_entry(self, parent, label_text, row, column, validate=False, textvariable=None):
        label = ttk.Label(parent, text=label_text)
        label.grid(column=column, row=row * 2)

        if validate:
            validate_command = self.register(self.validate_input)
            entry = ttk.Entry(parent, width=40, validate='key', validatecommand=(
                validate_command, '%P'), textvariable=textvariable)  # Cambié width a 40
        else:
            # Cambié width a 40
            entry = ttk.Entry(parent, width=40, textvariable=textvariable)

        entry.grid(column=column, row=row * 2 + 1)
        return entry, label  # Devuelve tanto la entrada como la etiqueta

    def is_valid_youtube_url(self, url):
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+')
        return youtube_regex.match(url) is not None

    def create_button(self, parent, text, command, row, column):
        btn = ttk.Button(parent, text=text, command=command)
        btn.grid(column=column, row=row)
        return btn

    def select_file(self):
        filename = fd.askopenfilename(
            filetypes=[('videos', '*.mp4'), ('All files', '*.*')])
        if filename:  # Si un archivo fue seleccionado
            self.yt_url_var.set(filename)  # Establecer la URL de YouTube
            self.show_miniature_frame_and_button()
        else:  # Si no se seleccionó ningún archivo (se presionó 'Cancelar')
            self.hide_miniature_frame_and_button()

    def process_video(self):

        save_directory = self.save_directory_var.get()
        if not save_directory:
            messagebox.showerror('Error', 'Selecciona un directorio para guardar el resultado')
            return

        # print current language
        print(self.opcion_seleccionada.get())
        # print current model
        print(self.option_model.get())
        # print current url
        print(self.yt_url_var.get())

        if self.is_valid_youtube_url(self.yt_url_var.get()):
            audio_route = getVideoYT(self.yt_url_var.get())
            print('Procesando video youtube')
        else:
            audio_route =  convert_video_to_audio_ffmpeg(self.yt_url_var.get(), route_save=FOLDER_SOUNDS)
            print('Procesando archivo local')
        modelTranscribe = whisper.load_model(self.option_model.get(),None,'./models/')
        
        language_video = next(idioma for idioma in languages if idioma[1] == self.opcion_seleccionada.get())
        decode_options = dict(language=language_video[0])

        print(audio_route,'audio_route')
        result = modelTranscribe.transcribe(audio_route,verbose=True,verbose_callback=verbose_callback, fp16=False,**decode_options)
        name_transcribe = f"{audio_route.split('/')[-1].replace('.mp3','')}-{language_video[0]}"

        output_path = os.path.join(save_directory, f"{name_transcribe}.vtt")
        writer = get_writer("vtt", save_directory)
        writer(result, save_directory, optionsWriter)  

        

        # remove audio
        if os.path.exists(audio_route):
            os.remove(audio_route)

        print('Transcripción completa')
        run_sound_finish()

    def validate_input(self, value_if_allowed):
        if value_if_allowed == '' or value_if_allowed.isdigit():
            return True
        return False

    def show_miniature_frame_and_button(self):
        self.miniature_frame.grid(
            column=0, row=4, padx=10, pady=10, sticky=(tk.W, tk.E))
        self.process_video_btn.grid(column=1, row=1)  # Muestra el botón

    def hide_miniature_frame_and_button(self):
        self.miniature_frame.grid_remove()
        self.process_video_btn.grid_remove()  # Oculta el botón

    def reset(self):
        self.yt_url_var.set('')  # Limpiar la entrada de la URL de YouTube
        self.hide_miniature_frame_and_button()  # Ocultar los widgets
        self.yt_url.grid(column=0, row=1)  # Muestra la entrada de URL de YouTube
        self.select_file_btn.grid(column=0, row=3)  # Muestra el botón de selección de archivo


from moviepy.editor import *

def getVideoYT(url):
    try:
        yt = pt.YouTube(url)
        clear_name = clearName(yt.title)
        duration = yt.length
        # video_time.set(f"Duración del video: {duration} segundos")
        nameMp3 = nameToMp3(yt.title)
        audio_route = f"{FOLDER_SOUNDS}{nameMp3}"
        if os.path.exists(audio_route):
            os.remove(audio_route)
            
        temp_file = f"{FOLDER_SOUNDS}{clear_name}.mp4"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        # concat_current_line(root,current_line,f"Descargando video de youtube...")
        t = yt.streams.filter(only_audio=True).order_by('abr').desc()
        video_name = f"{clear_name}.mp4"
        t[0].download(output_path=FOLDER_SOUNDS, filename=video_name)
        # concat_current_line(root,current_line,f"Renombrando video a audio...")

        # Convertir el archivo a MP3
        audio = AudioFileClip(temp_file)
        audio.write_audiofile(audio_route)

        # Eliminar el archivo temporal
        if os.path.exists(temp_file):
            os.remove(temp_file)

        # return route audio
        return audio_route

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def verbose_callback(language,start, end, result, text):
    print(f"[{start} --> {end}]")



if __name__ == "__main__":
    app = App()
    app.mainloop()