"""
Módulo cliente para interactuar con la API de Groq.

Este módulo maneja la comunicación con la API de Groq, incluyendo el envío de
mensajes, recepción de respuestas en streaming y manejo de errores.
"""
import os
import logging
from typing import Dict, List, Optional, Generator, Any, Callable
from dotenv import load_dotenv
from groq import Groq

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Cargar variables de entorno desde .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("La API key de Groq no está configurada. Establezca GROQ_API_KEY en el archivo .env")

# Inicializar cliente con manejo de errores
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    raise RuntimeError(f"Error al inicializar el cliente de Groq: {str(e)}")

# Constantes y configuraciones
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 1024

# Prompt del sistema para usar con todos los mensajes
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres el CEO de una multinacional experta en Python. "
        "Tu misión es guiar a un desarrollador junior con orientación profesional: "
        "arquitectura de software, principios SOLID, buenas prácticas, Clean Architecture, CI/CD, testing. "
        "Debes responder con claridad, profesionalidad y honestidad. "
        "Si no sabes algo, debes decir explícitamente \"No tengo información al respecto\" y no inventes respuestas. "
        "Tus respuestas deben incluir ejemplos de código real, referencias a documentación oficial, "
        "y seguir estilos de código Python modernos (PEP 8, tipado, docstrings)."
    ),
}


