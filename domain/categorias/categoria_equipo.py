from abc import ABC, abstractmethod


class CategoriaEquipo(ABC):

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre de la categoría (ej: 'PORTATIL')."""

    @property
    @abstractmethod
    def plazo_maximo_dias(self) -> int:
        """Días máximos del préstamo. R3."""

    @property
    @abstractmethod
    def cuota_diaria(self) -> int:
        """Tarifa en pesos por día de retraso. R5."""

    def calcular_multa(self, dias_retraso: int) -> int:
        """R5: multa = días completos de retraso × cuota diaria."""
        return dias_retraso * self.cuota_diaria
