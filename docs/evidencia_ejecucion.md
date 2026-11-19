# Evidencia de ejecución — Software FJ (Fase 4)

Fecha de corrida de ejemplo: 2026-11-19.

Comando usado (solo simulación, sin abrir la GUI):

```text
python -c "ejecutar_simulacion()"
```

En la práctica se invocó ejecutar_simulacion() desde el módulo prueba 2.0.py.
La ejecución completa del entregable es:

```bash
python "prueba 2.0.py"
```

## Resultado observado

- Operaciones ejecutadas: **40**
- Exitosas: **17**
- Rechazadas/controladas: **23**
- Errores inesperados: **0**
- El programa **no se detuvo** ante datos inválidos ni transiciones ilegales.
- Se generó/actualizó la bitácora local software_fj.log (ignorada por git; no contiene secretos de acceso).

## Salida de consola (extracto de la simulación)

```text
python : 11:01:40 | INFO     | Gestor de Software FJ inicializado (almacenamiento en memoria).
En C:\Users\Admin\AppData\Local\Temp\ps-script-cecfa8b3-5a46-49e7-8f78-da89e22cc42c.ps1: 117 Carácter: 1
+ python "C:\Users\Admin\Documents\SoftwareFJ-fase4\_run_sim.py" 2>&1 | ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (11:01:40 | INFO...to en memoria).:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
11:01:40 | INFO     | ==============================================================================
11:01:40 | INFO     | INICIO DE LA SIMULACI├ôN - SOFTWARE FJ
11:01:40 | INFO     | ==============================================================================
11:01:40 | INFO     | --- BLOQUE A: Registro de clientes (v├ílidos e inv├ílidos) ---
11:01:40 | INFO     | [OP-01] Iniciando: Registrar cliente v├ílido (Laura G├│mez)
11:01:40 | INFO     | Cliente registrado: CLI-001 | Laura G├│mez | laura.gomez@softwarefj.co
11:01:40 | INFO     | [OP-01] OK
11:01:40 | INFO     | [OP-02] Iniciando: Registrar cliente v├ílido (Carlos Ram├¡rez)
11:01:40 | INFO     | Cliente registrado: CLI-002 | Carlos Ram├¡rez | carlos.ramirez@correo.com
11:01:40 | INFO     | [OP-02] OK
11:01:40 | INFO     | [OP-03] Iniciando: Registrar cliente con correo inv├ílido
11:01:40 | ERROR    | Registro de cliente rechazado (DatoInvalidoError): Formato de correo electr├│nico inv├ílido: 
'pedro.perez#correo'.
11:01:40 | ERROR    | [OP-03] ERROR CONTROLADO (DatoInvalidoError, FJ-100): Formato de correo electr├│nico inv├ílido: 
'pedro.perez#correo'.
11:01:40 | INFO     | [OP-04] Iniciando: Registrar cliente con nombre demasiado corto
11:01:40 | ERROR    | Registro de cliente rechazado (DatoInvalidoError): El nombre debe tener entre 3 y 60 caracteres 
(recibido: 2).
11:01:40 | ERROR    | [OP-04] ERROR CONTROLADO (DatoInvalidoError, FJ-100): El nombre debe tener entre 3 y 60 
caracteres (recibido: 2).
11:01:40 | INFO     | [OP-05] Iniciando: Registrar cliente con tel├⌐fono no num├⌐rico
11:01:40 | ERROR    | Registro de cliente rechazado (DatoInvalidoError): El tel├⌐fono debe contener solo d├¡gitos (7 a 
10); recibido: '31A-456'.
11:01:40 | ERROR    | [OP-05] ERROR CONTROLADO (DatoInvalidoError, FJ-100): El tel├⌐fono debe contener solo d├¡gitos 
(7 a 10); recibido: '31A-456'.
11:01:40 | INFO     | [OP-06] Iniciando: Registrar cliente con tel├⌐fono demasiado corto
11:01:40 | ERROR    | Registro de cliente rechazado (DatoInvalidoError): El tel├⌐fono debe contener solo d├¡gitos (7 a 
10); recibido: '123'.
11:01:40 | ERROR    | [OP-06] ERROR CONTROLADO (DatoInvalidoError, FJ-100): El tel├⌐fono debe contener solo d├¡gitos 
(7 a 10); recibido: '123'.
11:01:40 | INFO     | [OP-07] Iniciando: Registrar cliente con correo vac├¡o
11:01:40 | ERROR    | Registro de cliente rechazado (DatoInvalidoError): Formato de correo electr├│nico inv├ílido: ''.
11:01:40 | ERROR    | [OP-07] ERROR CONTROLADO (DatoInvalidoError, FJ-100): Formato de correo electr├│nico inv├ílido: 
''.
11:01:40 | INFO     | [OP-08] Iniciando: Registrar cliente con correo duplicado
11:01:40 | ERROR    | Registro de cliente rechazado (DatoInvalidoError): Ya existe un cliente registrado con el correo 
'laura.gomez@softwarefj.co'.
11:01:40 | ERROR    | [OP-08] ERROR CONTROLADO (DatoInvalidoError, FJ-100): Ya existe un cliente registrado con el 
correo 'laura.gomez@softwarefj.co'.
11:01:40 | INFO     | --- BLOQUE B: Creaci├│n de servicios (v├ílidos e inv├ílidos) ---
11:01:40 | INFO     | [OP-09] Iniciando: Crear ReservaSala v├ílida
11:01:40 | INFO     | Servicio creado: SRV-001 | Sala Innovaci├│n | tarifa base $60,000.00 COP por hora
11:01:40 | INFO     | [OP-09] OK
11:01:40 | INFO     | [OP-10] Iniciando: Crear AlquilerEquipo v├ílido
11:01:40 | INFO     | Servicio creado: SRV-002 | Port├ítil Workstation | tarifa base $45,000.00 COP por d├¡a
11:01:40 | INFO     | [OP-10] OK
11:01:40 | INFO     | [OP-11] Iniciando: Crear AsesoriaEspecializada v├ílida
11:01:40 | INFO     | Servicio creado: SRV-003 | Asesor├¡a en Arquitectura de Software | tarifa base $80,000.00 COP 
por hora
11:01:40 | INFO     | [OP-11] OK
11:01:40 | INFO     | [OP-12] Iniciando: Crear ReservaSala inv├ílida (capacidad negativa)
11:01:40 | ERROR    | Creaci├│n de servicio rechazada (DatoInvalidoError): La capacidad debe estar entre 1 y 200 
personas (recibido: -5).
11:01:40 | ERROR    | [OP-12] ERROR CONTROLADO (DatoInvalidoError, FJ-100): La capacidad debe estar entre 1 y 200 
personas (recibido: -5).
11:01:40 | INFO     | [OP-13] Iniciando: Crear ReservaSala inv├ílida (tarifa <= 0)
11:01:40 | ERROR    | Creaci├│n de servicio rechazada (DatoInvalidoError): La tarifa debe ser un n├║mero finito mayor 
que cero (recibido: 0).
11:01:40 | ERROR    | [OP-13] ERROR CONTROLADO (DatoInvalidoError, FJ-100): La tarifa debe ser un n├║mero finito mayor 
que cero (recibido: 0).
11:01:40 | INFO     | [OP-14] Iniciando: Crear AlquilerEquipo inv├ílido (rechaza el seguro obligatorio)
11:01:40 | ERROR    | Creaci├│n de servicio rechazada (DatoInvalidoError): El seguro es obligatorio en el alquiler de 
equipos y no puede omitirse.
11:01:40 | ERROR    | [OP-14] ERROR CONTROLADO (DatoInvalidoError, FJ-100): El seguro es obligatorio en el alquiler de 
equipos y no puede omitirse.
11:01:40 | INFO     | [OP-15] Iniciando: Crear AsesoriaEspecializada inv├ílida (nivel inexistente)
11:01:40 | ERROR    | Creaci├│n de servicio rechazada (DatoInvalidoError): Nivel de consultor 'GURU' inv├ílido. 
Niveles permitidos: JUNIOR, SEMISENIOR, SENIOR, EXPERTO.
11:01:40 | ERROR    | [OP-15] ERROR CONTROLADO (DatoInvalidoError, FJ-100): Nivel de consultor 'GURU' inv├ílido. 
Niveles permitidos: JUNIOR, SEMISENIOR, SENIOR, EXPERTO.
11:01:40 | INFO     | [OP-16] Iniciando: Crear servicio con tipo desconocido
11:01:40 | ERROR    | Creaci├│n de servicio rechazada (DatoInvalidoError): Tipo de servicio 'CONSULTORIA' no 
soportado. Tipos v├ílidos: SALA, EQUIPO, ASESORIA.
11:01:40 | ERROR    | [OP-16] ERROR CONTROLADO (DatoInvalidoError, FJ-100): Tipo de servicio 'CONSULTORIA' no 
soportado. Tipos v├ílidos: SALA, EQUIPO, ASESORIA.
11:01:40 | INFO     | [OP-17] Iniciando: Crear servicio con par├ímetros incompletos (falta tarifa y capacidad)
11:01:40 | ERROR    | Creaci├│n de servicio rechazada (DatoInvalidoError): Par├ímetros incompletos o no reconocidos 
para el servicio 'SALA': ReservaSala.__init__() missing 2 required positional arguments: 'tarifa_hora' and 'capacidad'
11:01:40 | ERROR    | [OP-17] ERROR CONTROLADO (DatoInvalidoError, FJ-100): Par├ímetros incompletos o no reconocidos 
para el servicio 'SALA': ReservaSala.__init__() missing 2 required positional arguments: 'tarifa_hora' and 'capacidad' 
| causa original: TypeError: ReservaSala.__init__() missing 2 required positional arguments: 'tarifa_hora' and 
'capacidad'
11:01:40 | INFO     | --- BLOQUE C: Polimorfismo y sobrecarga de calcular_costo() ---
11:01:40 | INFO     | [OP-18] Iniciando: Calcular costos de todos los servicios con distintas variantes
11:01:40 | INFO     |    ReservaSala            | 2 horas | sin ajustes              -> $150,000.00 COP
11:01:40 | INFO     |    ReservaSala            | 2 horas | descuento 10%            -> $135,000.00 COP
11:01:40 | INFO     |    ReservaSala            | 2 horas | con IVA 19%              -> $178,500.00 COP
11:01:40 | INFO     |    ReservaSala            | 2 horas | urgente +15%             -> $172,500.00 COP
11:01:40 | INFO     |    ReservaSala            | 2 horas | descuento+IVA+urgente    -> $184,747.50 COP
11:01:40 | INFO     |    ReservaSala            | 2 horas | IVA personalizado 16%    -> $174,000.00 COP
11:01:40 | INFO     |    AlquilerEquipo         | 2 d├¡as  | sin ajustes              -> $97,200.00 COP
11:01:40 | INFO     |    AlquilerEquipo         | 2 d├¡as  | descuento 10%            -> $87,480.00 COP
11:01:40 | INFO     |    AlquilerEquipo         | 2 d├¡as  | con IVA 19%              -> $115,668.00 COP
11:01:40 | INFO     |    AlquilerEquipo         | 2 d├¡as  | urgente +15%             -> $111,780.00 COP
11:01:40 | INFO     |    AlquilerEquipo         | 2 d├¡as  | descuento+IVA+urgente    -> $119,716.38 COP
11:01:40 | INFO     |    AlquilerEquipo         | 2 d├¡as  | IVA personalizado 16%    -> $112,752.00 COP
11:01:40 | INFO     |    AsesoriaEspecializada  | 2 horas | sin ajustes              -> $288,000.00 COP
11:01:40 | INFO     |    AsesoriaEspecializada  | 2 horas | descuento 10%            -> $259,200.00 COP
11:01:40 | INFO     |    AsesoriaEspecializada  | 2 horas | con IVA 19%              -> $342,720.00 COP
11:01:40 | INFO     |    AsesoriaEspecializada  | 2 horas | urgente +15%             -> $331,200.00 COP
11:01:40 | INFO     |    AsesoriaEspecializada  | 2 horas | descuento+IVA+urgente    -> $354,715.20 COP
11:01:40 | INFO     |    AsesoriaEspecializada  | 2 horas | IVA personalizado 16%    -> $334,080.00 COP
11:01:40 | INFO     | [OP-18] OK
11:01:40 | INFO     | --- BLOQUE D: Reservas exitosas, duplicadas y fuera de rango ---
11:01:40 | INFO     | [OP-19] Iniciando: Crear reserva de sala (3 horas) para Laura
11:01:40 | INFO     | Reserva creada: RES-001 | cliente=Laura G├│mez | servicio=Sala Innovaci├│n | duraci├│n=3 horas
11:01:40 | INFO     | [OP-19] OK
11:01:40 | INFO     | [OP-20] Iniciando: Procesar reserva de sala con descuento 10% + IVA
11:01:40 | INFO     | Reserva RES-001 procesada. Costo total: $240,975.00 COP | opciones={'descuento': 0.1, 
'aplicar_iva': True}
11:01:40 | INFO     | [OP-20] OK
11:01:40 | INFO     | [OP-21] Iniciando: Confirmar reserva de sala
11:01:40 | INFO     | Reserva RES-001 CONFIRMADA (cliente=Laura G├│mez, servicio=Sala Innovaci├│n).
11:01:40 | INFO     | [OP-21] OK
11:01:40 | INFO     | [OP-22] Iniciando: Confirmar NUEVAMENTE la misma reserva (duplicada)
11:01:40 | WARNING  | Confirmaci├│n rechazada para RES-001: Operaci├│n duplicada: la reserva RES-001 ya est├í 
CONFIRMADA.
11:01:40 | WARNING  | [OP-22] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): Operaci├│n duplicada: la 
reserva RES-001 ya est├í CONFIRMADA.
11:01:40 | INFO     | [OP-23] Iniciando: Flujo completo de alquiler de equipo (5 d├¡as, urgente, 5% desc., IVA)
11:01:40 | INFO     | Reserva creada: RES-002 | cliente=Carlos Ram├¡rez | servicio=Port├ítil Workstation | duraci├│n=5 
d├¡as
11:01:40 | INFO     | Reserva RES-002 procesada. Costo total: $315,918.22 COP | opciones={'descuento': 0.05, 
'aplicar_iva': True, 'urgente': True}
11:01:40 | INFO     | Reserva RES-002 CONFIRMADA (cliente=Carlos Ram├¡rez, servicio=Port├ítil Workstation).
11:01:40 | INFO     | [OP-23] OK
11:01:40 | INFO     | [OP-24] Iniciando: Crear reserva de sala con duraci├│n fuera de rango (20 horas)
11:01:40 | WARNING  | Creaci├│n de reserva rechazada (ReservaInvalidaError): Duraci├│n de 20 horas fuera del rango 
permitido (1 a 12 horas) para 'Sala Innovaci├│n'.
11:01:40 | WARNING  | [OP-24] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): Duraci├│n de 20 horas 
fuera del rango permitido (1 a 12 horas) para 'Sala Innovaci├│n'.
11:01:40 | INFO     | [OP-25] Iniciando: Crear reserva de asesor├¡a con duraci├│n no num├⌐rica ('dos horas')
11:01:40 | WARNING  | Creaci├│n de reserva rechazada (ReservaInvalidaError): La duraci├│n 'dos horas' no es un valor 
num├⌐rico.
11:01:40 | WARNING  | [OP-25] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): La duraci├│n 'dos horas' 
no es un valor num├⌐rico. | causa original: ValueError: could not convert string to float: 'dos horas'
11:01:40 | INFO     | [OP-26] Iniciando: Crear reserva con cliente inexistente
11:01:40 | WARNING  | Creaci├│n de reserva rechazada (ReservaInvalidaError): No se puede crear la reserva: No existe 
un cliente con id 'CLI-999'.
11:01:40 | WARNING  | [OP-26] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): No se puede crear la 
reserva: No existe un cliente con id 'CLI-999'. | causa original: DatoInvalidoError: No existe un cliente con id 
'CLI-999'.
11:01:40 | INFO     | --- BLOQUE E: C├ílculos inv├ílidos, inconsistentes y transiciones ---
11:01:40 | INFO     | [OP-27] Iniciando: Crear reserva de asesor├¡a (2 horas) para Carlos
11:01:40 | INFO     | Reserva creada: RES-003 | cliente=Carlos Ram├¡rez | servicio=Asesor├¡a en Arquitectura de 
Software | duraci├│n=2 horas
11:01:40 | INFO     | [OP-27] OK
11:01:40 | INFO     | [OP-28] Iniciando: Procesar con descuento del 100% (costo resultante inconsistente)
11:01:40 | WARNING  | Descuento elevado solicitado (100%) en el servicio SRV-003.
11:01:40 | ERROR    | C├ílculo inconsistente en RES-003: El c├ílculo del servicio SRV-003 produjo un costo incoherente 
(0.0). Revise descuentos y recargos aplicados.
11:01:40 | ERROR    | [OP-28] ERROR CONTROLADO (CalculoInconsistenteError, FJ-400): El c├ílculo del servicio SRV-003 
produjo un costo incoherente (0.0). Revise descuentos y recargos aplicados.
11:01:40 | INFO     | [OP-29] Iniciando: Procesar con descuento del 150% (dato inv├ílido encadenado)
11:01:40 | ERROR    | Opciones de costo inv├ílidas en RES-003: 'descuento' debe estar entre 0 y 1 (recibido: 1.5).
11:01:40 | WARNING  | [OP-29] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): No se pudo procesar la 
reserva RES-003: opciones de costo inv├ílidas ('descuento' debe estar entre 0 y 1 (recibido: 1.5).). | causa original: 
DatoInvalidoError: 'descuento' debe estar entre 0 y 1 (recibido: 1.5).
11:01:40 | INFO     | [OP-30] Iniciando: Procesar con opci├│n de c├ílculo no soportada ('cupon')
11:01:40 | ERROR    | Opciones de costo inv├ílidas en RES-003: Opciones de c├ílculo no soportadas: cupon.
11:01:40 | WARNING  | [OP-30] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): No se pudo procesar la 
reserva RES-003: opciones de costo inv├ílidas (Opciones de c├ílculo no soportadas: cupon.). | causa original: 
DatoInvalidoError: Opciones de c├ílculo no soportadas: cupon.
11:01:40 | INFO     | [OP-31] Iniciando: Procesar asesor├¡a con descuento alto (35%) + IVA [v├ílido, genera 
advertencia]
11:01:40 | WARNING  | Descuento elevado solicitado (35%) en el servicio SRV-003.
11:01:40 | INFO     | Reserva RES-003 procesada. Costo total: $222,768.00 COP | opciones={'descuento': 0.35, 
'aplicar_iva': True}
11:01:40 | INFO     | [OP-31] OK
11:01:40 | INFO     | [OP-32] Iniciando: Confirmar reserva de asesor├¡a
11:01:40 | INFO     | Reserva RES-003 CONFIRMADA (cliente=Carlos Ram├¡rez, servicio=Asesor├¡a en Arquitectura de 
Software).
11:01:40 | INFO     | [OP-32] OK
11:01:40 | INFO     | [OP-33] Iniciando: Crear reserva de sala (2 horas) sin procesar
11:01:40 | INFO     | Reserva creada: RES-004 | cliente=Carlos Ram├¡rez | servicio=Sala Innovaci├│n | duraci├│n=2 horas
11:01:40 | INFO     | [OP-33] OK
11:01:40 | INFO     | [OP-34] Iniciando: Confirmar reserva sin haber calculado su costo
11:01:40 | WARNING  | Confirmaci├│n rechazada para RES-004: La reserva RES-004 debe procesarse (calcular costo) antes 
de confirmarse.
11:01:40 | WARNING  | [OP-34] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): La reserva RES-004 debe 
procesarse (calcular costo) antes de confirmarse.
11:01:40 | INFO     | --- BLOQUE F: Disponibilidad y cancelaciones ---
11:01:40 | INFO     | [OP-35] Iniciando: Deshabilitar equipo por mantenimiento
11:01:40 | WARNING  | Servicio SRV-002 ('Port├ítil Workstation') deshabilitado. Motivo: Mantenimiento correctivo
11:01:40 | INFO     | [OP-35] OK
11:01:40 | INFO     | [OP-36] Iniciando: Reservar un equipo NO disponible
11:01:40 | WARNING  | Creaci├│n de reserva rechazada (ServicioNoDisponibleError): El servicio SRV-002 ('Port├ítil 
Workstation') no est├í disponible.
11:01:40 | WARNING  | [OP-36] RECHAZADA por regla de negocio (ServicioNoDisponibleError, FJ-200): El servicio SRV-002 
('Port├ítil Workstation') no est├í disponible.
11:01:40 | INFO     | [OP-37] Iniciando: Cancelar reserva PENDIENTE sin confirmaci├│n previa
11:01:40 | INFO     | Reserva RES-004 CANCELADA. Motivo: Cliente desisti├│ antes de confirmar
11:01:40 | INFO     | [OP-37] OK
11:01:40 | INFO     | [OP-38] Iniciando: Cancelar reserva de sala ya confirmada
11:01:40 | INFO     | Reserva RES-001 CANCELADA. Motivo: El cliente reprogram├│ su evento
11:01:40 | INFO     | [OP-38] OK
11:01:40 | INFO     | [OP-39] Iniciando: Cancelar NUEVAMENTE la misma reserva (duplicada)
11:01:40 | WARNING  | Cancelaci├│n rechazada para RES-001: Operaci├│n duplicada: la reserva RES-001 ya est├í CANCELADA.
11:01:40 | WARNING  | [OP-39] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): Operaci├│n duplicada: la 
reserva RES-001 ya est├í CANCELADA.
11:01:40 | INFO     | [OP-40] Iniciando: Confirmar una reserva ya cancelada
11:01:40 | WARNING  | Confirmaci├│n rechazada para RES-001: Transici├│n no permitida en la reserva RES-001: CANCELADA 
-> CONFIRMADA.
11:01:40 | WARNING  | [OP-40] RECHAZADA por regla de negocio (ReservaInvalidaError, FJ-300): Transici├│n no permitida 
en la reserva RES-001: CANCELADA -> CONFIRMADA.
11:01:40 | INFO     | ==============================================================================
11:01:40 | INFO     | RESUMEN FINAL DEL SISTEMA (datos en memoria)
11:01:40 | INFO     | ==============================================================================
11:01:40 | INFO     | Clientes registrados : 2 (intentos de registro: 8)
11:01:40 | INFO     | Servicios creados    : 3
11:01:40 | INFO     | Reservas creadas     : 4 (intentos de reserva: 8)
11:01:40 | INFO     | Detalle de clientes:
11:01:40 | INFO     |   CLI-001 | Laura G├│mez              | laura.gomez@softwarefj.co        | 3105551234
11:01:40 | INFO     |   CLI-002 | Carlos Ram├¡rez           | carlos.ramirez@correo.com        | 3201234567
11:01:40 | INFO     | Detalle de servicios:
11:01:40 | INFO     |   SRV-001 | ReservaSala            | Sala Innovaci├│n                    | $60,000.00 COP | 
disp=S├¡
11:01:40 | INFO     |   SRV-002 | AlquilerEquipo         | Port├ítil Workstation               | $45,000.00 COP | 
disp=No
11:01:40 | INFO     |   SRV-003 | AsesoriaEspecializada  | Asesor├¡a en Arquitectura de Software | $80,000.00 COP | 
disp=S├¡
11:01:40 | INFO     | Detalle de reservas:
11:01:40 | INFO     |   RES-001 | CANCELADA  | CLI-001 - Laura G├│mez    | SRV-001 - Sala Innovaci├│n          | 3 
horas    | $240,975.00 COP
11:01:40 | INFO     |   RES-002 | CONFIRMADA | CLI-002 - Carlos Ram├¡rez | SRV-002 - Port├ítil Workstation     | 5 
d├¡as     | $315,918.22 COP
11:01:40 | INFO     |   RES-003 | CONFIRMADA | CLI-002 - Carlos Ram├¡rez | SRV-003 - Asesor├¡a en Arquitectura de 
Software | 2 horas    | $222,768.00 COP
11:01:40 | INFO     |   RES-004 | CANCELADA  | CLI-002 - Carlos Ram├¡rez | SRV-001 - Sala Innovaci├│n          | 2 
horas    | N/A (sin procesar)
11:01:40 | INFO     | Ingresos por reservas CONFIRMADAS: $538,686.22 COP
11:01:40 | INFO     | ------------------------------------------------------------------------------
11:01:40 | INFO     | Operaciones ejecutadas              : 40
11:01:40 | INFO     |   Exitosas                          : 17
11:01:40 | INFO     |   Rechazadas/controladas            : 23
11:01:40 | INFO     |   Errores inesperados (capturados)  : 0
11:01:40 | INFO     | Resultado: el sistema captur├│ todos los errores y finaliz├│ con estabilidad total.
11:01:40 | INFO     | ==============================================================================
```

## Notas

- No se incluyen credenciales, tokens ni datos personales reales: los clientes/correos son de prueba.
- La GUI se abre después de la simulación en la ejecución normal; esta evidencia cubre el requisito de ≥10 operaciones automatizadas del Anexo 3.
