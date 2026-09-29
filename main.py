import datetime
import os

# ─── Infraestructura (Composition Root: solo main.py conoce clases concretas) ──
from infrastructure.adaptadores import NotificadorConsola, ProveedorFechaFija
from infrastructure.repositorios_sql import (
    RepositorioEquiposSQL,
    RepositorioEstudiantesSQL,
    RepositorioPrestamosSQL,
)
from infrastructure.repositorios_memoria import (
    RepositorioEquiposMemoria,
    RepositorioEstudiantesMemoria,
    RepositorioPrestamosMemoria,
)

# ─── Categorías (Composition Root para OCP) ────────────────────────────────
from domain.categorias.portatil import Portatil
from domain.categorias.camara import Camara
from domain.categorias.kit_robotica import KitRobotica
from domain.categorias.proyector import Proyector          # CA6: línea de composición

# ─── Dominio ────────────────────────────────────────────────────────────────
from domain.equipo import Equipo
from domain.estudiante import Estudiante
from domain.prestamo import Prestamo
from domain.excepciones import (
    LimitePrestamosExcedidoError,
    EquipoNoDisponibleError,
    EstudianteConMultaPendienteError,
)

# ─── Casos de uso ───────────────────────────────────────────────────────────
from app.casos_uso import RegistrarPrestamo, RegistrarDevolucion


# ─── Constantes del demo ────────────────────────────────────────────────────
NOMBRE_DB = "prestamos_demo.db"
FECHA_DEMO = datetime.date(2026, 10, 5)
FECHA_DEVOLUCION_TARDIA = datetime.date(2026, 10, 6)   # CA3: devolución tardía

# ─── LSP: cambiar solo esta línea para alternar entre persistencias ─────────
#   "sqlite"  → repositorios reales con SQLite
#   "memoria" → repositorios en memoria (demuestra LSP)
MODO_PERSISTENCIA = "sqlite"
# ────────────────────────────────────────────────────────────────────────────


def construir_registro_categorias():
    """Mapa nombre→objeto para que el repo SQL reconstruya categorías. OCP."""
    return {
        "PORTATIL": Portatil(),
        "CAMARA": Camara(),
        "KIT_ROBOTICA": KitRobotica(),
        "PROYECTOR": Proyector(),
    }


def construir_repositorios(registro):
    """Inyecta la implementación según MODO_PERSISTENCIA (LSP)."""
    if MODO_PERSISTENCIA == "sqlite":
        repo_equipos = RepositorioEquiposSQL(NOMBRE_DB, registro)
        repo_estudiantes = RepositorioEstudiantesSQL(NOMBRE_DB)
        repo_prestamos = RepositorioPrestamosSQL(NOMBRE_DB, repo_equipos, repo_estudiantes)
    else:
        repo_equipos = RepositorioEquiposMemoria()
        repo_estudiantes = RepositorioEstudiantesMemoria()
        repo_prestamos = RepositorioPrestamosMemoria()
    return repo_equipos, repo_estudiantes, repo_prestamos


