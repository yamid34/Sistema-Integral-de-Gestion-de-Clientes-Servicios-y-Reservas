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
    
# IMPLEMENTACIÓN CONCRETA DE RESERVA
class ReservaEstandar(Reserva):
    def calculate_cost(self, duration):
        if hasattr(self.service, 'calculate_daily_cost'):
            return self.service.calculate_daily_cost(duration)
        return self.service.price * duration

    def description(self):
        return f"Reserva estándar del servicio {self.service.name} por {self.duration} horas"

    def validate_parameters(self, **kwargs):
        duration = kwargs.get('duration', self.duration)
        return duration > 0 and self.service.disponible

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
        self.catalogo_servicios = CatalogoServicios()
        self.reservas = []

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
        self.cargar_datos_ejemplo()
    
    def cargar_datos_ejemplo(self):
        """Carga servicios de ejemplo para mostrar"""
        servicio1 = ServicioEstandar(1, "Limpieza General", 25000, "Limpieza completa de oficinas")
        servicio2 = ServicioPremium(2, "Mantenimiento IT", 45000, "Soporte técnico especializado", "Respuesta en 2 horas")
        servicio3 = ServicioExpress(3, "Urgencias Eléctricas", 60000, "Atención inmediata")
        servicio4 = ServicioEstandar(4, "Jardinería", 30000, "Mantenimiento de áreas verdes")
        
        self.catalogo_servicios.agregar_servicio(servicio1)
        self.catalogo_servicios.agregar_servicio(servicio2)
        self.catalogo_servicios.agregar_servicio(servicio3)
        self.catalogo_servicios.agregar_servicio(servicio4)
        
        # Actualizar tabla de servicios
        self.actualizar_tabla_servicios()
        
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
        
    def create_frame_service(self):
        """Crea la pestaña de gestión de servicios"""
        # Frame para registrar nuevo servicio
        form_frame = ttk.LabelFrame(self.frame_services, text="Registrar Nuevo Servicio", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Tipo de servicio
        ttk.Label(form_frame, text="Tipo de Servicio:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.service_type = ttk.Combobox(form_frame, values=["Estándar", "Premium", "Express"], width=23, state="readonly")
        self.service_type.grid(row=0, column=1, padx=5, pady=5)
        self.service_type.set("Estándar")
        
        # Nombre del servicio
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.service_name = ttk.Entry(form_frame, width=25)
        self.service_name.grid(row=1, column=1, padx=5, pady=5)
        
        # Precio
        ttk.Label(form_frame, text="Precio por hora ($):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.service_price = ttk.Entry(form_frame, width=25)
        self.service_price.grid(row=2, column=1, padx=5, pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, padx=5, pady=5, sticky="ne")
        self.service_description = tk.Text(form_frame, width=25, height=3, font=("Arial", 10))
        self.service_description.grid(row=3, column=1, padx=5, pady=5)
        
        # Beneficio extra (solo para premium)
        ttk.Label(form_frame, text="Beneficio Extra (Premium):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
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
        
        ttk.Button(button_frame, text="📝 Registrar Servicio", command=self.register_service).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="🔄 Cambiar Disponibilidad", command=self.toggle_service_availability, style="Green.TButton").pack(side="left", padx=5)
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
        descripcion = self.service_description.get("1.0", tk.END).strip()
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
        self.service_description.delete("1.0", tk.END)
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

        
view = tk.Tk()

app = main_window(view)

view.mainloop()
