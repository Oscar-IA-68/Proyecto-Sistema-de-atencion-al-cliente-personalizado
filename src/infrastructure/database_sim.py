"""
Base de datos simulada - Implementa IDatabase
Lee/escribe datos desde archivos JSON para simular una BD real
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from src.core.interfaces import IDatabase
from src.core.config import Config


class DatabaseSimulator(IDatabase):
    """
    Simulador de base de datos usando JSON
    Implementa IDatabase para cumplir con DIP (Dependency Inversion Principle)
    
    En producción podría reemplazarse por PostgreSQL, MongoDB, etc. sin cambiar código
    """
    
    def __init__(self):
        """Inicializa el simulador cargando datos JSON"""
        self.customers_file = Config.CUSTOMERS_FILE
        self.products_file = Config.PRODUCTS_FILE
        self.tickets_file = Config.TICKETS_FILE
        self.faq_file = Config.FAQ_FILE
        
        # Cargar datos en memoria
        self._customers = self._load_json(self.customers_file)
        self._products = self._load_json(self.products_file)
        self._tickets = self._load_json(self.tickets_file)
        self._faq = self._load_json(self.faq_file)
        
        print("✅ Base de datos simulada cargada correctamente")
    
    def _load_json(self, filepath: str) -> List[Dict[str, Any]]:
        """Carga datos desde archivo JSON"""
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"⚠️  Archivo no encontrado: {filepath}, usando lista vacía")
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error al cargar {filepath}: {e}")
            return []
    
    def _save_json(self, filepath: str, data: List[Dict[str, Any]]) -> bool:
        """Guarda datos a archivo JSON"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error al guardar {filepath}: {e}")
            return False
    
    # ==================== CUSTOMERS ====================
    
    def get_customers(self) -> List[Dict[str, Any]]:
        """Obtiene lista de todos los clientes"""
        print("📊 [SIMULACIÓN BD] Consultando base de datos de clientes...")
        return self._customers.copy()
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente específico por ID"""
        print(f"🔍 [SIMULACIÓN BD] Buscando cliente con ID {customer_id}...")
        for customer in self._customers:
            if customer.get("id") == customer_id:
                return customer.copy()
        return None
    
    # ==================== PRODUCTS ====================
    
    def get_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene productos, opcionalmente filtrados por categoría"""
        print(f"📦 [SIMULACIÓN BD] Consultando productos" + 
              (f" en categoría '{category}'" if category else "") + "...")
        
        if category:
            return [p.copy() for p in self._products if p.get("category") == category]
        return self._products.copy()
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto específico por ID"""
        print(f"🔍 [SIMULACIÓN BD] Buscando producto con ID {product_id}...")
        for product in self._products:
            if product.get("id") == product_id:
                return product.copy()
        return None
    
    # ==================== TICKETS ====================
    
    def get_tickets(self, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene tickets, opcionalmente filtrados por cliente"""
        print(f"🎫 [SIMULACIÓN BD] Consultando tickets" + 
              (f" del cliente {customer_id}" if customer_id else "") + "...")
        
        if customer_id:
            return [t.copy() for t in self._tickets if t.get("customer_id") == customer_id]
        return self._tickets.copy()
    
    def create_ticket(self, customer_id: int, ticket_type: str, 
                     subject: str) -> Dict[str, Any]:
        """Crea un nuevo ticket de soporte"""
        print(f"✍️  [SIMULACIÓN BD] Creando nuevo ticket de tipo '{ticket_type}'...")
        
        # Generar nuevo ID
        new_id = max([t.get("id", 0) for t in self._tickets], default=0) + 1
        
        new_ticket = {
            "id": new_id,
            "customer_id": customer_id,
            "type": ticket_type,
            "subject": subject,
            "status": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "resolved_at": None
        }
        
        self._tickets.append(new_ticket)
        saved = self._save_json(self.tickets_file, self._tickets)

        if not saved:
            print(
                f"⚠️  Ticket #{new_id} creado en memoria, "
                "pero no se pudo persistir en disco"
            )
            new_ticket["persisted"] = False
            return new_ticket.copy()

        new_ticket["persisted"] = True
        print(f"✅ Ticket #{new_id} creado exitosamente")
        return new_ticket.copy()
    
    # ==================== FAQ ====================
    
    def get_faq(self) -> List[Dict[str, Any]]:
        """Obtiene todas las preguntas frecuentes"""
        print("❓ [SIMULACIÓN BD] Consultando FAQ...")
        return self._faq.copy()
    
    def search_faq(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca en FAQ por similitud de texto
        Implementación simple basada en palabras clave
        """
        print(f"🔎 [SIMULACIÓN BD] Buscando en FAQ: '{query}'...")
        
        query_lower = query.lower()
        results = []
        
        for faq_item in self._faq:
            question = faq_item.get("question", "").lower()
            answer = faq_item.get("answer", "").lower()
            
            # Búsqueda simple por palabras clave
            query_words = set(query_lower.split())
            question_words = set(question.split())
            answer_words = set(answer.split())
            
            # Calcular coincidencias
            question_match = len(query_words & question_words)
            answer_match = len(query_words & answer_words)
            
            if question_match > 0 or answer_match > 0:
                # Agregar con score de relevancia
                score = question_match * 2 + answer_match  # Preguntas valen más
                results.append({
                    **faq_item,
                    "relevance_score": score
                })
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Retornar top 3
        return results[:3]
    
    # ==================== STATS & UTILS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos"""
        return {
            "total_customers": len(self._customers),
            "total_products": len(self._products),
            "total_tickets": len(self._tickets),
            "total_faq": len(self._faq),
            "open_tickets": len([t for t in self._tickets if t.get("status") == "open"]),
            "product_categories": list(set(p.get("category") for p in self._products))
        }
