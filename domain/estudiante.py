class Estudiante:
    def __init__(self, nombre, edad, carrera):
        self.id = None
        self.nombre = nombre
        self.edad = edad
        self.carrera = carrera
        self.tiene_multa = False

    def set_tiene_multa(self, tiene_multa):
        self.tiene_multa = tiene_multa

    def get_tiene_multa(self):
        return self.tiene_multa

    def mostrar_informacion(self):
        return f"Nombre: {self.nombre}, Edad: {self.edad}, Carrera: {self.carrera}"

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def __str__(self):
        return self.mostrar_informacion()