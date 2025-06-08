"""
CLI para interactuar con un asistente de programación experto en Python.

Este módulo proporciona una interfaz de línea de comandos para hacer preguntas,
ver el historial y exportar conversaciones con un asistente de IA especializado
en desarrollo de software profesional.

Características:
- Streaming controlado para respuestas largas
- Paginación del historial
- Exportación a múltiples formatos
- Interfaz enriquecida con Rich
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, List, TypedDict

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

from chat_db import add_message, get_all_messages
from groq_client import stream_response


# Definición de tipo para la configuración
class ConfigDict(TypedDict):
    max_chunk_size: int
    default_model: str
    default_temperature: float
    default_max_tokens: int
    show_usage: bool
    auto_scroll: bool
    confirm_continue: bool

# Configuración
CONFIG: ConfigDict = {
    'max_chunk_size': 30,  # palabras por chunk
    'default_model': os.environ.get('DEFAULT_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct'),
    'default_temperature': float(os.environ.get('DEFAULT_TEMPERATURE', 0.3)),
    'default_max_tokens': int(os.environ.get('DEFAULT_MAX_TOKENS', 8192)),  # Máximo soportado por el modelo
    'show_usage': os.environ.get('SHOW_USAGE', 'true').lower() == 'true',
    'auto_scroll': True,   # auto-scroll en respuestas largas
    'confirm_continue': True  # pedir confirmación para continuar respuestas largas
}

# Configuración de la aplicación
app = typer.Typer(
    name="ceo-python",
    help="Asistente experto en Python para desarrollo profesional",
    add_completion=False,
)
console = Console()

# Constantes
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
EXPORT_FORMATS = ["md", "pdf"]


def display_welcome() -> None:
    """Muestra un mensaje de bienvenida en la consola."""
    welcome_msg = """
    [bold blue]CEO-Python[/bold blue] - Tu mentor experto en desarrollo Python profesional
    Escribe 'exit' o presiona Ctrl+C para salir
    """
    console.print(Panel.fit(welcome_msg, style="blue"))


def process_stream(
    messages: List[Dict[str, str]],
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
    max_tokens: int = 8192,  # Máximo soportado por el modelo
    temperature: float = 0.3
) -> tuple[str, Dict[str, Any]]:
    """
    Procesa el stream de respuesta con manejo de chunks controlados.
    
    Args:
        messages: Historial de mensajes
        model: Modelo a utilizar
        max_tokens: Máximo de tokens a generar
        temperature: Control de aleatoriedad (0-1)
        
    Returns:
        Tupla con (respuesta_completa, metadatos)
    """
    console = Console()
    full_response = []
    current_chunk = []
    chunk_count = 0
    start_time = time.time()

    # Mostrar estado inicial
    with Status("[bold green]Generando respuesta...[/bold green]") as status:
        try:
            # Configurar el stream
            stream = stream_response(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                chunk_size=int(CONFIG['max_chunk_size']),
                on_chunk=on_chunk_callback
            )

            # Procesar cada chunk
            for chunk_data in stream:
                if chunk_data.get('error'):
                    console.print(f"[red]Error: {chunk_data['error']}")
                    break

                chunk = chunk_data['chunk']
                current_chunk.append(chunk)
                full_response.append(chunk)

                # Actualizar estado
                if CONFIG['show_usage'] and 'usage' in chunk_data:
                    usage = chunk_data['usage']
                    status.update(
                        f"[bold green]Generando...[/bold green] "
                        f"[dim]({usage['total_tokens']} tokens)[/dim]"
                    )

                # Mostrar el chunk actual
                if chunk.strip():
                    console.print(chunk, end="", highlight=False)

                # Manejar pausa si el chunk es grande
                if (len(''.join(current_chunk).split()) > int(CONFIG['max_chunk_size']) * 3 and
                    CONFIG['confirm_continue'] and not chunk_data.get('finished')):
                    console.print("\n[bold yellow]\n--- Presiona Enter para continuar (q para salir) ---[/bold yellow]")
                    user_input = input().lower()
                    if user_input == 'q':
                        break
                    current_chunk = []

            # Mostrar resumen
            end_time = time.time()
            console.print(f"\n[dim]Tiempo de generación: {end_time - start_time:.2f}s[/dim]")

            return ''.join(full_response), {
                'model': model,
                'tokens': chunk_data.get('usage', {}).get('total_tokens', 0) if 'chunk_data' in locals() else 0,
                'time_elapsed': end_time - start_time
            }

        except KeyboardInterrupt:
            console.print("\n[red]Generación interrumpida por el usuario")
            return ''.join(full_response), {'interrupted': True}
        except Exception as e:
            console.print(f"[red]Error durante la generación: {str(e)}")
            return ''.join(full_response), {'error': str(e)}

def on_chunk_callback(chunk: str, finished: bool, metadata: Dict) -> bool:
    """Callback para procesar cada chunk de la respuesta.
    
    Args:
        chunk: Fragmento de texto recibido
        finished: Si es el último chunk
        metadata: Metadatos adicionales (tokens, modelo, etc.)
        
    Returns:
        bool: True para continuar, False para detener
    """
    # Aquí podrías agregar lógica adicional, como guardar en caché
    # o monitorear el progreso
    return True  # Continuar con el stream


def ensure_export_dir() -> Path:
    """Asegura que exista el directorio de exportación.
    
    Returns:
        Path: Ruta al directorio de exportación
    """
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    return export_dir


@app.command()
def ask(
    question: str = typer.Argument(
        ..., help="Pregunta para el asistente"
    ),
    model: str = typer.Option(
        CONFIG['default_model'], "--model", "-m", help="Modelo a utilizar"
    ),
    temperature: float = typer.Option(
        CONFIG['default_temperature'], "--temperature", "-t",
        help="Temperatura para la generación (0.0-1.0)"
    ),
    max_tokens: int = typer.Option(
        CONFIG['default_max_tokens'], "--max-tokens", "-mt",
        help="Número máximo de tokens a generar"
    ),
):
    """Realiza una pregunta al asistente."""
    if not question.strip():
        console.print("[red]Error:[/] La pregunta no puede estar vacía.")
        raise typer.Exit(1)

    if question.lower() in ("exit", "quit", "salir"):
        raise typer.Exit()

    try:
        # Añadir pregunta al historial
        add_message("user", question)

        # Mostrar la pregunta
        console.print(f"\n[bold blue]Tú:[/bold blue] {question}\n")

        # Obtener historial para el contexto solo de la conversación actual
        # El parámetro current_conversation_only=True (por defecto) asegura que solo se obtengan
        # los mensajes desde el último separador de conversación
        message_records, _ = get_all_messages(limit=20, current_conversation_only=True)

        # Convertir registros a formato para la API
        messages = []
        for msg in message_records:
            if isinstance(msg, dict):
                role = "user" if msg.get("role") == "user" else "assistant"
                content = msg.get("content", "")
            else:
                role = "user" if msg.role == "user" else "assistant"
                content = msg.content

            messages.append({"role": role, "content": content})

        # Procesar la respuesta con manejo de streaming
        console.print("[bold green]Asistente:[/bold green] ", end="")

        # Obtener la respuesta con streaming controlado
        response, metadata = process_stream(
            messages=messages,
            model=model,
            temperature=max(0, min(1, temperature)),  # Asegurar valor entre 0 y 1
            max_tokens=max_tokens,
        )

        # Mostrar resumen de uso si está habilitado
        if CONFIG['show_usage'] and 'tokens' in metadata:
            console.print(
                f"\n[dim]Tokens usados: {metadata['tokens']} | "
                f"Tiempo: {metadata['time_elapsed']:.1f}s"
            )

        # Guardar la respuesta en la base de datos
        if not metadata.get('interrupted') and not metadata.get('error'):
            add_message("assistant", response)

    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        raise typer.Exit(1)


@app.command()
def history(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Número máximo de mensajes a mostrar"
    ),
    full: bool = typer.Option(
        False, "--full", "-f", help="Mostrar todo el historial de mensajes"
    ),
    reverse: bool = typer.Option(
        False, "--reverse", "-r", help="Mostrar mensajes más antiguos primero"
    ),
) -> None:
    """Muestra el historial de la conversación.
    
    Args:
        limit: Número máximo de mensajes a mostrar
        full: Mostrar todo el historial sin límite
        reverse: Ordenar de más antiguo a más reciente
    """
    """Muestra el historial de la conversación."""
    messages_result = get_all_messages()
    # Corregimos la anotación de tipo para coincidir con lo que devuelve get_all_messages
    messages = messages_result[0]  # List[dict], no List[Message]

    if not messages:
        console.print("[yellow]No hay historial de mensajes.[/]")
        return

    if not full:
        messages = messages[-limit:] if limit > 0 else messages

    console.print("\n[bold]📜 Historial de la conversación:[/]\n")

    for msg in messages:
        role_display = "👤 Tú" if msg['role'] == "user" else "🤖 Asistente"
        # Convertir el timestamp ISO a objeto datetime si es un string
        if isinstance(msg['created_at'], str):
            from datetime import datetime
            timestamp = datetime.fromisoformat(msg['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = msg['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[dim]{timestamp}[/] - {role_display}:")
        console.print(Markdown(msg['content']), justify="left")
        console.print()  # Espacio entre mensajes


@app.command()
def export(
    format: str = typer.Option(
        "md",
        "--format",
        "-f",
        help=f"Formato de exportación ({', '.join(EXPORT_FORMATS)})",
        case_sensitive=False,
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Nombre del archivo de salida (sin extensión)",
    ),
    limit: int = typer.Option(
        None,
        "--limit",
        "-l",
        help="Número máximo de mensajes a exportar (últimos N mensajes)",
    ),
) -> None:
    """Exporta el historial de chat a diferentes formatos.
    
    Args:
        format: Formato de salida (md, pdf, etc.)
        output: Nombre del archivo de salida
        limit: Límite de mensajes a exportar
    """
    """Exporta el historial de chat a diferentes formatos.
    
    Por defecto exporta a Markdown (.md). Para exportar a PDF se requiere Pandoc.
    """
    try:
        from exporter import convert_md_to_pdf, export_markdown
    except ImportError as e:
        console.print(f"[red]Error:[/] {e}")
        console.print("Instala las dependencias necesarias con: pip install -r requirements.txt")
        raise typer.Exit(1)

    format = format.lower()
    if format not in EXPORT_FORMATS:
        console.print(f"[red]Error:[/] Formato no soportado. Usa uno de: {', '.join(EXPORT_FORMATS)}")
        raise typer.Exit(1)

    # Obtener mensajes
    messages = get_all_messages()
    if not messages:
        console.print("[yellow]No hay mensajes para exportar.[/]")
        return

    # Configurar nombres de archivo
    export_dir = ensure_export_dir()
    base_name = output or "chat_export"
    md_file = export_dir / f"{base_name}.md"

    try:
        # Exportar a Markdown
        md_content = export_markdown(messages)
        md_file.write_text(md_content, encoding="utf-8")
        console.print(f"✓ [green]Exportado:[/] {md_file.absolute()}")

        # Convertir a PDF si es necesario
        if format == "pdf":
            pdf_file = export_dir / f"{base_name}.pdf"
            convert_md_to_pdf(str(md_file), str(pdf_file))
            console.print(f"✓ [green]Exportado:[/] {pdf_file.absolute()}")

    except Exception as e:
        console.print(f"[red]Error al exportar:[/] {str(e)}")
        raise typer.Exit(1)


def main() -> None:
    """Punto de entrada principal de la aplicación.
    
    Maneja la inicialización y el cierre limpio de la aplicación.
    """
    try:
        # Mostrar mensaje de bienvenida
        display_welcome()

        # Iniciar la aplicación Typer
        app()

    except KeyboardInterrupt:
        console.print("\n[blue]¡Hasta luego![/] 👋")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"\n[red]Error inesperado:[/] {str(e)}")
        if os.getenv("DEBUG"):
            import traceback
            console.print(f"\n[dim]{traceback.format_exc()}[/dim]")
        if "GROQ_API_KEY" in str(e):
            console.print("Asegúrate de configurar tu GROQ_API_KEY en el archivo .env")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    main()

