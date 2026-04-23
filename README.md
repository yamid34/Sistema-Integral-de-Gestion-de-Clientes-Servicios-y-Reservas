# Sistema Integral de Gestión de Clientes, Servicios y Reservas

## Descripción

Este repositorio contiene la solución de un ejercicio aplicado que consiste en el desarrollo de un **sistema integral de gestión de clientes, servicios y reservas** para la empresa **Software FJ**.
El sistema está diseñado bajo el paradigma de **Programación Orientada a Objetos (POO)**, sin el uso de bases de datos, garantizando una arquitectura **modular, robusta y extensible**.

---
## Objetivo
Desarrollar una aplicación capaz de gestionar:

- Clientes  
- Servicios (reservas de salas, alquiler de equipos, asesorías especializadas)  
- Reservas  

Aplicando de forma rigurosa los principios de:

- Abstracción  
- Herencia  
- Polimorfismo  
- Encapsulación  
- Manejo avanzado de excepciones  

---
## Características del Sistema

- No utiliza bases de datos  
- Manejo de información mediante objetos y listas  
- Registro de eventos y errores en archivos (logs)  
- Validaciones estrictas de datos  
- Sistema tolerante a fallos (no se detiene ante errores)

---
## Arquitectura del Sistema

El sistema debe incluir como mínimo:

### Clases principales

- **Clase abstracta base**
  - Representa entidades generales del sistema

- **Clase Cliente**
  - Validación de datos personales
  - Encapsulación

- **Clase abstracta Servicio**
  - Base para los diferentes tipos de servicios

- **Clases derivadas de Servicio**
  - Reserva de salas  
  - Alquiler de equipos  
  - Asesorías especializadas  
  - Implementación de polimorfismo y métodos sobrescritos

- **Clase Reserva**
  - Integra cliente, servicio, duración y estado
  - Permite:
    - Confirmación
    - Cancelación
    - Procesamiento con manejo de errores

---

## Funcionalidades Clave

- Métodos sobrecargados (cálculo de costos con impuestos, descuentos, etc.)
- Manejo de listas internas
- Validaciones robustas
- Simulación de operaciones reales

---

## Manejo de Excepciones

El sistema implementa un manejo avanzado de errores incluyendo:

- `try / except`
- `try / except / else`
- `try / except / finally`
- Excepciones personalizadas
- Encadenamiento de excepciones

### Tipos de errores controlados

- Datos inválidos  
- Parámetros faltantes  
- Operaciones no permitidas  
- Reservas incorrectas  
- Servicios no disponibles  
- Errores de cálculo  
- Fallos inesperados  

Todos los errores son registrados en un archivo de logs, asegurando que el sistema continúe funcionando correctamente.

---

## Simulación del Sistema

El sistema debe ejecutar al menos:

- 10 Operaciones completas, incluyendo:
  - Registros de clientes (válidos e inválidos)
  - Creación de servicios (correctos e incorrectos)
  - Reservas exitosas y fallidas

Esto garantiza la **resiliencia del sistema ante errores**.

---

## Requisitos del Proyecto

- Aplicación completamente funcional  
- Código organizado y documentado  
- Ejecución sin interrupciones  
- Uso correcto de POO  
- Manejo avanzado de excepciones  
- Sin uso de bases de datos  

---

## Equipo de Trabajo

Proyecto desarrollado en equipo (5 integrantes).

---

## Tecnologías

```bash
Lenguaje: Python
Paradigma: Programación Orientada a Objetos
Persistencia: Archivos (logs)
