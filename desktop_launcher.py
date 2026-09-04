"""
Desktop Launcher — Executável de 1 Clique para o Rota Calculada Video Studio.
Inicia o servidor local FastAPI com SQLite e abre a interface gráfica no navegador padrão.
"""
import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# Configura o path do projeto
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.resilience import ensure_ffmpeg_configured
import uvicorn

def open_browser(url: str, delay: float = 1.5):
    time.sleep(delay)
    print(f"\n🌐 Abrindo interface no navegador: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Não foi possível abrir o navegador automaticamente: {e}")

def main():
    print("==========================================================")
    print(" 🌟 INICIANDO ROTA CALCULADA VIDEO STUDIO (DESKTOP) 🌟")
    print("==========================================================")

    # 1. Configura FFmpeg embutido
    ffmpeg_path = ensure_ffmpeg_configured()
    print(f"✓ FFmpeg configurado: {ffmpeg_path}")

    # 2. Prepara diretórios
    for d in ["uploads", "videos", "thumbnails", "audio", "data"]:
        (project_root / "output" / d).mkdir(parents=True, exist_ok=True)
    print("✓ Diretórios de dados e saída prontos.")

    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    # 3. Dispara abertura do navegador em thread separada
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # 4. Inicia o servidor local FastAPI
    print(f"✓ Servidor iniciado em {url}")
    print("Pressione CTRL+C para encerrar o aplicativo.\n")
    
    from api.server import app
    uvicorn.run(app, host=host, port=port, log_level="warning")

if __name__ == "__main__":
    main()
