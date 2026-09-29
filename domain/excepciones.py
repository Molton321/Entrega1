class LimitePrestamosExcedidoError(Exception):
    """R1: El estudiante ya tiene 2 préstamos activos."""


class EquipoNoDisponibleError(Exception):
    """R2: El equipo no está en estado DISPONIBLE."""


class EstudianteConMultaPendienteError(Exception):
    """R4: El estudiante tiene una multa sin pagar."""


class EquipoEnMantenimientoError(Exception):
    """R6: El equipo quedó en mantenimiento y no puede prestarse."""
