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

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from abc import ABC, abstractmethod
import datetime
import traceback
from enum import Enum

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
    def __init__(self, id_servicio, name, price):
        self._id = id_servicio
        self.name = name
        self.price = price
        self._disponible = True
    
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
    
    @abstractmethod
    def calculate_cost(self, duration):
        pass

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def validate_parameters(self, **kwargs):
        pass
    
    # Métodos sobrecargados para cálculo de costos
    def calculate_cost_with_tax(self, duration, tax=0.19):
        """Calcula costo con impuesto"""
        base = self.calculate_cost(duration)
        return base * (1 + tax)

    def calculate_cost_with_discount(self, duration, discount=0):
        """Calcula costo con descuento (método sobrecargado)"""
        base = self.calculate_cost(duration)
        return base * (1 - discount)

    def calculate_total_cost(self, duration, tax=0.19, discount=0):
        """Calcula costo con impuesto y descuento (sobrecarga)"""
        base = self.calculate_cost(duration)
        with_tax = base * (1 + tax)
        return with_tax * (1 - discount)

    @property
    def name(self):
        return self._name

    @property
    def available(self):
        return self._available

    @available.setter
    def available(self, value):
        self._available = value

    def show_info(self):
        return f"Service: {self._name} - Base price: ${self._base_price:,.0f}"  