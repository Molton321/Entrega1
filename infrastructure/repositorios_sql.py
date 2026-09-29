import sqlite3
import datetime

from app.ports import RepositorioEquipos, RepositorioEstudiantes, RepositorioPrestamos
from domain.equipo import Equipo
from domain.estudiante import Estudiante
from domain.prestamo import Prestamo


class RepositorioEquiposSQL(RepositorioEquipos):
    """Adaptador SQLite para equipos. Recibe un registro de categorías para
    reconstruir objetos CategoriaEquipo al leer de la BD (OCP)."""

    def __init__(self, nombre_db, registro_categorias):
        self._db = nombre_db
        self._registro_categorias = registro_categorias
        self._crear_tabla()

    def _crear_tabla(self):
        with sqlite3.connect(self._db) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS equipos (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre   TEXT    NOT NULL,
                    categoria TEXT   NOT NULL,
                    estado   TEXT    NOT NULL
                )
            """)

    def guardar(self, equipo):
        """INSERT si es nuevo, UPDATE si ya tiene id."""
        with sqlite3.connect(self._db) as con:
            if equipo.id is None:
                cursor = con.execute(
                    "INSERT INTO equipos (nombre, categoria, estado) VALUES (?, ?, ?)",
                    (equipo.get_nombre(), equipo.get_categoria().nombre, equipo.get_estado()),
                )
                equipo.set_id(cursor.lastrowid)
            else:
                con.execute(
                    "UPDATE equipos SET nombre=?, categoria=?, estado=? WHERE id=?",
                    (equipo.get_nombre(), equipo.get_categoria().nombre, equipo.get_estado(), equipo.id),
                )
        return equipo

    def buscar_por_id(self, equipo_id):
        with sqlite3.connect(self._db) as con:
            fila = con.execute(
                "SELECT id, nombre, categoria, estado FROM equipos WHERE id=?",
                (equipo_id,),
            ).fetchone()
        return self._fila_a_equipo(fila) if fila else None

    def listar_todos(self):
        with sqlite3.connect(self._db) as con:
            filas = con.execute("SELECT id, nombre, categoria, estado FROM equipos").fetchall()
        return [self._fila_a_equipo(f) for f in filas]

    def _fila_a_equipo(self, fila):
        id_, nombre, categoria_nombre, estado = fila
        categoria = self._registro_categorias[categoria_nombre]
        equipo = Equipo(nombre, categoria)
        equipo.set_id(id_)
        equipo.set_estado(estado)
        return equipo


class RepositorioEstudiantesSQL(RepositorioEstudiantes):
    """Adaptador SQLite para estudiantes."""

    def __init__(self, nombre_db):
        self._db = nombre_db
        self._crear_tabla()

    def _crear_tabla(self):
        with sqlite3.connect(self._db) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS estudiantes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre      TEXT    NOT NULL,
                    edad        INTEGER NOT NULL,
                    carrera     TEXT    NOT NULL,
                    tiene_multa INTEGER NOT NULL DEFAULT 0
                )
            """)

    def guardar(self, estudiante):
        """INSERT si es nuevo, UPDATE si ya tiene id."""
        with sqlite3.connect(self._db) as con:
            if estudiante.id is None:
                cursor = con.execute(
                    "INSERT INTO estudiantes (nombre, edad, carrera, tiene_multa) VALUES (?, ?, ?, ?)",
                    (estudiante.nombre, estudiante.edad, estudiante.carrera, int(estudiante.get_tiene_multa())),
                )
                estudiante.set_id(cursor.lastrowid)
            else:
                con.execute(
                    "UPDATE estudiantes SET nombre=?, edad=?, carrera=?, tiene_multa=? WHERE id=?",
                    (estudiante.nombre, estudiante.edad, estudiante.carrera, int(estudiante.get_tiene_multa()), estudiante.id),
                )
        return estudiante

    def buscar_por_id(self, estudiante_id):
        with sqlite3.connect(self._db) as con:
            fila = con.execute(
                "SELECT id, nombre, edad, carrera, tiene_multa FROM estudiantes WHERE id=?",
                (estudiante_id,),
            ).fetchone()
        return self._fila_a_estudiante(fila) if fila else None

    def listar_todos(self):
        with sqlite3.connect(self._db) as con:
            filas = con.execute(
                "SELECT id, nombre, edad, carrera, tiene_multa FROM estudiantes"
            ).fetchall()
        return [self._fila_a_estudiante(f) for f in filas]

    def _fila_a_estudiante(self, fila):
        id_, nombre, edad, carrera, tiene_multa = fila
        estudiante = Estudiante(nombre, edad, carrera)
        estudiante.set_id(id_)
        estudiante.set_tiene_multa(bool(tiene_multa))
        return estudiante


