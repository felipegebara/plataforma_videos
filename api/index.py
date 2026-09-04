"""
api/index.py
============
Entrypoint para deploy Serverless na Vercel.
Exporta a aplicação FastAPI 'app' do arquivo api/server.py.
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from api.server import app
