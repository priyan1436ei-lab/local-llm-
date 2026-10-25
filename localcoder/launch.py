"""Check prerequisites, fetch missing model and open the local agent."""
import shutil
import subprocess
import sys
import time
from pathlib import Path
from .config import Settings
from .ollama_client import OllamaClient, OllamaError


def prepare(settings, client):
    executable = shutil.which('ollama')
    if not executable:
        print('Install Ollama first: https://ollama.com/download/windows')
        return False
    try:
        tags = client.tags()
    except OllamaError:
        print('Starting Ollama...')
        subprocess.Popen([executable, 'serve'], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        for _ in range(40):
            time.sleep(.5)
            try:
                tags = client.tags()
                break
            except OllamaError:
                pass
        else:
            print('Ollama could not start. Open it manually and try again.')
            return False
    if settings.model not in {m.get('name') for m in tags.get('models', [])}:
        print(f'First setup: downloading {settings.model}. Internet is needed once.')
        if subprocess.call([executable, 'pull', settings.model]) != 0:
            print('Model download failed. Check your connection and launch again.')
            return False
    return True


def main():
    print('LOCALCODER RTX | Your local coding agent')
    settings = Settings.auto()
    print(f'Model: {settings.model} | Context: {settings.num_ctx}')
    if not prepare(settings, OllamaClient(settings.ollama_url)):
        return 1
    from .web import main as start_web
    start_web()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
