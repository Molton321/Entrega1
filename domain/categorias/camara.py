from domain.categorias.categoria_equipo import CategoriaEquipo


class Camara(CategoriaEquipo):

    @property
    def nombre(self) -> str:
        return "CAMARA"

    @property
    def plazo_maximo_dias(self) -> int:
        return 2

    @property
    def cuota_diaria(self) -> int:
        return 8_000
