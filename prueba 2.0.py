#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
 Curso: Programación (213023) - Fase 4 - UNAD
===============================================================================

Descripción general
-------------------
Aplicación de consola y escritorio (Tkinter) desarrollada con Programación
Orientada a Objetos (POO) que gestiona clientes, servicios y reservas de
la empresa "Software FJ".

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
 9. `InterfazSoftwareFJ` (interfaz gráfica aportada/mejorada por el equipo).

Ejecución
---------
    python "prueba 2.0.py"

Al iniciar se ejecuta la simulación (>=10 operaciones) y luego se abre la GUI.
"""

import logging
import math
import re
import tkinter as tk
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from tkinter import messagebox, ttk
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


# =============================================================================
# 5. SERVICIOS: CLASE ABSTRACTA Y CLASES DERIVADAS (POLIMORFISMO)
# =============================================================================

class Servicio(EntidadBase, ABC):
    """
    Clase abstracta que modela cualquier servicio ofrecido por Software FJ.

    Agrupa lo común (nombre, tarifa base, disponibilidad, reglas de ajuste de
    costos) y OBLIGA a cada servicio concreto a implementar:
      * `calcular_costo()`      -> POLIMORFISMO: cada servicio calcula distinto.
      * `validar_parametros()`  -> cada servicio valida sus propias reglas.

    SOBRECARGA DE MÉTODOS
    ---------------------
    Python no admite sobrecarga clásica (varias firmas con el mismo nombre),
    así que se emula con parámetros opcionales y `**kwargs`. Así,
    `calcular_costo(2)`, `calcular_costo(2, descuento=0.1)` o
    `calcular_costo(2, aplicar_iva=True, urgente=True)` son variantes del
    mismo método con comportamientos distintos.
    """

    # Parámetros de negocio generales (ajustables por clase o por llamada).
    IVA_GENERAL: float = 0.19          # IVA vigente en Colombia (19 %).
    RECARGO_URGENCIA: float = 0.15     # Recargo por servicio urgente (15 %).
    DESCUENTO_ALTO: float = 0.30       # Sobre este valor se emite advertencia.
    NOMBRE_MIN = 3
    NOMBRE_MAX = 80

    # Cada servicio concreto redefine estas constantes.
    UNIDAD: str = "horas"              # Unidad de duración (horas / días).
    DURACION_MIN: float = 1            # Duración mínima reservable.
    DURACION_MAX: float = 8            # Duración máxima reservable.

    def __init__(self, identificador: str, nombre: str, tarifa_base: Any) -> None:
        """
        Args:
            identificador: código único del servicio.
            nombre: nombre comercial.
            tarifa_base: valor por unidad de duración (hora o día), en COP.

        Raises:
            DatoInvalidoError: si el nombre o la tarifa son inválidos.
        """
        super().__init__(identificador)
        self.nombre = nombre            # Usa el setter (validación).
        self.tarifa_base = tarifa_base  # Usa el setter (validación).
        self._disponible: bool = True

    # ---- propiedades --------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Nombre comercial del servicio."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida que el nombre sea texto con longitud permitida."""
        if not isinstance(valor, str):
            raise DatoInvalidoError("El nombre del servicio debe ser un texto.")
        limpio = " ".join(valor.split())
        if not (self.NOMBRE_MIN <= len(limpio) <= self.NOMBRE_MAX):
            raise DatoInvalidoError(
                f"El nombre del servicio debe tener entre {self.NOMBRE_MIN} y "
                f"{self.NOMBRE_MAX} caracteres."
            )
        self._nombre = limpio

    @property
    def tarifa_base(self) -> float:
        """Tarifa por unidad de duración (hora o día)."""
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: Any) -> None:
        """
        Valida que la tarifa sea numérica, finita y mayor que cero.

        [ESTRUCTURA try/except + ENCADENAMIENTO]
        Si la conversión a número falla, se captura el error nativo
        (ValueError/TypeError) y se relanza como `DatoInvalidoError`
        conservando la causa original con `raise ... from e`.
        """
        try:
            tarifa = float(valor)
        except (TypeError, ValueError) as e:
            raise DatoInvalidoError(f"La tarifa '{valor}' no es un número válido.") from e

        if isinstance(valor, bool) or not math.isfinite(tarifa) or tarifa <= 0:
            raise DatoInvalidoError(f"La tarifa debe ser un número finito mayor que cero (recibido: {valor!r}).")
        self._tarifa_base = tarifa

    @property
    def disponible(self) -> bool:
        """Indica si el servicio puede reservarse actualmente."""
        return self._disponible

    # ---- disponibilidad -----------------------------------------------------
    def deshabilitar(self, motivo: str = "sin motivo especificado") -> None:
        """Marca el servicio como no disponible y deja una advertencia en el log."""
        self._disponible = False
        logger.warning("Servicio %s ('%s') deshabilitado. Motivo: %s", self.identificador, self.nombre, motivo)

    def habilitar(self) -> None:
        """Vuelve a poner el servicio disponible."""
        self._disponible = True
        logger.info("Servicio %s ('%s') habilitado nuevamente.", self.identificador, self.nombre)

    def verificar_disponibilidad(self) -> None:
        """
        Raises:
            ServicioNoDisponibleError: si el servicio está deshabilitado.
        """
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio {self.identificador} ('{self.nombre}') no está disponible."
            )

    # ---- utilidades de cálculo compartidas ----------------------------------
    @staticmethod
    def _validar_fraccion(nombre: str, valor: Any) -> float:
        """
        Valida que `valor` sea un número entre 0 y 1 (porcentaje en fracción).

        Raises:
            DatoInvalidoError: si no es numérico o está fuera de [0, 1].
        """
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"'{nombre}' debe ser numérico (recibido: {valor!r}).")
        if not math.isfinite(valor) or not 0.0 <= valor <= 1.0:
            raise DatoInvalidoError(f"'{nombre}' debe estar entre 0 y 1 (recibido: {valor}).")
        return float(valor)

    def _normalizar_duracion(self, duracion: Any) -> float:
        """
        Convierte la duración a número positivo para poder calcular costos.

        Raises:
            DatoInvalidoError: si no es un número finito mayor que cero.
        """
        try:
            valor = float(duracion)
        except (TypeError, ValueError) as e:
            raise DatoInvalidoError(f"La duración '{duracion}' no es numérica.") from e
        if isinstance(duracion, bool) or not math.isfinite(valor) or valor <= 0:
            raise DatoInvalidoError(f"La duración debe ser mayor que cero (recibido: {duracion!r}).")
        return valor

    def _aplicar_ajustes(self, subtotal: float, descuento: Any = 0.0, aplicar_iva: Any = False,
                         urgente: Any = False, **extras: Any) -> float:
        """
        Aplica, en este orden, los ajustes opcionales al subtotal:

            1) Recargo por urgencia  (subtotal + 15 %)
            2) Descuento             (resta el porcentaje indicado)
            3) IVA                   (suma 19 %)

        Opciones extra admitidas vía `**extras` (sobrecarga flexible):
            * tasa_iva (float 0-1)          -> reemplaza el IVA general.
            * recargo_urgencia (float 0-1)  -> reemplaza el recargo estándar.

        Returns:
            float: costo final redondeado a 2 decimales.

        Raises:
            DatoInvalidoError: opciones mal formadas o no soportadas.
            CalculoInconsistenteError: si el resultado no es finito o es <= 0.
        """
        # Se extraen las opciones extra; lo que sobre es una opción desconocida.
        tasa_iva = self._validar_fraccion("tasa_iva", extras.pop("tasa_iva", self.IVA_GENERAL))
        recargo = self._validar_fraccion("recargo_urgencia", extras.pop("recargo_urgencia", self.RECARGO_URGENCIA))
        if extras:
            raise DatoInvalidoError(f"Opciones de cálculo no soportadas: {', '.join(sorted(extras))}.")

        descuento = self._validar_fraccion("descuento", descuento)
        if not isinstance(aplicar_iva, bool) or not isinstance(urgente, bool):
            raise DatoInvalidoError("'aplicar_iva' y 'urgente' deben ser valores booleanos.")

        if descuento > self.DESCUENTO_ALTO:
            logger.warning("Descuento elevado solicitado (%.0f%%) en el servicio %s.", descuento * 100, self.identificador)

        total = subtotal
        if urgente:
            total += total * recargo          # 1) recargo por urgencia
        if descuento > 0:
            total -= total * descuento        # 2) descuento
        if aplicar_iva:
            total += total * tasa_iva         # 3) impuesto
        total = round(total, 2)

        logger.debug("Cálculo %s: subtotal=%.2f urgente=%s descuento=%.2f iva=%s -> total=%.2f",
                     self.identificador, subtotal, urgente, descuento, aplicar_iva, total)

        # Verificación de coherencia del resultado.
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(
                f"El cálculo del servicio {self.identificador} produjo un costo incoherente ({total}). "
                "Revise descuentos y recargos aplicados."
            )
        return total

    # ---- métodos abstractos (contrato para las clases derivadas) ------------
    @abstractmethod
    def calcular_costo(self, duracion: Any, descuento: Any = 0.0, aplicar_iva: Any = False,
                       urgente: Any = False, **kwargs: Any) -> float:
        """
        Calcula el costo total del servicio para una duración dada.
        Cada servicio define su propia fórmula (polimorfismo).
        """

    @abstractmethod
    def validar_parametros(self) -> None:
        """
        Valida los parámetros específicos del servicio concreto.

        Raises:
            DatoInvalidoError: si algún parámetro incumple las reglas.
        """

    # ---- implementación común de EntidadBase --------------------------------
    def obtener_detalles(self) -> Dict[str, Any]:
        """Datos comunes a todos los servicios; las derivadas añaden los suyos."""
        return {
            "id": self.identificador,
            "tipo": type(self).__name__,
            "nombre": self.nombre,
            "tarifa_base": self.tarifa_base,
            "unidad": self.UNIDAD,
            "duracion_permitida": f"{self.DURACION_MIN:g} a {self.DURACION_MAX:g} {self.UNIDAD}",
            "disponible": self.disponible,
            "creado": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }


