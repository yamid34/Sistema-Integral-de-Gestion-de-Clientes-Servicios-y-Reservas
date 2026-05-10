from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from abc import ABC, abstractmethod
import datetime
import traceback
import os
import time
import logging
import re
from enum import Enum
import json

# ------------------------------------------------------------
# Solución del Sistema de gestión de Clientes Servivios y Reservas
# Grupo: 213023_145
# Programa: Ingeniería de Sistemas
# Código fuente: Autoría propia
#
# INTEGRANTES
# Yamid Claro Alvarez
# Libardo Antonio Galeano Rios
# Oscar Fernando Arias Alba 
# ------------------------------------------------------------

# INICIO
# ============================================================
# CONFIGURACIÓN DE LOGS
# ============================================================

# =========================================
# CONFIGURACIÓN LOGS
# =========================================

LOG_FILE = "logs_error.log"

# =========================================
# ELIMINAR CONTENIDO SI PASARON 15 DÍAS
# =========================================

DIAS_LIMITE = 15

if os.path.exists(LOG_FILE):

    tiempo_creacion = os.path.getctime(LOG_FILE)

    tiempo_actual = time.time()

    dias_transcurridos = (
        tiempo_actual - tiempo_creacion
    ) / (60 * 60 * 24)

    # Si pasaron más de 15 días
    if dias_transcurridos >= DIAS_LIMITE:

        # Vaciar archivo
        open(LOG_FILE, "w", encoding="utf-8").close()

# =========================================
# LOGGER
# =========================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# CLASE ABSTRACTA BASE
class Entidad(ABC):
    def __init__(self, id):
        self._id = id

    @abstractmethod
    def show_info(self):
        pass


# CLASE CLIENTE
class Cliente(Entidad):
    def __init__(self, id, name, email, phone):
        super().__init__(id)
        self._name = name
        self._email = email
        self._phone = phone

    def show_info(self):
        return f"Cliente: {self._name} - {self._email} - {self._phone}"

    def __eq__(self, other):
        """Compara clientes por email, teléfono o nombre"""
        if isinstance(other, Cliente):
            return (self._email.lower() == other._email.lower() or 
                    self._phone == other._phone or
                    self._name.lower() == other._name.lower())
        return False
    
    
# CLASE SERVICIO
class Servicio(ABC):
    def __init__(self, id_servicio, name, price, description=""):
        self._id = id_servicio
        self.name = name
        self.price = price
        self._description = description    
        self._disponible = True
        self._category = "General"
        
    @abstractmethod
    def get_details(self):
        """Retorna detalles específicos del servicio"""
        pass   
    
    @abstractmethod
    def calculate_daily_cost(self, hours):
        """Calcula costo según horas trabajadas"""
        pass

    # Propiedades
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value > 0:
            self._price = value

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, value):
        self._disponible = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    def show_info(self):
        estado = "✓ Disponible" if self._disponible else "✗ No Disponible"
        return f"{self._name} - ${self._price:,.0f} - {estado}"
    
    def __eq__(self, other):
        """Compara servicios por nombre"""
        if isinstance(other, Servicio):
            return self._name.lower() == other._name.lower()
        return False
  

# CLASE SERVICIO ESTÁNDAR
class ServicioEstandar(Servicio):
    def __init__(self, id_servicio, name, price, description=""):
        super().__init__(id_servicio, name, price, description)
        self._category = "Estándar"
        self._tiempo_base = 1  # horas mínimas

    def get_details(self):
        return f"Servicio Estándar - {self._description if self._description else 'Sin descripción'}"

    def calculate_daily_cost(self, hours):
        """Costo base por horas (sin impuestos)"""
        if hours < self._tiempo_base:
            hours = self._tiempo_base
        return self._price * hours


# CLASE SERVICIO PREMIUM
class ServicioPremium(Servicio):
    def __init__(self, id_servicio, name, price, description="", beneficio_extra=""):
        super().__init__(id_servicio, name, price, description)
        self._category = "Premium"
        self._factor_calidad = 1.3  # 30% más caro por hora

    def get_details(self):
        detalles = f"Servicio Premium - {self._description}"
        return detalles

    def calculate_daily_cost(self, hours):
        """Costo premium con factor de calidad"""
        if hours < 1:
            hours = 1
        return self._price * hours * self._factor_calidad


# CLASE SERVICIO EXPRESS
class ServicioExpress(Servicio):
    def __init__(self, id_servicio, name, price, description=""):
        super().__init__(id_servicio, name, price, description)
        self._category = "Express"
        self._recargo_urgencia = 1.5  # 50% más caro

    def get_details(self):
        return f"Servicio Express - Entrega rápida - {self._description if self._description else 'Sin descripción'}"

    def calculate_daily_cost(self, hours):
        """Costo express con recargo por urgencia"""
        if hours < 0.5:
            hours = 0.5
        costo_base = self._price * hours
        return costo_base * self._recargo_urgencia


# CLASE CATÁLOGO DE SERVICIOS (para gestionarlos)
class CatalogoServicios:
    def __init__(self):
        self._servicios = []
        self._ultimo_id = 0

    def agregar_servicio(self, servicio):
        """Agrega un servicio al catálogo"""
        self._servicios.append(servicio)
        self._ultimo_id = max(self._ultimo_id, servicio.id)

    def eliminar_servicio(self, servicio_id):
        """Elimina un servicio por ID"""
        self._servicios = [s for s in self._servicios if s.id != servicio_id]

    def buscar_servicio(self, servicio_id):
        """Busca servicio por ID"""
        for servicio in self._servicios:
            if servicio.id == servicio_id:
                return servicio
        return None

    def buscar_por_nombre(self, nombre):
        """Busca servicios que contengan el nombre"""
        return [s for s in self._servicios if nombre.lower() in s.name.lower()]

    def listar_servicios(self):
        """Retorna lista de todos los servicios"""
        return self._servicios.copy()

    def listar_disponibles(self):
        """Retorna solo servicios disponibles"""
        return [s for s in self._servicios if s.disponible]

    def obtener_nuevo_id(self):
        """Genera nuevo ID automático"""
        self._ultimo_id += 1
        return self._ultimo_id

    def obtener_servicios_por_categoria(self, categoria):
        """Filtra servicios por categoría"""
        return [s for s in self._servicios if s.category == categoria]
    
    def servicio_duplicado(self, nombre, id_excluir=None):
        """Verifica si existe un servicio con el mismo nombre"""
        for servicio in self._servicios:
            if servicio.name.lower() == nombre.lower():
                if id_excluir is None or servicio.id != id_excluir:
                    return True
        return False

# CLASE RESERVA
# ============================================================
# NUEVO MÓDULO DE RESERVAS
# ============================================================

class EstadoReserva(Enum):
    """Enumeración para los estados de una reserva"""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"


class ExcepcionReserva(Exception):
    """Excepción personalizada para errores de reserva"""
    pass

class ExcepcionCliente(Exception):
    """Excepción base de clientes"""
    pass


class ClienteInvalidoError(ExcepcionCliente):
    """Error de validación de cliente"""
    pass


class ClienteDuplicadoError(ExcepcionCliente):
    """Cliente ya registrado"""
    pass

class ClienteNoEncontradoError(ExcepcionCliente):
    """Cliente no encontrado"""
    pass


# ============================================================
# EXCEPCIONES PERSONALIZADAS PARA SERVICIOS
# ============================================================

class ExcepcionServicio(Exception):
    """Excepción base de servicios"""
    pass


class ServicioInvalidoError(ExcepcionServicio):
    """Datos inválidos del servicio"""
    pass


class ServicioDuplicadoError(ExcepcionServicio):
    """Servicio duplicado"""
    pass


class ServicioNoEncontradoError(ExcepcionServicio):
    """Servicio no encontrado"""
    pass


class Reserva:
    """Clase principal para gestionar reservas"""
    
    def __init__(self, cliente, servicio, duracion_horas, fecha=None):
        """
        Inicializa una nueva reserva
        
        Args:
            cliente: Objeto Cliente
            servicio: Objeto Servicio
            duracion_horas: Duración en horas
            fecha: Fecha de la reserva (datetime.date)
        """
        self._id = None
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._fecha = fecha or datetime.date.today()
        self._estado = EstadoReserva.PENDIENTE
        self._fecha_creacion = datetime.datetime.now()
        self._fecha_confirmacion = None
        self._fecha_cancelacion = None
        self._costo_total = None
        
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def servicio(self):
        return self._servicio
    
    @property
    def duracion_horas(self):
        return self._duracion_horas
    
    @property
    def fecha(self):
        return self._fecha
    
    @property
    def estado(self):
        return self._estado.value if isinstance(self._estado, EstadoReserva) else self._estado
    
    @property
    def costo_total(self):
        return self._costo_total
    
    def confirmar(self):
        """
        Confirma la reserva
        
        Raises:
            ExcepcionReserva: Si la reserva no se puede confirmar
        """
        if self._estado != EstadoReserva.PENDIENTE:
            raise ExcepcionReserva(f"No se puede confirmar una reserva en estado {self._estado.value}")
        
        if not self._servicio.disponible:
            raise ExcepcionReserva(f"El servicio '{self._servicio.name}' no está disponible")
        
        self._estado = EstadoReserva.CONFIRMADA
        self._fecha_confirmacion = datetime.datetime.now()
        
        # Calcular costo total
        self._costo_total = self._servicio.calculate_daily_cost(self._duracion_horas)
        
    def cancelar(self):
        """
        Cancela la reserva
        
        Raises:
            ExcepcionReserva: Si la reserva no se puede cancelar
        """
        if self._estado == EstadoReserva.CANCELADA:
            raise ExcepcionReserva("La reserva ya está cancelada")
        
        if self._estado == EstadoReserva.COMPLETADA:
            raise ExcepcionReserva("No se puede cancelar una reserva completada")
        
        self._estado = EstadoReserva.CANCELADA
        self._fecha_cancelacion = datetime.datetime.now()
    
    def completar(self):
        """
        Marca la reserva como completada
        
        Raises:
            ExcepcionReserva: Si la reserva no se puede completar
        """
        if self._estado != EstadoReserva.CONFIRMADA:
            raise ExcepcionReserva(f"Solo se pueden completar reservas confirmadas. Estado actual: {self._estado.value}")
        
        self._estado = EstadoReserva.COMPLETADA
    
    def calcular_costo_con_impuesto(self, tasa_impuesto=0.19):
        """
        Calcula el costo total incluyendo impuesto
        
        Args:
            tasa_impuesto: Tasa de impuesto (default 19%)
        
        Returns:
            float: Costo total con impuesto
        """
        if self._costo_total is None:
            self._costo_total = self._servicio.calculate_daily_cost(self._duracion_horas)
        return self._costo_total * (1 + tasa_impuesto)
    
    def calcular_costo_con_descuento(self, porcentaje_descuento=0):
        """
        Calcula el costo total aplicando descuento
        
        Args:
            porcentaje_descuento: Porcentaje de descuento (0-1)
        
        Returns:
            float: Costo total con descuento
        """
        if self._costo_total is None:
            self._costo_total = self._servicio.calculate_daily_cost(self._duracion_horas)
        return self._costo_total * (1 - porcentaje_descuento)
    
    def obtener_info_completa(self):
        """Retorna información completa de la reserva"""
        info = {
            "ID": self._id,
            "Cliente": self._cliente._name,
            "Servicio": self._servicio.name,
            "Categoría": self._servicio.category,
            "Duración (horas)": self._duracion_horas,
            "Fecha": self._fecha.strftime("%d/%m/%Y") if hasattr(self._fecha, 'strftime') else str(self._fecha),
            "Estado": self.estado,
            "Costo Total": f"${self._costo_total:,.0f}" if self._costo_total else "No calculado",
            "Fecha Creación": self._fecha_creacion.strftime("%d/%m/%Y %H:%M")
        }
        return info
    
    def __str__(self):
        return f"Reserva #{self._id} - {self._cliente._name} - {self._servicio.name} - {self.estado}"


