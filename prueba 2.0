#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
 Curso: Programación (213023) - Fase 4 - UNAD
===============================================================================

Descripción general
-------------------
Aplicación de consola desarrollada con Programación Orientada a Objetos (POO)
que gestiona clientes, servicios y reservas de la empresa "Software FJ".

Restricciones de diseño que cumple este programa
------------------------------------------------
* NO se usan bases de datos ni archivos JSON/CSV como almacenamiento.
  Toda la información (clientes, servicios, reservas) vive únicamente en
  memoria, dentro de listas internas de la clase `GestorFJ`.
* El único uso de archivos es el registro de eventos/errores en el archivo
  `software_fj.log`, mediante el módulo nativo `logging`.

Estructura del módulo
---------------------
 1. Configuración del sistema de logs.
 2. Jerarquía de excepciones personalizadas.
 3. `EntidadBase`      (clase abstracta general).
 4. `Cliente`          (encapsulación estricta + validaciones).
 5. `Servicio`         (clase abstracta) y tres derivadas especializadas:
                       `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`.
 6. `EstadoReserva` y `Reserva` (máquina de estados).
 7. `GestorFJ`         (almacenamiento en memoria y orquestación).
 8. Simulación de pruebas (más de 10 operaciones válidas e inválidas).

Ejecución
---------
    python software_fj.py
"""

import logging
import math
import re
import tkinter as tk
from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import messagebox, ttk
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# =============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS
# =============================================================================

#: Nombre del único archivo que el programa escribe (solo para auditoría).
ARCHIVO_LOG = "software_fj.log"


def configurar_logging() -> logging.Logger:
    """
    Configura (una sola vez) el registrador principal de la aplicación.

    - Archivo `software_fj.log`: guarda TODOS los niveles (DEBUG en adelante)
      con marca de tiempo, nivel y función que generó el evento.
    - Consola: muestra desde INFO en adelante para seguir la ejecución.

    La función es idempotente: si ya hay manejadores configurados, no vuelve a
    agregarlos (evita líneas duplicadas en el log).

    Returns:
        logging.Logger: registrador listo para usar en todo el sistema.
    """
    registrador = logging.getLogger("SoftwareFJ")

    # Si ya fue configurado, se reutiliza tal cual.
    if registrador.handlers:
        return registrador

    registrador.setLevel(logging.DEBUG)
    registrador.propagate = False  # Evita duplicar mensajes en el logger raíz.

    # Formato detallado para el archivo de auditoría.
    formato_archivo = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(funcName)-26s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Formato más compacto para la consola.
    formato_consola = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Manejador de archivo (modo "a": conserva el historial entre ejecuciones).
    manejador_archivo = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    manejador_archivo.setLevel(logging.DEBUG)
    manejador_archivo.setFormatter(formato_archivo)

    # Manejador de consola.
    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.INFO)
    manejador_consola.setFormatter(formato_consola)

    registrador.addHandler(manejador_archivo)
    registrador.addHandler(manejador_consola)
    return registrador


#: Registrador global usado por todas las clases del módulo.
logger = configurar_logging()


# =============================================================================
# 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
# =============================================================================

class SoftwareFJException(Exception):
    """
    Excepción base de todo el sistema.

    Permite capturar cualquier error propio de la aplicación con un único
    `except SoftwareFJException`, distinguiéndolo de errores del intérprete.

    Attributes:
        mensaje (str): descripción legible del problema.
        codigo (str): código interno para facilitar la auditoría en el log.
    """

    def __init__(self, mensaje: str, codigo: str = "FJ-000") -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


class DatoInvalidoError(SoftwareFJException):
    """Se lanza cuando un dato de entrada no cumple formato, tipo o rango."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="FJ-100")


class ServicioNoDisponibleError(SoftwareFJException):
    """Se lanza cuando se intenta usar un servicio deshabilitado/no disponible."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="FJ-200")


class ReservaInvalidaError(SoftwareFJException):
    """Se lanza ante reservas mal formadas o transiciones de estado no permitidas."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="FJ-300")


