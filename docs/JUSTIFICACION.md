# Justificación de Principios de Diseño y Arquitectura

### Principio | Archivo | Decisión concreta donde se aplica 

| **Inversión de Dependencias (DIP)** | `app/ports.py` | Define las interfaces abstractas (puertos) para repositorios, notificadores y proveedores de fecha. Permite que la capa de aplicación dependa exclusivamente de abstracciones y no de detalles de implementación de la infraestructura. |
| **Separación de Responsabilidades (SoC) / Arquitectura Hexagonal** | `app/casos_uso.py` | Implementa la lógica de orquestación (Casos de Uso) de la aplicación aislando las reglas de negocio de la UI y la base de datos. Depende únicamente del dominio y puertos, y las dependencias reales se inyectan en su constructor. |
| **Responsabilidad Única (SRP)** | `domain/prestamo.py` | Encapsula exclusivamente la lógica de negocio de los préstamos (cálculo de fechas, multas, cambio de estado de préstamo). No conoce ni importa elementos de persistencia, interfaz gráfica o infraestructura. |
| **Responsabilidad Única (SRP)** | `domain/excepciones.py` | Centraliza de manera exclusiva todas las excepciones semánticas de dominio asociadas a las reglas de negocio, permitiendo que cada error represente de manera única una violación de regla y sin mezclar con errores de sistema. |
| **Encapsulamiento del Dominio** | `domain/equipo.py` | Los cambios de estado de un equipo se realizan únicamente a través de métodos semánticos (`marcar_prestado()`, `marcar_disponible()`) protegiendo las propiedades internas y garantizando que se cumplan las invariantes del estado. |
| **Principio Abierto/Cerrado (OCP)** | `domain/categorias/` | Las categorías de los equipos se definen para ser extendidas. Si en el futuro se agregan nuevas categorías de activos, se pueden crear nuevas subclases o implementaciones sin necesidad de alterar la lógica central del `Equipo`. |
| **Acoplamiento Mínimo e Implementación de Adaptadores** | `infrastructure/repositorios_sql.py` | Es la única capa con conocimiento de la base de datos (SQLite). Implementa las interfaces de `app/ports.py` para aislar las operaciones CRUD, asegurando que el modelo de datos externo no contamine el modelo de dominio. |
| **Inyección de Dependencias (DI)** | `main.py` | Actúa como el Composition Root (Punto de Composición). Instancia las dependencias concretas de infraestructura (repositorios SQLite, notificadores de consola) y las inyecta en los casos de uso que la aplicación necesita. |
| **Inversión de Dependencias (DIP) y OCP** | `infrastructure/adaptadores.py` | Provee implementaciones concretas, como el envío de notificaciones o generación de fechas. Estas implementaciones abstractas permiten reemplazar fácilmente el canal (por ejemplo, cambiar a envío de SMS o correo) sin modificar ningún caso de uso. |


