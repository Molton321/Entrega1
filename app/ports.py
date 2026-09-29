from abc import ABC, abstractmethod


class RepositorioEquipos(ABC):
    @abstractmethod
    def guardar(self, equipo):
        pass

    @abstractmethod
    def buscar_por_id(self, equipo_id):
        pass

    @abstractmethod
    def listar_todos(self):
        pass


class RepositorioEstudiantes(ABC):
    @abstractmethod
    def guardar(self, estudiante):
        pass

    @abstractmethod
    def buscar_por_id(self, estudiante_id):
        pass

    @abstractmethod
    def listar_todos(self):
        pass


class RepositorioPrestamos(ABC):
    @abstractmethod
    def guardar(self, prestamo):
        pass

    @abstractmethod
    def buscar_por_id(self, prestamo_id):
        pass

    @abstractmethod
    def listar_todos(self):
        pass

    @abstractmethod
    def listar_activos_por_estudiante(self, estudiante_id):
        pass


class Notificador(ABC):
    @abstractmethod
    def enviar(self, mensaje, destinatario):
        pass


class ProveedorFecha(ABC):
    @abstractmethod
    def hoy(self):
        """Retorna la fecha actual como datetime.date. R3, R5."""
        pass
