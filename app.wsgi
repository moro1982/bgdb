import sys
import os

sys.path.insert(0, '/usr/local/lib/python3.12/site-packages')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app as application
