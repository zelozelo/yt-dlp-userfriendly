# 🎬 YT-DLP App (GUI)

Aplicação gráfica em Python para download de vídeos e playlists usando **yt-dlp**, com interface simples, escolha de formato, pasta de destino, progresso em tempo real e suporte a playlists.

O projeto foi desenvolvido para funcionar **sem privilégios de administrador**, focando em portabilidade, aprendizado e facilidade de uso.

---

## ✨ Funcionalidades

- 📥 Download de vídeos individuais ou playlists
- 🎞 Escolha de formato de saída:
  - Melhor qualidade
  - MP4
  - WEBM
  - Somente áudio
  - MP3
  - Vídeo até 480p
- 📁 Seleção da pasta de destino
- 📊 Barra de progresso em tempo real
- 📦 Suporte a playlists:
  - Exibe **qual vídeo está sendo baixado** (ex: 3 de 12)
  - Atualização automática a cada item
- 🎵 Exibe o **nome do vídeo atual**
- ⏹ Botão para **cancelar o download**
- 🧵 Execução em thread (a interface não trava)
- 📦 Preparado para empacotamento em `.exe` com PyInstaller

---

## 🖥 Interface

A interface gráfica foi construída com **Tkinter**, sem dependências externas para GUI.

Durante o download, a aplicação exibe informações como:

Playlist: vídeo 2 de 8
[2/8] 45.3% | 3.2MiB/s | ETA 00:09
Nome do vídeo atual


---

## 🧰 Tecnologias utilizadas

- Python 3.10+
- yt-dlp
- ffmpeg
- Tkinter
- subprocess
- threading
- PyInstaller (opcional)

---

## 📦 Requisitos

- Python instalado (não requer privilégios de administrador)
- Node.js acessível no PATH (necessário para desafios JS do YouTube)
- ffmpeg portátil (binário)

---

## ⚙️ Instalação (recomendado usar venv)

```bash
python -m venv venv
venv\Scripts\activate
pip install yt-dlp
```
Garanta que o node esteja acessível via terminal.

---

##▶️Executando a aplicação
```bash
python gui_app.py
```
- também existe a opção de usar o ```run.cmd```
  
---

##📁 Estrutura do projeto

YT-DLP APP/
│
├── gui_app.py          # Interface gráfica (Tkinter)
├── cli_downloader.py   # Engine de download (yt-dlp via subprocess)
├── ffmpeg/
│   └── bin/
│       └── ffmpeg.exe
├── venv/
└── README.md

---

🛑 Cancelamento

O botão Cancelar encerra o processo do yt-dlp com segurança, sem travar a interface.

---

📦 Gerando executável (.exe)

Instale o PyInstaller:
```bash
pip install pyinstaller
```
Gere o executável
```bash
py -m PyInstaller ^
  --onefile ^
  --name YTDLP-App ^
  --add-binary "ffmpeg/bin/ffmpeg.exe;ffmpeg/bin" ^
  gui_app.py
```
Executável sera criado em dist/YTDLP-App.exe

---

🚀 Roadmap (ideias futuras)

-📊 Progresso total da playlist

-⚙️Configurações Avançadas

-📁 Lista visual dos vídeos da playlist

-🧵 Fila de downloads

-🎨 Melhorias visuais na interface

-🧾 Log detalhado opcional

-🌍 Suporte a mais sites

----

##Desenvolvido por Zelo


