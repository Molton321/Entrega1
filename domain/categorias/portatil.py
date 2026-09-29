from domain.categorias.categoria_equipo import CategoriaEquipo


class Portatil(CategoriaEquipo):

    @property
    def nombre(self) -> str:
        return "PORTATIL"

    @property
    def plazo_maximo_dias(self) -> int:
        return 3

    @property
    def cuota_diaria(self) -> int:
        return 5_000