class CalculoInconsistenteError(SoftwareFJException):
    """Se lanza cuando un cálculo de costos produce un resultado incoherente."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo="FJ-400")


# =============================================================================
# 3. CLASE ABSTRACTA GENERAL: EntidadBase
# =============================================================================

class EntidadBase(ABC):
    """
    Clase abstracta raíz de todas las entidades del dominio.

    Define los atributos comunes (identificador y fecha de creación),
    protegidos mediante atributos "privados" (name mangling con doble guion
    bajo) y expuestos solo en lectura mediante `@property`.

    Obliga a las clases hijas a implementar `obtener_detalles()`.
    """

    def __init__(self, identificador: str) -> None:
        """
        Args:
            identificador: código único de la entidad (p. ej. "CLI-001").

        Raises:
            DatoInvalidoError: si el identificador no es un texto no vacío.
        """
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatoInvalidoError("El identificador de la entidad debe ser un texto no vacío.")
        # Atributos privados: solo accesibles por las propiedades de solo lectura.
        self.__identificador: str = identificador.strip()
        self.__fecha_creacion: datetime = datetime.now()

    @property
    def identificador(self) -> str:
        """Identificador único (solo lectura)."""
        return self.__identificador

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora en que se creó el objeto (solo lectura)."""
        return self.__fecha_creacion

    @abstractmethod
    def obtener_detalles(self) -> Dict[str, Any]:
        """
        Devuelve un diccionario con la información descriptiva de la entidad.
        Cada clase concreta decide qué datos expone.
        """

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.__identificador})"

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.__identificador!r}>"


# =============================================================================
# 4. CLASE Cliente (ENCAPSULACIÓN ESTRICTA)
# =============================================================================

class Cliente(EntidadBase):
    """
    Representa a un cliente de Software FJ.

    Todos sus atributos son privados y se acceden mediante `@property`.
    Cada `setter` valida el dato recibido y lanza `DatoInvalidoError` si es
    incorrecto, por lo que es imposible construir un cliente con datos
    inválidos (el constructor también usa los setters).
    """

    # Reglas de validación (constantes de clase).
    NOMBRE_MIN = 3
    NOMBRE_MAX = 60
    TELEFONO_MIN_DIGITOS = 7
    TELEFONO_MAX_DIGITOS = 10

    # Expresión regular de correo: usuario@dominio.extensión
    #  - usuario : letras, números y . _ % + -
    #  - dominio : letras, números y guiones, con subdominios opcionales
    #  - extensión: mínimo 2 letras (.com, .co, .edu.co, etc.)
    _PATRON_CORREO = re.compile(
        r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}"
    )
    # Teléfono: únicamente dígitos ASCII, entre 7 (fijo) y 10 (celular).
    _PATRON_TELEFONO = re.compile(r"[0-9]{7,10}")

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: Any) -> None:
        """
        Raises:
            DatoInvalidoError: si algún dato no supera su validación.
        """
        super().__init__(identificador)
        # Se asigna a través de los setters para forzar la validación.
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    # ---- nombre -------------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida tipo y longitud (entre NOMBRE_MIN y NOMBRE_MAX caracteres)."""
        if not isinstance(valor, str):
            raise DatoInvalidoError("El nombre del cliente debe ser un texto.")
        # Normaliza espacios repetidos o al inicio/fin.
        limpio = " ".join(valor.split())
        if not (self.NOMBRE_MIN <= len(limpio) <= self.NOMBRE_MAX):
            raise DatoInvalidoError(
                f"El nombre debe tener entre {self.NOMBRE_MIN} y {self.NOMBRE_MAX} "
                f"caracteres (recibido: {len(limpio)})."
            )
        self.__nombre = limpio

    # ---- correo -------------------------------------------------------------
    @property
    def correo(self) -> str:
        """Correo electrónico (siempre en minúsculas)."""
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato del correo mediante expresión regular."""
        if not isinstance(valor, str):
            raise DatoInvalidoError("El correo electrónico debe ser un texto.")
        limpio = valor.strip().lower()
        if not self._PATRON_CORREO.fullmatch(limpio):
            raise DatoInvalidoError(f"Formato de correo electrónico inválido: '{valor}'.")
        self.__correo = limpio

    # ---- teléfono -----------------------------------------------------------
    @property
    def telefono(self) -> str:
        """Teléfono (solo dígitos)."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: Any) -> None:
        """Valida que contenga solo dígitos y la cantidad permitida."""
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise DatoInvalidoError("El teléfono debe ser un texto o número entero.")
        limpio = str(valor).strip().replace(" ", "")
        if not self._PATRON_TELEFONO.fullmatch(limpio):
            raise DatoInvalidoError(
                f"El teléfono debe contener solo dígitos ({self.TELEFONO_MIN_DIGITOS} a "
                f"{self.TELEFONO_MAX_DIGITOS}); recibido: '{valor}'."
            )
        self.__telefono = limpio

    def obtener_detalles(self) -> Dict[str, Any]:
        """Implementación del método abstracto de `EntidadBase`."""
        return {
            "id": self.identificador,
            "tipo": "Cliente",
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono,
            "creado": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }
