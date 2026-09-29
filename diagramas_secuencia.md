# Diagramas de Secuencia — Sistema de Préstamo de Equipos

## Diagrama 1: Préstamo Exitoso (CA1 — R1, R2, R4)

```mermaid
sequenceDiagram
    autonumber
    actor Main as main.py
    participant UC as RegistrarPrestamo
    participant RE as RepositorioEquipos
    participant RES as RepositorioEstudiantes
    participant RP as RepositorioPrestamos
    participant EQ as Equipo
    participant EST as Estudiante
    participant PF as ProveedorFecha
    participant P as Prestamo
    participant N as Notificador

    Main->>UC: ejecutar(equipo_id, estudiante_id)

    UC->>RE: buscar_por_id(equipo_id)
    RE-->>UC: equipo

    UC->>RES: buscar_por_id(estudiante_id)
    RES-->>UC: estudiante

    UC->>EQ: esta_disponible()
    EQ-->>UC: True

    UC->>EST: get_tiene_multa()
    EST-->>UC: False

    UC->>RP: listar_activos_por_estudiante(estudiante_id)
    RP-->>UC: lista con 0 prestamos activos

    UC->>PF: hoy()
    PF-->>UC: 2026-10-05

    UC->>P: new Prestamo(equipo, estudiante, 2026-10-05)
    activate P
    Note over P: fecha_limite = 2026-10-05 + 3 dias = 2026-10-08
    Note over P: multa = 0, estado = ACTIVO
    P-->>UC: prestamo
    deactivate P

    UC->>EQ: marcar_prestado()
    Note over EQ: estado cambia a PRESTADO

    UC->>RE: guardar(equipo)
    UC->>RP: guardar(prestamo)

    UC->>N: enviar(Prestamo registrado. Fecha limite 2026-10-08, estudiante)

    UC-->>Main: prestamo
```

---

## Diagrama 2: Préstamo Rechazado por Multa Pendiente (CA4 — R4)

```mermaid
sequenceDiagram
    autonumber
    actor Main as main.py
    participant UC as RegistrarPrestamo
    participant RE as RepositorioEquipos
    participant RES as RepositorioEstudiantes
    participant EQ as Equipo
    participant EST as Estudiante

    Main->>UC: ejecutar(equipo_id, estudiante_id)

    UC->>RE: buscar_por_id(equipo_id)
    RE-->>UC: equipo

    UC->>RES: buscar_por_id(estudiante_id)
    RES-->>UC: estudiante (Luis)

    UC->>EQ: esta_disponible()
    EQ-->>UC: True

    UC->>EST: get_tiene_multa()
    EST-->>UC: True

    Note over UC: Validacion falla, R4 violada
    UC->>UC: raise EstudianteConMultaPendienteError

    UC-->>Main: EstudianteConMultaPendienteError

    Note over Main: Sin Prestamo creado, sin cambios en repositorios
```

---

## Diagrama 3: Devolución Tardía con Multa (CA3 — R5, R6, R7)

```mermaid
sequenceDiagram
    autonumber
    actor Main as main.py
    participant UC as RegistrarDevolucion
    participant RP as RepositorioPrestamos
    participant RE as RepositorioEquipos
    participant RES as RepositorioEstudiantes
    participant P as Prestamo
    participant EQ as Equipo
    participant EST as Estudiante
    participant PF as ProveedorFecha
    participant N as Notificador

    Main->>UC: ejecutar(prestamo_id, equipo_danado=False)

    UC->>RP: buscar_por_id(prestamo_id)
    RP-->>UC: prestamo con fecha_limite 2026-10-03

    UC->>PF: hoy()
    PF-->>UC: 2026-10-06

    UC->>P: marcar_devuelto(2026-10-06)
    activate P
    Note over P: dias_retraso = 2026-10-06 menos 2026-10-03 = 3
    Note over P: multa = 3 x 8000 = 24000
    P->>P: fecha_devolucion = 2026-10-06
    P->>P: multa = 24000
    P->>P: estado = DEVUELTO
    deactivate P

    Note over UC: equipo_danado=False, aplica R6
    UC->>EQ: marcar_disponible()
    Note over EQ: estado = DISPONIBLE

    Note over UC: prestamo.multa = 24000 mayor que 0, aplica R7
    UC->>EST: set_tiene_multa(True)
    UC->>RES: guardar(estudiante)

    UC->>N: enviar(Devolucion con retraso. Multa 24000, estudiante)

    UC->>RE: guardar(equipo)
    UC->>RP: guardar(prestamo)

    UC-->>Main: prestamo
```

## Diagrama 1: Préstamo Exitoso (CA1)
> Ana no tiene préstamos y pide PORTATIL-01. Se crea el préstamo con fecha límite y se notifica.

