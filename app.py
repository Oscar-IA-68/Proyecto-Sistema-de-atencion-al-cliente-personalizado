"""
Entry Point - Streamlit Interface
Punto de entrada para la interfaz web Streamlit
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.streamlit_ui import main

if __name__ == "__main__":
    main()
