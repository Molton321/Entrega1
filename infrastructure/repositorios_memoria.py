import datetime

from app.ports import RepositorioEquipos, RepositorioEstudiantes, RepositorioPrestamos
from domain.equipo import Equipo
from domain.estudiante import Estudiante
from domain.prestamo import Prestamo
from domain.categorias.portatil import Portatil
from domain.categorias.camara import Camara
from domain.categorias.kit_robotica import KitRobotica
from domain.categorias.proyector import Proyector


class RepositorioEstudiantesMemoria(RepositorioEstudiantes):
    def __init__(self):
        self._estudiantes = {}
        self._contador = 0

        ana   = Estudiante("Ana",    20, "Ingeniería de Sistemas")
        luis  = Estudiante("Luis",   22, "Diseño Industrial")
        luis.set_tiene_multa(True)                        # CA4: multa preexistente
        carlos = Estudiante("Carlos", 21, "Electrónica")  # tomará CAMARA-02 (setup CA3)
        pedro  = Estudiante("Pedro",  23, "Mecatrónica")  # CA5 y CA6

        for est in [ana, luis, carlos, pedro]:
            self.guardar(est)

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


class RepositorioEquiposMemoria(RepositorioEquipos):
    def __init__(self):
        self._equipos = {}
        self._contador = 0

        portatil_01  = Equipo("PORTATIL-01",  Portatil())    # CA1
        camara_01    = Equipo("CAMARA-01",    Camara())       # setup silencioso CA2
        camara_02    = Equipo("CAMARA-02",    Camara())       # CA3
        kit_01       = Equipo("KIT-01",       KitRobotica())  # intento rechazado CA2
        kit_02       = Equipo("KIT-02",       KitRobotica())  # intento rechazado CA4, daño CA5
        proyector_01 = Equipo("PROYECTOR-01", Proyector())    # CA6

        for eq in [portatil_01, camara_01, camara_02, kit_01, kit_02, proyector_01]:
            self.guardar(eq)

        # Setup CA3: CAMARA-02 ya está prestada al iniciar
        camara_02.marcar_prestado()

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


class RepositorioPrestamosMemoria(RepositorioPrestamos):
    def __init__(self, repo_equipos: RepositorioEquiposMemoria,
                 repo_estudiantes: RepositorioEstudiantesMemoria):
        self._prestamos = {}
        self._contador = 0

        # Setup CA3: Carlos tomó CAMARA-02 el 2026-10-01 (límite: 2026-10-03)
        camara_02 = next(e for e in repo_equipos.listar_todos() if e.nombre == "CAMARA-02")
        carlos    = next(e for e in repo_estudiantes.listar_todos() if e.nombre == "Carlos")
        prestamo_ca3 = Prestamo(camara_02, carlos, datetime.date(2026, 10, 1))
        self.guardar(prestamo_ca3)

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
