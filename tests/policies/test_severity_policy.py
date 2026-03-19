"""
Tests para SeverityPolicy.
"""

import pytest

from src.policies.severity_policy import SeverityPolicy


class TestSeverityPolicy:
    def test_assess_high(self):
        policy = SeverityPolicy()

        assert policy.assess("Esto es terrible, parece fraude") == "high"

    def test_assess_medium(self):
        policy = SeverityPolicy()

        assert policy.assess("Estoy molesto por este problema") == "medium"

    def test_assess_low(self):
        policy = SeverityPolicy()

        assert policy.assess("Tengo una duda sobre mi pedido") == "low"

    @pytest.mark.parametrize(
        "message, expected",
        [
            ("Servicio terrible e inaceptable", "high"),
            ("Esto parece una estafa", "high"),
            ("Estoy muy decepcionado y molesto", "medium"),
            ("Hubo un error con mi producto", "medium"),
            ("Solo queria pedir informacion", "low"),
            ("Necesito saber los tiempos de envio", "low"),
        ],
    )
    def test_assess_classification_matrix(self, message, expected):
        policy = SeverityPolicy()

        assert policy.assess(message) == expected

    def test_assess_should_accept_accent_variants(self):
        policy = SeverityPolicy()

        assert policy.assess("El servicio es pesimo") == "high"
        assert policy.assess("El servicio es pésimo") == "high"

    def test_assess_should_reduce_false_positives_on_negations(self):
        policy = SeverityPolicy()

        assert policy.assess("No es terrible, solo una duda") == "low"
        assert policy.assess("Sin problema, solo quiero informacion") == "low"
