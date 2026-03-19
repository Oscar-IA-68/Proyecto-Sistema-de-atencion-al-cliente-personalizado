"""
Entry Point - CLI Interface
Punto de entrada para la interfaz de línea de comandos
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.cli_interface import main

if __name__ == "__main__":
    main()
