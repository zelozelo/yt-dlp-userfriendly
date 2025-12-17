from tkinter import filedialog
from tkinter import ttk, messagebox
import tkinter as tk
import threading
import time

from cli_downloader import CLIDownloader


PROFILES = {
    "Melhor qualidade": "best",
    "Vídeo MP4": "mp4",
    "Vídeo WEBM": "webm",
    "Somente áudio": "audio",
    "Áudio MP3": "mp3",
    "Vídeo até 480p": "low"
}


class YTDLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT-DLP App")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        self.output_dir = None
        self.downloader = None
        
        self.playlist_index = None
        self.playlist_total = None


        self._build_ui()
        
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.path_label.config(text=folder)
    
    def _build_ui(self):
        # URL
        tk.Label(self.root, text="Link do vídeo:").pack(anchor="w", padx=10, pady=(10, 0))
        self.url_entry = tk.Entry(self.root)
        self.url_entry.pack(fill="x", padx=10)
        
        # Pasta de destino
        tk.Label(self.root, text="Pasta de download:").pack(anchor="w", padx=10, pady=(10, 0))

        path_frame = tk.Frame(self.root)
        path_frame.pack(fill="x", padx=10)

        self.path_label = tk.Label(
            path_frame,
            text="(padrão: Downloads/yt-dlp)",
            anchor="w"
        )
        self.path_label.pack(side="left", fill="x", expand=True)

        tk.Button(
            path_frame,
            text="Escolher...",
            command=self.choose_folder
        ).pack(side="right")


        # Perfil
        tk.Label(self.root, text="Formato de saída:").pack(anchor="w", padx=10, pady=(10, 0))
        self.profile_var = tk.StringVar(value="Melhor qualidade")
        self.profile_menu = ttk.Combobox(
            self.root,
            textvariable=self.profile_var,
            values=list(PROFILES.keys()),
            state="readonly"
        )
        self.profile_menu.pack(fill="x", padx=10)

        # Progresso
        self.progress = ttk.Progressbar(self.root, length=100, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=15)

        # Status
        self.status_label = tk.Label(self.root, text="Aguardando ação...")
        self.status_label.pack(anchor="w", padx=10)

        
        # Nome do vídeo atual
        self.title_label = tk.Label(
            self.root,
            text="",
            wraplength=480,
            justify="left",
            fg="#444"
        )
        self.title_label.pack(anchor="w", padx=10, pady=(2, 8))

        # Botões
        btn_frame = tk.Frame(self.root)
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
    # DOWNLOAD FLOW
    # ======================

    def start_download(self):
        self.title_label.config(text="")
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Erro", "URL inválida")
            return

        profile = PROFILES[self.profile_var.get()]

        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress["value"] = 0
        self.status_label.config(text="Iniciando download...")

        self.downloader = CLIDownloader(output_dir=self.output_dir)

        thread = threading.Thread(
            target=self._run_download,
            args=(url, profile),
            daemon=True
        )
        thread.start()

    def _run_download(self, url, profile):
        self.downloader.download(
            url,
            profile=profile,
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
