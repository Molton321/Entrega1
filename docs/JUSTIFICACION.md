# Justificación — Sistema de Préstamo de Equipos

## Tabla de Principios SOLID / Arquitectura

| Principio | Archivo | Decisión concreta donde se aplica |
|-----------|---------|-----------------------------------|
| **SRP** | `domain/prestamo.py` | Encapsula exclusivamente la lógica de un préstamo: cálculo de fecha límite, multa por retraso y cambio de estado. No contiene referencias a persistencia ni a UI. |
| **SRP** | `domain/excepciones.py` | Archivo dedicado solo a definir excepciones semánticas del dominio (`LimitePrestamosExcedidoError`, `EquipoNoDisponibleError`, `EstudianteConMultaPendienteError`). |
| **OCP** | `domain/categorias/` | Cada categoría (`Portatil`, `Camara`, `KitRobotica`, `Proyector`) extiende `CategoriaEquipo` sin modificar clases existentes. Agregar una nueva categoría solo requiere crear un archivo nuevo. |
| **LSP** | `infrastructure/repositorios_memoria.py` y `repositorios_sql.py` | Ambos implementan las mismas interfaces de `app/ports.py`. En `main.py` se puede intercambiar uno por otro con una sola línea sin afectar los casos de uso. |
| **ISP** | `app/ports.py` | Se definen interfaces separadas y específicas: `RepositorioEquipos`, `RepositorioEstudiantes`, `RepositorioPrestamos`, `Notificador` y `ProveedorFecha`. Cada caso de uso recibe solo la interfaz que necesita. |
| **DIP** | `app/casos_uso.py` | `RegistrarPrestamo` y `RegistrarDevolucion` dependen de abstracciones inyectadas en el constructor (puertos), nunca de clases concretas como SQLite o consola. |
| **Composition Root** | `main.py` | Único lugar que instancia clases concretas de infraestructura y las inyecta en los casos de uso. El resto del sistema nunca importa clases de `infrastructure/`. |

## Revisión de Importaciones por Capa

| Capa | Importa de | Nunca importa de |
|------|-----------|-----------------|
| `domain/` | `abc`, `datetime` (stdlib) | `app/`, `infrastructure/` |
| `app/ports.py` | `abc` (stdlib) | `domain/`, `infrastructure/` |
| `app/casos_uso.py` | `domain/` y `app/ports.py` | `infrastructure/` |
| `infrastructure/` | `app/ports.py`, `domain/`, stdlib (`sqlite3`, `datetime`) | — |
| `main.py` | `infrastructure/`, `app/casos_uso`, `domain/` | — (Composition Root) |

La regla de dependencia fluye en una sola dirección: `infrastructure → app → domain`. El dominio es el núcleo y no conoce ninguna capa exterior.

## Declaración de Uso de IA

La inteligencia artificial fue utilizada como complemento de apoyo en los siguientes aspectos:

- **Orquestación de `main.py`**: se empleó IA para asistir en la construcción del menú interactivo, el flujo de inicio y el enrutamiento de acciones entre casos de uso.
- **Repositorios** (`repositorios_memoria.py` y `repositorios_sql.py`): por disponibilidad de tiempo, la IA asistió en la escritura de los scripts y métodos CRUD de ambos repositorios.
- **Diagramas**: los diagramas arquitectónicos y de clases fueron diseñados y estructurados a mano por el equipo. Una vez definido el contenido, se utilizó IA exclusivamente para mejorar su presentación visual y legibilidad, sin alterar la estructura ni las decisiones de diseño originales.

En todos los casos, el resultado fue leído, comprendido y validado individualmente por cada integrante del equipo antes de ser incorporado al proyecto.
