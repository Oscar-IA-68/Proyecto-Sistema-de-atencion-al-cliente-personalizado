"""
Configuración de pytest
"""

import sys
import os
import shutil
from pathlib import Path

import pytest

from src.core.config import Config

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def isolated_data_dir(tmp_path_factory):
	"""Crea una copia aislada de data/ para evitar mutaciones en archivos reales."""
	project_root = Path(__file__).resolve().parent.parent
	source_data_dir = project_root / "data"
	temp_data_dir = tmp_path_factory.mktemp("isolated_data")

	for filename in ["customers.json", "products.json", "tickets.json", "faq.json"]:
		shutil.copy2(source_data_dir / filename, temp_data_dir / filename)

	return temp_data_dir


@pytest.fixture(autouse=True)
def patch_config_data_paths(monkeypatch, isolated_data_dir):
	"""Redirecciona Config para que DatabaseSimulator use archivos temporales."""
	monkeypatch.setattr(Config, "DATA_DIR", str(isolated_data_dir))
	monkeypatch.setattr(Config, "CUSTOMERS_FILE", str(isolated_data_dir / "customers.json"))
	monkeypatch.setattr(Config, "PRODUCTS_FILE", str(isolated_data_dir / "products.json"))
	monkeypatch.setattr(Config, "TICKETS_FILE", str(isolated_data_dir / "tickets.json"))
	monkeypatch.setattr(Config, "FAQ_FILE", str(isolated_data_dir / "faq.json"))
