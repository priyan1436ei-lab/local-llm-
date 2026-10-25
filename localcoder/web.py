"""Loopback-only local UI; no third-party Python dependencies."""
import json
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .agent import CodingAgent
from .config import Settings, detect_vram_gb
from .ollama_client import OllamaClient

BASE = Path(__file__).resolve().parent.parent
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.RLock()
STATE = {'running': False, 'events': [], 'pending': None, 'result': '', 'workspace': ''}
STOP = threading.Event()
APPROVED = threading.Event()
DECISION = False

def event(data):
    with LOCK:
        STATE['events'].append(data)
        STATE['events'] = STATE['events'][-200:]

def approve(command):
    global DECISION
    with LOCK:
        APPROVED.clear()
        DECISION = False
        STATE['pending'] = command
    while not APPROVED.wait(.25):
        if STOP.is_set():
            break
    with LOCK:
        STATE['pending'] = None
        return DECISION and not STOP.is_set()

def work(data):
    try:
        settings = Settings.auto()
        settings.model = data.get('model') or settings.model
        settings.num_ctx = int(data.get('context', 4096))
        if settings.num_ctx not in (2048, 4096, 8192):
            raise ValueError('Unsupported context size')
        root = Path(data.get('workspace') or str(BASE/'workspace')).expanduser().resolve()
        agent = CodingAgent(root, settings, verbose=False)
        agent.tools.approve = approve
        agent.on_event = event
        agent.cancelled = STOP.is_set
        with LOCK:
            STATE['workspace'] = str(root)
        result = agent.run(data['prompt'][:12000])
        with LOCK:
            STATE['result'] = result
    except Exception as exc:
        with LOCK:
            STATE['result'] = f'Error: {exc}'
    finally:
        with LOCK:
            STATE['running'] = False
            STATE['pending'] = None
            snapshot = dict(STATE)
        try:
            logdir = BASE/'runs'
            logdir.mkdir(exist_ok=True)
            (logdir/f'{time.time_ns()}.json').write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
        except OSError:
            pass

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send(self, data, code=200, html=False):
        body = data.encode() if html else json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8' if html else 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get('Host') in ('127.0.0.1:8765', 'localhost:8765')

    def do_GET(self):
        if not self.valid_host():
            return self.send({'error':'Invalid host'},403)
        if self.path == '/':
            return self.send((BASE/'localcoder/ui.html').read_text(encoding='utf-8').replace('__TOKEN__',TOKEN),html=True)
        if self.headers.get('X-LocalCoder-Token') != TOKEN:
            return self.send({'error':'Unauthorized'},403)
        if self.path == '/api/state':
            with LOCK:
                return self.send(STATE)
        if self.path == '/api/status':
            settings = Settings.auto()
            try:
                models = OllamaClient(settings.ollama_url).tags().get('models', [])
                self.send({'models':[m['name'] for m in models], 'default':settings.model, 'vram':detect_vram_gb()})
            except Exception as exc:
                self.send({'error':str(exc), 'default':settings.model, 'models':[]})
            return
        self.send({'error':'Not found'},404)

    def do_POST(self):
        global DECISION
        if not self.valid_host() or self.headers.get('X-LocalCoder-Token') != TOKEN:
            return self.send({'error':'Unauthorized'},403)
        try:
            size = int(self.headers.get('Content-Length','0'))
            if not 0 < size <= 32000:
                raise ValueError('Invalid request size')
            data = json.loads(self.rfile.read(size))
            with LOCK:
                if self.path == '/api/start':
                    if STATE['running']:
                        return self.send({'error':'A task is already running'},409)
                    if not isinstance(data.get('prompt'),str) or not data['prompt'].strip():
                        raise ValueError('Enter a prompt')
                    STATE.update(running=True,events=[],pending=None,result='')
                    STOP.clear()
                    threading.Thread(target=work,args=(data,),daemon=True).start()
                elif self.path == '/api/approve':
                    if STATE['pending'] is None:
                        raise ValueError('No pending command')
                    DECISION = data.get('allow') is True
                    APPROVED.set()
                elif self.path == '/api/stop':
                    STOP.set()
                    APPROVED.set()
                else:
                    return self.send({'error':'Not found'},404)
            self.send({'ok':True})
        except (ValueError,TypeError) as exc:
            self.send({'error':str(exc)},400)

def main():
    server = ThreadingHTTPServer(('127.0.0.1',8765),Handler)
    print('LocalCoder: http://127.0.0.1:8765 — Ctrl+C to exit')
    webbrowser.open('http://127.0.0.1:8765')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        STOP.set()
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
