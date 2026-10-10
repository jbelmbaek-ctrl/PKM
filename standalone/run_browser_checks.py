"""Serve only on loopback and run current standalone integration checks."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os,subprocess,sys,threading
root=Path(__file__).resolve().parent
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root.parent/'dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
env={**os.environ,'PKM_TEST_URL':f'http://127.0.0.1:{server.server_port}/PKM-UI-V2.3.html'}
try:
 for name in sys.argv[1:] or ['v5','details','ui_v2','cardmarket','security','bundle','sv7','scroll','import_workflow','inventory_workflow']:
  subprocess.run([sys.executable,str(root/f'browser_check_{name}.py')],env=env,check=True)
finally:server.shutdown();server.server_close()