def cargar_datos_iniciales(repo_equipos, repo_estudiantes, repo_prestamos):
    """Carga el estado inicial en la BD para reproducir todos los casos de aceptación."""

    # Estudiantes
    ana = Estudiante("Ana", 20, "Ingeniería de Sistemas")
    luis = Estudiante("Luis", 22, "Diseño Industrial")
    luis.set_tiene_multa(True)                              # CA4: multa preexistente
    carlos = Estudiante("Carlos", 21, "Electrónica")        # tomará CAMARA-02 en setup CA3
    pedro = Estudiante("Pedro", 23, "Mecatrónica")          # CA5 y CA6

    for est in [ana, luis, carlos, pedro]:
        repo_estudiantes.guardar(est)

    # Equipos
    portatil_01 = Equipo("PORTATIL-01", Portatil())         # CA1
    camara_01 = Equipo("CAMARA-01", Camara())               # setup silencioso CA2
    camara_02 = Equipo("CAMARA-02", Camara())               # CA3
    kit_01 = Equipo("KIT-01", KitRobotica())                # intento rechazado CA2
    kit_02 = Equipo("KIT-02", KitRobotica())                # intento rechazado CA4, daño CA5
    proyector_01 = Equipo("PROYECTOR-01", Proyector())      # CA6

    for eq in [portatil_01, camara_01, camara_02, kit_01, kit_02, proyector_01]:
        repo_equipos.guardar(eq)

    # Setup CA3: Carlos tomó CAMARA-02 el 2026-10-01 (límite: 2026-10-03)
    prestamo_ca3 = Prestamo(camara_02, carlos, datetime.date(2026, 10, 1))
    camara_02.marcar_prestado()
    repo_equipos.guardar(camara_02)
    repo_prestamos.guardar(prestamo_ca3)

    return {
        "ana": ana, "luis": luis, "carlos": carlos, "pedro": pedro,
        "portatil_01": portatil_01, "camara_01": camara_01,
        "camara_02": camara_02, "kit_01": kit_01,
        "kit_02": kit_02, "proyector_01": proyector_01,
        "prestamo_ca3": prestamo_ca3,
    }


def titulo_caso(numero, descripcion):
    print(f"\n{'─' * 65}")
    print(f"  CA{numero}: {descripcion}")
    print(f"{'─' * 65}")


