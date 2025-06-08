"""
Script para mantener una sesión interactiva con el asistente.
"""
import os
import sys
import typer
import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from app import app, CONFIG

console = Console()

# Cargar variables de entorno
BANNER = """
🤖 Asistente Experto con LLaMA-4 Scout | Groq API 
--------------------------------
- Ventana de contexto: 131,072 tokens
- Respuestas hasta: 8,192 tokens
- Modo: Interactivo optimizado

Para iniciar una conversación, simplemente escribe tu pregunta.
El historial se guarda automáticamente en la base de datos.
"""

def show_help():
    """Muestra la ayuda con comandos disponibles"""
    help_text = """
Comandos disponibles:
  /exit, /quit      Salir del asistente
  /clear            Limpiar la conversación actual
  /help             Mostrar esta ayuda
  /temp [0.0-1.0]   Cambiar temperatura (0.0=preciso, 1.0=creativo)
  /tokens [n]       Cambiar máximo de tokens (máx 8192)
  /info             Mostrar información sobre el modelo actual
  /export markdown  Exportar conversación a archivo Markdown
  /export pdf       Exportar conversación a archivo PDF
  
Para preguntar al asistente:
  Simplemente escribe tu pregunta y presiona Enter
    """
    console.print(Panel(help_text, title="Ayuda", border_style="blue"))

def clear_conversation():
    """Limpia el historial de la conversación (marca temporal)"""
    # Se usará para implementar limpieza de conversación
    try:
        # Importamos aquí para evitar referencias circulares
        from chat_db import create_new_conversation
        create_new_conversation()
        console.print("[green]✓[/green] Conversación reiniciada")
        return True
    except Exception as e:
        console.print(f"[red]Error al limpiar conversación: {str(e)}[/red]")
        return False

def show_model_info():
    """Muestra información sobre el modelo y configuración actual"""
    model_info = f"""
    [bold]Modelo:[/bold] {CONFIG['default_model']}
    [bold]Temperatura:[/bold] {CONFIG['default_temperature']} (0.0=preciso, 1.0=creativo)
    [bold]Máx. tokens respuesta:[/bold] {CONFIG['default_max_tokens']} (máx. 8192 para este modelo)
    [bold]Ventana de contexto:[/bold] 131,072 tokens (aprox. ~100,000 palabras)
    [bold]Optimizado para:[/bold] Respuestas precisas, profesionales y contextuales
    """
    console.print(Panel(model_info, title="⚙️ Configuración del modelo", border_style="green"))
    
def export_to_markdown(filename=None):
    """Exporta la conversación actual a un archivo markdown"""
    try:
        # Importamos aquí para evitar referencias circulares
        from chat_db import get_all_messages
        
        # Obtener todos los mensajes de la base de datos
        messages, total = get_all_messages(limit=1000)  # Obtenemos hasta 1000 mensajes
        
        # Crear el contenido del archivo markdown
        content = f"# Chat con LLaMA-4 Scout | Groq API\n\n"
        content += f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Agregar cada mensaje al contenido
        for msg in messages:
            role = "Usuario" if msg['role'] == "user" else "Asistente"
            content += f"## {role}\n\n{msg['content']}\n\n"
            content += f"*{msg['created_at']}*\n\n---\n\n"
        
        # Definir el nombre del archivo si no se especificó
        if not filename:
            filename = f"chat_llama4_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
        
        # Asegurar que el archivo tenga extensión .md
        if not filename.lower().endswith('.md'):
            filename += '.md'
            
        # Guardar el archivo
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        console.print(f"[green]✓[/green] Conversación exportada a [bold]{filename}[/bold]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error al exportar a markdown: {str(e)}[/red]")
        return False

