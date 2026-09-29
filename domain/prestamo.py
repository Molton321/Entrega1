from datetime import timedelta


class Prestamo:
    """Entidad que representa un préstamo de equipo a un estudiante."""

    def __init__(self, equipo, estudiante, fecha_prestamo):
        self.id = None
        self.equipo = equipo
        self.estudiante = estudiante
        self.fecha_prestamo = fecha_prestamo
        self.fecha_limite = fecha_prestamo + timedelta(days=equipo.categoria.plazo_maximo_dias)
        self.fecha_devolucion = None
        self.multa = 0
        self.estado = "ACTIVO"

    # --- Consultas de estado ---

    def esta_activo(self) -> bool:
        """Indica si el préstamo sigue abierto (R1: contar préstamos activos)."""
        return self.estado == "ACTIVO"

    # --- Lógica de negocio (R5) ---

    def calcular_multa(self, fecha_devolucion) -> int:
        """R5: (días completos de retraso) × cuota diaria de la categoría.
        Devolver el mismo día del límite no genera multa."""
        dias_retraso = (fecha_devolucion - self.fecha_limite).days
        if dias_retraso > 0:
            return dias_retraso * self.equipo.categoria.cuota_diaria
        return 0

    def marcar_devuelto(self, fecha_devolucion):
        """Registra la devolución y calcula la multa si hubo retraso."""
        self.fecha_devolucion = fecha_devolucion
        self.multa = self.calcular_multa(fecha_devolucion)
        self.estado = "DEVUELTO"

    # --- Getters / Setters ---

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def __str__(self):
        equipo_nombre = self.equipo.get_nombre() if self.equipo else None
        estudiante_nombre = self.estudiante.nombre if self.estudiante else None
        return f"Prestamo(id={self.id}, equipo={equipo_nombre}, estudiante={estudiante_nombre})"
