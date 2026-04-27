from abc import ABC, abstractmethod
# ------------------------------------------------------------
# Solución del Sistema de gestión de Clientes Servivios y Reservas
# Grupo: 213023_145
# Programa: Ingeniería de Sistemas
# Código fuente: Autoría propia
#
# INTEGRANTES
# Yamid Claro Alvarez
# Libardo Antonio Galeano Rios
# ------------------------------------------------------------

# INICIO

# CLASE ABSTRACTA BASE
class Entidad(ABC):
    def __init__(self, id):
        self._id = id
        
    @abstractmethod
    def show_info(self):
        pass

# CLASE CLIENTE
class Cliente(Entidad):
    def __init__(self, id, name, email):
        super().__init__(id)
        self._name= name
        self._email= email
        
    def show_info(self):
        return f"Cliente: {self._name} - {self._email}"
    
# CLASE SERVICIO
class Servicio(ABC):
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    @abstractmethod
    def description(self):
        pass
    
# CLASE RESERVA
class Reserva:
    def __init__(self, client, service, duration):
        self.client = client
        self.service = service
        self.duration = duration
        self.status = "PENDIENTE"
        
    def cancel(self):
        self.status == "CANCELADA"
        
    def show(self):
        return f"{self.client.show_info()} - {self.service.description()} - Estado: {self.status}"
            