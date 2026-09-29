from domain.categorias.categoria_equipo import CategoriaEquipo


class Equipo:
    """Entidad que representa un equipo físico del laboratorio."""

    ESTADOS = ["DISPONIBLE", "PRESTADO", "EN_MANTENIMIENTO"]

    def __init__(self, nombre: str, categoria: CategoriaEquipo):
        self.id = None
        self.nombre = nombre
        self.categoria = categoria
        self.estado = "DISPONIBLE"

    # --- Transiciones de estado (R2, R6) ---

    def marcar_prestado(self):
        self.estado = "PRESTADO"

    def marcar_disponible(self):
        self.estado = "DISPONIBLE"

    def marcar_en_mantenimiento(self):
        self.estado = "EN_MANTENIMIENTO"

    def esta_disponible(self) -> bool:
        return self.estado == "DISPONIBLE"

    # --- Getters / Setters ---

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_nombre(self):
        return self.nombre

    def get_estado(self):
        return self.estado

    def set_estado(self, estado):
        """Usado solo por la capa de infraestructura al reconstruir desde BD."""
        self.estado = estado

    def get_categoria(self):
        return self.categoria

    def mostrar_informacion(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria.nombre,
            "estado": self.estado,
            "cuota_diaria": self.categoria.cuota_diaria,
            "plazo_maximo_dias": self.categoria.plazo_maximo_dias,
        }

    def __str__(self):
        return f"Equipo({self.nombre}, {self.categoria.nombre}, {self.estado})"
