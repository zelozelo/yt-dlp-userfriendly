import subprocess
import threading
import os
import re
import sys
from pathlib import Path


class CLIDownloader:

    _progress_re = re.compile(
        r'\[download\]\s+(\d+(?:\.\d+)?)%\s+of\s+.*?at\s+(.*?)\s+ETA\s+(.*)'
    )
        
    _playlist_re = re.compile(
    r'Downloading item (\d+) of (\d+)'
    )
    _title_re = re.compile(
    r'\[download\] Destination:\s+(.*)'
    )

    OUTPUT_PROFILES = {
        "best": {
            "format": "bv*+ba/b",
            "merge": True
        },
        "mp4": {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
            "merge": True
        },
        "webm": {
            "format": "bv*[ext=webm]+ba[ext=webm]/b[ext=webm]",
            "merge": True
        },
        "audio": {
            "format": "ba",
            "merge": False
        },
        "mp3": {
            "format": "ba",
            "merge": False,
            "postprocess": "mp3"
        },
        "wav": {
            "format": "ba",
            "merge": False,
            "postprocess": "wav"
        },
        "low": {
            "format": "bv*[height<=480]+ba/b",
            "merge": True
        }
    }
    DEFAULT_OPTIONS = {
    "continue": True,
    "no_overwrites": True,
    "write_subs": False,
    "write_auto_subs": False,
    "keep_files": False,
    "verbose": False,
    "playlist": False
    }




    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            )

        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.ffmpeg_path = self._get_ffmpeg_path()

        self.process = None
        self._is_running = False
        
    def _get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = Path(__file__).parent

        return str(Path(base_path) / "ffmpeg" / "bin")
    
    def download(self, url, profile="best", options=None,
             on_output=None, on_finish=None, on_error=None):

        if self._is_running:
            return
        
        if options is None:
            options = self.DEFAULT_OPTIONS.copy()

        self._is_running = True

        thread = threading.Thread(
            target=self._run,
            args=(url, profile, options, on_output, on_finish, on_error),
            daemon=True
        )
        thread.start()

    def _run(self, url, profile, options, on_output, on_finish, on_error):
        
        profile_cfg = self.OUTPUT_PROFILES.get(profile)
        if not profile_cfg:
            if on_error:
                on_error(f"Perfil inválido: {profile}")
            self._is_running = False
            return
        try:
            cmd = [
                "py", "-m", "yt_dlp",
                "--newline",
                "--js-runtimes", "node",
                "--remote-components", "ejs:github",
                "--ffmpeg-location", self.ffmpeg_path,
                "-f", profile_cfg["format"],
                "-o", os.path.join(self.output_dir,
                "%(title)s - %(artist,creator,uploader)s.%(ext)s"),
                
                url
            ]
            # Opções adicionais
            if options.get("continue"):
                cmd.append("--continue")

            if options.get("no_overwrites"):
                cmd.append("--no-overwrites")

            if options.get("write_subs"):
                cmd.append("--write-subs")

            if options.get("write_auto_subs"):
                cmd.append("--write-auto-subs")

            if options.get("keep_files"):
                cmd.append("-k")

            if options.get("verbose"):
                cmd.append("--verbose")

            if options.get("thumbnail"):
                cmd.append("--embed-thumbnail")

            if not options.get("playlist", True):
                cmd.append("--no-playlist")

            if profile_cfg.get("postprocess") == "mp3":
                cmd.extend([
                    "--extract-audio",
                    "--audio-format", "mp3"
                ])
            if profile_cfg.get("postprocess") == "wav":
                cmd.extend([
                    "--extract-audio",
                    "--audio-format", "wav"
                ])
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=self.output_dir
            )

            for line in self.process.stdout:
                line = line.strip()

                if not line:
                    continue
                                # 📦 PROGRESSO DE PLAYLIST
                playlist_match = self._playlist_re.search(line)
                if playlist_match:
                    index = int(playlist_match.group(1))
                    total = int(playlist_match.group(2))

                    if on_output:
                        on_output({
                            "type": "playlist",
                            "index": index,
                            "total": total
                        })
                    continue
                
                title_match = self._title_re.search(line)
                if title_match:
                    filename = title_match.group(1)
                    title = os.path.splitext(os.path.basename(filename))[0]

                    if on_output:
                        on_output({
                            "type": "title",
                            "title": title
                        })
                    continue
                

                # ⏬ PROGRESSO DO DOWNLOAD ATUAL
                match = self._progress_re.search(line)
                if match:
                    if on_output:
                        on_output({
                            "type": "progress",
                            "percent": float(match.group(1)),
                            "speed": match.group(2),
                            "eta": match.group(3)
                        })
                    continue

                # eventos importantes
                if "Merging formats" in line:
                    on_output and on_output({
                        "type": "status",
                        "message": "Mesclando áudio e vídeo..."
                    })
                    continue

                if "Extracting audio" in line:
                    on_output and on_output({
                        "type": "status",
                        "message": "Convertendo áudio..."
                    })
                    continue

                # log genérico
                if on_output:
                    on_output({
                        "type": "log",
                        "message": line
                    })

                # eventos importantes
                if "Merging formats" in line:
                    on_output and on_output({
                        "type": "status",
                        "message": "Mesclando áudio e vídeo..."
                    })
                    continue

                if "Extracting audio" in line:
                    on_output and on_output({
                        "type": "status",
                        "message": "Convertendo áudio..."
                    })
                    continue

                # log genérico
                if on_output:
                    on_output({
                        "type": "log",
                        "message": line
                    })

            self.process.wait()

            if self.process.returncode == 0:
                if on_finish:
                    on_finish()
            else:
                if on_error:
                    on_error("Falha no download")

        except Exception as e:
            if self.process and self.process.poll() is not None:
                # processo já terminou
                pass
            else:
                if on_error:
                    on_error(f"Erro: {e}")

                
        finally:
            self._is_running = False
            self.process = None
            
            
        if getattr(self, "_cancelled", False):
            on_output and on_output({
                "type": "status",
                "message": "Download cancelado pelo usuário"
            })


    def is_running(self):
        return self._is_running
    
    def cancel(self):
        if self.process and self._is_running:
            try:
                self.process.terminate()
            except Exception:
                pass
        self._is_running = False
        self._cancelled = True