# -----------------------------------------------------------------------------
# 5.1 ReservaSala
# -----------------------------------------------------------------------------
class ReservaSala(Servicio):
    """
    Alquiler de una sala de reuniones.

    Cobro: tarifa por hora x horas (+ cargo por hora si incluye proyector).
    """

    UNIDAD = "horas"
    DURACION_MIN = 1
    DURACION_MAX = 12
    CAPACIDAD_MIN = 1
    CAPACIDAD_MAX = 200
    CARGO_PROYECTOR_POR_HORA = 15000.0  # COP por hora cuando se solicita proyector.

    def __init__(self, identificador: str, nombre: str, tarifa_hora: Any, capacidad: Any,
                 proyector: Any = False) -> None:
        """
        Args:
            tarifa_hora: costo por hora de la sala.
            capacidad: número máximo de personas.
            proyector: True si se incluye proyector (opcional, por defecto False).
        """
        super().__init__(identificador, nombre, tarifa_hora)
        self._capacidad = capacidad
        self._proyector = proyector
        self.validar_parametros()  # Garantiza que no exista una sala inválida.

    @property
    def capacidad(self) -> int:
        """Capacidad máxima de personas."""
        return self._capacidad

    @property
    def proyector(self) -> bool:
        """Indica si la sala incluye proyector."""
        return self._proyector

    def validar_parametros(self) -> None:
        """Valida capacidad (entero en rango) y bandera de proyector (booleano)."""
        if isinstance(self._capacidad, bool) or not isinstance(self._capacidad, int):
            raise DatoInvalidoError(f"La capacidad debe ser un entero (recibido: {self._capacidad!r}).")
        if not (self.CAPACIDAD_MIN <= self._capacidad <= self.CAPACIDAD_MAX):
            raise DatoInvalidoError(
                f"La capacidad debe estar entre {self.CAPACIDAD_MIN} y {self.CAPACIDAD_MAX} "
                f"personas (recibido: {self._capacidad})."
            )
        if not isinstance(self._proyector, bool):
            raise DatoInvalidoError("El campo 'proyector' debe ser verdadero o falso.")

    def calcular_costo(self, duracion: Any, descuento: Any = 0.0, aplicar_iva: Any = False,
                       urgente: Any = False, **kwargs: Any) -> float:
        """
        Costo = (tarifa_hora [+ proyector]) x horas, con ajustes opcionales.

        Variantes (sobrecarga mediante parámetros opcionales):
            calcular_costo(3)
            calcular_costo(3, descuento=0.10)
            calcular_costo(3, aplicar_iva=True, urgente=True)
        """
        horas = self._normalizar_duracion(duracion)
        tarifa_efectiva = self.tarifa_base + (self.CARGO_PROYECTOR_POR_HORA if self._proyector else 0.0)
        subtotal = tarifa_efectiva * horas
        return self._aplicar_ajustes(subtotal, descuento, aplicar_iva, urgente, **kwargs)

    def obtener_detalles(self) -> Dict[str, Any]:
        detalles = super().obtener_detalles()
        detalles.update({"capacidad": self.capacidad, "proyector": self.proyector})
        return detalles


# -----------------------------------------------------------------------------
# 5.2 AlquilerEquipo
# -----------------------------------------------------------------------------
class AlquilerEquipo(Servicio):
    """
    Alquiler de equipos tecnológicos.

    Cobro: tarifa por día x días + SEGURO OBLIGATORIO (8 % del subtotal).
    El seguro no es negociable: si el cliente no lo acepta, el servicio es inválido.
    """

    UNIDAD = "días"
    DURACION_MIN = 1
    DURACION_MAX = 30
    TASA_SEGURO = 0.08  # 8 % del subtotal, siempre aplicado.

    def __init__(self, identificador: str, nombre: str, tarifa_dia: Any, acepta_seguro: Any = True) -> None:
        """
        Args:
            tarifa_dia: costo por día del equipo.
            acepta_seguro: el seguro es obligatorio; debe ser True.
        """
        super().__init__(identificador, nombre, tarifa_dia)
        self._acepta_seguro = acepta_seguro
        self.validar_parametros()

    def validar_parametros(self) -> None:
        """Verifica que el seguro obligatorio haya sido aceptado."""
        if self._acepta_seguro is not True:
            raise DatoInvalidoError("El seguro es obligatorio en el alquiler de equipos y no puede omitirse.")

    def calcular_costo(self, duracion: Any, descuento: Any = 0.0, aplicar_iva: Any = False,
                       urgente: Any = False, **kwargs: Any) -> float:
        """
        Costo = (tarifa_dia x días) + seguro (8 %), con ajustes opcionales.
        El seguro se incluye ANTES de aplicar urgencia, descuento e IVA.
        """
        dias = self._normalizar_duracion(duracion)
        alquiler = self.tarifa_base * dias
        seguro = alquiler * self.TASA_SEGURO
        return self._aplicar_ajustes(alquiler + seguro, descuento, aplicar_iva, urgente, **kwargs)

    def obtener_detalles(self) -> Dict[str, Any]:
        detalles = super().obtener_detalles()
        detalles.update({"seguro_obligatorio": True, "tasa_seguro": f"{self.TASA_SEGURO:.0%}"})
        return detalles


# -----------------------------------------------------------------------------
# 5.3 AsesoriaEspecializada
# -----------------------------------------------------------------------------
class AsesoriaEspecializada(Servicio):
    """
    Asesoría técnica prestada por un consultor.

    Cobro: tarifa por hora x horas x multiplicador del nivel del consultor.
    """

    UNIDAD = "horas"
    DURACION_MIN = 1
    DURACION_MAX = 8
    #: Multiplicador de tarifa según experiencia del consultor.
    NIVELES: Dict[str, float] = {
        "JUNIOR": 1.0,
        "SEMISENIOR": 1.4,
        "SENIOR": 1.8,
        "EXPERTO": 2.5,
    }

    def __init__(self, identificador: str, nombre: str, tarifa_hora: Any, nivel_consultor: Any) -> None:
        """
        Args:
            tarifa_hora: tarifa base por hora.
            nivel_consultor: JUNIOR, SEMISENIOR, SENIOR o EXPERTO.
        """
        super().__init__(identificador, nombre, tarifa_hora)
        self._nivel_consultor = nivel_consultor
        self.validar_parametros()
        # Se normaliza el nivel (ya validado) a mayúsculas.
        self._nivel_consultor = str(nivel_consultor).strip().upper()

    @property
    def nivel_consultor(self) -> str:
        """Nivel del consultor asignado."""
        return self._nivel_consultor

    @property
    def multiplicador(self) -> float:
        """Multiplicador de tarifa correspondiente al nivel."""
        return self.NIVELES[self._nivel_consultor]

    def validar_parametros(self) -> None:
        """Verifica que el nivel del consultor exista en la tabla de niveles."""
        nivel = str(self._nivel_consultor).strip().upper()
        if nivel not in self.NIVELES:
            raise DatoInvalidoError(
                f"Nivel de consultor '{self._nivel_consultor}' inválido. "
                f"Niveles permitidos: {', '.join(self.NIVELES)}."
            )

    def calcular_costo(self, duracion: Any, descuento: Any = 0.0, aplicar_iva: Any = False,
                       urgente: Any = False, **kwargs: Any) -> float:
        """Costo = tarifa_hora x horas x multiplicador, con ajustes opcionales."""
        horas = self._normalizar_duracion(duracion)
        subtotal = self.tarifa_base * horas * self.multiplicador
        return self._aplicar_ajustes(subtotal, descuento, aplicar_iva, urgente, **kwargs)

    def obtener_detalles(self) -> Dict[str, Any]:
        detalles = super().obtener_detalles()
        detalles.update({"nivel_consultor": self.nivel_consultor, "multiplicador": self.multiplicador})
        return detalles


