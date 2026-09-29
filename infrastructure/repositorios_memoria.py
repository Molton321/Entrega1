from app.ports import RepositorioEquipos, RepositorioEstudiantes, RepositorioPrestamos


class RepositorioEquiposMemoria(RepositorioEquipos):
    def __init__(self):
        self._equipos = {}
        self._contador = 0

    def guardar(self, equipo):
        """Guarda o actualiza un equipo. Asigna ID automático si no tiene."""
        if equipo.id is None:
            self._contador += 1
            equipo.set_id(self._contador)
        self._equipos[equipo.id] = equipo
        return equipo

    def buscar_por_id(self, equipo_id):
        """Busca un equipo por su identificador."""
        return self._equipos.get(equipo_id)

    def listar_todos(self):
        """Devuelve todos los equipos almacenados."""
        return list(self._equipos.values())


class RepositorioEstudiantesMemoria(RepositorioEstudiantes):
    def __init__(self):
        self._estudiantes = {}
        self._contador = 0

    def guardar(self, estudiante):
        """Guarda o actualiza un estudiante. Asigna ID automático si no tiene."""
        if estudiante.id is None:
            self._contador += 1
            estudiante.set_id(self._contador)
        self._estudiantes[estudiante.id] = estudiante
        return estudiante

    def buscar_por_id(self, estudiante_id):
        """Busca un estudiante por su identificador."""
        return self._estudiantes.get(estudiante_id)

    def listar_todos(self):
        """Devuelve todos los estudiantes almacenados."""
        return list(self._estudiantes.values())


class RepositorioPrestamosMemoria(RepositorioPrestamos):
    def __init__(self):
        self._prestamos = {}
        self._contador = 0

    def guardar(self, prestamo):
        """Guarda o actualiza un préstamo. Asigna ID automático si no tiene."""
        if prestamo.id is None:
            self._contador += 1
            prestamo.set_id(self._contador)
        self._prestamos[prestamo.id] = prestamo
        return prestamo

    def buscar_por_id(self, prestamo_id):
        """Busca un préstamo por su identificador."""
        return self._prestamos.get(prestamo_id)

    def listar_todos(self):
        """Devuelve todos los préstamos almacenados."""
        return list(self._prestamos.values())

    def listar_activos_por_estudiante(self, estudiante_id):
        """R1: Retorna solo los préstamos activos de un estudiante dado."""
        return [
            p for p in self._prestamos.values()
            if p.estudiante.get_id() == estudiante_id and p.esta_activo()
        ]