class GestorReservas:
    """Clase para gestionar el conjunto de reservas"""
    
    def __init__(self):
        self._reservas = []
        self._ultimo_id = 0
    
    def crear_reserva(self, cliente, servicio, duracion_horas, fecha=None):
        """
        Crea una nueva reserva
        
        Args:
            cliente: Objeto Cliente
            servicio: Objeto Servicio
            duracion_horas: Duración en horas
            fecha: Fecha de la reserva
        
        Returns:
            Reserva: La reserva creada
        
        Raises:
            ExcepcionReserva: Si hay errores en la creación
        """
        # Validaciones
        if not cliente:
            raise ExcepcionReserva("Debe seleccionar un cliente")
        
        if not servicio:
            raise ExcepcionReserva("Debe seleccionar un servicio")
        
        if duracion_horas <= 0:
            raise ExcepcionReserva("La duración debe ser mayor a 0 horas")
        
        if duracion_horas > 24:
            raise ExcepcionReserva("La duración máxima por reserva es de 24 horas")
        
        # Crear reserva
        reserva = Reserva(cliente, servicio, duracion_horas, fecha)
        self._ultimo_id += 1
        reserva.id = self._ultimo_id
        
        self._reservas.append(reserva)
        
        # Log de creación
        logging.info(f"Reserva creada: #{reserva.id} - Cliente: {cliente._name} - Servicio: {servicio.name} - Duración: {duracion_horas}h")
        
        return reserva
    
    def confirmar_reserva(self, reserva_id):
        """
        Confirma una reserva por ID
        
        Args:
            reserva_id: ID de la reserva
        
        Returns:
            bool: True si se confirmó correctamente
        
        Raises:
            ExcepcionReserva: Si la reserva no existe o no se puede confirmar
        """
        reserva = self.buscar_reserva(reserva_id)
        if not reserva:
            raise ExcepcionReserva(f"No se encontró la reserva con ID {reserva_id}")
        
        reserva.confirmar()
        
        # Log de confirmación
        logging.info(f"Reserva confirmada: #{reserva_id} - Cliente: {reserva.cliente._name} - Costo: ${reserva.costo_total:,.0f}")
        
        return True
    
    def cancelar_reserva(self, reserva_id):
        """
        Cancela una reserva por ID
        
        Args:
            reserva_id: ID de la reserva
        
        Returns:
            bool: True si se canceló correctamente
        
        Raises:
            ExcepcionReserva: Si la reserva no existe o no se puede cancelar
        """
        reserva = self.buscar_reserva(reserva_id)
        if not reserva:
            raise ExcepcionReserva(f"No se encontró la reserva con ID {reserva_id}")
        
        reserva.cancelar()
        
        # Log de cancelación
        logging.info(f"Reserva cancelada: #{reserva_id} - Cliente: {reserva.cliente._name} - Servicio: {reserva.servicio.name}")
        
        return True
    
    def completar_reserva(self, reserva_id):
        """
        Marca una reserva como completada
        
        Args:
            reserva_id: ID de la reserva
        
        Returns:
            bool: True si se completó correctamente
        
        Raises:
            ExcepcionReserva: Si la reserva no existe o no se puede completar
        """
        reserva = self.buscar_reserva(reserva_id)
        if not reserva:
            raise ExcepcionReserva(f"No se encontró la reserva con ID {reserva_id}")
        
        reserva.completar()
        
        # Log de completado
        logging.info(f"Reserva completada: #{reserva_id} - Cliente: {reserva.cliente._name} - Servicio: {reserva.servicio.name}")
        
        return True
    
    def buscar_reserva(self, reserva_id):
        """Busca una reserva por ID"""
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        return None
    
    def listar_reservas(self, estado=None):
        """
        Lista todas las reservas, opcionalmente filtradas por estado
        
        Args:
            estado: EstadoReserva o string para filtrar
        
        Returns:
            list: Lista de reservas
        """
        if estado is None:
            return self._reservas.copy()
        
        estado_str = estado.value if isinstance(estado, EstadoReserva) else str(estado).upper()
        return [r for r in self._reservas if r.estado == estado_str]
    
    def listar_reservas_por_cliente(self, cliente_id):
        """Lista reservas de un cliente específico"""
        return [r for r in self._reservas if r.cliente._id == cliente_id]
    
    def obtener_resumen(self):
        """Obtiene un resumen estadístico de las reservas"""
        total = len(self._reservas)
        pendientes = len(self.listar_reservas(EstadoReserva.PENDIENTE))
        confirmadas = len(self.listar_reservas(EstadoReserva.CONFIRMADA))
        canceladas = len(self.listar_reservas(EstadoReserva.CANCELADA))
        completadas = len(self.listar_reservas(EstadoReserva.COMPLETADA))
        
        return {
            "total": total,
            "pendientes": pendientes,
            "confirmadas": confirmadas,
            "canceladas": canceladas,
            "completadas": completadas
        }


# ============================================================
# FIN MÓDULO DE RESERVAS
# ============================================================


# CLASE RESERVA (Original - Corregida)
class ReservaOriginal(ABC):
    def __init__(self, client, service, duration):
        self.client = client
        self.service = service
        self.duration = duration
        self.status = "PENDIENTE"

    def cancel(self):
        self.status = "CANCELADA"

    def show(self):
        return f"{self.client.show_info()} - {self.service.show_info()} - Estado: {self.status}"

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


# IMPLEMENTACIÓN CONCRETA DE RESERVA
class ReservaEstandar(ReservaOriginal):
    def calculate_cost(self, duration):
        if hasattr(self.service, 'calculate_daily_cost'):
            return self.service.calculate_daily_cost(duration)
        return self.service.price * duration

    def description(self):
        return f"Reserva estándar del servicio {self.service.name} por {self.duration} horas"

    def validate_parameters(self, **kwargs):
        duration = kwargs.get('duration', self.duration)
        return duration > 0 and self.service.disponible