def export_to_pdf(filename=None):
    """Exporta la conversación actual a un archivo PDF"""
    try:
        # Primero exportamos a markdown
        temp_md = f"temp_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
        if export_to_markdown(temp_md):
            # Definir el nombre del archivo PDF si no se especificó
            if not filename:
                filename = f"chat_llama4_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            
            # Asegurar que el archivo tenga extensión .pdf
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            # Importar las librerías necesarias para la conversión a PDF
            try:
                from weasyprint import HTML
                
                # Crear HTML intermedio con estilos
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Chat Export</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #2c3e50; }}
                        h2 {{ color: #3498db; margin-top: 20px; }}
                        .user {{ background-color: #f8f9fa; padding: 10px; border-left: 4px solid #3498db; }}
                        .assistant {{ background-color: #f0f4f8; padding: 10px; border-left: 4px solid #2ecc71; }}
                        .timestamp {{ color: #7f8c8d; font-size: 0.8em; }}
                        hr {{ border: 0; height: 1px; background: #ddd; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                """
                
                # Leer el contenido del archivo markdown
                with open(temp_md, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Procesar el markdown a HTML
                from markdown import markdown
                html_content += markdown(md_content)
                html_content += "</body></html>"
                
                # Crear un archivo HTML temporal
                temp_html = temp_md.replace('.md', '.html')
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Convertir HTML a PDF
                HTML(temp_html).write_pdf(filename)
                
                # Eliminar archivos temporales
                try:
                    os.remove(temp_md)
                    os.remove(temp_html)
                except:
                    pass
                
                console.print(f"[green]✓[/green] Conversación exportada a [bold]{filename}[/bold]")
                return True
                
            except ImportError:
                console.print("[yellow]⚠️ Se requiere WeasyPrint para exportar a PDF. Usando solo markdown.[/yellow]")
                # Renombrar el archivo temporal
                os.rename(temp_md, filename.replace('.pdf', '.md'))
                console.print(f"[green]✓[/green] Conversación exportada a [bold]{filename.replace('.pdf', '.md')}[/bold]")
                return True
                
        return False
        
    except Exception as e:
        console.print(f"[red]Error al exportar a PDF: {str(e)}[/red]")
        return False

def process_query_with_streaming(query, temperature, max_tokens, model, console):
    """
    Procesa una pregunta y muestra la respuesta en streaming.
    Esta función enviará los parámetros a la CLI principal.
    """
    try:
        # Construir los argumentos y llamar al comando ask
        sys.argv = [
            "app.py", "ask", query,
            "--temperature", str(temperature),
            "--max-tokens", str(max_tokens),
            "--model", model
        ]
        app()
        # La respuesta se maneja directamente por app()
        return True
    except Exception as e:
        console.print(f"[red]Error al procesar la pregunta: {str(e)}[/red]")
        if os.getenv("DEBUG"):
            import traceback
            console.print(traceback.format_exc(), style="red")
        return False

def run_interactive():
    """Mantiene una sesión interactiva con el asistente."""
    # Configuración por defecto para esta sesión
    session_config = {
        "temperature": CONFIG.get('default_temperature', 0.3),
        "max_tokens": CONFIG.get('default_max_tokens', 8192),
        "model": CONFIG.get('default_model', "meta-llama/llama-4-scout-17b-16e-instruct"),
    }
    
    # Iniciar una nueva conversación para evitar contaminación del contexto
    try:
        from chat_db import create_new_conversation
        create_new_conversation()
        # También podríamos usar clear_conversation() aquí, pero así es más directo
    except Exception as e:
        console.print(f"[yellow]Advertencia: No se pudo iniciar una nueva conversación: {str(e)}[/yellow]")
    
    # Mostrar mensaje de bienvenida
    console.clear()
    console.print(Panel(BANNER, border_style="green", expand=False))
    console.print(Panel("¡Bienvenido al Chat! Puedes escribir directamente en esta terminal.", title="ℹ️ INSTRUCCIONES", border_style="blue"))
    console.print("\n[bold cyan]Escribe /help para ver todos los comandos disponibles[/bold cyan]")
    console.print("[italic]Para hacer una pregunta, solo escribe y presiona Enter[/italic]\n")
    
    try:
        while True:
            # Solicitar input al usuario
            user_input = Prompt.ask("\n[bold blue]Tú[/bold blue]", console=console)
            
            # Procesar comandos especiales
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()
                if cmd in ("/exit", "/quit", "/salir"):
                    console.print("\n[bold]¡Hasta luego! 👋[/bold]")
                    break
                    
                elif cmd == "/help":
                    show_help()
                    continue
                    
                elif cmd == "/clear":
                    clear_conversation()
                    continue
                    
                elif cmd == "/info":
                    show_model_info()
                    continue
                
                elif cmd.startswith("/export"):
                    parts = cmd.split()
                    if len(parts) < 2:
                        console.print("[yellow]⚠️ Uso: /export [markdown|pdf] [nombre_archivo_opcional][/yellow]")
                        continue
                        
                    export_type = parts[1].lower()
                    filename = parts[2] if len(parts) > 2 else None
                    
                    if export_type == "markdown":
                        export_to_markdown(filename)
                    elif export_type == "pdf":
                        export_to_pdf(filename)
                    else:
                        console.print("[yellow]⚠️ Formato no válido. Use 'markdown' o 'pdf'[/yellow]")
                    continue
                    
                elif cmd.startswith("/temp "):
                    try:
                        temp_value = float(cmd.split()[1])
                        if 0 <= temp_value <= 1:
                            session_config["temperature"] = temp_value
                            console.print(f"[green]✓[/green] Temperatura ajustada a {temp_value}")
                        else:
                            console.print("[yellow]⚠️ La temperatura debe estar entre 0.0 y 1.0[/yellow]")
                    except (IndexError, ValueError):
                        console.print("[yellow]⚠️ Uso: /temp [0.0-1.0][/yellow]")
                    continue
                    
                elif cmd.startswith("/tokens "):
                    try:
                        tokens = int(cmd.split()[1])
                        if 100 <= tokens <= 8192:
                            session_config["max_tokens"] = tokens
                            console.print(f"[green]✓[/green] Máximo de tokens ajustado a {tokens}")
                        else:
                            console.print("[yellow]⚠️ El valor debe estar entre 100 y 8192[/yellow]")
                    except (IndexError, ValueError):
                        console.print("[yellow]⚠️ Uso: /tokens [100-8192][/yellow]")
                    continue
                else:
                    console.print("[yellow]⚠️ Comando no reconocido. Usa /help para ver los comandos disponibles.[/yellow]")
                    continue
            
            # Si el input no está vacío y no es un comando, procesarlo como pregunta
            elif user_input.strip():
                # Mostrar con un panel destacado que se ha recibido la pregunta
                console.print(Panel("[bold yellow]⌛ Pregunta recibida. Generando respuesta...[/bold yellow]", 
                                   expand=False, border_style="yellow"))
                
                # Mostrar un spinner mientras procesa con indicación de progreso
                with console.status("[bold green]Conectando con modelo LLaMA-4 Scout... Por favor espera[/bold green]", 
                                    spinner="dots12"):
                    # Procesar la pregunta usando nuestra función auxiliar
                    process_query_with_streaming(
                        query=user_input,
                        temperature=session_config.get("temperature", 0.3),
                        max_tokens=session_config.get("max_tokens", 8192),
                        model=session_config.get("model", "meta-llama/llama-4-scout-17b-16e-instruct"),
                        console=console
                    )
                    
    except KeyboardInterrupt:
        console.print("\n[bold]¡Hasta luego! 👋[/bold]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        if os.getenv("DEBUG"):
            import traceback
            console.print(traceback.format_exc(), style="red")

if __name__ == "__main__":
    run_interactive()
