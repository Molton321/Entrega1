import datetime

from app.ports import Notificador, ProveedorFecha


class NotificadorConsola(Notificador):
    """R7: Notificación simulada imprimiendo en consola."""

    def enviar(self, mensaje, destinatario):
        print(f"[NOTIFICACION] → {destinatario.nombre}: {mensaje}")


class ProveedorFechaSistema(ProveedorFecha):
    """Entrega la fecha real del sistema."""

    def hoy(self):
        return datetime.date.today()


class ProveedorFechaFija(ProveedorFecha):
    """Fecha fija para el demo. Taller: fecha fija 2026-10-05."""

    def __init__(self, fecha):
        self._fecha = fecha

    def hoy(self):
        return self._fecha
