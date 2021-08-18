import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = os.path.join(BASE_DIR, 'data', 'preprocessing', 'template.jpg')