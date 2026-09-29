import os
import datetime

# ─── Infraestructura ────────────────────────────────────────────────────────────
from infrastructure.adaptadores import NotificadorConsola, ProveedorFechaSistema, ProveedorFechaFija
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

# ─── Categorías ─────────────────────────────────────────────────────────────────
from domain.categorias.portatil import Portatil
from domain.categorias.camara import Camara
from domain.categorias.kit_robotica import KitRobotica
from domain.categorias.proyector import Proyector

# ─── Dominio ────────────────────────────────────────────────────────────────────
from domain.equipo import Equipo
from domain.estudiante import Estudiante
from domain.excepciones import (
    LimitePrestamosExcedidoError,
    EquipoNoDisponibleError,
    EstudianteConMultaPendienteError,
)

# ─── Casos de uso ───────────────────────────────────────────────────────────────
from app.casos_uso import (
    RegistrarPrestamo,
    RegistrarDevolucion,
    GestionEquipos,
    GestionEstudiantes,
)

NOMBRE_DB = "prestamos.db"

CATEGORIAS = {
    "1": Portatil(),
    "2": Camara(),
    "3": KitRobotica(),
    "4": Proyector(),
}


# ══════════════════════════════════════════════════════════════════════════════
# Helpers de pantalla
# ══════════════════════════════════════════════════════════════════════════════

def limpiar():
    os.system("clear" if os.name == "posix" else "cls")


def separador():
    print("─" * 55)


def titulo(texto):
    separador()
    print(f"  {texto}")
    separador()


def pausa():
    input("\n  [Enter para continuar]")


def pedir_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  ✗ Ingresa un número válido.")


def pedir_opcion(prompt, validas):
    while True:
        v = input(prompt).strip()
        if v in validas:
            return v
        print(f"  ✗ Opción inválida. Elige entre: {', '.join(validas)}")


# ══════════════════════════════════════════════════════════════════════════════
# Construcción de repositorios
# ══════════════════════════════════════════════════════════════════════════════

def elegir_repositorio():
    limpiar()
    titulo("Sistema de Préstamo de Equipos")
    print("  ¿Qué repositorio deseas usar?\n")
    print("  1. Memoria  (datos de ejemplo precargados)")
    print("  2. SQLite   (base de datos persistente)")
    print()
    opcion = pedir_opcion("  Opción: ", {"1", "2"})

    if opcion == "1":
        repo_eq  = RepositorioEquiposMemoria()
        repo_est = RepositorioEstudiantesMemoria()
        repo_pr  = RepositorioPrestamosMemoria(repo_eq, repo_est)
        print("\n  ✓ Repositorio en memoria cargado con datos de ejemplo.")
    else:
        registro = {"PORTATIL": Portatil(), "CAMARA": Camara(),
                    "KIT_ROBOTICA": KitRobotica(), "PROYECTOR": Proyector()}
        repo_eq  = RepositorioEquiposSQL(NOMBRE_DB, registro)
        repo_est = RepositorioEstudiantesSQL(NOMBRE_DB)
        repo_pr  = RepositorioPrestamosSQL(NOMBRE_DB, repo_eq, repo_est)
        print(f"\n  ✓ Conectado a SQLite → {NOMBRE_DB}")

    pausa()
    return repo_eq, repo_est, repo_pr


def elegir_proveedor_fecha():
    limpiar()
    titulo("Configurar Fecha del Sistema")
    hoy = datetime.date.today()
    print(f"  Fecha real del sistema: {hoy}\n")
    print("  1. Usar fecha del sistema  (siempre la fecha de hoy)")
    print("  2. Usar fecha fija         (tú defines la fecha)")
    print()
    opcion = pedir_opcion("  Opción: ", {"1", "2"})

    if opcion == "1":
        proveedor = ProveedorFechaSistema()
        print(f"\n  ✓ Proveedor: sistema  →  {proveedor.hoy()}")
    else:
        while True:
            raw = input("  Ingresa la fecha (YYYY-MM-DD): ").strip()
            try:
                fecha = datetime.date.fromisoformat(raw)
                proveedor = ProveedorFechaFija(fecha)
                print(f"\n  ✓ Proveedor: fecha fija  →  {fecha}")
                break
            except ValueError:
                print("  ✗ Formato inválido. Usa YYYY-MM-DD (ej: 2026-10-05)")

    pausa()
    return proveedor


# ══════════════════════════════════════════════════════════════════════════════
# Vistas de listado
# ══════════════════════════════════════════════════════════════════════════════

