"""
Tests para TicketPolicy.
"""

import pytest

from src.policies.ticket_policy import TicketPolicy


class TestTicketPolicy:
    def test_should_create_ticket_for_trigger_words(self):
        policy = TicketPolicy()

        assert policy.should_create_ticket("Tengo un error en mi cuenta") is True
        assert policy.should_create_ticket("No funciona el sistema") is True
        assert policy.should_create_ticket("Esto es urgente") is True

    def test_should_not_create_ticket_for_general_messages(self):
        policy = TicketPolicy()

        assert policy.should_create_ticket("Hola, solo queria saludar") is False
        assert policy.should_create_ticket("Gracias por tu ayuda") is False

    @pytest.mark.parametrize(
        "message, expected",
        [
            ("ERROR al iniciar sesion", True),
            ("No Funciona el checkout", True),
            ("Esto es un problema grave", True),
            ("Necesito ayuda urgente con mi pago", True),
            ("Tengo un problema leve", False),
            ("Consulta sobre metodos de pago", False),
            ("No hay error ahora", False),
        ],
    )
    def test_ticket_policy_behavior_matrix(self, message, expected):
        policy = TicketPolicy()

        assert policy.should_create_ticket(message) is expected

    def test_should_create_when_negated_error_but_real_trigger_exists(self):
        policy = TicketPolicy()

        assert policy.should_create_ticket("No hay error, pero no funciona el sistema") is True

    def test_should_respect_custom_trigger_words(self):
        policy = TicketPolicy(trigger_words=["caido", "caido total"])

        assert policy.should_create_ticket("Servicio caido") is True
        assert policy.should_create_ticket("Tengo un error") is False