def stream_response(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    chunk_size: int = 30,
    on_chunk: Optional[Callable[[str, bool, Dict], bool]] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Envía una solicitud al modelo y transmite la respuesta por stream.
    
    Args:
        messages: Lista de mensajes para enviar al modelo
        model: Modelo a utilizar
        temperature: Temperatura para la generación (0-1)
        max_tokens: Número máximo de tokens a generar
        chunk_size: Tamaño de los chunks a emitir (en palabras)
        on_chunk: Función callback que recibe cada chunk
        
    Yields:
        Diccionarios con partes de la respuesta
    """
    buffer = []
    word_count = 0
    
    # Asegurarse de que tenemos un prompt del sistema
    if not any(msg.get('role') == 'system' for msg in messages):
        messages = [SYSTEM_PROMPT] + messages
    
    # Limitar a un máximo de 20 mensajes para evitar superar el límite de tokens
    # pero mantener suficiente contexto para la conversación
    if len(messages) > 21:  # 20 mensajes + sistema prompt
        # Mantener el sistema prompt y los últimos 20 mensajes
        system_msgs = [msg for msg in messages if msg.get('role') == 'system']
        non_system_msgs = [msg for msg in messages if msg.get('role') != 'system']
        
        # Tomar los mensajes más recientes
        recent_msgs = non_system_msgs[-20:]
        messages = system_msgs + recent_msgs
    
    logging.debug(f"Enviando {len(messages)} mensajes al modelo")
    
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=True,
        )
        
        for chunk in stream:
            if not chunk.choices or not chunk.choices[0].delta:
                continue
                
            content = chunk.choices[0].delta.content or ''
            
            # Agregar al buffer para chunks más grandes y procesables
            buffer.append(content)
            word_count += len(content.split())
            
            if word_count >= chunk_size:
                joined_content = ''.join(buffer)
                buffer = []
                word_count = 0
                
                result = {
                    'chunk': joined_content,
                    'finished': False,
                    'usage': {'tokens': len(joined_content) // 4, 'total_tokens': len(joined_content) // 4},
                    'error': None,
                }
                
                yield result
                
                if on_chunk and not on_chunk(joined_content, False, {}):
                    break
        
        # Emitir el buffer restante
        if buffer:
            final_chunk = ''.join(buffer)
            result = {
                'chunk': final_chunk,
                'finished': True,
                'usage': {'tokens': len(final_chunk) // 4, 'total_tokens': len(final_chunk) // 4},
                'error': None,
            }
            
            yield result
            
            if on_chunk:
                on_chunk(final_chunk, True, {})
                
    except Exception as e:
        error_msg = f"Error en la generación: {str(e)}"
        logging.error(error_msg)
        
        yield {
            'chunk': '',
            'finished': True,
            'usage': {'tokens': 0, 'total_tokens': 0},
            'error': error_msg
        }
        
        if on_chunk:
            on_chunk('', True, {'error': error_msg})


def stream_chat_response(
    question: str,
    history: List[Dict[str, str]] = None,
    on_token: Optional[Callable[[str], None]] = None
) -> str:
    """Envía una pregunta al modelo y transmite la respuesta por stream.
    Guarda cada token recibido en tiempo real usando on_token() si se define.
    
    Args:
        question: Pregunta o mensaje del usuario
        history: Historial de mensajes anteriores (opcional)
        on_token: Función callback que recibe cada token de la respuesta
        
    Returns:
        Respuesta completa generada por el modelo
    """
    full_response = ""
    
    # Preparar mensajes incluyendo historial si está disponible
    if history:
        # El historial ya viene filtrado desde app.py con current_conversation_only=True
        # Solo aplicaremos un límite máximo por seguridad
        if len(history) > 40:  # Ampliamos el límite ya que el filtrado principal se hace en chat_db
            history = history[-40:]
            
        # Verificamos si hay algún separador de nueva conversación en el historial
        # y eliminamos todo lo anterior al separador
        for i, msg in enumerate(history):
            is_separator = (msg.get("role") == "system" and 
                           isinstance(msg.get("content"), str) and
                           msg.get("content").startswith("--- NUEVA CONVERSACIÓN"))
            if is_separator:
                # Solo mantener mensajes desde este separador en adelante
                history = history[i+1:]
                break
        
        messages = [SYSTEM_PROMPT] + history + [{"role": "user", "content": question}]
    else:
        messages = [
            SYSTEM_PROMPT,
            {"role": "user", "content": question},
        ]
    
    try:
        # Usar ventana de contexto amplia para este modelo específico
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE,
            max_completion_tokens=DEFAULT_MAX_TOKENS,
            top_p=1,
            stream=True,
        )

        for chunk in completion:
            token = chunk.choices[0].delta.content or ""
            full_response += token
            if on_token:
                on_token(token)

        return full_response
    except Exception as e:
        error_msg = f"Error en la generación: {str(e)}"
        logging.error(error_msg)
        raise


def get_chat_response(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Dict[str, Any]:
    """Obtiene una respuesta completa del modelo sin streaming.
    
    Args:
        messages: Lista de mensajes para enviar al modelo
        model: Modelo a utilizar
        temperature: Temperatura para la generación (0-1)
        max_tokens: Número máximo de tokens a generar
        
    Returns:
        Diccionario con la respuesta y metadatos
    """
    start_time = time.time()
    result = {
        'response': '',
        'elapsed': 0,
        'tokens': 0,
        'total_tokens': 0,
        'error': None,
    }
    
    # Asegurarse de que tenemos un prompt del sistema
    if not any(msg.get('role') == 'system' for msg in messages):
        messages = [SYSTEM_PROMPT] + messages
    
    # Limitar a un máximo de 20 mensajes para evitar superar el límite de tokens
    # pero mantener suficiente contexto para la conversación
    if len(messages) > 21:  # 20 mensajes + sistema prompt
        # Mantener el sistema prompt y los últimos 20 mensajes
        system_msgs = [msg for msg in messages if msg.get('role') == 'system']
        non_system_msgs = [msg for msg in messages if msg.get('role') != 'system']
        
        # Tomar los mensajes más recientes
        recent_msgs = non_system_msgs[-20:]
        messages = system_msgs + recent_msgs
    
    logging.debug(f"Enviando {len(messages)} mensajes al modelo sin streaming")
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
        )
        
        response = completion.choices[0].message.content or ""
        
        return {
            'response': response,
            'usage': {'tokens': len(response) // 4, 'total_tokens': len(response) // 4},
            'error': None
        }
        
    except Exception as e:
        error_msg = f"Error al comunicarse con la API: {str(e)}"
        logging.error(error_msg)
        
        return {
            'response': "",
            'usage': {'tokens': 0, 'total_tokens': 0},
            'error': error_msg
        }