def ejecutar_demo(repo_equipos, repo_estudiantes, repo_prestamos, datos):
    notificador = NotificadorConsola()

    registrar_prestamo = RegistrarPrestamo(
        repo_prestamos, repo_equipos, repo_estudiantes,
        notificador, ProveedorFechaFija(FECHA_DEMO),
    )
    registrar_devolucion = RegistrarDevolucion(
        repo_prestamos, repo_equipos, repo_estudiantes,
        notificador, ProveedorFechaFija(FECHA_DEMO),
    )
    registrar_devolucion_tardia = RegistrarDevolucion(
        repo_prestamos, repo_equipos, repo_estudiantes,
        notificador, ProveedorFechaFija(FECHA_DEVOLUCION_TARDIA),
    )

    ana_id = datos["ana"].get_id()
    luis_id = datos["luis"].get_id()
    pedro_id = datos["pedro"].get_id()
    portatil_01_id = datos["portatil_01"].get_id()
    camara_01_id = datos["camara_01"].get_id()
    kit_01_id = datos["kit_01"].get_id()
    kit_02_id = datos["kit_02"].get_id()
    proyector_01_id = datos["proyector_01"].get_id()
    prestamo_ca3_id = datos["prestamo_ca3"].get_id()

    # ── CA1: Préstamo exitoso ─────────────────────────────────────────────
    titulo_caso(1, "Ana pide PORTATIL-01 (sin préstamos previos)")
    try:
        prestamo = registrar_prestamo.ejecutar(portatil_01_id, ana_id)
        print(f"  OK  Prestamo registrado | Fecha limite: {prestamo.fecha_limite}")
    except (LimitePrestamosExcedidoError, EquipoNoDisponibleError, EstudianteConMultaPendienteError) as exc:
        print(f"  ERROR  {exc}")

    # Setup silencioso CA2: Ana ahora necesita 2 préstamos activos
    registrar_prestamo.ejecutar(camara_01_id, ana_id)

    # ── CA2: Límite de préstamos ──────────────────────────────────────────
    titulo_caso(2, "Ana intenta un 3er prestamo (ya tiene 2 activos) → rechazado")
    try:
        registrar_prestamo.ejecutar(kit_01_id, ana_id)
        print("  ERROR  Debio rechazarse pero no lo hizo")
    except LimitePrestamosExcedidoError as exc:
        print(f"  OK  Rechazado correctamente: {exc}")

    # ── CA3: Devolución tardía con multa ─────────────────────────────────
    titulo_caso(3, "CAMARA-02 devuelta el 2026-10-06 (3 dias tarde) → multa $24.000")
    try:
        prestamo = registrar_devolucion_tardia.ejecutar(prestamo_ca3_id, equipo_danado=False)
        retraso = (FECHA_DEVOLUCION_TARDIA - prestamo.fecha_limite).days
        print(f"  OK  Devolucion registrada")
        print(f"      Fecha limite: {prestamo.fecha_limite} | Fecha devolucion: {FECHA_DEVOLUCION_TARDIA}")
        print(f"      Retraso: {retraso} dia(s) | Multa generada: ${prestamo.multa:,}")
    except Exception as exc:
        print(f"  ERROR  {exc}")

    # ── CA4: Estudiante con multa pendiente ───────────────────────────────
    titulo_caso(4, "Luis (multa pendiente) intenta pedir equipo → rechazado")
    try:
        registrar_prestamo.ejecutar(kit_02_id, luis_id)
        print("  ERROR  Debio rechazarse pero no lo hizo")
    except EstudianteConMultaPendienteError as exc:
        print(f"  OK  Rechazado correctamente: {exc}")

    # ── CA5: Equipo dañado → EN_MANTENIMIENTO ────────────────────────────
    titulo_caso(5, "Equipo devuelto con dano → EN_MANTENIMIENTO, no se puede prestar")
    try:
        prestamo_pedro = registrar_prestamo.ejecutar(kit_02_id, pedro_id)
        print(f"  OK  Pedro tomo KIT-02 | Fecha limite: {prestamo_pedro.fecha_limite}")

        registrar_devolucion.ejecutar(prestamo_pedro.get_id(), equipo_danado=True)
        estado_actual = repo_equipos.buscar_por_id(kit_02_id).get_estado()
        print(f"  OK  Devuelto con dano | Estado del equipo: {estado_actual}")

        try:
            registrar_prestamo.ejecutar(kit_02_id, pedro_id)
            print("  ERROR  Debio rechazarse pero no lo hizo")
        except EquipoNoDisponibleError as exc:
            print(f"  OK  Prestamo rechazado correctamente: {exc}")
    except Exception as exc:
        print(f"  ERROR inesperado: {exc}")

    # ── CA6: Nueva categoría PROYECTOR (OCP) ─────────────────────────────
    titulo_caso(6, "PROYECTOR-01 (nueva categoria OCP) → funciona sin modificar dominio")
    try:
        prestamo = registrar_prestamo.ejecutar(proyector_01_id, pedro_id)
        cat = prestamo.equipo.get_categoria()
        print(f"  OK  Prestamo de {cat.nombre} registrado")
        print(f"      Plazo: {cat.plazo_maximo_dias} dias | Cuota: ${cat.cuota_diaria:,}/dia")
        print(f"      Fecha limite: {prestamo.fecha_limite}")
        print(f"      [Ningun archivo del dominio ni casos de uso fue modificado]")
    except (LimitePrestamosExcedidoError, EquipoNoDisponibleError, EstudianteConMultaPendienteError) as exc:
        print(f"  ERROR  {exc}")


if __name__ == "__main__":
    # Limpiar BD de demos anteriores para empezar desde cero
    if MODO_PERSISTENCIA == "sqlite" and os.path.exists(NOMBRE_DB):
        os.remove(NOMBRE_DB)

    print("\n" + "=" * 65)
    print("  DEMO - Sistema de Prestamo de Equipos del Laboratorio")
    print(f"  Fecha del sistema (fija): {FECHA_DEMO}")
    print(f"  Persistencia: {MODO_PERSISTENCIA.upper()}")
    print("=" * 65)

    registro = construir_registro_categorias()
    repo_equipos, repo_estudiantes, repo_prestamos = construir_repositorios(registro)
    datos = cargar_datos_iniciales(repo_equipos, repo_estudiantes, repo_prestamos)

    ejecutar_demo(repo_equipos, repo_estudiantes, repo_prestamos, datos)

    print(f"\n{'=' * 65}")
    print("  Demo completado exitosamente.")
    print("=" * 65 + "\n")
