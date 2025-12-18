from tkinter import filedialog
from tkinter import ttk, messagebox
import tkinter as tk
import threading
import time
import json
from pathlib import Path

from cli_downloader import CLIDownloader


CONFIG_DIR = Path.home() / ".yt-dlp-app"
CONFIG_FILE = CONFIG_DIR / "config.json"

PROFILES = {
    "Melhor qualidade": "best",
    "Vídeo MP4": "mp4",
    "Vídeo WEBM": "webm",
    "Somente áudio": "audio",
    "Áudio MP3": "mp3",
    "Áudio WAV": "wav",
    "Vídeo até 480p": "low"
}

def shorten_path(path, max_len=45):
    if not path:
        return ""
    if len(path) <= max_len:
        return path
    return "..." + path[-(max_len - 3):]



class YTDLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT-DLP App")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.output_dir = None
        self.downloader = None
        
        self.playlist_index = None
        self.playlist_total = None
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        self.tab_download = ttk.Frame(self.notebook) 
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_download, text="Download")
        self.notebook.add(self.tab_settings, text="Configurações")
        
        self.config = self.load_config()

        self._build_download_ui()
        if self.output_dir:
            self.path_label.config(text=shorten_path(self.output_dir))

        self._build_settings_ui()

        self.apply_config()
        
        self.output_dir = self.config.get("output_dir")
        
        if self.output_dir:
            self.path_label.config(text=self.output_dir)
            
        self.profile_var.set(
            self.config.get("profile", "Melhor qualidade")
            )
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



        
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.path_label.config(text=shorten_path(folder))

                        
            self.config["output_dir"] = folder
            self.save_config(self.config)
            
    
    def _build_download_ui(self):
        # URL
        tk.Label(self.tab_download, text="Link do vídeo:").pack(anchor="w", padx=10, pady=(10, 0))
        self.url_entry = tk.Entry(self.tab_download)
        self.url_entry.pack(fill="x", padx=10)
        
        # Pasta de destino
        tk.Label(self.tab_download, text="Pasta de download:").pack(anchor="w", padx=10, pady=(10, 0))

        path_frame = tk.Frame(self.tab_download)
        path_frame.pack(fill="x", padx=10)

        self.path_label = tk.Label(
            path_frame,
            text="(padrão: Downloads/yt-dlp)",
            anchor="w",
            width=45,        #  largura fixa
            wraplength=350,  #  quebra de linha
            justify="left"
        )

        self.path_label.pack(side="left", fill="x")

        tk.Button(
            path_frame,
            text="Escolher...",
            command=self.choose_folder
        ).pack(side="right")


        # Perfil
        tk.Label(self.tab_download, text="Formato de saída:").pack(anchor="w", padx=10, pady=(10, 0))
        self.profile_var = tk.StringVar(value="Melhor qualidade")
        self.profile_menu = ttk.Combobox(
            self.tab_download,
            textvariable=self.profile_var,
            values=list(PROFILES.keys()),
            state="readonly"
        )
        self.profile_menu.pack(fill="x", padx=10)
        
        # Opções adicionais
        opts_frame = tk.LabelFrame(self.tab_download, text="Configurações adicionais")
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        self.opt_continue = tk.BooleanVar(value=True)
        self.opt_no_overwrites = tk.BooleanVar(value=True)
        self.opt_subs = tk.BooleanVar(value=False)
        self.opt_auto_subs = tk.BooleanVar(value=False)
        self.opt_keep = tk.BooleanVar(value=False)
        self.opt_playlist = tk.BooleanVar(value=False)
        self.opt_thumbnail = tk.BooleanVar(value=False)



        # Progresso
        self.progress = ttk.Progressbar(self.tab_download, length=100, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=15)

        # Status
        self.status_label = tk.Label(self.tab_download, text="Aguardando ação...")
        self.status_label.pack(anchor="w", padx=10)

        
        # Nome do vídeo atual
        self.title_label = tk.Label(
            self.tab_download,
            text="",
            wraplength=480,
            justify="left",
            fg="#444"
        )
        self.title_label.pack(anchor="w", padx=10, pady=(2, 8))

        
        # Botões
        btn_frame = tk.Frame(self.tab_download)
        btn_frame.pack(pady=15)

        self.download_btn = tk.Button(btn_frame, text="Baixar", command=self.start_download)
        self.download_btn.pack(side="left", padx=5)

        self.cancel_btn = tk.Button(
            btn_frame,
            text="Cancelar",
            state="disabled",
            command=self.cancel_download
        )
        self.cancel_btn.pack(side="left", padx=5)
        
    # ======================
    # Guia Opções Avançadas
    # ======================
    
    def _build_settings_ui(self):
        frame = self.tab_settings

        #Opções Avançadas
        ttk.Checkbutton(frame,
         text="Continuar downloads", 
         variable=self.opt_continue).pack(anchor="w")
        
        ttk.Checkbutton(frame,
         text="Não sobrescrever arquivos", 
         variable=self.opt_no_overwrites
         ).pack(anchor="w")
        
        ttk.Checkbutton(frame,
         text="Baixar legendas", 
         variable=self.opt_subs
         ).pack(anchor="w")
        
        ttk.Checkbutton(frame,
         text="Legendas automáticas", 
         variable=self.opt_auto_subs
         ).pack(anchor="w")
        
        ttk.Checkbutton(frame,
         text="Manter arquivos temporários", 
         variable=self.opt_keep
         ).pack(anchor="w")
        
        ttk.Checkbutton(frame,
         text="Baixar playlist inteira", 
         variable=self.opt_playlist
         ).pack(anchor="w")
        
        ttk.Checkbutton(frame,
         text="Adicionar a Thumbnail", 
         variable=self.opt_thumbnail
         ).pack(anchor="w")
        
    # ======================
    # Salvar Configs
    # ======================

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}


    def save_config(self,data):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def on_close(self):
        config = {
            "output_dir": self.output_dir,
            "profile": self.profile_var.get(),

            "continue": self.opt_continue.get(),
            "no_overwrites": self.opt_no_overwrites.get(),
            "write_subs": self.opt_subs.get(),
            "write_auto_subs": self.opt_auto_subs.get(),
            "keep_files": self.opt_keep.get(),
            "playlist": self.opt_playlist.get(),
            "thumbnail": self.opt_thumbnail.get()
        }
        self.save_config(config)
        self.root.destroy()

    def apply_config(self):
        # Pasta de download
        self.output_dir = self.config.get("output_dir")
        if self.output_dir:
            self.path_label.config(text=self.output_dir)

        # Perfil
        profile = self.config.get("profile")
        if profile in PROFILES:
            self.profile_var.set(profile)

        # Opções booleanas
        self.opt_continue.set(self.config.get("continue", True))
        self.opt_no_overwrites.set(self.config.get("no_overwrites", True))
        self.opt_subs.set(self.config.get("write_subs", False))
        self.opt_auto_subs.set(self.config.get("write_auto_subs", False))
        self.opt_keep.set(self.config.get("keep_files", False))
        self.opt_playlist.set(self.config.get("playlist", False))
        self.opt_thumbnail.set(self.config.get("thumbnail", False))


        
        

        

    # ======================
    # DOWNLOAD FLOW
    # ======================

    def start_download(self):
        self.title_label.config(text="")
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Erro", "URL inválida")
            return

        profile = PROFILES[self.profile_var.get()]
        
        options = {
            "continue": self.opt_continue.get(),
            "no_overwrites": self.opt_no_overwrites.get(),
            "write_subs": self.opt_subs.get(),
            "write_auto_subs": self.opt_auto_subs.get(),
            "keep_files": self.opt_keep.get(),
            "playlist": self.opt_playlist.get(),
            "thumbnail": self.opt_thumbnail.get()
        }

        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress["value"] = 0
        self.status_label.config(text="Iniciando download...")

        self.downloader = CLIDownloader(output_dir=self.output_dir)

        thread = threading.Thread(
            target=self._run_download,
            args=(url, profile, options),
            daemon=True
        )
        thread.start()

    def _run_download(self, url, profile, options):
        self.downloader.download(
            url,
            profile=profile,
            options=options,
            on_output=self.on_output,
            on_finish=self.on_finish,
            on_error=self.on_error
        )

        while self.downloader.is_running():
            time.sleep(0.1)

    def cancel_download(self):
        if self.downloader:
            self.downloader.cancel()
            self.status_label.config(text="Download cancelado")

    # ======================
    # CALLBACKS
    # ======================

    def on_output(self, data):
        self.root.after(0, self._handle_output, data)

    def _handle_output(self, data):
        t = data["type"]

        if t == "playlist":
            self.playlist_index = data["index"]
            self.playlist_total = data["total"]

            self.status_label.config(
                text=f"Playlist: vídeo {self.playlist_index} de {self.playlist_total}"
            )

        elif t == "title":
            # 🔹 NOME DO VÍDEO ATUAL
            self.title_label.config(text=data["title"])

        elif t == "progress":
            self.progress["value"] = data["percent"]

            if self.playlist_index and self.playlist_total:
                prefix = f"[{self.playlist_index}/{self.playlist_total}] "
            else:
                prefix = ""

            self.status_label.config(
                text=f"{prefix}{data['percent']:.1f}% | {data['speed']} | ETA {data['eta']}"
            )

        elif t == "status":
            self.status_label.config(text=data["message"])

    def on_finish(self):
        self.root.after(0, self._finish_ui)

    def _finish_ui(self):
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.title_label.config(text="")
        self.status_label.config(text="Download concluído!")
        messagebox.showinfo("Concluído", "Download finalizado com sucesso!")

    def on_error(self, msg):
        self.root.after(0, self._error_ui, msg)

    def _error_ui(self, msg):
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.status_label.config(text="Erro no download")
        messagebox.showerror("Erro", msg)
        self.title_label.config(text=" ")


if __name__ == "__main__":
    root = tk.Tk()
    app = YTDLPApp(root)
    root.mainloop()