class main_window:
    def __init__(self, view):
        """========================
        COLORES DEL SISTEMA
        ========================"""

        # Azules principales
        self.COLOR_AZUL_CLARO = "#dbeafe"
        self.COLOR_AZUL = "#60a5fa"
        self.COLOR_AZUL_HOVER = "#3b82f6"
        self.COLOR_AZUL_OSCURO = "#2563eb"
        self.COLOR_AZUL_TITULO = "#1e3a8a"

        # Blancos y fondos
        self.COLOR_BLANCO = "#ffffff"
        self.COLOR_FONDO = "#f0f0f0"
        self.COLOR_HEADER = "#f5f5f5"
        
        # Rojos
        self.COLOR_ROJO = "#dc2626"
        self.COLOR_ROJO_HOVER = "#b91c1c"
        self.COLOR_ROJO_CLARO = "#fecaca"
        
        # Verde
        self.COLOR_VERDE = "#10b981"
        self.COLOR_VERDE_HOVER = "#059669"

        # Grises
        self.COLOR_GRIS = "#555555"
        self.COLOR_GRIS_OSCURO = "#1f2937"
        self.COLOR_BORDE = "#d0d0d0"

        """========================
        INICIALIZAR VENTANA
        ========================"""
        
        self.clients = []
        self.catalogo_servicios = CatalogoServicios()
        self.reservas = []
        self.gestor_reservas = GestorReservas()
        
        
        self.simulador_datos_correctos = 0
        self.simulador_datos_incorrectos = 0

        self.view = view
        self.view.title("Software FJ - Sistema Integral de Gestión")
        
        
        self.view.state('zoomed')
        
        self.view.configure(bg=self.COLOR_BLANCO)

        header = tk.Frame(self.view, bg=self.COLOR_HEADER, height=120)
        header.pack(fill="x")

        line = tk.Frame(self.view, bg=self.COLOR_BORDE, height=1)
        line.pack(fill="x")

        container = tk.Frame(header, bg=self.COLOR_HEADER)
        container.place(relx=0.5, rely=0.5, anchor="center")

        icon = tk.Label(
            container,
            text="🏢",
            font=("Arial", 30),
            bg=self.COLOR_HEADER,
            fg=self.COLOR_AZUL_TITULO,
        )
        icon.pack()

        title = tk.Label(
            container,
            text="SOFTWARE FJ",
            font=("Arial", 24, "bold"),
            bg=self.COLOR_HEADER,
            fg=self.COLOR_AZUL_TITULO,
        )
        title.pack()

        caption = tk.Label(
            container,
            text="Sistema Integral de Gestión de Clientes, Servicios y Reservas",
            font=("Arial", 11),
            bg=self.COLOR_HEADER,
            fg=self.COLOR_GRIS,
        )
        caption.pack()

        # Configurar estilos adicionales
        self.configure_styles()
        self.create_widgets()

        
    def configure_styles(self):
        """Configura estilos adicionales para botones"""
        style = ttk.Style()
        
        # Botón verde para confirmar/completar
        style.configure(
            "Green.TButton",
            font=("Arial", 10, "bold"),
            padding=6,
            background=self.COLOR_VERDE,
            foreground="white",
            borderwidth=0
        )
        
        style.map(
            "Green.TButton",
            background=[("active", self.COLOR_VERDE_HOVER)]
        )
        
        # Botón naranja para confirmar
        style.configure(
            "Orange.TButton",
            font=("Arial", 10, "bold"),
            padding=6,
            background="#f59e0b",
            foreground="white",
            borderwidth=0
        )
        
        style.map(
            "Orange.TButton",
            background=[("active", "#d97706")]
        )

    def create_widgets(self):

        style = ttk.Style()
        style.theme_use("clam")
            
        # Notebook
        style.configure("TNotebook", background=self.COLOR_FONDO, borderwidth=0)

        style.configure(
            "TNotebook.Tab",
            font=("Arial", 11, "bold"),
            padding=[10, 4],
            background=self.COLOR_AZUL_CLARO,
            foreground=self.COLOR_AZUL_OSCURO,
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", self.COLOR_AZUL)],
            foreground=[("selected", self.COLOR_BLANCO)],
        )

        # LabelFrame
        style.configure(
            "TLabelframe",
            background=self.COLOR_BLANCO,
            bordercolor=self.COLOR_AZUL,
            borderwidth=2,
        )

        style.configure(
            "TLabelframe.Label",
            foreground=self.COLOR_AZUL_TITULO,
            font=("Arial", 11, "bold"),
            background=self.COLOR_BLANCO,
        )

        # Labels
        style.configure(
            "TLabel",
            background=self.COLOR_BLANCO,
            foreground=self.COLOR_GRIS_OSCURO,
            font=("Arial", 10),
        )

        # Entry
        style.configure("TEntry", padding=5)

        # Botones
        style.configure(
            "TButton",
            font=("Arial", 10, "bold"),
            padding=6,
            background=self.COLOR_AZUL_OSCURO,
            foreground=self.COLOR_BLANCO,
            borderwidth=0,
        )

        style.map("TButton", background=[("active", self.COLOR_AZUL_HOVER)])
        
        style.configure(
            "Red.TButton",
            font=("Arial", 10, "bold"),
            padding=6,
            background=self.COLOR_ROJO,
            foreground="white",
            borderwidth=0
        )

        style.map(
            "Red.TButton",
            background=[("active", self.COLOR_ROJO_HOVER)]
        )

        # Tabla
        style.configure(
            "Treeview",
            font=("Arial", 10),
            rowheight=28,
            background=self.COLOR_BLANCO,
            fieldbackground=self.COLOR_BLANCO,
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background=self.COLOR_AZUL_OSCURO,
            foreground=self.COLOR_BLANCO,
        )

        style.map("Treeview.Heading", background=[("active", self.COLOR_AZUL_HOVER)])

        # Notebook de clientes
        self.notebook = ttk.Notebook(self.view)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        #crear pestañas
        self.frame_clients = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_clients, text="👥 Clientes")
        self.create_frame_client()
        
        self.frame_services = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_services, text="🔧 Servicios")
        self.create_frame_service()
        
        # NUEVA PESTAÑA DE RESERVAS
        self.frame_reservations = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_reservations, text="📅 Reservas")
        self.create_frame_reservations()
        
        # NUEVA PESTAÑA DE SIMULADOR
        self.frame_simulator = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_simulator, text="🎮 Simulador")
        self.create_frame_simulator()
        
        # PESTAÑA LOGS
        self.frame_logs = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_logs, text="📄 Logs")
        self.create_frame_logs()
        
    def create_frame_client(self):
        from_frame = ttk.LabelFrame(self.frame_clients, text="Registrar Nuevo Cliente", padding=10)
        from_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(from_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = ttk.Entry(from_frame, width=25)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(from_frame, text="Correo:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_email = ttk.Entry(from_frame, width=25)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(from_frame, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_phone = ttk.Entry(from_frame, width=25)
        self.entry_phone.grid(row=2, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(from_frame)
        button_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        ttk.Button(button_frame, text="Registrar Cliente", command=self.register_client).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar Cliente", command=self.delete_client, style="Red.TButton").pack(side="left", padx=5)
        
        list_frame = ttk.LabelFrame(self.frame_clients, text="Lista de Clientes", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Nombre", "Correo", "Teléfono")
        
        self.table_client = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.table_client.heading(col, text=col)
            self.table_client.column(col, width=200)
            
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.table_client.yview)
        self.table_client.configure(yscrollcommand=scrollbar.set)
        self.table_client.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
         
    def register_client(self):

        try:

            # Obtener datos
            name = self.entry_name.get().strip()
            email = self.entry_email.get().strip()
            phone = self.entry_phone.get().strip()

            # ====================================
            # VALIDAR NOMBRE
            # ====================================

            if not name:
                raise ClienteInvalidoError("El nombre es obligatorio")

            # Solo letras y espacios
            if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", name):
                raise ClienteInvalidoError("El nombre solo puede contener letras y espacios")

            if len(name) < 3:
                raise ClienteInvalidoError("El nombre es demasiado corto")

            # ====================================
            # VALIDAR EMAIL
            # ====================================

            if not email:
                raise ClienteInvalidoError("El correo es obligatorio")

            # Validación básica de email
            if "@" not in email or "." not in email:
                raise ClienteInvalidoError("Ingrese un correo válido")

            # Expresión regular email
            patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"

            if not re.fullmatch(patron_email, email):
                raise ClienteInvalidoError("Formato de correo inválido")

            # ====================================
            # VALIDAR TELÉFONO
            # ====================================

            if not phone:
                raise ClienteInvalidoError("El teléfono es obligatorio")

            if not phone.isdigit():
                raise ClienteInvalidoError("El teléfono solo debe contener números")
                
            # Máximo 10 dígitos
            if len(phone) != 10:
                raise ClienteInvalidoError("El teléfono debe tener exactamente 10 dígitos")

            # ====================================
            # VALIDAR DUPLICADOS
            # ====================================

            # Validar duplicados por nombre, email O teléfono
            for client in self.clients:
                # Validar nombre duplicado (insensible a mayúsculas/minúsculas)
                if client._name.lower() == name.lower():
                    logging.warning(f"Intento de registro duplicado - Nombre: {name}")
                    raise ClienteDuplicadoError(f"Ya existe un cliente con el nombre '{name}'")
                
                # Validar correo duplicado
                if client._email.lower() == email.lower():
                    logging.warning(f"Intento de registro duplicado - Correo: {email}")
                    raise ClienteDuplicadoError(f"Ya existe un cliente con el correo '{email}'")
                
                # Validar teléfono duplicado
                if client._phone == phone:
                    logging.warning(f"Intento de registro duplicado - Teléfono: {phone}")
                    raise ClienteDuplicadoError(f"Ya existe un cliente con el teléfono '{phone}'")

            # ====================================
            # GENERAR ID
            # ====================================

            if len(self.clients) == 0:
                new_id = 1
            else:
                new_id = self.clients[-1]._id + 1

            # ====================================
            # CREAR CLIENTE
            # ====================================

            try:
                client = Cliente(new_id, name, email, phone)

            except Exception as e:
                raise ClienteInvalidoError("Error creando el cliente") from e

        # ====================================
        # EXCEPCIONES PERSONALIZADAS
        # ====================================

        except ClienteDuplicadoError as e:

            logging.error(f"Cliente duplicado: {str(e)}")

            messagebox.showerror("Cliente Duplicado", str(e))

        except ClienteInvalidoError as e:
            logging.error(f"Cliente inválido: {str(e)}")
            messagebox.showerror("Datos Inválidos", str(e))

        # ====================================
        # ERROR GENERAL
        # ====================================

        except Exception as e:
            logging.error(f"Error inesperado:\n{traceback.format_exc()}")
            messagebox.showerror("Error", "Ocurrió un error inesperado")

        # ====================================
        # ELSE
        # ====================================

        else:

            self.clients.append(client)

            self.table_client.insert(
            "",
            "end",
            iid=str(client._id),
            values=(
                client._id,
                client._name,
                client._email,
                client._phone
            ))

            logging.info(f"Cliente registrado: {client._name}")

            messagebox.showinfo("Éxito","Cliente registrado correctamente")
            self.entry_name.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_phone.delete(0, tk.END)           
        
    def delete_client(self):
        try:
            # ====================================
            # VALIDAR SELECCIÓN
            # ====================================

            selection = self.table_client.selection()

            if not selection:
                raise ClienteNoEncontradoError("Debe seleccionar un cliente")

            item_id = selection[0]

            # ====================================
            # BUSCAR CLIENTE
            # ====================================

            cliente = next(
            (
                client for client in self.clients
                if str(client._id) == item_id), None)

            if not cliente:
                raise ClienteNoEncontradoError("El cliente seleccionado no existe")

            # ====================================
            # VALIDAR RESERVAS ASOCIADAS
            # ====================================

            reservas_cliente = self.gestor_reservas.listar_reservas_por_cliente(cliente._id)

            if reservas_cliente:
                raise ClienteInvalidoError("No se puede eliminar un cliente con reservas asociadas")

            # ====================================
            # CONFIRMAR ELIMINACIÓN
            # ====================================

            confirmar = messagebox.askyesno("Confirmar Eliminación",f"¿Desea eliminar el cliente {cliente._name}?")

            if not confirmar:
                return

        # ====================================
        # EXCEPCIONES PERSONALIZADAS
        # ====================================

        except ClienteNoEncontradoError as e:
            logging.error(f"Cliente no encontrado: {str(e)}")
            messagebox.showwarning("Cliente", str(e))

        except ClienteInvalidoError as e:
            logging.error(f"No se puede eliminar cliente: {str(e)}")
            messagebox.showerror("Error",str(e))

        # ====================================
        # ERROR GENERAL
        # ====================================

        except Exception as e:
            logging.error(f"Error eliminando cliente:\n{traceback.format_exc()}")
            messagebox.showerror("Error", "Ocurrió un error eliminando el cliente")

        # ====================================
        # ELSE
        # ====================================

        else:
            # Guardar nombre para log
            nombre_cliente = cliente._name
            
            # Eliminar de tabla
            self.table_client.delete(item_id)

            # Eliminar de lista
            self.clients = [
            client for client in self.clients
            if str(client._id) != item_id
            ]

            logging.info(f"Cliente eliminado: {cliente._name}")

            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
        
    def create_frame_service(self):
        """Crea la pestaña de gestión de servicios"""
        # Frame para registrar nuevo servicio
        form_frame = ttk.LabelFrame(self.frame_services, text="Registrar Nuevo Servicio", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10, anchor="w")
        
        # Tipo de servicio
        ttk.Label(form_frame, text="Tipo de Servicio:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.service_type = ttk.Combobox(form_frame, values=["Estándar", "Premium", "Express"], width=23, state="readonly")
        self.service_type.grid(row=0, column=1, padx=5, pady=5)
        self.service_type.set("Estándar")
        
        # Nombre del servicio
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.service_name = ttk.Entry(form_frame, width=25)
        self.service_name.grid(row=1, column=1, padx=5, pady=5)
        
        # Precio
        ttk.Label(form_frame, text="Precio por hora ($):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.service_price = ttk.Entry(form_frame, width=25)
        self.service_price.grid(row=2, column=1, padx=5, pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.service_description = ttk.Entry(form_frame, width=25)
        self.service_description.grid(row=3, column=1, padx=5, pady=5)
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Registrar Servicio", command=self.register_service).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Cambiar Disponibilidad", command=self.toggle_service_availability, style="Green.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar Servicio", command=self.delete_service, style="Red.TButton").pack(anchor="w", pady=2)
        
        # Lista de servicios
        list_frame = ttk.LabelFrame(self.frame_services, text="Lista de Servicios", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Nombre", "Categoría", "Precio/hora", "Disponible", "Descripción")
        
        self.table_service = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configurar columnas
        self.table_service.heading("ID", text="ID")
        self.table_service.heading("Nombre", text="Nombre")
        self.table_service.heading("Categoría", text="Categoría")
        self.table_service.heading("Precio/hora", text="Precio/hora")
        self.table_service.heading("Disponible", text="Disponible")
        self.table_service.heading("Descripción", text="Descripción")
        
        self.table_service.column("ID", width=50)
        self.table_service.column("Nombre", width=180)
        self.table_service.column("Categoría", width=100)
        self.table_service.column("Precio/hora", width=100)
        self.table_service.column("Disponible", width=80)
        self.table_service.column("Descripción", width=300)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.table_service.yview)
        self.table_service.configure(yscrollcommand=scrollbar.set)
        self.table_service.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
      
    def register_service(self):
        """Registra un nuevo servicio en el sistema"""
        try:
            # ====================================
            # OBTENER DATOS
            # ====================================
            tipo = self.service_type.get()
            nombre = self.service_name.get()
            precio_str = self.service_price.get()
            descripcion = self.service_description.get().strip()
        
            # ====================================
            # VALIDACIONES DEL NOMBRE (solo letras y espacios)
            # ====================================
            if not nombre:
                raise ServicioInvalidoError("El nombre del servicio es obligatorio")
            
            if len(nombre) < 3:
                raise ServicioInvalidoError("El nombre del servicio debe tener al menos 3 caracteres")
            
            if len(nombre) > 100:
                raise ServicioInvalidoError("El nombre del servicio no puede exceder los 100 caracteres")
            
            # Solo letras y espacios (sin números)
            if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", nombre):
                raise ServicioInvalidoError("El nombre solo puede contener letras y espacios (sin números)")
            
            # ====================================
            # VALIDAR DESCRIPCIÓN (obligatoria)
            # ====================================
            if not descripcion:
                raise ServicioInvalidoError("La descripción del servicio es obligatoria")

            if len(descripcion) < 5:
                raise ServicioInvalidoError("La descripción debe tener al menos 5 caracteres")

            if len(descripcion) > 500:
                raise ServicioInvalidoError("La descripción no puede exceder los 500 caracteres")

            # ====================================
            # VALIDAR DUPLICADOS
            # ====================================
            for servicio in self.catalogo_servicios.listar_servicios():
                if servicio.name.lower() == nombre.lower():
                    logging.warning(f"Intento de registro duplicado - Servicio: {nombre}")
                    raise ServicioDuplicadoError(f"Ya existe un servicio con el nombre '{nombre}'")

            # ====================================
            # VALIDACIONES DEL PRECIO
            # ====================================
            if not precio_str:
                raise ServicioInvalidoError("El precio del servicio es obligatorio")
            
            try:
                precio = float(precio_str)
            except ValueError:
                raise ServicioInvalidoError("Ingrese un precio válido")

                if precio <= 0:
                    messagebox.showwarning("Advertencia", "El precio debe ser mayor a 0")
                
                if precio > 1000000:
                    messagebox.showwarning("Advertencia", "El precio no puede superar $1,000,000 por hora")
                
            # Máximo 2 decimales
            if "." in precio_str:
                decimales = precio_str.split(".")[1]
                if len(decimales) > 2:
                    raise ServicioInvalidoError("El precio solo puede tener máximo 2 decimales")

        
            # Generar ID
            new_id = self.catalogo_servicios.obtener_nuevo_id()
            

            # CREAR SERVICIO
            try:
                if tipo == "Estándar":
                    servicio = ServicioEstandar(
                        new_id,
                        nombre,
                        precio,
                        descripcion
                    )
                elif tipo == "Premium":
                    servicio = ServicioPremium(
                        new_id,
                        nombre,
                        precio,
                        descripcion
                    )
                elif tipo == "Express":
                    servicio = ServicioExpress(
                        new_id,
                        nombre,
                        precio,
                        descripcion
                    )
                else:
                    raise ServicioInvalidoError("Tipo de servicio no válido")
            except Exception as e:
                raise ServicioInvalidoError("Error creando el servicio") from e
            

        # EXCEPCIONES PERSONALIZADAS
        except ServicioDuplicadoError as e:
            logging.error(f"Error: {str(e)}")
            messagebox.showerror("Servicio Duplicado", str(e))

        except ServicioInvalidoError as e:
            logging.error(f"Error: {str(e)}")
            messagebox.showerror("Datos Inválidos", str(e))


        # ERROR GENERAL
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
            messagebox.showerror("Error", "Ocurrió un error inesperado")


        # ELSE (ÉXITO)
        else:   
            # Agregar al catálogo
            self.catalogo_servicios.agregar_servicio(servicio)
            
            # Actualizar tabla
            self.actualizar_tabla_servicios()
            
            # Limpiar campos
            self.service_name.delete(0, tk.END)
            self.service_price.delete(0, tk.END)
            self.service_description.delete(0, tk.END)
            self.service_type.set("Estándar")
            
            logging.info(f"Servicio registrado: {nombre} - Tipo: {tipo} - Precio: ${precio:,.0f}")
            
            messagebox.showinfo("Éxito", f"Servicio '{nombre}' registrado correctamente")
     
    def actualizar_tabla_servicios(self):
        """Actualiza la tabla de servicios con los datos actuales"""
        # Limpiar tabla
        for item in self.table_service.get_children():
            self.table_service.delete(item)
        
        # Insertar servicios
        for servicio in self.catalogo_servicios.listar_servicios():
            disponible = "✓ Sí" if servicio.disponible else "✗ No"
            descripcion_corta = servicio._description[:50] + "..." if len(servicio._description) > 50 else servicio._description
            
            self.table_service.insert("", "end", iid=str(servicio.id), values=(
                servicio.id,
                servicio.name,
                servicio.category,
                f"${servicio.price:,.0f}",
                disponible,
                descripcion_corta
            ))
    
    def delete_service(self):
        """Elimina un servicio seleccionado"""
        try:
            selection = self.table_service.selection()
        
            if not selection:
                messagebox.showwarning("Advertencia", "Seleccione un servicio")
                return
        
            servicio_id = int(selection[0])
            servicio = self.catalogo_servicios.buscar_servicio(servicio_id)
            
            if not servicio:
                messagebox.showerror("Error", "El servicio seleccionado no existe")
                return
            
            # VALIDAR RESERVAS ASOCIADAS

            # Verificar si hay reservas activas con este servicio
            reservas_asociadas = []
            for reserva in self.gestor_reservas.listar_reservas():
                if reserva.servicio.id == servicio_id and reserva.estado in ["PENDIENTE", "CONFIRMADA"]:
                    reservas_asociadas.append(reserva)
            
            if reservas_asociadas:
                messagebox.showerror("Error", 
                                    f"No se puede eliminar el servicio '{servicio.name}' porque tiene {len(reservas_asociadas)} reservas pendientes o confirmadas.\n"
                                    "Primero debe cancelar o completar las reservas asociadas.")
                return
        
            # Confirmar eliminación
            if not messagebox.askyesno("Confirmar Eliminación", 
                                      f"¿Está seguro de eliminar el servicio '{servicio.name}'?\n\n"
                                      f"Tipo: {servicio.category}\n"
                                      f"Precio: ${servicio.price:,.0f}"):
                return
            
            # ELIMINAR SERVICIO
            nombre_servicio = servicio.name
            self.catalogo_servicios.eliminar_servicio(servicio_id)
            self.actualizar_tabla_servicios()
            

            # REGISTRAR EN LOG
            logging.info(f"Servicio eliminado: {servicio.name} (ID: {servicio_id})")
            
            messagebox.showinfo("Éxito", f"Servicio '{servicio.name}' eliminado correctamente")
            
        except Exception as e:
            logging.error(f"Error eliminando servicio:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}")
    
    def toggle_service_availability(self):
        """Cambia la disponibilidad de un servicio con validaciones"""
        try:
            selection = self.table_service.selection()
            
            # VALIDAR SELECCIÓN

            if not selection:
                messagebox.showwarning("Advertencia", "Debe seleccionar un servicio")
                return
            
            servicio_id = int(selection[0])
            servicio = self.catalogo_servicios.buscar_servicio(servicio_id)
            
            if not servicio:
                messagebox.showerror("Error", "El servicio seleccionado no existe")
                return
            
            # VALIDAR ANTES DE CAMBIAR DISPONIBILIDAD
            nuevo_estado = not servicio.disponible
            
            # Si se va a marcar como NO disponible, verificar reservas pendientes
            if not nuevo_estado:
                reservas_activas = []
                for reserva in self.gestor_reservas.listar_reservas():
                    if reserva.servicio.id == servicio_id and reserva.estado in ["PENDIENTE", "CONFIRMADA"]:
                        reservas_activas.append(reserva)
                
                if reservas_activas:
                    messagebox.showerror("Error", 
                                       f"No se puede marcar el servicio '{servicio.name}' como NO disponible porque tiene {len(reservas_activas)} reservas pendientes o confirmadas.\n"
                                       "Primero debe cancelar o completar las reservas asociadas.")
                    return
            
            # CONFIRMAR CAMBIO
            estado_texto = "disponible" if nuevo_estado else "no disponible"
            
            if not messagebox.askyesno("Confirmar Cambio", 
                                      f"¿Está seguro de cambiar la disponibilidad del servicio '{servicio.name}' a '{estado_texto}'?"):
                return
            
            # CAMBIAR DISPONIBILIDAD
            servicio.disponible = nuevo_estado
            self.actualizar_tabla_servicios()
            
            # REGISTRAR EN LOG
            logging.info(f"Disponibilidad cambiada: {servicio.name} - {estado_texto}")
            
            messagebox.showinfo("Éxito", f"Servicio '{servicio.name}' ahora está {estado_texto}")
            
            # ACTUALIZAR COMBO DE SERVICIOS EN RESERVAS
            if hasattr(self, 'refrescar_servicios_reserva'):
                self.refrescar_servicios_reserva()
                
        except Exception as e:
            logging.error(f"Error cambiando disponibilidad:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}")

    # ============================================================
    # NUEVOS MÉTODOS PARA RESERVAS
    # ============================================================
    
    def create_frame_reservations(self):
        """Crea la pestaña de gestión de reservas"""
        
        # Frame superior para crear nueva reserva
        form_frame = ttk.LabelFrame(self.frame_reservations, text="Crear Nueva Reserva", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Selección de Cliente
        ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.reserva_cliente_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.reserva_cliente_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Botón refrescar clientes
        ttk.Button(form_frame, text="🔄", width=3, command=self.refrescar_clientes_reserva).grid(row=0, column=2, padx=5)
        
        # Selección de Servicio
        ttk.Label(form_frame, text="Servicio:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.reserva_servicio_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.reserva_servicio_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="🔄", width=3, command=self.refrescar_servicios_reserva).grid(row=1, column=2, padx=5)
        
        # Duración
        ttk.Label(form_frame, text="Duración (horas):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.reserva_duracion = ttk.Entry(form_frame, width=25)
        self.reserva_duracion.grid(row=2, column=1, padx=5, pady=5)
        
        # Fecha
        ttk.Label(form_frame, text="Fecha (DD/MM/AAAA):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.reserva_fecha = ttk.Entry(form_frame, width=25)
        self.reserva_fecha.grid(row=3, column=1, padx=5, pady=5)
        self.reserva_fecha.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
        
        # Botones de acción
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="📅 Crear Reserva", command=self.crear_reserva).pack(side="left", padx=5)
        ttk.Button(button_frame, text="✅ Confirmar", command=self.confirmar_reserva, style="Orange.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.cancelar_reserva, style="Red.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="⭐ Completar", command=self.completar_reserva, style="Green.TButton").pack(side="left", padx=5)
        
        # Frame para lista de reservas
        list_frame = ttk.LabelFrame(self.frame_reservations, text="Lista de Reservas", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Filtrar por estado:").pack(side="left", padx=5)
        self.filtro_estado = ttk.Combobox(filter_frame, values=["Todos", "PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA"], 
                                          width=15, state="readonly")
        self.filtro_estado.pack(side="left", padx=5)
        self.filtro_estado.set("Todos")
        self.filtro_estado.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tabla_reservas())
        
        ttk.Button(filter_frame, text="Buscar", command=self.actualizar_tabla_reservas).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Actualizar", command=self.refrescar_todo_reservas).pack(side="left", padx=5)
        
        # Tabla de reservas
        columns = ("ID", "Cliente", "Servicio", "Duración", "Fecha", "Estado", "Costo Total")
        
        self.table_reservas = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configurar columnas
        for col in columns:
            self.table_reservas.heading(col, text=col)
        
        self.table_reservas.column("ID", width=50)
        self.table_reservas.column("Cliente", width=150)
        self.table_reservas.column("Servicio", width=150)
        self.table_reservas.column("Duración", width=80)
        self.table_reservas.column("Fecha", width=100)
        self.table_reservas.column("Estado", width=100)
        self.table_reservas.column("Costo Total", width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.table_reservas.yview)
        self.table_reservas.configure(yscrollcommand=scrollbar.set)
        self.table_reservas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de resumen
        resumen_frame = ttk.LabelFrame(self.frame_reservations, text="Resumen de Reservas", padding=10)
        resumen_frame.pack(fill="x", padx=10, pady=10)
        
        self.resumen_label = ttk.Label(resumen_frame, text="", font=("Arial", 10))
        self.resumen_label.pack()
        
        # Inicializar combos
        self.refrescar_clientes_reserva()
        self.refrescar_servicios_reserva()
        self.actualizar_tabla_reservas()
    
    def refrescar_clientes_reserva(self):
        """Refresca el combo de clientes"""
        clientes_lista = [f"{c._id} - {c._name}" for c in self.clients]
        self.reserva_cliente_combo['values'] = clientes_lista
        if clientes_lista:
            self.reserva_cliente_combo.set(clientes_lista[0])
    
    def refrescar_servicios_reserva(self):
        """Refresca el combo de servicios (solo disponibles)"""
        servicios_lista = [f"{s.id} - {s.name} (${s.price:,.0f}/h)" 
                          for s in self.catalogo_servicios.listar_disponibles()]
        self.reserva_servicio_combo['values'] = servicios_lista
        if servicios_lista:
            self.reserva_servicio_combo.set(servicios_lista[0])
    
    def crear_reserva(self):
        """Crea una nueva reserva"""
        try:
            # Obtener cliente seleccionado
            cliente_seleccionado = self.reserva_cliente_combo.get()
            if not cliente_seleccionado:
                raise ExcepcionReserva("Advertencia", "Debe seleccionar un cliente")
            
            cliente_id = int(cliente_seleccionado.split(" - ")[0])
            cliente = next((c for c in self.clients if c._id == cliente_id), None)
            
            if not cliente:
                raise ExcepcionReserva("Cliente no encontrado")
            
            # Obtener servicio seleccionado
            servicio_seleccionado = self.reserva_servicio_combo.get()
            if not servicio_seleccionado:
                raise ExcepcionReserva("Advertencia", "Debe seleccionar un servicio")
            
            servicio_id = int(servicio_seleccionado.split(" - ")[0])
            servicio = self.catalogo_servicios.buscar_servicio(servicio_id)
            
            if not servicio:
                raise ExcepcionReserva("Error", "Servicio no encontrado")
            
            if not servicio.disponible:
                raise ExcepcionReserva("Error", "El servicio seleccionado no está disponible")
            
            # Obtener duración
            duracion_str = self.reserva_duracion.get()
            if not duracion_str:
                raise ExcepcionReserva("Advertencia", "Debe ingresar la duración")
            
            try:
                duracion = float(duracion_str)
            except ValueError:
                raise ExcepcionReserva("Error", "Duración inválida")
            
            # Obtener fecha
            fecha_str = self.reserva_fecha.get()
            try:
                fecha = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
            except ValueError:
                fecha = datetime.date.today()
            
            # Crear reserva usando el gestor
            reserva = self.gestor_reservas.crear_reserva(cliente, servicio, duracion, fecha)
            
            # Actualizar tabla
            self.actualizar_tabla_reservas()
            self.actualizar_resumen_reservas()
            
            # Limpiar campos
            self.reserva_duracion.delete(0, tk.END)
            
            messagebox.showinfo("Éxito", f"Reserva #{reserva.id} creada correctamente.\nEstado: {reserva.estado}")
            
        except ExcepcionReserva as e:
            logging.error(f"Error: {str(e)}")
            messagebox.showerror("Error de Reserva", str(e))
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def confirmar_reserva(self):
        """Confirma la reserva seleccionada"""
        selection = self.table_reservas.selection()
        
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una reserva")
            return
        
        reserva_id = int(selection[0])
        
        try:
            self.gestor_reservas.confirmar_reserva(reserva_id)
            self.actualizar_tabla_reservas()
            self.actualizar_resumen_reservas()
            
            # Mostrar información de costo
            reserva = self.gestor_reservas.buscar_reserva(reserva_id)
            if reserva and reserva.costo_total:
                costo_con_impuesto = reserva.calcular_costo_con_impuesto()
                messagebox.showinfo("Confirmación Exitosa", 
                                   f"Reserva #{reserva_id} confirmada.\n\n"
                                   f"Costo base: ${reserva.costo_total:,.0f}\n"
                                   f"Costo con IVA (19%): ${costo_con_impuesto:,.0f}")
            else:
                messagebox.showinfo("Éxito", f"Reserva #{reserva_id} confirmada correctamente")
                
        except ExcepcionReserva as e:
            logging.error(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def cancelar_reserva(self):
        """Cancela la reserva seleccionada"""
        selection = self.table_reservas.selection()
        
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una reserva")
            return
        
        reserva_id = int(selection[0])
        
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de cancelar la reserva #{reserva_id}?"):
            return
        
        try:
            self.gestor_reservas.cancelar_reserva(reserva_id)
            self.actualizar_tabla_reservas()
            self.actualizar_resumen_reservas()
            messagebox.showinfo("Éxito", f"Reserva #{reserva_id} cancelada correctamente")
        except ExcepcionReserva as e:
            logging.error(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def completar_reserva(self):
        """Marca como completada la reserva seleccionada"""
        selection = self.table_reservas.selection()
        
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una reserva")
            return
        
        reserva_id = int(selection[0])
        
        try:
            self.gestor_reservas.completar_reserva(reserva_id)
            self.actualizar_tabla_reservas()
            self.actualizar_resumen_reservas()
            messagebox.showinfo("Éxito", f"Reserva #{reserva_id} completada correctamente")
        except ExcepcionReserva as e:
            logging.error(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def actualizar_tabla_reservas(self):
        """Actualiza la tabla de reservas con los datos actuales"""
        # Limpiar tabla
        for item in self.table_reservas.get_children():
            self.table_reservas.delete(item)
        
        # Obtener filtro
        filtro = self.filtro_estado.get()
        
        if filtro == "Todos":
            reservas = self.gestor_reservas.listar_reservas()
        else:
            reservas = self.gestor_reservas.listar_reservas(filtro)
        
        # Insertar reservas
        for reserva in reservas:
            estado = reserva.estado
            # Color según estado (opcional)
            costo_str = f"${reserva.costo_total:,.0f}" if reserva.costo_total else "No calculado"
            
            self.table_reservas.insert("", "end", iid=str(reserva.id), values=(
                reserva.id,
                reserva.cliente._name,
                reserva.servicio.name,
                f"{reserva.duracion_horas}h",
                reserva.fecha.strftime("%d/%m/%Y") if hasattr(reserva.fecha, 'strftime') else str(reserva.fecha),
                estado,
                costo_str
            ))
    
    def actualizar_resumen_reservas(self):
        """Actualiza el resumen estadístico de reservas"""
        resumen = self.gestor_reservas.obtener_resumen()
        
        texto = (f"📊 Resumen: Total: {resumen['total']} | "
                f"⏳ Pendientes: {resumen['pendientes']} | "
                f"✅ Confirmadas: {resumen['confirmadas']} | "
                f"❌ Canceladas: {resumen['canceladas']} | "
                f"⭐ Completadas: {resumen['completadas']}")
        
        self.resumen_label.config(text=texto)
    
    def refrescar_todo_reservas(self):
        """Refresca todos los datos de la pestaña de reservas"""
        self.refrescar_clientes_reserva()
        self.refrescar_servicios_reserva()
        self.actualizar_tabla_reservas()
        self.actualizar_resumen_reservas()
        
    # ============================================================
    # NUEVA PESTAÑA SIMULADOR (VERSIÓN OPTIMIZADA - SIN ESPACIOS EN BLANCO)
    # ============================================================
    
    def create_frame_simulator(self):
        """Crea la pestaña del simulador - Versión optimizada sin espacios en blanco"""
        
        # Frame principal que ocupa todo el espacio
        main_container = ttk.Frame(self.frame_simulator)
        main_container.pack(fill="both", expand=True)
        
        # Configurar grid para que ocupe todo el espacio
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        
        # Columna 1: Formulario de entrada
        col1 = ttk.Frame(main_container)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        col1.grid_rowconfigure(1, weight=1)
        col1.grid_columnconfigure(0, weight=1)
        
        # Selector de tipo
        selector_frame = ttk.LabelFrame(col1, text="🎯 Tipo de Datos a Ingresar", padding=10)
        selector_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        selector_frame.grid_columnconfigure(0, weight=1)
        
        # AÑADIDO "Reserva" al combobox
        self.simulador_tipo = ttk.Combobox(selector_frame,
                                           values=["Cliente", "Servicio", "Reserva"],
                                           state="readonly", font=("Arial", 11))
        self.simulador_tipo.pack(fill="x", pady=5)
        self.simulador_tipo.set("Cliente")
        self.simulador_tipo.bind("<<ComboboxSelected>>", self.cambiar_formulario_simulador)
        
        # Formulario dinámico
        self.formulario_simulador_frame = ttk.LabelFrame(col1, text="📝 Ingrese los Datos", padding=10)
        self.formulario_simulador_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.formulario_simulador_frame.grid_columnconfigure(0, weight=1)
        
        # Contenedor interno para el formulario
        self.formulario_inner = ttk.Frame(self.formulario_simulador_frame)
        self.formulario_inner.pack(fill="both", expand=True)
        
        self.widgets_simulador = {}
        
        # Botones de acción del formulario
        form_buttons = ttk.Frame(col1)
        form_buttons.grid(row=2, column=0, sticky="ew")
        form_buttons.grid_columnconfigure(0, weight=1)
        form_buttons.grid_columnconfigure(1, weight=1)
        
        ttk.Button(form_buttons, text="➕ Agregar a la Lista", command=self.agregar_dato_lista,
                  style="Green.TButton").grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(form_buttons, text="🗑️ Limpiar Formulario", command=self.limpiar_formulario_simulador,
                  style="Red.TButton").grid(row=0, column=1, padx=5, sticky="ew")
        
        # Columna 2: Lista de datos acumulados
        col2 = ttk.Frame(main_container)
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        col2.grid_rowconfigure(0, weight=1)
        col2.grid_columnconfigure(0, weight=1)
        
        list_frame = ttk.LabelFrame(col2, text="📋 Datos Acumulados para Insertar", padding=10)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview para mostrar la lista de datos
        tree_container = ttk.Frame(list_frame)
        tree_container.grid(row=0, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        columns = ("#", "Tipo", "Datos")
        self.lista_datos_tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        
        self.lista_datos_tree.heading("#", text="#")
        self.lista_datos_tree.heading("Tipo", text="Tipo")
        self.lista_datos_tree.heading("Datos", text="Datos")
        
        self.lista_datos_tree.column("#", width=50)
        self.lista_datos_tree.column("Tipo", width=100)
        self.lista_datos_tree.column("Datos", width=350)
        
        scrollbar_lista = ttk.Scrollbar(tree_container, orient="vertical", command=self.lista_datos_tree.yview)
        self.lista_datos_tree.configure(yscrollcommand=scrollbar_lista.set)
        
        self.lista_datos_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_lista.grid(row=0, column=1, sticky="ns")
        
        # Botones para gestionar la lista
        list_buttons = ttk.Frame(list_frame)
        list_buttons.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        list_buttons.grid_columnconfigure(0, weight=1)
        list_buttons.grid_columnconfigure(1, weight=1)
        
        ttk.Button(list_buttons, text="🗑️ Eliminar Seleccionado", command=self.eliminar_dato_lista,
                  style="Red.TButton").grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(list_buttons, text="🧹 Limpiar Lista", command=self.limpiar_lista_datos,
                  style="Red.TButton").grid(row=0, column=1, padx=5, sticky="ew")
        
        # Columna 3: Estadísticas y botón de inserción masiva
        col3 = ttk.Frame(main_container)
        col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        col3.grid_rowconfigure(1, weight=1)
        col3.grid_columnconfigure(0, weight=1)
        
        # Botón de inserción masiva
        insert_frame = ttk.LabelFrame(col3, text="🚀 Acción Masiva", padding=10)
        insert_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        insert_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(insert_frame, text="📥 INSERTAR TODOS LOS DATOS", 
                  command=self.insertar_datos_masivos,
                  style="Green.TButton").grid(row=0, column=0, sticky="ew", pady=5)
        
        ttk.Label(insert_frame, text="Total en lista:", font=("Arial", 10)).grid(row=1, column=0, pady=5)
        self.total_lista_label = ttk.Label(insert_frame, text="0", font=("Arial", 14, "bold"))
        self.total_lista_label.grid(row=2, column=0)
        
        # Panel de estadísticas
        stats_frame = ttk.LabelFrame(col3, text="📊 Estadísticas del Simulador", padding=15)
        stats_frame.grid(row=1, column=0, sticky="nsew")
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Variables para estadísticas
        self.stats_correctos = tk.StringVar(value="0")
        self.stats_incorrectos = tk.StringVar(value="0")
        self.stats_totales = tk.StringVar(value="0")
        
        # Datos correctos
        correct_frame = ttk.Frame(stats_frame)
        correct_frame.grid(row=0, column=0, sticky="ew", pady=10)
        correct_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(correct_frame, text="✅", font=("Arial", 24)).grid(row=0, column=0, padx=10)
        ttk.Label(correct_frame, text="Datos Correctos:", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(correct_frame, textvariable=self.stats_correctos, font=("Arial", 18, "bold"), 
                 foreground=self.COLOR_VERDE).grid(row=0, column=2, padx=5)
        
        ttk.Separator(stats_frame, orient='horizontal').grid(row=1, column=0, sticky="ew", pady=10)
        
        # Datos incorrectos
        incorrect_frame = ttk.Frame(stats_frame)
        incorrect_frame.grid(row=2, column=0, sticky="ew", pady=10)
        incorrect_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(incorrect_frame, text="❌", font=("Arial", 24)).grid(row=0, column=0, padx=10)
        ttk.Label(incorrect_frame, text="Datos Incorrectos:", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(incorrect_frame, textvariable=self.stats_incorrectos, font=("Arial", 18, "bold"), 
                 foreground=self.COLOR_ROJO).grid(row=0, column=2, padx=5)
        
        ttk.Separator(stats_frame, orient='horizontal').grid(row=3, column=0, sticky="ew", pady=10)
        
        # Total
        total_frame = ttk.Frame(stats_frame)
        total_frame.grid(row=4, column=0, sticky="ew", pady=10)
        total_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(total_frame, text="📊", font=("Arial", 24)).grid(row=0, column=0, padx=10)
        ttk.Label(total_frame, text="Total Simulaciones:", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(total_frame, textvariable=self.stats_totales, font=("Arial", 18, "bold"), 
                 foreground=self.COLOR_AZUL_OSCURO).grid(row=0, column=2, padx=5)
        
        # Botón para resetear estadísticas
        ttk.Button(stats_frame, text="🔄 Resetear Estadísticas", command=self.resetear_estadisticas,
                  style="Red.TButton").grid(row=5, column=0, pady=15, sticky="ew")
        
        # Variable para almacenar los datos acumulados
        self.datos_acumulados = []
        
        # Crear formulario inicial
        self.cambiar_formulario_simulador()
    
    def resetear_estadisticas(self):
        """Resetea las estadísticas del simulador"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de resetear las estadísticas?"):
            self.simulador_datos_correctos = 0
            self.simulador_datos_incorrectos = 0
            self.actualizar_estadisticas()
            logging.info("[SIMULADOR] Estadísticas reseteadas")
            messagebox.showinfo("Éxito", "Estadísticas reseteadas correctamente")
    
    def actualizar_estadisticas(self):
        """Actualiza la pantalla de estadísticas"""
        self.stats_correctos.set(str(self.simulador_datos_correctos))
        self.stats_incorrectos.set(str(self.simulador_datos_incorrectos))
        self.stats_totales.set(str(self.simulador_datos_correctos + self.simulador_datos_incorrectos))
    
    def actualizar_total_lista(self):
        """Actualiza el contador de la lista"""
        self.total_lista_label.config(text=str(len(self.datos_acumulados)))
    
    def cambiar_formulario_simulador(self, event=None):
        """Cambia el formulario según el tipo seleccionado"""
        # Limpiar frame interno
        for widget in self.formulario_inner.winfo_children():
            widget.destroy()
        
        tipo = self.simulador_tipo.get()
        self.widgets_simulador.clear()
        
        if tipo == "Cliente":
            self.crear_formulario_cliente_simulador()
        elif tipo == "Servicio":
            self.crear_formulario_servicio_simulador()
        elif tipo == "Reserva":
            self.crear_formulario_reserva_simulador()
    
    def crear_formulario_cliente_simulador(self):
        """Crea el formulario para simular clientes"""
        # Nombre
        nombre_frame = ttk.Frame(self.formulario_inner)
        nombre_frame.pack(fill="x", pady=5)
        ttk.Label(nombre_frame, text="Nombre:*", width=15, anchor="w").pack(side="left", padx=5)
        entry_nombre = ttk.Entry(nombre_frame)
        entry_nombre.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["nombre"] = entry_nombre
        
        # Email
        email_frame = ttk.Frame(self.formulario_inner)
        email_frame.pack(fill="x", pady=5)
        ttk.Label(email_frame, text="Correo:*", width=15, anchor="w").pack(side="left", padx=5)
        entry_email = ttk.Entry(email_frame)
        entry_email.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["email"] = entry_email
        
        # Teléfono
        phone_frame = ttk.Frame(self.formulario_inner)
        phone_frame.pack(fill="x", pady=5)
        ttk.Label(phone_frame, text="Teléfono:* (10 dígitos)", width=15, anchor="w").pack(side="left", padx=5)
        entry_phone = ttk.Entry(phone_frame)
        entry_phone.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["phone"] = entry_phone
        
        # Campos requeridos
        req_frame = ttk.Frame(self.formulario_inner)
        req_frame.pack(fill="x", pady=10)
        ttk.Label(req_frame, text="* Campos obligatorios", font=("Arial", 8, "italic"), foreground="red").pack()
    
    def crear_formulario_servicio_simulador(self):
        """Crea el formulario para simular servicios"""
        # Tipo de servicio
        tipo_frame = ttk.Frame(self.formulario_inner)
        tipo_frame.pack(fill="x", pady=5)
        ttk.Label(tipo_frame, text="Tipo de Servicio:*", width=15, anchor="w").pack(side="left", padx=5)
        combo_tipo = ttk.Combobox(tipo_frame, values=["Estándar", "Premium", "Express"], state="readonly")
        combo_tipo.pack(side="left", padx=5, fill="x", expand=True)
        combo_tipo.set("Estándar")
        self.widgets_simulador["tipo"] = combo_tipo
        
        # Nombre
        nombre_frame = ttk.Frame(self.formulario_inner)
        nombre_frame.pack(fill="x", pady=5)
        ttk.Label(nombre_frame, text="Nombre:* (solo letras)", width=15, anchor="w").pack(side="left", padx=5)
        entry_nombre = ttk.Entry(nombre_frame)
        entry_nombre.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["nombre"] = entry_nombre
        
        # Precio
        precio_frame = ttk.Frame(self.formulario_inner)
        precio_frame.pack(fill="x", pady=5)
        ttk.Label(precio_frame, text="Precio por hora:* (>0)", width=15, anchor="w").pack(side="left", padx=5)
        entry_precio = ttk.Entry(precio_frame)
        entry_precio.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["precio"] = entry_precio
        
        # Descripción
        desc_frame = ttk.Frame(self.formulario_inner)
        desc_frame.pack(fill="x", pady=5)
        ttk.Label(desc_frame, text="Descripción:* (mínimo 5)", width=15, anchor="w").pack(side="left", padx=5)
        entry_desc = ttk.Entry(desc_frame)
        entry_desc.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["descripcion"] = entry_desc
        
        # Campos requeridos
        req_frame = ttk.Frame(self.formulario_inner)
        req_frame.pack(fill="x", pady=10)
        ttk.Label(req_frame, text="* Campos obligatorios", font=("Arial", 8, "italic"), foreground="red").pack()
    
    def crear_formulario_reserva_simulador(self):
        """Crea el formulario para simular reservas"""

        # Aviso si no hay clientes o servicios registrados
        aviso = []
        if not self.clients:
            aviso.append("⚠ No hay clientes registrados.")
        if not self.catalogo_servicios.listar_disponibles():
            aviso.append("⚠ No hay servicios disponibles.")
        if aviso:
            ttk.Label(self.formulario_inner, text="\n".join(aviso),
                      foreground="#b45309", font=("Arial", 9, "italic"),
                      wraplength=300, justify="left").pack(fill="x", padx=5, pady=(0, 5))

        # Cliente
        cliente_frame = ttk.Frame(self.formulario_inner)
        cliente_frame.pack(fill="x", pady=5)
        ttk.Label(cliente_frame, text="Cliente:*", width=18, anchor="w").pack(side="left", padx=5)
        clientes_lista = [f"{c._id} - {c._name}" for c in self.clients]
        combo_cliente = ttk.Combobox(cliente_frame, values=clientes_lista, state="readonly")
        combo_cliente.pack(side="left", padx=5, fill="x", expand=True)
        if clientes_lista:
            combo_cliente.set(clientes_lista[0])
        self.widgets_simulador["cliente"] = combo_cliente

        # Servicio (solo disponibles)
        servicio_frame = ttk.Frame(self.formulario_inner)
        servicio_frame.pack(fill="x", pady=5)
        ttk.Label(servicio_frame, text="Servicio:*", width=18, anchor="w").pack(side="left", padx=5)
        servicios_lista = [f"{s.id} - {s.name} (${s.price:,.0f}/h)"
                          for s in self.catalogo_servicios.listar_disponibles()]
        combo_servicio = ttk.Combobox(servicio_frame, values=servicios_lista, state="readonly")
        combo_servicio.pack(side="left", padx=5, fill="x", expand=True)
        if servicios_lista:
            combo_servicio.set(servicios_lista[0])
        self.widgets_simulador["servicio"] = combo_servicio

        # Duración
        dur_frame = ttk.Frame(self.formulario_inner)
        dur_frame.pack(fill="x", pady=5)
        ttk.Label(dur_frame, text="Duración (horas):*", width=18, anchor="w").pack(side="left", padx=5)
        entry_dur = ttk.Entry(dur_frame)
        entry_dur.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["duracion"] = entry_dur

        # Fecha
        fecha_frame = ttk.Frame(self.formulario_inner)
        fecha_frame.pack(fill="x", pady=5)
        ttk.Label(fecha_frame, text="Fecha (DD/MM/AAAA):*", width=18, anchor="w").pack(side="left", padx=5)
        entry_fecha = ttk.Entry(fecha_frame)
        entry_fecha.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
        entry_fecha.pack(side="left", padx=5, fill="x", expand=True)
        self.widgets_simulador["fecha"] = entry_fecha

        # Botón refrescar combos (por si se registraron clientes/servicios después de abrir el simulador)
        btn_ref = ttk.Frame(self.formulario_inner)
        btn_ref.pack(fill="x", pady=(5, 0))
        ttk.Button(btn_ref, text="🔄 Refrescar listas",
                   command=self._refrescar_combos_reserva_simulador).pack(side="left", padx=5)

        ttk.Label(self.formulario_inner, text="* Campos obligatorios",
                  font=("Arial", 8, "italic"), foreground="red").pack(pady=8)

    def _refrescar_combos_reserva_simulador(self):
        """Actualiza los combos de cliente y servicio dentro del formulario de reserva del simulador"""
        if "cliente" in self.widgets_simulador:
            nuevos_clientes = [f"{c._id} - {c._name}" for c in self.clients]
            self.widgets_simulador["cliente"]["values"] = nuevos_clientes
            if nuevos_clientes:
                self.widgets_simulador["cliente"].set(nuevos_clientes[0])

        if "servicio" in self.widgets_simulador:
            nuevos_servicios = [f"{s.id} - {s.name} (${s.price:,.0f}/h)"
                               for s in self.catalogo_servicios.listar_disponibles()]
            self.widgets_simulador["servicio"]["values"] = nuevos_servicios
            if nuevos_servicios:
                self.widgets_simulador["servicio"].set(nuevos_servicios[0])

        messagebox.showinfo("Actualizado", "Listas de clientes y servicios actualizadas.")
    
    def agregar_dato_lista(self):
        """Agrega el dato actual del formulario a la lista acumulada"""
        tipo = self.simulador_tipo.get()
        
        if tipo == "Cliente":
            nombre = self.widgets_simulador.get("nombre", ttk.Entry()).get().strip()
            email = self.widgets_simulador.get("email", ttk.Entry()).get().strip()
            phone = self.widgets_simulador.get("phone", ttk.Entry()).get().strip()
            
            if not nombre or not email or not phone:
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos del cliente")
                return
            
            dato = {
                "tipo": "Cliente",
                "datos": {
                    "nombre": nombre,
                    "email": email,
                    "phone": phone
                }
            }
            resumen = f"Nombre: {nombre}, Email: {email}, Tel: {phone}"
            
        elif tipo == "Servicio":
            tipo_servicio = self.widgets_simulador.get("tipo", ttk.Combobox()).get()
            nombre = self.widgets_simulador.get("nombre", ttk.Entry()).get().strip()
            precio = self.widgets_simulador.get("precio", ttk.Entry()).get().strip()
            descripcion = self.widgets_simulador.get("descripcion", ttk.Entry()).get().strip()
            
            if not nombre or not precio or not descripcion:
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos del servicio")
                return
            
            dato = {
                "tipo": "Servicio",
                "datos": {
                    "tipo_servicio": tipo_servicio,
                    "nombre": nombre,
                    "precio": precio,
                    "descripcion": descripcion
                }
            }
            resumen = f"Tipo: {tipo_servicio}, Nombre: {nombre}, Precio: ${precio}, Desc: {descripcion[:30]}..."
            
        elif tipo == "Reserva":
            cliente_sel  = self.widgets_simulador.get("cliente",  ttk.Combobox()).get()
            servicio_sel = self.widgets_simulador.get("servicio", ttk.Combobox()).get()
            duracion     = self.widgets_simulador.get("duracion", ttk.Entry()).get().strip()
            fecha        = self.widgets_simulador.get("fecha",    ttk.Entry()).get().strip()

            if not cliente_sel or not servicio_sel or not duracion or not fecha:
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos de la reserva")
                return

            dato = {"tipo": "Reserva",
                    "datos": {"cliente": cliente_sel, "servicio": servicio_sel,
                               "duracion": duracion, "fecha": fecha}}
            resumen = f"Cliente: {cliente_sel.split(' - ')[1] if ' - ' in cliente_sel else cliente_sel}, "\
                      f"Servicio: {servicio_sel.split(' - ')[1].split(' (')[0] if ' - ' in servicio_sel else servicio_sel}, "\
                      f"Duración: {duracion}h, Fecha: {fecha}"
        else:
            return
        
        self.datos_acumulados.append(dato)
        item_id = len(self.datos_acumulados)
        self.lista_datos_tree.insert("", "end", iid=str(item_id), values=(item_id, tipo, resumen))
        self.actualizar_total_lista()
        self.limpiar_formulario_simulador()
        messagebox.showinfo("Dato Agregado", f"Dato de {tipo} agregado correctamente a la lista.\nTotal en lista: {len(self.datos_acumulados)}")
    
    def eliminar_dato_lista(self):
        """Elimina el dato seleccionado de la lista"""
        selection = self.lista_datos_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un dato para eliminar")
            return
        
        item_id = int(selection[0])
        index = item_id - 1
        
        if 0 <= index < len(self.datos_acumulados):
            del self.datos_acumulados[index]
            self.lista_datos_tree.delete(*self.lista_datos_tree.get_children())
            
            for i, dato in enumerate(self.datos_acumulados, 1):
                if dato["tipo"] == "Cliente":
                    resumen = f"Nombre: {dato['datos']['nombre']}, Email: {dato['datos']['email']}, Tel: {dato['datos']['phone']}"
                elif dato["tipo"] == "Servicio":
                    resumen = f"Tipo: {dato['datos']['tipo_servicio']}, Nombre: {dato['datos']['nombre']}, Precio: ${dato['datos']['precio']}"
                else:
                    d = dato["datos"]
                    resumen = f"Cliente: {d['cliente']}, Servicio: {d['servicio']}, Duración: {d['duracion']}h"
                self.lista_datos_tree.insert("", "end", iid=str(i), values=(i, dato["tipo"], resumen))
            
            self.actualizar_total_lista()
            messagebox.showinfo("Éxito", "Dato eliminado correctamente")
    
    def limpiar_lista_datos(self):
        """Limpia toda la lista de datos acumulados"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de limpiar toda la lista de datos?"):
            self.datos_acumulados.clear()
            self.lista_datos_tree.delete(*self.lista_datos_tree.get_children())
            self.actualizar_total_lista()
            messagebox.showinfo("Éxito", "Lista limpiada correctamente")
    
    def insertar_datos_masivos(self):
        """Inserta todos los datos acumulados en el sistema"""
        if not self.datos_acumulados:
            messagebox.showwarning("Advertencia", "No hay datos para insertar. Agregue datos a la lista primero.")
            return
        
        if not messagebox.askyesno("Confirmar Inserción Masiva", 
                                   f"¿Está seguro de insertar {len(self.datos_acumulados)} datos en el sistema?\n\n"
                                   "Los datos válidos se insertarán automáticamente.\n"
                                   "Los datos inválidos se registrarán en los logs."):
            return
        
        correctos = 0
        incorrectos = 0
        
        for dato in self.datos_acumulados:
            if dato["tipo"] == "Cliente":
                ok = self.insertar_cliente_simulado(dato["datos"])
            elif dato["tipo"] == "Servicio":
                ok = self.insertar_servicio_simulado(dato["datos"])
            elif dato["tipo"] == "Reserva":
                ok = self.insertar_reserva_simulada(dato["datos"])
            else:
                ok = False

            if ok:
                correctos += 1
                self.simulador_datos_correctos += 1
            else:
                incorrectos += 1
                self.simulador_datos_incorrectos += 1
        
        self.actualizar_estadisticas()
        self.datos_acumulados.clear()
        self.lista_datos_tree.delete(*self.lista_datos_tree.get_children())
        self.actualizar_total_lista()
        self.refrescar_clientes_reserva()
        self.refrescar_servicios_reserva()
        self.actualizar_tabla_reservas()
        self.actualizar_resumen_reservas()
        self.load_logs()
        
        messagebox.showinfo("Inserción Masiva Completada", 
                           f"Proceso finalizado:\n\n✅ Datos correctos insertados: {correctos}\n❌ Datos incorrectos: {incorrectos}\n\n"
                           f"Total procesados: {correctos + incorrectos}\n\n"
                           "Los datos incorrectos se han registrado en la pestaña de Logs.")
    
    def insertar_cliente_simulado(self, datos):
        """Inserta un cliente simulado, retorna True si fue exitoso"""
        nombre = datos["nombre"]
        email = datos["email"]
        phone = datos["phone"]
        new_id = len(self.clients) + 1 if self.clients else 1
        
        try:
            if not nombre:
                raise ClienteInvalidoError("El nombre es obligatorio")
            if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", nombre):
                raise ClienteInvalidoError("El nombre solo puede contener letras y espacios")
            if len(nombre) < 3:
                raise ClienteInvalidoError("El nombre es demasiado corto")
            
            if not email:
                raise ClienteInvalidoError("El correo es obligatorio")
            if "@" not in email or "." not in email:
                raise ClienteInvalidoError("Ingrese un correo válido")
            patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.fullmatch(patron_email, email):
                raise ClienteInvalidoError("Formato de correo inválido")
            
            if not phone:
                raise ClienteInvalidoError("El teléfono es obligatorio")
            if not phone.isdigit():
                raise ClienteInvalidoError("El teléfono solo debe contener números")
            if len(phone) != 10:
                raise ClienteInvalidoError("El teléfono debe tener exactamente 10 dígitos")
            
            for client in self.clients:
                if client._name.lower() == nombre.lower():
                    raise ClienteDuplicadoError(f"Ya existe un cliente con el nombre '{nombre}'")
                if client._email.lower() == email.lower():
                    raise ClienteDuplicadoError(f"Ya existe un cliente con el correo '{email}'")
                if client._phone == phone:
                    raise ClienteDuplicadoError(f"Ya existe un cliente con el teléfono '{phone}'")
            
            cliente = Cliente(new_id, nombre, email, phone)
            self.clients.append(cliente)
            self.table_client.insert("", "end", iid=str(cliente._id), values=(cliente._id, cliente._name, cliente._email, cliente._phone))
            logging.info(f"[SIMULADOR] Cliente válido registrado: {nombre} (ID: {new_id})")
            return True
            
        except (ClienteInvalidoError, ClienteDuplicadoError) as e:
            logging.error(f"[SIMULADOR] Error al insertar cliente - Datos: Nombre='{nombre}', Email='{email}', Teléfono='{phone}' - Error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"[SIMULADOR] Error inesperado al insertar cliente: {str(e)}")
            return False
    
    def insertar_servicio_simulado(self, datos):
        """Inserta un servicio simulado, retorna True si fue exitoso"""
        tipo_servicio = datos["tipo_servicio"]
        nombre = datos["nombre"]
        precio_str = datos["precio"]
        descripcion = datos["descripcion"]
        new_id = self.catalogo_servicios.obtener_nuevo_id()
        
        try:
            if not nombre:
                raise ServicioInvalidoError("El nombre del servicio es obligatorio")
            if len(nombre) < 3:
                raise ServicioInvalidoError("El nombre del servicio debe tener al menos 3 caracteres")
            if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", nombre):
                raise ServicioInvalidoError("El nombre solo puede contener letras y espacios (sin números)")
            
            if not descripcion:
                raise ServicioInvalidoError("La descripción del servicio es obligatoria")
            if len(descripcion) < 5:
                raise ServicioInvalidoError("La descripción debe tener al menos 5 caracteres")
            
            for servicio in self.catalogo_servicios.listar_servicios():
                if servicio.name.lower() == nombre.lower():
                    raise ServicioDuplicadoError(f"Ya existe un servicio con el nombre '{nombre}'")
            
            if not precio_str:
                raise ServicioInvalidoError("El precio del servicio es obligatorio")
            try:
                precio = float(precio_str)
            except ValueError:
                raise ServicioInvalidoError("Ingrese un precio válido")
            if precio <= 0:
                raise ServicioInvalidoError("El precio debe ser mayor a 0")
            if precio > 1000000:
                raise ServicioInvalidoError("El precio no puede superar $1,000,000")
            
            if tipo_servicio == "Estándar":
                servicio = ServicioEstandar(new_id, nombre, precio, descripcion)
            elif tipo_servicio == "Premium":
                servicio = ServicioPremium(new_id, nombre, precio, descripcion)
            elif tipo_servicio == "Express":
                servicio = ServicioExpress(new_id, nombre, precio, descripcion)
            else:
                raise ServicioInvalidoError("Tipo de servicio no válido")
            
            self.catalogo_servicios.agregar_servicio(servicio)
            self.actualizar_tabla_servicios()
            logging.info(f"[SIMULADOR] Servicio válido registrado: {nombre} (ID: {new_id}) - Tipo: {tipo_servicio}")
            return True
            
        except (ServicioInvalidoError, ServicioDuplicadoError) as e:
            logging.error(f"[SIMULADOR] Error al insertar servicio - Datos: Nombre='{nombre}', Precio='{precio_str}', Tipo='{tipo_servicio}' - Error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"[SIMULADOR] Error inesperado al insertar servicio: {str(e)}")
            return False
    
    def insertar_reserva_simulada(self, datos):
        """
        Inserta una reserva simulada con validaciones completas.
        Retorna True si fue exitoso, False si falló (el error queda en el log).
        """
        cliente_sel  = datos.get("cliente", "")
        servicio_sel = datos.get("servicio", "")
        duracion_str = datos.get("duracion", "")
        fecha_str    = datos.get("fecha", "")

        try:
            # ---- Validar y obtener cliente ----
            if not cliente_sel:
                raise ExcepcionReserva("Debe seleccionar un cliente")

            try:
                cliente_id = int(cliente_sel.split(" - ")[0])
            except (ValueError, IndexError):
                raise ExcepcionReserva(f"Formato de cliente inválido: '{cliente_sel}'")

            cliente = next((c for c in self.clients if c._id == cliente_id), None)
            if not cliente:
                raise ExcepcionReserva(f"Cliente con ID {cliente_id} no encontrado en el sistema")

            # ---- Validar y obtener servicio ----
            if not servicio_sel:
                raise ExcepcionReserva("Debe seleccionar un servicio")

            try:
                servicio_id = int(servicio_sel.split(" - ")[0])
            except (ValueError, IndexError):
                raise ExcepcionReserva(f"Formato de servicio inválido: '{servicio_sel}'")

            servicio = self.catalogo_servicios.buscar_servicio(servicio_id)
            if not servicio:
                raise ExcepcionReserva(f"Servicio con ID {servicio_id} no encontrado en el catálogo")
            if not servicio.disponible:
                raise ExcepcionReserva(f"El servicio '{servicio.name}' no está disponible")

            # ---- Validar duración ----
            if not duracion_str:
                raise ExcepcionReserva("La duración es obligatoria")
            try:
                duracion = float(duracion_str)
            except ValueError:
                raise ExcepcionReserva(f"Duración inválida: '{duracion_str}'. Debe ser un número")
            if duracion <= 0:
                raise ExcepcionReserva("La duración debe ser mayor a 0 horas")
            if duracion > 24:
                raise ExcepcionReserva("La duración máxima por reserva es de 24 horas")

            # ---- Validar fecha ----
            if not fecha_str:
                raise ExcepcionReserva("La fecha es obligatoria")
            try:
                fecha = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
            except ValueError:
                raise ExcepcionReserva(f"Formato de fecha inválido: '{fecha_str}'. Use DD/MM/AAAA")

            # ---- Crear reserva ----
            reserva = self.gestor_reservas.crear_reserva(cliente, servicio, duracion, fecha)
            logging.info(
                f"[SIMULADOR] Reserva válida creada: #{reserva.id} - "
                f"Cliente: {cliente._name} - Servicio: {servicio.name} - "
                f"Duración: {duracion}h - Fecha: {fecha_str}"
            )
            return True

        except ExcepcionReserva as e:
            logging.error(
                f"[SIMULADOR] Error al insertar reserva - "
                f"Cliente='{cliente_sel}', Servicio='{servicio_sel}', "
                f"Duración='{duracion_str}', Fecha='{fecha_str}' - {str(e)}"
            )
            return False
        except Exception as e:
            logging.error(f"[SIMULADOR] Error inesperado al insertar reserva: {str(e)}")
            return False
        
    def limpiar_formulario_simulador(self):
        """Limpia todos los campos del formulario"""
        for key, widget in self.widgets_simulador.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                # Restaurar fecha por defecto en el campo de reserva
                if key == "fecha":
                    widget.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
            elif isinstance(widget, ttk.Combobox):
                vals = widget.cget("values")
                if vals:
                    widget.set(vals[0])
     
    def create_frame_logs(self):
        """Pestaña para visualizar logs del sistema"""

        # Frame principal
        log_frame = ttk.LabelFrame(self.frame_logs, text="Registro de Errores del Sistema", padding=10)

        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Caja de texto
        self.text_logs = tk.Text(log_frame, wrap="word", font=("Consolas", 10), bg="#f8fafc", fg="#1f2937", insertbackground="#1f2937",relief="flat")

        self.text_logs.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.text_logs.yview)

        scrollbar.pack(side="right", fill="y")

        self.text_logs.configure(yscrollcommand=scrollbar.set)

        # Frame botones
        button_frame = ttk.Frame(self.frame_logs)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="🔄 Actualizar Logs", command=self.load_logs).pack(side="left", padx=5)

        # Cargar logs al iniciar
        self.load_logs()
        
    def load_logs(self):
        """Carga el contenido del archivo de logs"""
        try:
            self.text_logs.delete("1.0", tk.END)

            with open("logs_error.log", "r", encoding="latin-1") as file:
                lineas = file.readlines()
                
                if not lineas:
                    self.text_logs.insert(tk.END, "No hay logs registrados")
                else:
                    for linea in lineas:
                        # Mostrar todas las líneas (INFO, ERROR, WARNING)
                        if "ERROR" in linea or "INFO" in linea or "WARNING" in linea:
                            partes = linea.split(" - ", 2)
                            if len(partes) >= 3:
                                mensaje_limpio = f"{partes[0]} - {partes[2]}"
                                self.text_logs.insert(tk.END, mensaje_limpio)
                            else:
                                self.text_logs.insert(tk.END, linea.strip() + "\n")
                        else:
                            self.text_logs.insert(tk.END, linea)
                            
        except FileNotFoundError:
            self.text_logs.insert(tk.END, "El archivo de logs no existe todavía")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los logs:\n{str(e)}")

        
# Ejecutar la aplicación
if __name__ == "__main__":
    view = tk.Tk()
    app = main_window(view)
    view.mainloop()