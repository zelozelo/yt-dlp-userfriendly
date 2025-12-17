from cli_downloader import CLIDownloader
import time
import threading
import msvcrt

PROFILES = {
    "1": ("best", "Melhor qualidade disponível"),
    "2": ("mp4", "Vídeo MP4"),
    "3": ("webm", "Vídeo WEBM"),
    "4": ("audio", "Somente áudio"),
    "5": ("mp3", "Áudio MP3"),
    "6": ("low", "Vídeo até 480p")
}

def choose_profile():
    print("\nEscolha o formato de saída:\n")

    for key, (_, desc) in PROFILES.items():
        print(f"{key} - {desc}")

    while True:
        choice = input("\nDigite o número do perfil: ").strip()
        if choice in PROFILES:
            return PROFILES[choice][0]

        print("❌ Opção inválida, tente novamente.")
        
def ask_url():
    while True:
        url = input("\nCole o link do vídeo: ").strip()
        if url.startswith("http"):
            return url
        print("❌ URL inválida.")
        
        
def on_output(data):
    t = data["type"]

    if t == "progress":
        print(f"{data['percent']:.1f}% | {data['speed']} | ETA {data['eta']}")

    elif t == "status":
        print(data["message"])

    elif t == "log":
        pass  # logs técnicos ocultos



def on_finish():
    print("\n✅ Download concluído!")


def on_error(msg):
    print("\n❌ Erro:", msg)
    return
def main():
    print("🎬 YT-DLP APP\n")

    while True:
        url = ask_url()
        profile = choose_profile()

        print(f"\n▶ Link: {url}")
        print(f"🎞 Perfil: {profile}")
        print("Iniciando download...")
        print("(pressione ESC para cancelar)\n")

        d = CLIDownloader()

        d.download(
            url,
            profile=profile,
            on_output=on_output,
            on_finish=on_finish,
            on_error=on_error
        )

        esc_thread = threading.Thread(
            target=listen_for_esc,
            args=(d,),
            daemon=True
        )
        esc_thread.start()

        while d.is_running():
            time.sleep(0.1)

        if not ask_repeat():
            print("\n👋 Encerrando aplicação.")
            break


def listen_for_esc(downloader):
    while downloader.is_running():
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x1b':  # ESC
                print("\n⛔ Cancelando download...")
                downloader.cancel()
                break
        time.sleep(0.1)

def ask_repeat():
    while True:
        choice = input("\nDeseja baixar outro vídeo? [S/N]: ").strip().lower()
        if choice in ("s", "n"):
            return choice == "s"
        print("❌ Opção inválida.")



if __name__ == "__main__":
    main()