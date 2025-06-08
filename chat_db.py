"""
Módulo de base de datos para el chat.

Este módulo maneja el almacenamiento y recuperación de mensajes del chat
utilizando SQLAlchemy con PostgreSQL.
"""

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional, Generator

from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configuración de la base de datos desde variables de entorno
DB_USER = os.getenv("DB_USER", "chatuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "chatpass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chatdb")

# Construir URL de conexión
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear motor y sesión
engine = create_engine(
    DATABASE_URL,
    echo=bool(os.getenv("SQL_ECHO", "False").lower() in ("true", "1", "yes")),  # Mejor manejo de variables booleanas
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=3600,  # Reciclar conexiones después de una hora
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definición de la clase base para los modelos
Base = declarative_base()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)


# Definición del modelo de datos
class Message(Base):  # type: ignore
    """Modelo para almacenar mensajes del chat.
    
    Atributos:
        id: Identificador único del mensaje
        role: Rol del emisor (user/assistant)
        content: Contenido del mensaje
        created_at: Fecha y hora de creación
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False, index=True)  # user o assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role='{self.role}', created_at='{self.created_at}')>"


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager para manejar sesiones de base de datos.
    
    Uso:
        with get_db() as db:
            db.query(Message).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def add_message(role: str, content: str) -> dict:
    """Agrega un nuevo mensaje a la base de datos.
    
    Args:
        role: Rol del emisor (user/assistant)
        content: Contenido del mensaje
        
    Returns:
        Un diccionario con los datos del mensaje creado
        
    Raises:
        ValueError: Si el rol o el contenido son inválidos
        SQLAlchemyError: Si ocurre un error en la base de datos
    """
    if not role or not isinstance(role, str):
        raise ValueError("El rol es requerido y debe ser un string")
    if not content or not isinstance(content, str):
        raise ValueError("El contenido es requerido y debe ser un string")
    
    try:
        with get_db() as db:
            message = Message(role=role.lower(), content=content)
            db.add(message)
            db.commit()
            
            # Crear un diccionario con los datos del mensaje para evitar problemas de sesión
            message_dict = {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None
            }
            return message_dict
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Error al agregar mensaje: {str(e)}")


def get_all_messages(
    limit: Optional[int] = 100,
    offset: int = 0,
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_conversation_only: bool = True
) -> tuple[List[dict], int]:
    """Obtiene mensajes del chat con opciones de paginación y búsqueda.
    
    Args:
        limit: Máximo número de mensajes a devolver (por defecto: 100)
        offset: Número de mensajes a omitir (para paginación)
        search: Texto para buscar en el contenido de los mensajes
        role: Filtrar por rol ('user' o 'assistant')
        current_conversation_only: Si es True, solo retorna mensajes de la conversación actual
        
    Returns:
        Tupla con (lista_de_diccionarios_de_mensajes, total_de_mensajes)
        
    Raises:
        SQLAlchemyError: Si ocurre un error en la base de datos
    """
    try:
        with get_db() as db:
            # Si queremos solo la conversación actual, primero encontramos el último separador
            last_separator_id = None
            if current_conversation_only:
                # Buscar el último separador (mensaje "system" que comienza con "--- NUEVA CONVERSACIÓN")
                separator_query = (
                    db.query(Message.id)
                    .filter(Message.role == "system")
                    .filter(Message.content.like("--- NUEVA CONVERSACIÓN%"))
                    .order_by(Message.created_at.desc())
                    .first()
                )
                
                if separator_query:
                    last_separator_id = separator_query[0]
            
            # Construir la consulta base
            query = db.query(Message)
            
            # Filtrar mensajes por conversación actual si es necesario
            if current_conversation_only and last_separator_id:
                query = query.filter(Message.id >= last_separator_id)
            
            # Aplicar filtros adicionales
            if search:
                query = query.filter(Message.content.ilike(f"%{search}%"))
            if role:
                query = query.filter(Message.role == role.lower())
            
            # Obtener el total de mensajes (para paginación)
            total = query.count()
            
            # Aplicar ordenamiento y paginación
            db_messages = (
                query.order_by(Message.created_at.desc())
                .offset(offset)
                .limit(limit if limit and limit > 0 else 100)
                .all()
            )
            
            # Convertir objetos SQLAlchemy a diccionarios para evitar problemas de sesión
            messages = [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in db_messages
            ]
            
            return messages, total
            
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Error al obtener mensajes: {str(e)}")


def format_message_for_display(message: Message, max_width: int = 80) -> str:
    """Formatea un mensaje para mostrarlo en la terminal.
    
    Args:
        message: El mensaje a formatear
        max_width: Ancho máximo de la salida
        
    Returns:
        String formateado para mostrar en terminal
    """
    from textwrap import fill
    from datetime import timezone
    
    # Convertir a zona horaria local si está en UTC
    created_at = message.created_at
    if created_at.tzinfo == timezone.utc:
        created_at = created_at.replace(tzinfo=timezone.utc).astimezone()
    
    # Encabezado del mensaje
    role_display = "👤 Tú" if message.role == "user" else "🤖 Asistente"
    timestamp = created_at.strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{timestamp}] {role_display}:"
    
    # Formatear el contenido con ajuste de línea
    content = fill(
        message.content,
        width=max_width,
        initial_indent="  ",
        subsequent_indent="  "
    )
    
    return f"{header}\n{content}\n"


def get_chat_summary() -> dict:
    """Obtiene un resumen de la conversación actual.
    
    Returns:
        Diccionario con estadísticas del chat
    """
    try:
        with get_db() as db:
            # Obtener estadísticas básicas
            total_msgs = db.query(Message).count()
            user_msgs = db.query(Message).filter_by(role="user").count()
            assistant_msgs = db.query(Message).filter_by(role="assistant").count()
            
            # Obtener la fecha del primer y último mensaje
            first_msg = db.query(Message).order_by(Message.created_at).first()
            last_msg = db.query(Message).order_by(Message.created_at.desc()).first()
            
            return {
                "total_messages": total_msgs,
                "user_messages": user_msgs,
                "assistant_messages": assistant_msgs,
                "first_message": first_msg.created_at if first_msg else None,
                "last_message": last_msg.created_at if last_msg else None,
                "avg_message_length": (
                    db.query(func.avg(func.length(Message.content))).scalar() or 0
                )
            }
            
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Error al obtener resumen del chat: {str(e)}")


def get_messages_by_role(role: str, limit: Optional[int] = None) -> List[Message]:
    """Obtiene mensajes filtrados por rol.
    
    Args:
        role: Rol a filtrar (user/assistant)
        limit: Número máximo de mensajes a devolver (opcional)
        
    Returns:
        Lista de mensajes del rol especificado
        
    Raises:
        SQLAlchemyError: Si ocurre un error en la base de datos
    """
    try:
        with get_db() as db:
            query = db.query(Message).filter(Message.role == role.lower()).order_by(Message.created_at)
            if limit and limit > 0:
                query = query.limit(limit)
            result: List[Message] = query.all()
            return result
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Error al obtener mensajes por rol: {str(e)}")


def clear_chat_history() -> None:
    """Elimina todos los mensajes del chat.
    
    Raises:
        SQLAlchemyError: Si ocurre un error en la base de datos
    """
    try:
        with get_db() as db:
            db.query(Message).delete()
            db.commit()
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Error al limpiar el historial: {str(e)}")


def create_new_conversation() -> None:
    """Crea una nueva conversación añadiendo un mensaje de sistema como separador.
    
    Esta función añade un marcador en la base de datos para indicar el inicio de
    una nueva conversación, lo que ayuda a evitar la contaminación del contexto entre
    sesiones diferentes. Se llama automáticamente al iniciar una nueva sesión interactiva.
    
    Raises:
        SQLAlchemyError: Si ocurre un error en la base de datos
    """
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        separator_message = f"--- NUEVA CONVERSACIÓN INICIADA: {timestamp} ---"
        
        with get_db() as db:
            # Añadir un mensaje especial de sistema como marcador de nueva conversación
            new_message = Message(
                role="system",
                content=separator_message,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_message)
            db.commit()
            
        return True
    except SQLAlchemyError as e:
        print(f"Error al crear nueva conversación: {str(e)}")
        return False

