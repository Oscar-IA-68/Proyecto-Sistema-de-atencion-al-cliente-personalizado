"""
Tests para Database Simulator
"""

import pytest
from src.infrastructure.database_sim import DatabaseSimulator


class TestDatabaseSimulator:
    """Tests para el simulador de base de datos"""
    
    @pytest.fixture
    def db(self):
        """Fixture que crea una instancia de BD para tests"""
        return DatabaseSimulator()
    
    def test_database_initialization(self, db):
        """Test que la BD se inicializa correctamente"""
        assert db is not None
        assert db._customers is not None
        assert db._products is not None
        assert db._tickets is not None
        assert db._faq is not None
    
    def test_get_customers(self, db):
        """Test que retorna lista de clientes"""
        customers = db.get_customers()
        
        assert isinstance(customers, list)
        assert len(customers) > 0
        # Verificar estructura de un cliente
        customer = customers[0]
        assert "id" in customer
        assert "name" in customer
        assert "email" in customer
    
    def test_get_customer_by_id(self, db):
        """Test que retorna un cliente por ID"""
        customer = db.get_customer_by_id(1)
        
        assert customer is not None
        assert customer["id"] == 1
        assert "name" in customer
    
    def test_get_customer_by_invalid_id(self, db):
        """Test que retorna None para ID inválido"""
        customer = db.get_customer_by_id(9999)
        
        assert customer is None
    
    def test_get_products(self, db):
        """Test que retorna lista de productos"""
        products = db.get_products()
        
        assert isinstance(products, list)
        assert len(products) > 0
        # Verificar estructura
        product = products[0]
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "category" in product
    
    def test_get_products_by_category(self, db):
        """Test que filtra productos por categoría"""
        # Primero obtenemos todas las categorías disponibles
        all_products = db.get_products()
        if all_products:
            category = all_products[0]["category"]
            filtered = db.get_products(category=category)
            
            assert isinstance(filtered, list)
            # Todos deben ser de la misma categoría
            for product in filtered:
                assert product["category"] == category
    
    def test_get_tickets(self, db):
        """Test que retorna lista de tickets"""
        tickets = db.get_tickets()
        
        assert isinstance(tickets, list)
        assert len(tickets) >= 0  # Puede estar vacío
    
    def test_get_tickets_by_customer(self, db):
        """Test que filtra tickets por cliente"""
        tickets = db.get_tickets(customer_id=1)
        
        assert isinstance(tickets, list)
        # Si hay tickets, verificar que son del cliente correcto
        for ticket in tickets:
            assert ticket["customer_id"] == 1
    
    def test_create_ticket(self, db):
        """Test que crea un nuevo ticket"""
        initial_count = len(db.get_tickets())
        
        new_ticket = db.create_ticket(
            customer_id=1,
            ticket_type="support",
            subject="Test ticket"
        )
        
        assert new_ticket is not None
        assert "id" in new_ticket
        assert new_ticket["customer_id"] == 1
        assert new_ticket["type"] == "support"
        assert new_ticket["subject"] == "Test ticket"
        assert new_ticket["status"] == "open"
        
        # Verificar que se agregó a la lista
        final_count = len(db.get_tickets())
        assert final_count == initial_count + 1
    
    def test_get_faq(self, db):
        """Test que retorna lista de FAQ"""
        faq = db.get_faq()
        
        assert isinstance(faq, list)
        assert len(faq) > 0
        # Verificar estructura
        faq_item = faq[0]
        assert "question" in faq_item
        assert "answer" in faq_item
    
    def test_search_faq(self, db):
        """Test búsqueda en FAQ"""
        results = db.search_faq("contraseña")
        
        assert isinstance(results, list)
        # Debería encontrar resultados relevantes
        assert len(results) > 0
        # Verificar que tienen score de relevancia
        assert "relevance_score" in results[0]
    
    def test_search_faq_no_results(self, db):
        """Test búsqueda en FAQ sin resultados"""
        results = db.search_faq("xyzabc123nonexistent")
        
        assert isinstance(results, list)
        # Puede estar vacío si no hay match
        assert len(results) >= 0
    
    def test_get_stats(self, db):
        """Test que retorna estadísticas"""
        stats = db.get_stats()
        
        assert isinstance(stats, dict)
        assert "total_customers" in stats
        assert "total_products" in stats
        assert "total_tickets" in stats
        assert "total_faq" in stats
        assert stats["total_customers"] > 0
        assert stats["total_products"] > 0
