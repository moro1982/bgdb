import sys
import os

venv_path = '/app/venv'  # Ruta al entorno virtual dentro del contenedor
sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.12', 'site-packages'))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src import app as application