def mostrar_equipos(repo_eq):
    equipos = repo_eq.listar_todos()
    if not equipos:
        print("  (sin equipos registrados)")
        return
    print(f"  {'ID':<4} {'Nombre':<16} {'Categoría':<14} {'Estado'}")
    separador()
    for e in equipos:
        cat = e.get_categoria()
        print(f"  {e.get_id()!s:<4} {e.get_nombre():<16} {cat.nombre:<14} {e.get_estado()}")


def mostrar_estudiantes(repo_est):
    estudiantes = repo_est.listar_todos()
    if not estudiantes:
        print("  (sin estudiantes registrados)")
        return
    print(f"  {'ID':<4} {'Nombre':<16} {'Edad':<6} {'Carrera':<20} Multa")
    separador()
    for est in estudiantes:
        multa = "SÍ" if est.get_tiene_multa() else "No"
        print(f"  {est.get_id()!s:<4} {est.nombre:<16} {est.edad:<6} {est.carrera:<20} {multa}")


def mostrar_prestamos(repo_pr):
    prestamos = repo_pr.listar_todos()
    if not prestamos:
        print("  (sin préstamos registrados)")
        return
    print(f"  {'ID':<4} {'Equipo':<16} {'Estudiante':<14} {'Estado':<10} {'F.Límite':<12} Multa")
    separador()
    for p in prestamos:
        multa = f"${p.multa:,}" if p.multa else "-"
        print(f"  {p.get_id()!s:<4} {p.equipo.get_nombre():<16} {p.estudiante.nombre:<14} "
              f"{p.estado:<10} {str(p.fecha_limite):<12} {multa}")


def mostrar_categorias():
    print(f"  {'#':<3} {'Categoría':<14} {'Plazo':<8} Cuota/día")
    separador()
    for k, cat in CATEGORIAS.items():
        print(f"  {k:<3} {cat.nombre:<14} {cat.plazo_maximo_dias} días   ${cat.cuota_diaria:,}")


# ══════════════════════════════════════════════════════════════════════════════
# Acciones de casos de uso
# ══════════════════════════════════════════════════════════════════════════════

def accion_registrar_prestamo(repo_eq, repo_est, repo_pr, proveedor_fecha):
    titulo("Registrar Préstamo")
    print("  Equipos disponibles:\n")
    disponibles = [e for e in repo_eq.listar_todos() if e.esta_disponible()]
    if not disponibles:
        print("  ✗ No hay equipos disponibles.")
        pausa()
        return
    print(f"  {'ID':<4} {'Nombre':<16} {'Categoría':<14} Plazo")
    separador()
    for e in disponibles:
        cat = e.get_categoria()
        print(f"  {e.get_id()!s:<4} {e.get_nombre():<16} {cat.nombre:<14} {cat.plazo_maximo_dias} días")

    print()
    equipo_id = pedir_int("  ID del equipo: ")

    print("\n  Estudiantes:\n")
    mostrar_estudiantes(repo_est)
    print()
    estudiante_id = pedir_int("  ID del estudiante: ")

    caso = RegistrarPrestamo(repo_pr, repo_eq, repo_est,
                             NotificadorConsola(), proveedor_fecha)
    try:
        prestamo = caso.ejecutar(equipo_id, estudiante_id)
        print(f"\n  ✓ Préstamo #{prestamo.get_id()} registrado.")
        print(f"    Equipo    : {prestamo.equipo.get_nombre()}")
        print(f"    Estudiante: {prestamo.estudiante.nombre}")
        print(f"    Fecha hoy : {prestamo.fecha_prestamo}")
        print(f"    Límite    : {prestamo.fecha_limite}")
    except (LimitePrestamosExcedidoError, EquipoNoDisponibleError,
            EstudianteConMultaPendienteError) as exc:
        print(f"\n  ✗ Préstamo rechazado: {exc}")
    pausa()


