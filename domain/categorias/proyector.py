from domain.categorias.categoria_equipo import CategoriaEquipo


class Proyector(CategoriaEquipo):

    @property
    def nombre(self) -> str:
        return "PROYECTOR"

    @property
    def plazo_maximo_dias(self) -> int:
        return 2

    @property
    def cuota_diaria(self) -> int:
        return 6_000
