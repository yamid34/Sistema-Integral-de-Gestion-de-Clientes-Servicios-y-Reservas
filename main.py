from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from abc import ABC, abstractmethod
import datetime
import traceback
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

        # Grises
        self.COLOR_GRIS = "#555555"
        self.COLOR_GRIS_OSCURO = "#1f2937"
        self.COLOR_BORDE = "#d0d0d0"

        """========================
        INICIALIZAR VENTANA
        ========================"""
        
        self.clients = []

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

        self.create_widgets()

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
        self.frame_clients = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_clients, text="👥 Clientes")
        self.create_frame_client()
        
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
        
        ttk.Button(button_frame, text="Registrar Cliente", command=self.register_client).pack(anchor="w", pady=2)
        ttk.Button(button_frame, text="Eliminar Cliente", command=self.delete_client, style="Red.TButton").pack(anchor="w", pady=2)
        
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

        name = self.entry_name.get()
        email = self.entry_email.get()
        phone = self.entry_phone.get()

        if not name or not email or not phone:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        # Generar ID automático
        if len(self.clients) == 0:
            new_id = 1
        else:
            new_id = self.clients[-1]._id + 1

        # Crear objeto Cliente
        client = Cliente(new_id, name, email, phone)

        # Guardar objeto en la lista
        self.clients.append(client)

        # Mostrar en tabla
        self.table_client.insert("", "end",
        iid=str(client._id),
        values=(client._id, client._name, client._email, client._phone))

        # Limpiar campos
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        
    def delete_client(self):
        selection = self.table_client.selection()

        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return

        item_id = selection[0]

        # Eliminar de la tabla
        self.table_client.delete(item_id)

        # Eliminar de la lista
        self.clients = [client for client in self.clients
        if str(client._id) != item_id]
        
        

view = tk.Tk()

app = main_window(view)

view.mainloop()