class RepositorioPrestamosSQL(RepositorioPrestamos):
    """Adaptador SQLite para préstamos. Depende de los otros dos repositorios
    para reconstruir las entidades Equipo y Estudiante al leer de la BD."""

    def __init__(self, nombre_db, repositorio_equipos, repositorio_estudiantes):
        self._db = nombre_db
        self._repo_equipos = repositorio_equipos
        self._repo_estudiantes = repositorio_estudiantes
        self._crear_tabla()

    def _crear_tabla(self):
        with sqlite3.connect(self._db) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipo_id        INTEGER NOT NULL,
                    estudiante_id    INTEGER NOT NULL,
                    fecha_prestamo   TEXT    NOT NULL,
                    fecha_limite     TEXT    NOT NULL,
                    fecha_devolucion TEXT,
                    multa            INTEGER NOT NULL DEFAULT 0,
                    estado           TEXT    NOT NULL
                )
            """)

    def guardar(self, prestamo):
        """INSERT si es nuevo, UPDATE si ya tiene id."""
        fecha_dev = prestamo.fecha_devolucion.isoformat() if prestamo.fecha_devolucion else None
        with sqlite3.connect(self._db) as con:
            if prestamo.id is None:
                cursor = con.execute(
                    """INSERT INTO prestamos
                       (equipo_id, estudiante_id, fecha_prestamo, fecha_limite, fecha_devolucion, multa, estado)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        prestamo.equipo.id,
                        prestamo.estudiante.id,
                        prestamo.fecha_prestamo.isoformat(),
                        prestamo.fecha_limite.isoformat(),
                        fecha_dev,
                        prestamo.multa,
                        prestamo.estado,
                    ),
                )
                prestamo.set_id(cursor.lastrowid)
            else:
                con.execute(
                    """UPDATE prestamos SET
                       equipo_id=?, estudiante_id=?, fecha_prestamo=?, fecha_limite=?,
                       fecha_devolucion=?, multa=?, estado=? WHERE id=?""",
                    (
                        prestamo.equipo.id,
                        prestamo.estudiante.id,
                        prestamo.fecha_prestamo.isoformat(),
                        prestamo.fecha_limite.isoformat(),
                        fecha_dev,
                        prestamo.multa,
                        prestamo.estado,
                        prestamo.id,
                    ),
                )
        return prestamo

    def buscar_por_id(self, prestamo_id):
        with sqlite3.connect(self._db) as con:
            fila = con.execute(
                "SELECT id, equipo_id, estudiante_id, fecha_prestamo, fecha_limite, fecha_devolucion, multa, estado FROM prestamos WHERE id=?",
                (prestamo_id,),
            ).fetchone()
        return self._fila_a_prestamo(fila) if fila else None

    def listar_todos(self):
        with sqlite3.connect(self._db) as con:
            filas = con.execute(
                "SELECT id, equipo_id, estudiante_id, fecha_prestamo, fecha_limite, fecha_devolucion, multa, estado FROM prestamos"
            ).fetchall()
        return [self._fila_a_prestamo(f) for f in filas]

    def listar_activos_por_estudiante(self, estudiante_id):
        """R1: Solo los préstamos en estado ACTIVO del estudiante dado."""
        with sqlite3.connect(self._db) as con:
            filas = con.execute(
                "SELECT id, equipo_id, estudiante_id, fecha_prestamo, fecha_limite, fecha_devolucion, multa, estado FROM prestamos WHERE estudiante_id=? AND estado='ACTIVO'",
                (estudiante_id,),
            ).fetchall()
        return [self._fila_a_prestamo(f) for f in filas]

    def _fila_a_prestamo(self, fila):
        id_, equipo_id, estudiante_id, fecha_p, fecha_l, fecha_d, multa, estado = fila
        equipo = self._repo_equipos.buscar_por_id(equipo_id)
        estudiante = self._repo_estudiantes.buscar_por_id(estudiante_id)

        prestamo = Prestamo(equipo, estudiante, datetime.date.fromisoformat(fecha_p))
        prestamo.set_id(id_)
        prestamo.fecha_limite = datetime.date.fromisoformat(fecha_l)
        prestamo.fecha_devolucion = datetime.date.fromisoformat(fecha_d) if fecha_d else None
        prestamo.multa = multa
        prestamo.estado = estado
        return prestamo