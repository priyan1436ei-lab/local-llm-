"""Exercise the actual HTTP -> worker -> tools flow with deterministic model actions."""
import json
import tempfile
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from localcoder import web

class WebFlowTests(unittest.TestCase):
    def test_prompt_creates_files_and_approval_runs_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            actions = iter([
                {'action':'write_file','path':'hello.py','content':'print("Hello Priyan")\n'},
                {'action':'run_command','command':'echo verified'},
                {'action':'finish','message':'Files created; command completed.'},
            ])
            with patch.object(web, 'BASE', root), patch('localcoder.ollama_client.OllamaClient.chat', side_effect=lambda **_: next(actions)):
                server = ThreadingHTTPServer(('127.0.0.1',0),web.Handler)
                thread = threading.Thread(target=server.serve_forever,daemon=True)
                thread.start()
                def request(path, data=None, authorized=True):
                    headers = {'Host':'127.0.0.1:8765','Content-Type':'application/json'}
                    if authorized: headers['X-LocalCoder-Token'] = web.TOKEN
                    req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/{path}',
                        data=json.dumps(data).encode() if data is not None else None, headers=headers)
                    with urllib.request.urlopen(req,timeout=3) as response:
                        return json.load(response)
                try:
                    with self.assertRaises(urllib.error.HTTPError) as denied:
                        request('state',authorized=False)
                    self.assertEqual(denied.exception.code,403)
                    request('start',{'prompt':'Build hello','workspace':str(root/'project')})
                    deadline=time.monotonic()+5
                    while time.monotonic()<deadline:
                        state=request('state')
                        if state['pending']: break
                        time.sleep(.02)
                    self.assertEqual(state['pending'],'echo verified')
                    self.assertEqual((root/'project/hello.py').read_text(),'print("Hello Priyan")\n')
                    request('approve',{'allow':True})
                    while time.monotonic()<deadline:
                        state=request('state')
                        if not state['running']: break
                        time.sleep(.02)
                    self.assertFalse(state['running'])
                    self.assertEqual(state['result'],'Files created; command completed.')
                    self.assertTrue(any('exit_code=0' in e.get('result','') for e in state['events']))
                finally:
                    web.STOP.set()
                    server.shutdown()
                    server.server_close()

if __name__ == '__main__': unittest.main()
