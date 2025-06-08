"""
Script para inicializar la base de datos.
"""
from chat_db import Base, engine

def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("¡Base de datos inicializada correctamente!")

if __name__ == "__main__":
    init_db()
