from domain.categorias.categoria_equipo import CategoriaEquipo


class KitRobotica(CategoriaEquipo):


    @property
    def nombre(self) -> str:
        return "KIT_ROBOTICA"

    @property
    def plazo_maximo_dias(self) -> int:
        return 1

    @property
    def cuota_diaria(self) -> int:
        return 12_000