def accion_registrar_devolucion(repo_eq, repo_est, repo_pr, proveedor_fecha):
    titulo("Registrar Devolución")
    activos = [p for p in repo_pr.listar_todos() if p.esta_activo()]
    if not activos:
        print("  ✗ No hay préstamos activos.")
        pausa()
        return

    print("  Préstamos activos:\n")
    print(f"  {'ID':<4} {'Equipo':<16} {'Estudiante':<14} F.Límite")
    separador()
    for p in activos:
        print(f"  {p.get_id()!s:<4} {p.equipo.get_nombre():<16} "
              f"{p.estudiante.nombre:<14} {p.fecha_limite}")

    print()
    prestamo_id = pedir_int("  ID del préstamo a devolver: ")
    danado = pedir_opcion("  ¿El equipo tiene daños? (s/n): ", {"s", "n"}) == "s"

    caso = RegistrarDevolucion(repo_pr, repo_eq, repo_est,
                               NotificadorConsola(), proveedor_fecha)
    try:
        prestamo = caso.ejecutar(prestamo_id, equipo_danado=danado)
        print(f"\n  ✓ Devolución registrada.")
        print(f"    Equipo    : {prestamo.equipo.get_nombre()} → {prestamo.equipo.get_estado()}")
        print(f"    Fecha dev.: {prestamo.fecha_devolucion}")
        if prestamo.multa > 0:
            print(f"    ⚠  Multa generada: ${prestamo.multa:,}")
        else:
            print("    Sin multa.")
    except Exception as exc:
        print(f"\n  ✗ Error: {exc}")
    pausa()


def accion_registrar_equipo(repo_eq):
    titulo("Registrar Equipo")
    nombre = input("  Nombre del equipo: ").strip()
    if not nombre:
        print("  ✗ El nombre no puede estar vacío.")
        pausa()
        return

    print("\n  Categorías disponibles:\n")
    mostrar_categorias()
    print()
    clave = pedir_opcion("  Número de categoría: ", set(CATEGORIAS))
    categoria = CATEGORIAS[clave]

    equipo = Equipo(nombre, categoria)
    GestionEquipos(repo_eq).registrar(equipo)
    print(f"\n  ✓ Equipo '{nombre}' registrado con categoría {categoria.nombre}.")
    pausa()


def accion_registrar_estudiante(repo_est):
    titulo("Registrar Estudiante")
    nombre  = input("  Nombre  : ").strip()
    edad    = pedir_int("  Edad    : ")
    carrera = input("  Carrera : ").strip()

    if not nombre or not carrera:
        print("  ✗ Nombre y carrera son obligatorios.")
        pausa()
        return

    est = Estudiante(nombre, edad, carrera)
    GestionEstudiantes(repo_est).registrar(est)
    print(f"\n  ✓ Estudiante '{nombre}' registrado (ID: {est.get_id()}).")
    pausa()


def accion_listar(repo_eq, repo_est, repo_pr):
    while True:
        limpiar()
        titulo("Consultar")
        print("  1. Equipos")
        print("  2. Estudiantes")
        print("  3. Préstamos")
        print("  0. Volver")
        print()
        op = pedir_opcion("  Opción: ", {"0", "1", "2", "3"})
        if op == "0":
            break
        limpiar()
        if op == "1":
            titulo("Equipos")
            mostrar_equipos(repo_eq)
        elif op == "2":
            titulo("Estudiantes")
            mostrar_estudiantes(repo_est)
        elif op == "3":
            titulo("Préstamos")
            mostrar_prestamos(repo_pr)
        pausa()


# ══════════════════════════════════════════════════════════════════════════════
# Menú principal
# ══════════════════════════════════════════════════════════════════════════════

def menu_principal(repo_eq, repo_est, repo_pr, proveedor_fecha):
    while True:
        limpiar()
        titulo("Menú Principal")
        print(f"  Fecha activa : {proveedor_fecha.hoy()}\n")
        print("  1. Registrar préstamo")
        print("  2. Registrar devolución")
        print("  3. Registrar nuevo equipo")
        print("  4. Registrar nuevo estudiante")
        print("  5. Consultar datos")
        print("  0. Salir")
        print()
        op = pedir_opcion("  Opción: ", {"0", "1", "2", "3", "4", "5"})

        if op == "0":
            print("\n  Hasta luego.\n")
            break
        limpiar()
        if op == "1":
            accion_registrar_prestamo(repo_eq, repo_est, repo_pr, proveedor_fecha)
        elif op == "2":
            accion_registrar_devolucion(repo_eq, repo_est, repo_pr, proveedor_fecha)
        elif op == "3":
            accion_registrar_equipo(repo_eq)
        elif op == "4":
            accion_registrar_estudiante(repo_est)
        elif op == "5":
            accion_listar(repo_eq, repo_est, repo_pr)


# ══════════════════════════════════════════════════════════════════════════════
# Punto de entrada
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    repo_eq, repo_est, repo_pr = elegir_repositorio()
    proveedor_fecha = elegir_proveedor_fecha()
    menu_principal(repo_eq, repo_est, repo_pr, proveedor_fecha)