# =============================================================================
# 6. RESERVAS
# =============================================================================

class EstadoReserva(Enum):
    """
    Máquina de estados de una reserva.

    Transiciones permitidas:
      - PENDIENTE  -> CONFIRMADA (solo si ya se calculó el costo)
      - PENDIENTE  -> CANCELADA
      - CONFIRMADA -> CANCELADA
      - CANCELADA  es estado final (no admite nuevas transiciones)
    """
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


def formatear_moneda(valor: Optional[float]) -> str:
    """Da formato legible a un valor en pesos colombianos (COP)."""
    if valor is None:
        return "N/A (sin procesar)"
    return f"${valor:,.2f} COP"


class Reserva(EntidadBase):
    """
    Reserva de un `Servicio` por parte de un `Cliente`.

    Ciclo de vida (máquina de estados):

        PENDIENTE --confirmar()--> CONFIRMADA
        PENDIENTE --cancelar()---> CANCELADA
        CONFIRMADA --cancelar()--> CANCELADA
        CANCELADA  (estado final: no admite más transiciones)
    """

    #: Transiciones permitidas entre estados.
    _TRANSICIONES: Dict[EstadoReserva, set] = {
        EstadoReserva.PENDIENTE: {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA},
        EstadoReserva.CONFIRMADA: {EstadoReserva.CANCELADA},
        EstadoReserva.CANCELADA: set(),
    }

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio, duracion: Any) -> None:
        """
        Args:
            cliente: cliente que reserva.
            servicio: servicio reservado.
            duracion: horas o días según el servicio.

        Raises:
            ReservaInvalidaError: tipos incorrectos o duración fuera de rango.
            ServicioNoDisponibleError: el servicio está deshabilitado.
        """
        super().__init__(identificador)

        # Validación de los objetos asociados.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un objeto Servicio válido.")
        servicio.verificar_disponibilidad()  # Puede lanzar ServicioNoDisponibleError.

        self._cliente: Cliente = cliente
        self._servicio: Servicio = servicio
        self._duracion: float = self._validar_duracion(servicio, duracion)
        self._estado: EstadoReserva = EstadoReserva.PENDIENTE
        self._costo_total: Optional[float] = None   # Se define al procesar.
        self._opciones_costo: Dict[str, Any] = {}
        self._motivo_cancelacion: Optional[str] = None

    # ---- propiedades de solo lectura ----------------------------------------
    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> Optional[float]:
        """Costo calculado (None mientras la reserva no se haya procesado)."""
        return self._costo_total

    # ---- validaciones internas ----------------------------------------------
    @staticmethod
    def _validar_duracion(servicio: Servicio, duracion: Any) -> float:
        """
        Verifica que la duración sea numérica y esté en el rango permitido
        por el servicio.

        Raises:
            ReservaInvalidaError: duración no numérica o fuera de rango.
        """
        # [try/except + encadenamiento] conversión segura a número.
        try:
            valor = float(duracion)
        except (TypeError, ValueError) as e:
            raise ReservaInvalidaError(f"La duración '{duracion}' no es un valor numérico.") from e

        if isinstance(duracion, bool) or not math.isfinite(valor):
            raise ReservaInvalidaError(f"La duración '{duracion}' no es válida.")
        if not (servicio.DURACION_MIN <= valor <= servicio.DURACION_MAX):
            raise ReservaInvalidaError(
                f"Duración de {valor:g} {servicio.UNIDAD} fuera del rango permitido "
                f"({servicio.DURACION_MIN:g} a {servicio.DURACION_MAX:g} {servicio.UNIDAD}) "
                f"para '{servicio.nombre}'."
            )
        return valor

    def _validar_transicion(self, destino: EstadoReserva) -> None:
        """
        Comprueba si el cambio de estado actual -> destino está permitido.

        Raises:
            ReservaInvalidaError: operación duplicada o transición no permitida.
        """
        if destino in self._TRANSICIONES[self._estado]:
            return
        if destino is self._estado:
            raise ReservaInvalidaError(
                f"Operación duplicada: la reserva {self.identificador} ya está {destino.value}."
            )
        raise ReservaInvalidaError(
            f"Transición no permitida en la reserva {self.identificador}: "
            f"{self._estado.value} -> {destino.value}."
        )

    # ---- operaciones del ciclo de vida --------------------------------------
    def procesar(self, **opciones_costo: Any) -> float:
        """
        Calcula el costo de la reserva delegando en el servicio (polimorfismo).

        Las opciones se reenvían a `Servicio.calcular_costo()`:
            descuento (0-1), aplicar_iva (bool), urgente (bool),
            tasa_iva, recargo_urgencia.

        [ESTRUCTURA try/except/else/finally COMPLETA]
          - try     : reglas previas + cálculo del costo.
          - except  : traduce/relanza errores (con `raise ... from e`).
          - else    : solo si NO hubo errores, guarda el costo.
          - finally : siempre deja constancia de que el proceso terminó.

        Returns:
            float: costo total calculado.

        Raises:
            ReservaInvalidaError: estado incorrecto u opciones de costo inválidas.
            ServicioNoDisponibleError: el servicio ya no está disponible.
            CalculoInconsistenteError: costo incoherente.
        """
        try:
            if self._estado is not EstadoReserva.PENDIENTE:
                raise ReservaInvalidaError(
                    f"La reserva {self.identificador} está {self._estado.value}; "
                    "solo pueden procesarse reservas PENDIENTES."
                )
            self._servicio.verificar_disponibilidad()
            costo = self._servicio.calcular_costo(self._duracion, **opciones_costo)
        except DatoInvalidoError as e:
            # Encadenamiento: el dato inválido es la causa de la reserva inválida.
            logger.error("Opciones de costo inválidas en %s: %s", self.identificador, e)
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva {self.identificador}: opciones de costo inválidas ({e})."
            ) from e
        except CalculoInconsistenteError as e:
            logger.error("Cálculo inconsistente en %s: %s", self.identificador, e)
            raise  # Se propaga tal cual: ya es un error propio y descriptivo.
        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            logger.warning("No se pudo procesar %s: %s", self.identificador, e)
            raise
        except (ArithmeticError, ValueError, TypeError) as e:
            # Cualquier fallo matemático inesperado se traduce al dominio.
            logger.error("Fallo aritmético inesperado en %s: %s", self.identificador, e)
            raise CalculoInconsistenteError(
                f"Fallo inesperado calculando la reserva {self.identificador}: {e}"
            ) from e
        else:
            # Solo se ejecuta si el try terminó sin excepciones.
            self._costo_total = costo
            self._opciones_costo = dict(opciones_costo)
            logger.info("Reserva %s procesada. Costo total: %s | opciones=%s",
                        self.identificador, formatear_moneda(costo), opciones_costo or "ninguna")
            return costo
        finally:
            # Se ejecuta SIEMPRE (con o sin error).
            logger.debug("Fin del procesamiento de la reserva %s (estado=%s)",
                         self.identificador, self._estado.value)

    def confirmar(self) -> None:
        """
        Confirma la reserva (PENDIENTE -> CONFIRMADA).

        Requiere que la reserva haya sido procesada (costo calculado) y que el
        servicio siga disponible.

        [ESTRUCTURA try/except/else]
          - try    : valida transición, costo calculado y disponibilidad.
          - except : registra la advertencia y relanza la excepción original.
          - else   : cambia el estado únicamente si todo salió bien.

        Raises:
            ReservaInvalidaError: confirmación duplicada, reserva cancelada o sin procesar.
            ServicioNoDisponibleError: el servicio fue deshabilitado.
        """
        try:
            self._validar_transicion(EstadoReserva.CONFIRMADA)
            if self._costo_total is None:
                raise ReservaInvalidaError(
                    f"La reserva {self.identificador} debe procesarse (calcular costo) antes de confirmarse."
                )
            self._servicio.verificar_disponibilidad()
        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            logger.warning("Confirmación rechazada para %s: %s", self.identificador, e)
            raise
        else:
            self._estado = EstadoReserva.CONFIRMADA
            logger.info("Reserva %s CONFIRMADA (cliente=%s, servicio=%s).",
                        self.identificador, self._cliente.nombre, self._servicio.nombre)

    def cancelar(self, motivo: str = "sin motivo especificado") -> None:
        """
        Cancela la reserva (desde PENDIENTE o CONFIRMADA).

        Raises:
            ReservaInvalidaError: si ya estaba cancelada.
        """
        try:
            self._validar_transicion(EstadoReserva.CANCELADA)
        except ReservaInvalidaError as e:
            logger.warning("Cancelación rechazada para %s: %s", self.identificador, e)
            raise
        self._estado = EstadoReserva.CANCELADA
        self._motivo_cancelacion = motivo
        logger.info("Reserva %s CANCELADA. Motivo: %s", self.identificador, motivo)

    def obtener_detalles(self) -> Dict[str, Any]:
        """Implementación del método abstracto de `EntidadBase`."""
        return {
            "id": self.identificador,
            "tipo": "Reserva",
            "cliente": f"{self._cliente.identificador} - {self._cliente.nombre}",
            "servicio": f"{self._servicio.identificador} - {self._servicio.nombre}",
            "duracion": f"{self._duracion:g} {self._servicio.UNIDAD}",
            "estado": self._estado.value,
            "costo_total": self._costo_total,
            "motivo_cancelacion": self._motivo_cancelacion,
            "creado": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }


