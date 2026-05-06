from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from abc import ABC, abstractmethod
import datetime
import traceback
import logging
import re
from enum import Enum

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
# ============================================================
# CONFIGURACIÓN DE LOGS
# ============================================================

logging.basicConfig(
    filename="logs_error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
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
        self._beneficio_extra = beneficio_extra
        self._factor_calidad = 1.3  # 30% más caro por hora

    def get_details(self):
        detalles = f"Servicio Premium - {self._description}"
        if self._beneficio_extra:
            detalles += f" | Beneficio: {self._beneficio_extra}"
        return detalles

    def calculate_daily_cost(self, hours):
        """Costo premium con factor de calidad"""
        if hours < 1:
            hours = 1
        return self._price * hours * self._factor_calidad

    @property
    def beneficio_extra(self):
        return self._beneficio_extra

    @beneficio_extra.setter
    def beneficio_extra(self, value):
        self._beneficio_extra = value


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

        self.view = view
        self.view.title("Software FJ - Sistema Integral de Gestión")
        self.view.geometry("1200x700")
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

            for client in self.clients:

                if client._email.lower() == email.lower():
                    raise ClienteDuplicadoError("Ya existe un cliente con ese correo")

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
        
        # Beneficio extra (solo para premium)
        ttk.Label(form_frame, text="Beneficio Extra (Premium):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.service_benefit = ttk.Entry(form_frame, width=25)
        self.service_benefit.grid(row=4, column=1, padx=5, pady=5)
        self.service_benefit.configure(state="disabled")
        
        # Habilitar/deshabilitar campo beneficio según tipo
        def on_type_change(*args):
            if self.service_type.get() == "Premium":
                self.service_benefit.configure(state="normal")
            else:
                self.service_benefit.configure(state="disabled")
                self.service_benefit.delete(0, tk.END)
        
        self.service_type.bind("<<ComboboxSelected>>", on_type_change)
        
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
        tipo = self.service_type.get()
        nombre = self.service_name.get()
        precio_str = self.service_price.get()
        descripcion = self.service_description.get().strip()
        beneficio = self.service_benefit.get() if tipo == "Premium" else ""
        
        # Validaciones
        if not nombre or not precio_str:
            messagebox.showwarning("Advertencia", "Nombre y precio son obligatorios")
            return
        
        try:
            precio = float(precio_str)
            if precio <= 0:
                messagebox.showwarning("Advertencia", "El precio debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "Precio inválido")
            return
        
        # Generar ID
        new_id = self.catalogo_servicios.obtener_nuevo_id()
        
        # Crear servicio según tipo
        if tipo == "Estándar":
            servicio = ServicioEstandar(new_id, nombre, precio, descripcion)
        elif tipo == "Premium":
            servicio = ServicioPremium(new_id, nombre, precio, descripcion, beneficio)
        elif tipo == "Express":
            servicio = ServicioExpress(new_id, nombre, precio, descripcion)
        else:
            messagebox.showerror("Error", "Tipo de servicio no válido")
            return
        
        # Agregar al catálogo
        self.catalogo_servicios.agregar_servicio(servicio)
        
        # Actualizar tabla
        self.actualizar_tabla_servicios()
        
        # Limpiar campos
        self.service_name.delete(0, tk.END)
        self.service_price.delete(0, tk.END)
        self.service_description.delete(0, tk.END)
        self.service_benefit.delete(0, tk.END)
        self.service_type.set("Estándar")
        
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
        selection = self.table_service.selection()
        
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un servicio")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este servicio?"):
            servicio_id = int(selection[0])
            self.catalogo_servicios.eliminar_servicio(servicio_id)
            self.actualizar_tabla_servicios()
            messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
    
    def toggle_service_availability(self):
        """Cambia la disponibilidad de un servicio"""
        selection = self.table_service.selection()
        
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un servicio")
            return
        
        servicio_id = int(selection[0])
        servicio = self.catalogo_servicios.buscar_servicio(servicio_id)
        
        if servicio:
            servicio.disponible = not servicio.disponible
            self.actualizar_tabla_servicios()
            estado = "disponible" if servicio.disponible else "no disponible"
            messagebox.showinfo("Éxito", f"Servicio ahora está {estado}")

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
                messagebox.showwarning("Advertencia", "Debe seleccionar un cliente")
                return
            
            cliente_id = int(cliente_seleccionado.split(" - ")[0])
            cliente = next((c for c in self.clients if c._id == cliente_id), None)
            
            if not cliente:
                messagebox.showerror("Error", "Cliente no encontrado")
                return
            
            # Obtener servicio seleccionado
            servicio_seleccionado = self.reserva_servicio_combo.get()
            if not servicio_seleccionado:
                messagebox.showwarning("Advertencia", "Debe seleccionar un servicio")
                return
            
            servicio_id = int(servicio_seleccionado.split(" - ")[0])
            servicio = self.catalogo_servicios.buscar_servicio(servicio_id)
            
            if not servicio:
                messagebox.showerror("Error", "Servicio no encontrado")
                return
            
            if not servicio.disponible:
                messagebox.showerror("Error", "El servicio seleccionado no está disponible")
                return
            
            # Obtener duración
            duracion_str = self.reserva_duracion.get()
            if not duracion_str:
                messagebox.showwarning("Advertencia", "Debe ingresar la duración")
                return
            
            try:
                duracion = float(duracion_str)
            except ValueError:
                messagebox.showerror("Error", "Duración inválida")
                return
            
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
            messagebox.showerror("Error de Reserva", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            traceback.print_exc()
    
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
            messagebox.showerror("Error", str(e))
        except Exception as e:
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
            messagebox.showerror("Error", str(e))
        except Exception as e:
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
            messagebox.showerror("Error", str(e))
        except Exception as e:
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


        
view = tk.Tk()

app = main_window(view)

view.mainloop()