```mermaid
sequenceDiagram
    autonumber
    actor main as main.py
    participant UC as RegistrarPrestamo
    participant RE as RepositorioEquipos
    participant RES as RepositorioEstudiantes
    participant RP as RepositorioPrestamos
    participant EQ as Equipo
    participant EST as Estudiante
    participant PF as ProveedorFecha
    participant P as Prestamo
    participant N as Notificador

    main->>UC: ejecutar(equipo_id, estudiante_id)

    UC->>RE: buscar_por_id(equipo_id)
    RE-->>UC: equipo (PORTATIL-01)

    UC->>RES: buscar_por_id(estudiante_id)
    RES-->>UC: estudiante (Ana)

    UC->>EQ: esta_disponible()
    EQ-->>UC: True ✅

    UC->>EST: get_tiene_multa()
    EST-->>UC: False ✅

    UC->>RP: listar_activos_por_estudiante(estudiante_id)
    RP-->>UC: [] → 0 activos ✅

    UC->>PF: hoy()
    PF-->>UC: 2026-10-05

    UC->>P: new Prestamo(equipo, estudiante, 2026-10-05)
    Note over P: fecha_limite = 2026-10-05 + 3 días<br/>= 2026-10-08<br/>multa = 0, estado = "ACTIVO"
    P-->>UC: prestamo

    UC->>EQ: marcar_prestado()
    Note over EQ: estado → "PRESTADO"

    UC->>RE: guardar(equipo)
    UC->>RP: guardar(prestamo)

    UC->>N: enviar("Fecha límite: 2026-10-08", Ana)
    N-->>main: [NOTIFICACION] → Ana: Fecha límite: 2026-10-08

    UC-->>main: prestamo
```

---

## Diagrama 2: Préstamo Rechazado por Multa Pendiente (CA4 — R4)
> Luis tiene una multa pendiente. El sistema rechaza el préstamo antes de crear cualquier objeto.

```mermaid
sequenceDiagram
    autonumber
    actor main as main.py
    participant UC as RegistrarPrestamo
    participant RE as RepositorioEquipos
    participant RES as RepositorioEstudiantes
    participant EQ as Equipo
    participant EST as Estudiante

    main->>UC: ejecutar(equipo_id, estudiante_id)

    UC->>RE: buscar_por_id(equipo_id)
    RE-->>UC: equipo (disponible)

    UC->>RES: buscar_por_id(estudiante_id)
    RES-->>UC: estudiante (Luis)

    UC->>EQ: esta_disponible()
    EQ-->>UC: True ✅

    UC->>EST: get_tiene_multa()
    EST-->>UC: True ❌

    UC->>UC: raise EstudianteConMultaPendienteError
    Note over UC: "Luis tiene una multa pendiente<br/>y no puede pedir prestado"

    UC-->>main: ❌ EstudianteConMultaPendienteError

    Note over main: El sistema captura la excepción<br/>y muestra el mensaje al usuario.<br/>No se creó ningún Prestamo,<br/>no se tocó el Equipo ni el Repositorio.
```

> **Variaciones del rechazo** — el mismo flujo aplica para:
> - **R1 (CA2):** `listar_activos_por_estudiante()` retorna 2 → `LimitePrestamosExcedidoError`
> - **R2 (CA5):** `esta_disponible()` retorna `False` → `EquipoNoDisponibleError`

---

## Diagrama 3: Devolución Tardía con Multa (CA3 — R5, R6, R7)
> CAMARA-02 fue prestada el 2026-10-01 (límite 2026-10-03) y se devuelve el 2026-10-06.
> Retraso: 3 días. Multa: 3 × $8.000 = $24.000.

```mermaid
sequenceDiagram
    autonumber
    actor main as main.py
    participant UC as RegistrarDevolucion
    participant RP as RepositorioPrestamos
    participant RE as RepositorioEquipos
    participant RES as RepositorioEstudiantes
    participant P as Prestamo
    participant EQ as Equipo
    participant EST as Estudiante
    participant PF as ProveedorFecha
    participant N as Notificador

    main->>UC: ejecutar(prestamo_id, equipo_danado=False)

    UC->>RP: buscar_por_id(prestamo_id)
    RP-->>UC: prestamo (CAMARA-02, fecha_limite=2026-10-03)

    UC->>PF: hoy()
    PF-->>UC: 2026-10-06

    UC->>P: marcar_devuelto(2026-10-06)
    activate P
        Note over P: calcular_multa(2026-10-06)<br/>dias_retraso = (10-06) - (10-03) = 3<br/>multa = 3 × 8.000 = 24.000
        P->>P: fecha_devolucion = 2026-10-06
        P->>P: multa = 24.000
        P->>P: estado = "DEVUELTO"
    deactivate P

    UC->>EQ: marcar_disponible()
    Note over EQ: equipo_danado=False → DISPONIBLE<br/>(Si fuera True → EN_MANTENIMIENTO)

    Note over UC: _aplicar_multa_si_corresponde(prestamo)<br/>prestamo.multa = 24.000 > 0 ✅

    UC->>EST: set_tiene_multa(True)
    Note over EST: Activa el bloqueo R4<br/>para futuros préstamos

    UC->>RES: guardar(estudiante)
    UC->>RE: guardar(equipo)
    UC->>RP: guardar(prestamo)

    UC->>N: enviar("Multa generada: $24.000", estudiante)
    N-->>main: [NOTIFICACION] → Ana: Multa generada: $24,000

    UC-->>main: prestamo (DEVUELTO, multa=24.000)
```