# =============================================================================
# 7. GESTOR: ALMACENAMIENTO EN MEMORIA Y ORQUESTACIÓN
# =============================================================================

class GestorFJ:
    """
    Núcleo del sistema: administra clientes, servicios y reservas.

    RESTRICCIÓN: no hay base de datos ni archivos de datos. Todo se guarda en
    listas internas que viven mientras el programa esté en ejecución.
    """

    #: Catálogo de tipos de servicio que se pueden crear por nombre.
    _TIPOS_SERVICIO: Dict[str, type] = {
        "SALA": ReservaSala,
        "EQUIPO": AlquilerEquipo,
        "ASESORIA": AsesoriaEspecializada,
    }

    def __init__(self) -> None:
        # Almacenamiento EXCLUSIVAMENTE en memoria.
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        # Contadores para generar identificadores consecutivos (solo si hay éxito).
        self._contadores: Dict[str, int] = {"CLI": 0, "SRV": 0, "RES": 0}
        # Contadores de auditoría (se actualizan en bloques `finally`).
        self.intentos_registro_cliente = 0
        self.intentos_reserva = 0
        logger.info("Gestor de Software FJ inicializado (almacenamiento en memoria).")

    # ---- consulta (copias inmutables para proteger el estado interno) -------
    @property
    def clientes(self) -> Tuple[Cliente, ...]:
        return tuple(self._clientes)

    @property
    def servicios(self) -> Tuple[Servicio, ...]:
        return tuple(self._servicios)

    @property
    def reservas(self) -> Tuple[Reserva, ...]:
        return tuple(self._reservas)

    # ---- utilidades internas -------------------------------------------------
    def _proponer_id(self, prefijo: str) -> str:
        """Genera el siguiente identificador (p. ej. CLI-001) sin consumirlo aún."""
        return f"{prefijo}-{self._contadores[prefijo] + 1:03d}"

    def _verificar_correo_no_duplicado(self, correo: Any) -> None:
        """
        Raises:
            DatoInvalidoError: si ya existe un cliente con ese correo.
        """
        candidato = str(correo).strip().lower()
        if any(c.correo == candidato for c in self._clientes):
            raise DatoInvalidoError(f"Ya existe un cliente registrado con el correo '{candidato}'.")

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        """Busca un cliente por id. Lanza DatoInvalidoError si no existe."""
        for cliente in self._clientes:
            if cliente.identificador == id_cliente:
                return cliente
        raise DatoInvalidoError(f"No existe un cliente con id '{id_cliente}'.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        """Busca un servicio por id. Lanza DatoInvalidoError si no existe."""
        for servicio in self._servicios:
            if servicio.identificador == id_servicio:
                return servicio
        raise DatoInvalidoError(f"No existe un servicio con id '{id_servicio}'.")

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        """Busca una reserva por id. Lanza DatoInvalidoError si no existe."""
        for reserva in self._reservas:
            if reserva.identificador == id_reserva:
                return reserva
        raise DatoInvalidoError(f"No existe una reserva con id '{id_reserva}'.")

    # ---- clientes ------------------------------------------------------------
    def registrar_cliente(self, nombre: str, correo: str, telefono: Any) -> Cliente:
        """
        Registra un nuevo cliente en memoria.

        [ESTRUCTURA try/except/else/finally]
          - except : registra el error en el log y lo relanza.
          - else   : solo guarda el cliente si fue creado correctamente.
          - finally: contabiliza SIEMPRE el intento (auditoría).

        Raises:
            DatoInvalidoError: datos inválidos o correo duplicado.
        """
        try:
            self._verificar_correo_no_duplicado(correo)
            cliente = Cliente(self._proponer_id("CLI"), nombre, correo, telefono)
        except SoftwareFJException as e:
            logger.error("Registro de cliente rechazado (%s): %s", type(e).__name__, e)
            raise
        else:
            self._clientes.append(cliente)
            self._contadores["CLI"] += 1
            logger.info("Cliente registrado: %s | %s | %s", cliente.identificador, cliente.nombre, cliente.correo)
            return cliente
        finally:
            self.intentos_registro_cliente += 1

    # ---- servicios -----------------------------------------------------------
    def crear_servicio(self, tipo: str, **parametros: Any) -> Servicio:
        """
        Crea un servicio de alguno de los tipos soportados (SALA, EQUIPO, ASESORIA).

        Raises:
            DatoInvalidoError: tipo desconocido, parámetros incompletos o inválidos.
        """
        try:
            clave = str(tipo).strip().upper()
            clase = self._TIPOS_SERVICIO.get(clave)
            if clase is None:
                raise DatoInvalidoError(
                    f"Tipo de servicio '{tipo}' no soportado. Tipos válidos: {', '.join(self._TIPOS_SERVICIO)}."
                )
            try:
                servicio = clase(self._proponer_id("SRV"), **parametros)
            except TypeError as e:
                # Faltan argumentos o se enviaron argumentos no reconocidos.
                raise DatoInvalidoError(
                    f"Parámetros incompletos o no reconocidos para el servicio '{clave}': {e}"
                ) from e
        except SoftwareFJException as e:
            logger.error("Creación de servicio rechazada (%s): %s", type(e).__name__, e)
            raise
        else:
            self._servicios.append(servicio)
            self._contadores["SRV"] += 1
            logger.info("Servicio creado: %s | %s | tarifa base %s por %s",
                        servicio.identificador, servicio.nombre,
                        formatear_moneda(servicio.tarifa_base), servicio.UNIDAD.rstrip("s"))
            return servicio

    def deshabilitar_servicio(self, id_servicio: str, motivo: str) -> Servicio:
        """Marca un servicio como no disponible."""
        servicio = self.buscar_servicio(id_servicio)
        servicio.deshabilitar(motivo)
        return servicio

    # ---- reservas ------------------------------------------------------------
    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion: Any) -> Reserva:
        """
        Crea una reserva PENDIENTE.

        [ESTRUCTURA try/except/else/finally]
          - finally: contabiliza SIEMPRE el intento de reserva.

        Raises:
            ReservaInvalidaError: cliente/servicio inexistente o duración inválida.
            ServicioNoDisponibleError: el servicio está deshabilitado.
        """
        try:
            try:
                cliente = self.buscar_cliente(id_cliente)
                servicio = self.buscar_servicio(id_servicio)
            except DatoInvalidoError as e:
                # Se eleva al nivel de dominio de reservas conservando la causa.
                raise ReservaInvalidaError(f"No se puede crear la reserva: {e}") from e
            reserva = Reserva(self._proponer_id("RES"), cliente, servicio, duracion)
        except SoftwareFJException as e:
            logger.warning("Creación de reserva rechazada (%s): %s", type(e).__name__, e)
            raise
        else:
            self._reservas.append(reserva)
            self._contadores["RES"] += 1
            logger.info("Reserva creada: %s | cliente=%s | servicio=%s | duración=%g %s",
                        reserva.identificador, cliente.nombre, servicio.nombre,
                        reserva.duracion, servicio.UNIDAD)
            return reserva
        finally:
            self.intentos_reserva += 1

    def procesar_reserva(self, id_reserva: str, **opciones_costo: Any) -> float:
        """Calcula el costo de una reserva (ver `Reserva.procesar`)."""
        return self.buscar_reserva(id_reserva).procesar(**opciones_costo)

    def confirmar_reserva(self, id_reserva: str) -> Reserva:
        """Confirma una reserva ya procesada."""
        reserva = self.buscar_reserva(id_reserva)
        reserva.confirmar()
        return reserva

    def cancelar_reserva(self, id_reserva: str, motivo: str = "sin motivo especificado") -> Reserva:
        """Cancela una reserva."""
        reserva = self.buscar_reserva(id_reserva)
        reserva.cancelar(motivo)
        return reserva


# =============================================================================
# 8. SIMULACIÓN DE PRUEBAS
# =============================================================================

class EjecutorOperaciones:
    """
    Ejecuta operaciones de forma segura: captura CUALQUIER excepción para que
    el programa nunca se detenga, y lleva estadísticas de los resultados.

    [ESTRUCTURA try/except/else/finally]
    """

    def __init__(self) -> None:
        self.total = 0
        self.exitosas = 0
        self.rechazadas = 0     # Errores propios del sistema, capturados y controlados.
        self.inesperadas = 0    # Errores no previstos (también capturados).

    @staticmethod
    def _causa(error: BaseException) -> str:
        """Devuelve la causa original si la excepción fue encadenada con `from`."""
        causa = error.__cause__
        return f" | causa original: {type(causa).__name__}: {causa}" if causa else ""

    def ejecutar(self, descripcion: str, operacion: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Ejecuta `operacion(*args, **kwargs)` y devuelve su resultado, o None si falló.

        Args:
            descripcion: texto que identifica la operación en el log.
            operacion: función o método a ejecutar.
        """
        self.total += 1
        etiqueta = f"OP-{self.total:02d}"
        logger.info("[%s] Iniciando: %s", etiqueta, descripcion)
        resultado = None
        try:
            resultado = operacion(*args, **kwargs)
        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            # Reglas de negocio incumplidas -> advertencia.
            self.rechazadas += 1
            logger.warning("[%s] RECHAZADA por regla de negocio (%s, %s): %s%s",
                           etiqueta, type(e).__name__, e.codigo, e, self._causa(e))
        except SoftwareFJException as e:
            # Datos o cálculos inválidos -> error controlado.
            self.rechazadas += 1
            logger.error("[%s] ERROR CONTROLADO (%s, %s): %s%s",
                         etiqueta, type(e).__name__, e.codigo, e, self._causa(e))
        except Exception as e:  # Última línea de defensa: nada detiene el programa.
            self.inesperadas += 1
            logger.exception("[%s] ERROR INESPERADO capturado (%s): %s", etiqueta, type(e).__name__, e)
        else:
            self.exitosas += 1
            logger.info("[%s] OK", etiqueta)
        finally:
            logger.debug("[%s] Fin de la operación | acumulado: ok=%d rechazadas=%d inesperadas=%d",
                         etiqueta, self.exitosas, self.rechazadas, self.inesperadas)
        return resultado


def _id_de(entidad: Optional[EntidadBase]) -> str:
    """Devuelve el id de una entidad o un marcador si la operación previa falló."""
    return entidad.identificador if entidad is not None else "ID-NO-DISPONIBLE"


def _demostrar_sobrecarga_y_polimorfismo(gestor: GestorFJ) -> None:
    """
    Recorre TODOS los servicios con la misma llamada `calcular_costo()`
    (polimorfismo) y prueba sus variantes con parámetros opcionales
    (sobrecarga emulada).
    """
    variantes = [
        ("sin ajustes", {}),
        ("descuento 10%", {"descuento": 0.10}),
        ("con IVA 19%", {"aplicar_iva": True}),
        ("urgente +15%", {"urgente": True}),
        ("descuento+IVA+urgente", {"descuento": 0.10, "aplicar_iva": True, "urgente": True}),
        ("IVA personalizado 16%", {"aplicar_iva": True, "tasa_iva": 0.16}),
    ]
    for servicio in gestor.servicios:
        for nombre_variante, opciones in variantes:
            costo = servicio.calcular_costo(2, **opciones)  # 2 horas/días: válido para todos.
            logger.info("   %-22s | 2 %-5s | %-24s -> %s",
                        type(servicio).__name__, servicio.UNIDAD, nombre_variante, formatear_moneda(costo))


def ejecutar_simulacion() -> None:
    """
    Función principal de simulación: ejecuta más de 10 operaciones completas,
    mezclando escenarios VÁLIDOS e INVÁLIDOS. Cada operación pasa por
    `EjecutorOperaciones`, por lo que ningún error detiene el programa.
    """
    gestor = GestorFJ()
    ejecutor = EjecutorOperaciones()
    ejecutar = ejecutor.ejecutar

    logger.info("=" * 78)
    logger.info("INICIO DE LA SIMULACIÓN - SOFTWARE FJ")
    logger.info("=" * 78)

    # ------------------------------------------------------------------ CLIENTES
    logger.info("--- BLOQUE A: Registro de clientes (válidos e inválidos) ---")
    laura = ejecutar("Registrar cliente válido (Laura Gómez)",
                     gestor.registrar_cliente, "Laura Gómez", "laura.gomez@softwarefj.co", "3105551234")
    carlos = ejecutar("Registrar cliente válido (Carlos Ramírez)",
                      gestor.registrar_cliente, "Carlos Ramírez", "carlos.ramirez@correo.com", "3201234567")
    ejecutar("Registrar cliente con correo inválido",
             gestor.registrar_cliente, "Pedro Pérez", "pedro.perez#correo", "3001112233")
    ejecutar("Registrar cliente con nombre demasiado corto",
             gestor.registrar_cliente, "Al", "al@correo.com", "3001112233")
    ejecutar("Registrar cliente con teléfono no numérico",
             gestor.registrar_cliente, "Marta Ruiz", "marta.ruiz@correo.com", "31A-456")
    ejecutar("Registrar cliente con teléfono demasiado corto",
             gestor.registrar_cliente, "Ana Cortés", "ana.cortes@correo.com", "123")
    ejecutar("Registrar cliente con correo vacío",
             gestor.registrar_cliente, "Luis Mora", "", "3009876543")
    ejecutar("Registrar cliente con correo duplicado",
             gestor.registrar_cliente, "Laura G.", "LAURA.GOMEZ@softwarefj.co", "3105559999")

    # ----------------------------------------------------------------- SERVICIOS
    logger.info("--- BLOQUE B: Creación de servicios (válidos e inválidos) ---")
    sala = ejecutar("Crear ReservaSala válida",
                    gestor.crear_servicio, "SALA", nombre="Sala Innovación",
                    tarifa_hora=60000, capacidad=12, proyector=True)
    equipo = ejecutar("Crear AlquilerEquipo válido",
                      gestor.crear_servicio, "EQUIPO", nombre="Portátil Workstation", tarifa_dia=45000)
    asesoria = ejecutar("Crear AsesoriaEspecializada válida",
                        gestor.crear_servicio, "ASESORIA", nombre="Asesoría en Arquitectura de Software",
                        tarifa_hora=80000, nivel_consultor="SENIOR")
    ejecutar("Crear ReservaSala inválida (capacidad negativa)",
             gestor.crear_servicio, "SALA", nombre="Sala Fantasma", tarifa_hora=50000, capacidad=-5)
    ejecutar("Crear ReservaSala inválida (tarifa <= 0)",
             gestor.crear_servicio, "SALA", nombre="Sala Sin Tarifa", tarifa_hora=0, capacidad=8, proyector=False)
    ejecutar("Crear AlquilerEquipo inválido (rechaza el seguro obligatorio)",
             gestor.crear_servicio, "EQUIPO", nombre="Proyector 4K", tarifa_dia=30000, acepta_seguro=False)
    ejecutar("Crear AsesoriaEspecializada inválida (nivel inexistente)",
             gestor.crear_servicio, "ASESORIA", nombre="Asesoría Mágica", tarifa_hora=90000, nivel_consultor="GURU")
    ejecutar("Crear servicio con tipo desconocido",
             gestor.crear_servicio, "CONSULTORIA", nombre="Consultoría Genérica", tarifa_hora=50000)
    ejecutar("Crear servicio con parámetros incompletos (falta tarifa y capacidad)",
             gestor.crear_servicio, "SALA", nombre="Sala Incompleta")

    # ---------------------------------------------- POLIMORFISMO Y SOBRECARGA
    logger.info("--- BLOQUE C: Polimorfismo y sobrecarga de calcular_costo() ---")
    ejecutar("Calcular costos de todos los servicios con distintas variantes",
             _demostrar_sobrecarga_y_polimorfismo, gestor)

    # ------------------------------------------------------------------ RESERVAS
    logger.info("--- BLOQUE D: Reservas exitosas, duplicadas y fuera de rango ---")
    reserva_sala = ejecutar("Crear reserva de sala (3 horas) para Laura",
                            gestor.crear_reserva, _id_de(laura), _id_de(sala), 3)
    ejecutar("Procesar reserva de sala con descuento 10% + IVA",
             gestor.procesar_reserva, _id_de(reserva_sala), descuento=0.10, aplicar_iva=True)
    ejecutar("Confirmar reserva de sala",
             gestor.confirmar_reserva, _id_de(reserva_sala))
    ejecutar("Confirmar NUEVAMENTE la misma reserva (duplicada)",
             gestor.confirmar_reserva, _id_de(reserva_sala))

    def flujo_equipo_urgente() -> Reserva:
        """Flujo completo: crear -> procesar (urgente + descuento + IVA) -> confirmar."""
        reserva = gestor.crear_reserva(_id_de(carlos), _id_de(equipo), 5)
        gestor.procesar_reserva(reserva.identificador, descuento=0.05, aplicar_iva=True, urgente=True)
        gestor.confirmar_reserva(reserva.identificador)
        return reserva

    ejecutar("Flujo completo de alquiler de equipo (5 días, urgente, 5% desc., IVA)", flujo_equipo_urgente)
    ejecutar("Crear reserva de sala con duración fuera de rango (20 horas)",
             gestor.crear_reserva, _id_de(laura), _id_de(sala), 20)
    ejecutar("Crear reserva de asesoría con duración no numérica ('dos horas')",
             gestor.crear_reserva, _id_de(laura), _id_de(asesoria), "dos horas")
    ejecutar("Crear reserva con cliente inexistente",
             gestor.crear_reserva, "CLI-999", _id_de(sala), 2)

    # ------------------------------------------- CÁLCULOS INCONSISTENTES / ERRORES
    logger.info("--- BLOQUE E: Cálculos inválidos, inconsistentes y transiciones ---")
    reserva_asesoria = ejecutar("Crear reserva de asesoría (2 horas) para Carlos",
                                gestor.crear_reserva, _id_de(carlos), _id_de(asesoria), 2)
    ejecutar("Procesar con descuento del 100% (costo resultante inconsistente)",
             gestor.procesar_reserva, _id_de(reserva_asesoria), descuento=1.0)
    ejecutar("Procesar con descuento del 150% (dato inválido encadenado)",
             gestor.procesar_reserva, _id_de(reserva_asesoria), descuento=1.5)
    ejecutar("Procesar con opción de cálculo no soportada ('cupon')",
             gestor.procesar_reserva, _id_de(reserva_asesoria), cupon="PROMO2026")
    ejecutar("Procesar asesoría con descuento alto (35%) + IVA [válido, genera advertencia]",
             gestor.procesar_reserva, _id_de(reserva_asesoria), descuento=0.35, aplicar_iva=True)
    ejecutar("Confirmar reserva de asesoría",
             gestor.confirmar_reserva, _id_de(reserva_asesoria))

    reserva_sin_procesar = ejecutar("Crear reserva de sala (2 horas) sin procesar",
                                    gestor.crear_reserva, _id_de(carlos), _id_de(sala), 2)
    ejecutar("Confirmar reserva sin haber calculado su costo",
             gestor.confirmar_reserva, _id_de(reserva_sin_procesar))

    # ------------------------------------------------- DISPONIBILIDAD Y CANCELACIÓN
    logger.info("--- BLOQUE F: Disponibilidad y cancelaciones ---")
    ejecutar("Deshabilitar equipo por mantenimiento",
             gestor.deshabilitar_servicio, _id_de(equipo), "Mantenimiento correctivo")
    ejecutar("Reservar un equipo NO disponible",
             gestor.crear_reserva, _id_de(laura), _id_de(equipo), 2)
    ejecutar("Cancelar reserva PENDIENTE sin confirmación previa",
             gestor.cancelar_reserva, _id_de(reserva_sin_procesar), "Cliente desistió antes de confirmar")
    ejecutar("Cancelar reserva de sala ya confirmada",
             gestor.cancelar_reserva, _id_de(reserva_sala), "El cliente reprogramó su evento")
    ejecutar("Cancelar NUEVAMENTE la misma reserva (duplicada)",
             gestor.cancelar_reserva, _id_de(reserva_sala), "Intento repetido")
    ejecutar("Confirmar una reserva ya cancelada",
             gestor.confirmar_reserva, _id_de(reserva_sala))

    # ------------------------------------------------------------ RESUMEN FINAL
    _imprimir_resumen(gestor, ejecutor)


def _imprimir_resumen(gestor: GestorFJ, ejecutor: EjecutorOperaciones) -> None:
    """Registra en consola y en el log el estado final del sistema en memoria."""
    logger.info("=" * 78)
    logger.info("RESUMEN FINAL DEL SISTEMA (datos en memoria)")
    logger.info("=" * 78)
    logger.info("Clientes registrados : %d (intentos de registro: %d)",
                len(gestor.clientes), gestor.intentos_registro_cliente)
    logger.info("Servicios creados    : %d", len(gestor.servicios))
    logger.info("Reservas creadas     : %d (intentos de reserva: %d)",
                len(gestor.reservas), gestor.intentos_reserva)

    logger.info("Detalle de clientes:")
    for cliente in gestor.clientes:
        d = cliente.obtener_detalles()
        logger.info("  %s | %-24s | %-32s | %s",
                    d["id"], d["nombre"], d["correo"], d["telefono"])

    logger.info("Detalle de servicios:")
    for servicio in gestor.servicios:
        d = servicio.obtener_detalles()
        logger.info("  %s | %-22s | %-34s | %-12s | disp=%s",
                    d["id"], d.get("tipo", type(servicio).__name__), d["nombre"],
                    formatear_moneda(d.get("tarifa_base")),
                    "Sí" if d.get("disponible", servicio.disponible) else "No")

    logger.info("Detalle de reservas:")
    ingresos = 0.0
    for reserva in gestor.reservas:
        d = reserva.obtener_detalles()
        logger.info("  %s | %-10s | %-24s | %-34s | %-10s | %s",
                    d["id"], d["estado"], d["cliente"], d["servicio"], d["duracion"],
                    formatear_moneda(d["costo_total"]))
        if reserva.estado is EstadoReserva.CONFIRMADA and reserva.costo_total is not None:
            ingresos += reserva.costo_total
    logger.info("Ingresos por reservas CONFIRMADAS: %s", formatear_moneda(ingresos))

    logger.info("-" * 78)
    logger.info("Operaciones ejecutadas              : %d", ejecutor.total)
    logger.info("  Exitosas                          : %d", ejecutor.exitosas)
    logger.info("  Rechazadas/controladas            : %d", ejecutor.rechazadas)
    logger.info("  Errores inesperados (capturados)  : %d", ejecutor.inesperadas)
    logger.info("Resultado: el sistema capturó todos los errores y finalizó con estabilidad total.")
    logger.info("=" * 78)


class InterfazSoftwareFJ:
    """
    Interfaz gráfica (Tkinter) para registrar clientes, crear servicios y
    gestionar reservas sobre un `GestorFJ` en memoria.

    Aporte de interfaz del equipo (base Juan / mejora Bryan). Los datos de la
    ventana son independientes de la simulación de consola: viven solo mientras
    la GUI permanece abierta.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Construye pestañas de clientes, servicios y reservas sobre `root`."""
        self.root = root
        self.gestor = GestorFJ()
        self.root.title("Software FJ | Gestión de servicios y reservas")
        self.root.geometry("1050x700")
        self.root.minsize(850, 580)

        estilo = ttk.Style()
        if "vista" in estilo.theme_names():
            estilo.theme_use("vista")
        estilo.configure("Treeview", rowheight=27)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        encabezado = ttk.Frame(root, padding=(18, 14))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Software FJ", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(
            encabezado,
            text="Administración de clientes, servicios y reservas",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))
        ttk.Label(
            encabezado,
            text=(
                "Para empezar: registra un cliente, crea un servicio y luego una reserva. "
                "En Reservas puedes calcular el costo, confirmar o cancelar. "
                "Los datos se conservan solo durante esta ejecución."
            ),
            wraplength=950,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        self.pestanas = ttk.Notebook(root)
        self.pestanas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._crear_pestana_clientes()
        self._crear_pestana_servicios()
        self._crear_pestana_reservas()
        self._actualizar_vistas()

    def _crear_pestana_clientes(self) -> None:
        pestana = ttk.Frame(self.pestanas, padding=16)
        self.pestanas.add(pestana, text="Clientes")
        formulario = ttk.LabelFrame(pestana, text="Registrar cliente", padding=12)
        formulario.pack(fill="x", pady=(0, 14))

        self.cliente_nombre = tk.StringVar()
        self.cliente_correo = tk.StringVar()
        self.cliente_telefono = tk.StringVar()
        self._campo(formulario, "Nombre", 0, 0, self.cliente_nombre)
        self._campo(formulario, "Correo", 0, 2, self.cliente_correo)
        self._campo(formulario, "Teléfono", 1, 0, self.cliente_telefono)
        ttk.Button(formulario, text="Registrar", command=self._registrar_cliente).grid(
            row=1, column=3, padx=6, pady=5, sticky="e"
        )
        for columna in range(4):
            formulario.columnconfigure(columna, weight=1)
        self.tabla_clientes = self._crear_tabla(
            pestana,
            (("id", "ID", 100), ("nombre", "Nombre", 230), ("correo", "Correo", 260),
             ("telefono", "Teléfono", 150)),
        )

    def _crear_pestana_servicios(self) -> None:
        pestana = ttk.Frame(self.pestanas, padding=16)
        self.pestanas.add(pestana, text="Servicios")
        formulario = ttk.LabelFrame(pestana, text="Crear servicio", padding=12)
        formulario.pack(fill="x", pady=(0, 14))

        self.servicio_tipo = tk.StringVar(value="SALA")
        self.servicio_nombre = tk.StringVar()
        self.servicio_tarifa = tk.StringVar()
        self.servicio_capacidad = tk.StringVar()
        self.servicio_proyector = tk.BooleanVar(value=False)
        self.servicio_nivel = tk.StringVar(value="JUNIOR")

        ttk.Label(formulario, text="Tipo").grid(
            row=0, column=0, sticky="w", padx=6, pady=5
        )
        self.servicio_tipo_combo = ttk.Combobox(
            formulario, textvariable=self.servicio_tipo,
            values=("SALA", "EQUIPO", "ASESORIA"),
            state="readonly", width=20,
        )
        self.servicio_tipo_combo.grid(
            row=0, column=1, sticky="ew", padx=6, pady=5
        )
        self.servicio_tipo_combo.bind(
            "<<ComboboxSelected>>", self._actualizar_campos_servicio
        )
        self._campo(formulario, "Nombre", 0, 2, self.servicio_nombre)
        self.servicio_tarifa_etiqueta = tk.StringVar(value="Tarifa por hora")
        ttk.Label(formulario, textvariable=self.servicio_tarifa_etiqueta).grid(
            row=1, column=0, sticky="w", padx=6, pady=5
        )
        ttk.Entry(formulario, textvariable=self.servicio_tarifa, width=24).grid(
            row=1, column=1, sticky="ew", padx=6, pady=5
        )

        self.etiqueta_capacidad = ttk.Label(formulario, text="Capacidad (personas)")
        self.entrada_capacidad = ttk.Entry(
            formulario, textvariable=self.servicio_capacidad, width=24
        )
        self.check_proyector = ttk.Checkbutton(
            formulario, text="Incluye proyector", variable=self.servicio_proyector
        )
        self.etiqueta_nivel = ttk.Label(formulario, text="Nivel del consultor")
        self.selector_nivel = ttk.Combobox(
            formulario, textvariable=self.servicio_nivel,
            values=tuple(AsesoriaEspecializada.NIVELES),
            state="readonly", width=20,
        )
        self.etiqueta_seguro = ttk.Label(
            formulario, text="Seguro obligatorio: 8% (incluido automáticamente)."
        )
        ttk.Button(formulario, text="Crear servicio", command=self._crear_servicio).grid(
            row=2, column=3, padx=6, pady=5, sticky="e"
        )
        for columna in range(4):
            formulario.columnconfigure(columna, weight=1)
        self._actualizar_campos_servicio()
        self.tabla_servicios = self._crear_tabla(
            pestana,
            (("id", "ID", 90), ("tipo", "Tipo", 180), ("nombre", "Nombre", 250),
             ("tarifa", "Tarifa base", 140), ("unidad", "Unidad", 80),
             ("disponible", "Disponible", 100)),
        )

    def _crear_pestana_reservas(self) -> None:
        pestana = ttk.Frame(self.pestanas, padding=16)
        self.pestanas.add(pestana, text="Reservas")
        formulario = ttk.LabelFrame(pestana, text="Crear reserva", padding=12)
        formulario.pack(fill="x", pady=(0, 12))

        self.reserva_cliente = tk.StringVar()
        self.reserva_servicio = tk.StringVar()
        self.reserva_duracion = tk.StringVar()
        self.reserva_cliente_combo = ttk.Combobox(
            formulario, textvariable=self.reserva_cliente, state="readonly", width=28,
        )
        self.reserva_servicio_combo = ttk.Combobox(
            formulario, textvariable=self.reserva_servicio, state="readonly", width=28,
        )
        self.reserva_servicio_combo.bind(
            "<<ComboboxSelected>>", self._actualizar_detalles_reserva
        )
        ttk.Label(formulario, text="Cliente").grid(
            row=0, column=0, sticky="w", padx=6, pady=5
        )
        self.reserva_cliente_combo.grid(
            row=0, column=1, sticky="ew", padx=6, pady=5
        )
        ttk.Label(formulario, text="Servicio").grid(
            row=0, column=2, sticky="w", padx=6, pady=5
        )
        self.reserva_servicio_combo.grid(
            row=0, column=3, sticky="ew", padx=6, pady=5
        )
        self.reserva_duracion_etiqueta = tk.StringVar(value="Duración")
        ttk.Label(formulario, textvariable=self.reserva_duracion_etiqueta).grid(
            row=1, column=0, sticky="w", padx=6, pady=5
        )
        ttk.Entry(formulario, textvariable=self.reserva_duracion).grid(
            row=1, column=1, sticky="ew", padx=6, pady=5
        )
        ttk.Button(formulario, text="Crear reserva", command=self._crear_reserva).grid(
            row=1, column=3, padx=6, pady=5, sticky="e"
        )
        for columna in range(4):
            formulario.columnconfigure(columna, weight=1)
        self.reserva_detalles_servicio = tk.StringVar(
            value="Selecciona un servicio para consultar sus requisitos."
        )
        ttk.Label(
            formulario, textvariable=self.reserva_detalles_servicio,
            wraplength=800, justify="left",
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))

        opciones = ttk.LabelFrame(pestana, text="Procesamiento y estado", padding=10)
        opciones.pack(fill="x", pady=(0, 12))
        self.reserva_descuento = tk.StringVar(value="0")
        self.reserva_iva = tk.BooleanVar(value=False)
        self.reserva_urgente = tk.BooleanVar(value=False)
        ttk.Label(opciones, text="Descuento (%)").pack(side="left")
        ttk.Entry(opciones, textvariable=self.reserva_descuento, width=7).pack(
            side="left", padx=(6, 14)
        )
        ttk.Checkbutton(opciones, text="Aplicar IVA (19%)", variable=self.reserva_iva).pack(
            side="left", padx=5
        )
        ttk.Checkbutton(opciones, text="Urgente (+15%)", variable=self.reserva_urgente).pack(
            side="left", padx=5
        )
        ttk.Button(opciones, text="Calcular costo", command=self._procesar_reserva).pack(
            side="left", padx=(14, 4)
        )
        ttk.Button(opciones, text="Confirmar", command=self._confirmar_reserva).pack(
            side="left", padx=4
        )
        ttk.Button(opciones, text="Cancelar", command=self._cancelar_reserva).pack(
            side="left", padx=4
        )
        self.tabla_reservas = self._crear_tabla(
            pestana,
            (("id", "ID", 90), ("cliente", "Cliente", 200), ("servicio", "Servicio", 220),
             ("duracion", "Duración", 100), ("estado", "Estado", 120), ("costo", "Costo total", 150)),
        )

    def _actualizar_campos_servicio(self, _evento: Optional[Any] = None) -> None:
        """Muestra únicamente los datos específicos requeridos por el servicio."""
        self.etiqueta_capacidad.grid_remove()
        self.entrada_capacidad.grid_remove()
        self.check_proyector.grid_remove()
        self.etiqueta_nivel.grid_remove()
        self.selector_nivel.grid_remove()
        self.etiqueta_seguro.grid_remove()

        tipo = self.servicio_tipo.get()
        if tipo == "SALA":
            self.servicio_tarifa_etiqueta.set("Tarifa por hora")
            self.etiqueta_capacidad.grid(
                row=1, column=2, sticky="w", padx=6, pady=5
            )
            self.entrada_capacidad.grid(
                row=1, column=3, sticky="ew", padx=6, pady=5
            )
            self.check_proyector.grid(
                row=2, column=0, columnspan=2, sticky="w", padx=6, pady=5
            )
        elif tipo == "EQUIPO":
            self.servicio_tarifa_etiqueta.set("Tarifa por hora")
            self.etiqueta_seguro.grid(
                row=1, column=2, columnspan=2, sticky="w", padx=6, pady=5
            )
        else:
            self.servicio_tarifa_etiqueta.set("Tarifa por hora")
            self.etiqueta_nivel.grid(
                row=1, column=2, sticky="w", padx=6, pady=5
            )
            self.selector_nivel.grid(
                row=1, column=3, sticky="ew", padx=6, pady=5
            )

    def _servicio_reserva_seleccionado(self) -> Optional[Servicio]:
        identificador = self.reserva_servicio.get().split(" - ", 1)[0]
        return next(
            (servicio for servicio in self.gestor.servicios
             if servicio.identificador == identificador),
            None,
        )

    def _actualizar_detalles_reserva(self, _evento: Optional[Any] = None) -> None:
        """Actualiza unidad, rango y datos del servicio seleccionado."""
        servicio = self._servicio_reserva_seleccionado()
        if servicio is None:
            self.reserva_duracion_etiqueta.set("Duración")
            self.reserva_detalles_servicio.set(
                "Selecciona un servicio para consultar sus requisitos."
            )
            return

        self.reserva_duracion_etiqueta.set(f"Duración ({servicio.UNIDAD})")
        detalles = (
            f"Duración permitida: {servicio.DURACION_MIN:g} a "
            f"{servicio.DURACION_MAX:g} {servicio.UNIDAD}."
        )
        if isinstance(servicio, ReservaSala):
            especificos = (
                f"Capacidad: {servicio.capacidad} personas. "
                f"Proyector: {'incluido' if servicio.proyector else 'no incluido'}."
            )
        elif isinstance(servicio, AlquilerEquipo):
            especificos = (
                f"Seguro obligatorio incluido: {servicio.TASA_SEGURO:.0%}."
            )
        elif isinstance(servicio, AsesoriaEspecializada):
            especificos = (
                f"Nivel del consultor: {servicio.nivel_consultor} "
                f"(multiplicador {servicio.multiplicador:g}x)."
            )
        else:
            especificos = ""
        self.reserva_detalles_servicio.set(f"{detalles} {especificos}".strip())

    @staticmethod
    def _campo(
        contenedor: ttk.Frame, etiqueta: str, fila: int, columna: int,
        variable: tk.StringVar,
    ) -> ttk.Entry:
        ttk.Label(contenedor, text=etiqueta).grid(
            row=fila, column=columna, sticky="w", padx=6, pady=5
        )
        entrada = ttk.Entry(contenedor, textvariable=variable, width=24)
        entrada.grid(
            row=fila, column=columna + 1, sticky="ew", padx=6, pady=5
        )
        return entrada

    @staticmethod
    def _agregar_campo(
        contenedor: ttk.Frame, etiqueta: str, entrada: ttk.Widget, columna: int
    ) -> None:
        ttk.Label(contenedor, text=etiqueta).grid(
            row=0, column=columna, sticky="w", padx=(0, 8)
        )
        entrada.grid(
            row=1, column=columna, sticky="ew", padx=(0, 8), pady=(4, 0)
        )

    @staticmethod
    def _crear_tabla(
        contenedor: ttk.Frame, columnas: Tuple[Tuple[str, str, int], ...]
    ) -> ttk.Treeview:
        tabla = ttk.Treeview(
            contenedor,
            columns=tuple(columna[0] for columna in columnas),
            show="headings",
            height=14,
        )
        for identificador, titulo, ancho in columnas:
            tabla.heading(identificador, text=titulo)
            tabla.column(identificador, width=ancho, minwidth=70, anchor="w")
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    @staticmethod
    def _limpiar_tabla(tabla: ttk.Treeview) -> None:
        tabla.delete(*tabla.get_children())

    def _actualizar_vistas(self) -> None:
        reservas_seleccionadas = self.tabla_reservas.selection()
        self._limpiar_tabla(self.tabla_clientes)
        for cliente in self.gestor.clientes:
            self.tabla_clientes.insert(
                "", "end", iid=cliente.identificador,
                values=(cliente.identificador, cliente.nombre, cliente.correo, cliente.telefono),
            )

        self._limpiar_tabla(self.tabla_servicios)
        for servicio in self.gestor.servicios:
            self.tabla_servicios.insert(
                "", "end", iid=servicio.identificador,
                values=(
                    servicio.identificador, type(servicio).__name__, servicio.nombre,
                    formatear_moneda(servicio.tarifa_base), servicio.UNIDAD,
                    "Sí" if servicio.disponible else "No",
                ),
            )

        self._limpiar_tabla(self.tabla_reservas)
        for reserva in self.gestor.reservas:
            self.tabla_reservas.insert(
                "", "end", iid=reserva.identificador,
                values=(
                    reserva.identificador, reserva.cliente.nombre, reserva.servicio.nombre,
                    f"{reserva.duracion:g} {reserva.servicio.UNIDAD}", reserva.estado.value,
                    formatear_moneda(reserva.costo_total),
                ),
            )
        if reservas_seleccionadas and self.tabla_reservas.exists(reservas_seleccionadas[0]):
            self.tabla_reservas.selection_set(reservas_seleccionadas[0])

        clientes = [f"{c.identificador} - {c.nombre}" for c in self.gestor.clientes]
        servicios = [
            f"{s.identificador} - {s.nombre} ({s.UNIDAD})"
            for s in self.gestor.servicios if s.disponible
        ]
        if hasattr(self, "reserva_cliente_combo"):
            self.reserva_cliente_combo.configure(values=clientes)
            self.reserva_servicio_combo.configure(values=servicios)
            if self.reserva_servicio.get() not in servicios:
                self.reserva_servicio.set("")
            self._actualizar_detalles_reserva()

    def _registrar_cliente(self) -> None:
        try:
            self.gestor.registrar_cliente(
                self.cliente_nombre.get(), self.cliente_correo.get(), self.cliente_telefono.get()
            )
        except SoftwareFJException as error:
            messagebox.showerror("No se pudo registrar el cliente", str(error), parent=self.root)
            return
        self.cliente_nombre.set("")
        self.cliente_correo.set("")
        self.cliente_telefono.set("")
        self._actualizar_vistas()
        messagebox.showinfo("Cliente registrado", "El cliente se registró correctamente.", parent=self.root)

    def _crear_servicio(self) -> None:
        try:
            tipo = self.servicio_tipo.get()
            parametros: Dict[str, Any] = {
                "nombre": self.servicio_nombre.get(),
            }
            tarifa = float(self.servicio_tarifa.get())
            if tipo == "SALA":
                parametros.update(
                    tarifa_hora=tarifa,
                    capacidad=int(self.servicio_capacidad.get()),
                    proyector=self.servicio_proyector.get(),
                )
            elif tipo == "EQUIPO":
                parametros["tarifa_hora"] = tarifa
            else:
                parametros.update(
                    tarifa_hora=tarifa, nivel_consultor=self.servicio_nivel.get()
                )
            self.gestor.crear_servicio(tipo, **parametros)
        except (SoftwareFJException, ValueError) as error:
            messagebox.showerror("No se pudo crear el servicio", str(error), parent=self.root)
            return
        self.servicio_nombre.set("")
        self.servicio_tarifa.set("")
        self.servicio_capacidad.set("")
        self.servicio_proyector.set(False)
        self._actualizar_vistas()
        messagebox.showinfo("Servicio creado", "El servicio se creó correctamente.", parent=self.root)

    def _crear_reserva(self) -> None:
        try:
            id_cliente = self.reserva_cliente.get().split(" - ", 1)[0]
            id_servicio = self.reserva_servicio.get().split(" - ", 1)[0]
            reserva = self.gestor.crear_reserva(
                id_cliente, id_servicio, self.reserva_duracion.get()
            )
        except SoftwareFJException as error:
            messagebox.showerror("No se pudo crear la reserva", str(error), parent=self.root)
            return
        except (ValueError, IndexError):
            messagebox.showerror(
                "Datos incompletos", "Selecciona un cliente y un servicio e indica la duración.",
                parent=self.root,
            )
            return
        self.reserva_duracion.set("")
        self._actualizar_vistas()
        self.tabla_reservas.selection_set(reserva.identificador)
        messagebox.showinfo("Reserva creada", f"Se creó la reserva {reserva.identificador}.", parent=self.root)

    def _reserva_seleccionada(self) -> Optional[Reserva]:
        seleccion = self.tabla_reservas.selection()
        if not seleccion:
            messagebox.showwarning(
                "Selecciona una reserva", "Selecciona una reserva de la tabla.", parent=self.root
            )
            return None
        return self.gestor.buscar_reserva(seleccion[0])

    def _procesar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if reserva is None:
            return
        try:
            descuento = float(self.reserva_descuento.get()) / 100
            costo = self.gestor.procesar_reserva(
                reserva.identificador,
                descuento=descuento,
                aplicar_iva=self.reserva_iva.get(),
                urgente=self.reserva_urgente.get(),
            )
        except (SoftwareFJException, ValueError) as error:
            messagebox.showerror("No se pudo calcular el costo", str(error), parent=self.root)
            return
        self._actualizar_vistas()
        messagebox.showinfo("Costo calculado", formatear_moneda(costo), parent=self.root)

    def _confirmar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if reserva is None:
            return
        try:
            self.gestor.confirmar_reserva(reserva.identificador)
        except SoftwareFJException as error:
            messagebox.showerror("No se pudo confirmar", str(error), parent=self.root)
            return
        self._actualizar_vistas()
        messagebox.showinfo("Reserva confirmada", "La reserva fue confirmada.", parent=self.root)

    def _cancelar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if reserva is None:
            return
        if not messagebox.askyesno(
            "Cancelar reserva", f"¿Deseas cancelar la reserva {reserva.identificador}?",
            parent=self.root,
        ):
            return
        try:
            self.gestor.cancelar_reserva(reserva.identificador, "Cancelada desde la interfaz")
        except SoftwareFJException as error:
            messagebox.showerror("No se pudo cancelar", str(error), parent=self.root)
            return
        self._actualizar_vistas()
        messagebox.showinfo("Reserva cancelada", "La reserva fue cancelada.", parent=self.root)


def main() -> None:
    """
    Punto de entrada del programa.

    [ESTRUCTURA try/except/finally]
      - try    : ejecuta la simulación completa y luego abre la interfaz gráfica.
      - except : red de seguridad final; registra cualquier fallo no previsto.
      - finally: cierra ordenadamente el sistema de logs.
    """
    root = None
    try:
        ejecutar_simulacion()
        root = tk.Tk()
        InterfazSoftwareFJ(root)
        root.mainloop()
    except Exception as e:  # Red de seguridad: no debería activarse jamás.
        logger.critical("Fallo crítico no controlado: %s", e, exc_info=True)
    finally:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass
        logger.info("Programa finalizado. Bitácora completa en '%s'.", ARCHIVO_LOG)
        logging.shutdown()


if __name__ == "__main__":
    main()
