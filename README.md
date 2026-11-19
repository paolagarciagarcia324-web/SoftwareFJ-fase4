# Software FJ — Fase 4 (Programación 213023)

Sistema integral de gestión de **clientes**, **servicios** y **reservas** para la empresa Software FJ (reservas de salas, alquiler de equipos y asesorías especializadas).

Trabajo colaborativo UNAD — curso Programación (213023). Sin bases de datos: todo vive en memoria (`GestorFJ`); el único archivo es la bitácora de eventos/errores.

## Cómo ejecutar

```bash
python "prueba 2.0.py"
```

Al iniciar:

1. Corre la **simulación automatizada** (≥10 operaciones válidas e inválidas).
2. Abre la **interfaz gráfica** (Tkinter) para operar el sistema de forma manual.

Requisito: Python 3.10+ (stdlib; no necesita `pip install`).

## Estructura de clases

| Pieza | Rol |
|-------|-----|
| `EntidadBase` | Clase abstracta general |
| `Cliente` | Encapsulación + validaciones de datos personales |
| `Servicio` | Clase abstracta; polimorfismo en costo/validación |
| `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` | Tres servicios especializados |
| `Reserva` + `EstadoReserva` | Ciclo PENDIENTE → CONFIRMADA / CANCELADA |
| `GestorFJ` | Listas en memoria y orquestación |
| `EjecutorOperaciones` | Ejecuta casos de prueba sin tumbar el programa |
| `InterfazSoftwareFJ` | GUI Tkinter (aporte del equipo) |
| Excepciones (`SoftwareFJException` y derivadas) | Errores de dominio controlados |

## Qué genera `software_fj.log`

Archivo de texto creado/actualizado al ejecutar el programa. Registra:

- Eventos relevantes (registros, creaciones, confirmaciones, cancelaciones).
- Errores controlados y advertencias (datos inválidos, transiciones no permitidas, etc.).
- Resumen final de la simulación (conteos y detalle de entidades en memoria).

No guarda la base de datos del negocio: solo auditoría. Está en `.gitignore` para no versionar corridas locales; la evidencia de una ejecución de ejemplo está en `docs/evidencia_ejecucion.md`.

## Checklist Anexo 3

- [x] POO con abstracción, herencia, polimorfismo y encapsulación
- [x] Clase abstracta general (`EntidadBase`)
- [x] Clase `Cliente` con validaciones y encapsulación
- [x] Clase abstracta `Servicio` + al menos 3 especializadas
- [x] Clase `Reserva` (cliente, servicio, duración, estado; confirmar/cancelar/procesar)
- [x] Métodos sobrecargados / variantes de cálculo de costos (descuento, IVA, urgencia)
- [x] Sin motor de base de datos; listas en memoria
- [x] Archivos solo para logs de eventos/errores
- [x] Excepciones personalizadas + `try/except`, `else`, `finally` y encadenamiento
- [x] Simulación de ≥10 operaciones (válidas e inválidas) sin detener el programa
- [x] Proyecto ejecutable y documentado (este README + docstrings)
