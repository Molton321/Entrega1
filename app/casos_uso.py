from domain.prestamo import Prestamo
from domain.excepciones import (
    LimitePrestamosExcedidoError,
    EquipoNoDisponibleError,
    EstudianteConMultaPendienteError,
)

LIMITE_PRESTAMOS_ACTIVOS = 2


class RegistrarPrestamo:
    """Caso de uso: registra un préstamo validando las reglas R1, R2 y R4."""

    def __init__(self, repositorio_prestamos, repositorio_equipos, repositorio_estudiantes, notificador, proveedor_fecha):
        self.repositorio_prestamos = repositorio_prestamos
        self.repositorio_equipos = repositorio_equipos
        self.repositorio_estudiantes = repositorio_estudiantes
        self.notificador = notificador
        self.proveedor_fecha = proveedor_fecha

    def ejecutar(self, equipo_id, estudiante_id):
        equipo = self.repositorio_equipos.buscar_por_id(equipo_id)
        estudiante = self.repositorio_estudiantes.buscar_por_id(estudiante_id)

        self._validar_disponibilidad(equipo)
        self._validar_sin_multa(estudiante)
        self._validar_limite_prestamos(estudiante_id)

        prestamo = Prestamo(equipo, estudiante, self.proveedor_fecha.hoy())
        equipo.marcar_prestado()

        self.repositorio_equipos.guardar(equipo)
        self.repositorio_prestamos.guardar(prestamo)

        self.notificador.enviar(
            f"Préstamo registrado. Fecha límite de devolución: {prestamo.fecha_limite}",
            estudiante,
        )
        return prestamo

    def _validar_disponibilidad(self, equipo):
        if not equipo.esta_disponible():
            raise EquipoNoDisponibleError(
                f"'{equipo.get_nombre()}' no está disponible (estado: {equipo.get_estado()})"
            )

    def _validar_sin_multa(self, estudiante):
        if estudiante.get_tiene_multa():
            raise EstudianteConMultaPendienteError(
                f"{estudiante.nombre} tiene una multa pendiente y no puede pedir prestado"
            )

    def _validar_limite_prestamos(self, estudiante_id):
        activos = self.repositorio_prestamos.listar_activos_por_estudiante(estudiante_id)
        if len(activos) >= LIMITE_PRESTAMOS_ACTIVOS:
            raise LimitePrestamosExcedidoError(
                f"El estudiante ya tiene {LIMITE_PRESTAMOS_ACTIVOS} préstamos activos"
            )


class RegistrarDevolucion:
    """Caso de uso: registra la devolución aplicando R5, R6 y R7."""

    def __init__(self, repositorio_prestamos, repositorio_equipos, repositorio_estudiantes, notificador, proveedor_fecha):
        self.repositorio_prestamos = repositorio_prestamos
        self.repositorio_equipos = repositorio_equipos
        self.repositorio_estudiantes = repositorio_estudiantes
        self.notificador = notificador
        self.proveedor_fecha = proveedor_fecha

    def ejecutar(self, prestamo_id, *, equipo_danado: bool):
        prestamo = self.repositorio_prestamos.buscar_por_id(prestamo_id)
        prestamo.marcar_devuelto(self.proveedor_fecha.hoy())

        self._actualizar_estado_equipo(prestamo.equipo, equipo_danado)
        self._aplicar_multa_si_corresponde(prestamo)

        self.repositorio_equipos.guardar(prestamo.equipo)
        self.repositorio_prestamos.guardar(prestamo)
        return prestamo

    def _actualizar_estado_equipo(self, equipo, equipo_danado):
        """R6: Si hay daño → EN_MANTENIMIENTO; si no → DISPONIBLE."""
        if equipo_danado:
            equipo.marcar_en_mantenimiento()
        else:
            equipo.marcar_disponible()

    def _aplicar_multa_si_corresponde(self, prestamo):
        """R7: Notifica al estudiante si se generó multa por retraso."""
        if prestamo.multa > 0:
            prestamo.estudiante.set_tiene_multa(True)
            self.repositorio_estudiantes.guardar(prestamo.estudiante)
            self.notificador.enviar(
                f"Devolución con retraso. Multa generada: ${prestamo.multa:,}",
                prestamo.estudiante,
            )


class GestionEquipos:
    """Servicio de aplicación para administrar el catálogo de equipos."""

    def __init__(self, repositorio_equipos):
        self.repositorio_equipos = repositorio_equipos

    def registrar(self, equipo):
        """Persiste un equipo nuevo en el repositorio."""
        return self.repositorio_equipos.guardar(equipo)

    def buscar_por_id(self, equipo_id):
        """Retorna el equipo correspondiente al ID dado."""
        return self.repositorio_equipos.buscar_por_id(equipo_id)

    def listar_todos(self):
        """Retorna todos los equipos registrados."""
        return self.repositorio_equipos.listar_todos()


class GestionEstudiantes:
    """Servicio de aplicación para administrar estudiantes."""

    def __init__(self, repositorio_estudiantes):
        self.repositorio_estudiantes = repositorio_estudiantes

    def registrar(self, estudiante):
        """Persiste un estudiante nuevo en el repositorio."""
        return self.repositorio_estudiantes.guardar(estudiante)

    def buscar_por_id(self, estudiante_id):
        """Retorna el estudiante correspondiente al ID dado."""
        return self.repositorio_estudiantes.buscar_por_id(estudiante_id)

    def listar_todos(self):
        """Retorna todos los estudiantes registrados."""
        return self.repositorio_estudiantes.listar_todos()
