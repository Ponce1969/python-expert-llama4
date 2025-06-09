# 🤖 Python Expert LLaMA-4

Una aplicación de línea de comandos especializada en Python que aprovecha el modelo LLaMA-4 Scout a través de la API de Groq. Diseñada específicamente para desarrolladores de Python, ofrece asistencia en código, buenas prácticas y resolución de problemas con capacidades de streaming optimizado, historial de chat persistente y exportación de conversaciones.

## 📝 Características

- **Asistente Experto en Python con LLaMA-4 Scout**
  - Especializado en código, patrones y buenas prácticas de Python
  - Respuestas prácticas con ejemplos de código funcional
  - Ventana de contexto extendida de 131,072 tokens
  - Respuestas de hasta 8,192 tokens
  - Temperatura configurable (0.0-1.0) para balancear precisión y creatividad

- **Interfaz CLI intuitiva** 
  - Diseño visual con Rich para una experiencia mejorada
  - Comandos intuitivos con explicaciones claras
  - Indicadores visuales de progreso durante la generación

- **Streaming optimizado y visual mejorado** 
  - Respuestas en tiempo real sin saturación de memoria
  - Visualización de tokens generados progresivamente
  - Respuestas completas y limpias en panel visual (Rich), sin cortes ni mensajes de estado mezclados
  - Experiencia de usuario mucho más fluida y profesional

- **Historial persistente avanzado** 
  - Almacenamiento en PostgreSQL para conversaciones duraderas
  - Sistema de separación de contextos que evita contaminación entre sesiones
  - Manejo de contexto optimizado con filtrado multi-capa
  - Preservación de la estructura conversacional limpia

- **Exportación profesional** 
  - Formatos Markdown y PDF con diseño profesional
  - Organización clara de mensajes con timestamps
  - Exportación simple con comandos directos `/export`

- **Docker Ready** 
  - Despliegue completo con docker-compose
  - Base de datos PostgreSQL incluida
  - Configuración centralizada en archivo `.env`

## 🆕 Mejoras recientes

- Las respuestas del asistente ahora se muestran en un **panel visual profesional** usando [Rich](https://rich.readthedocs.io/), con título y borde destacado.
- Se eliminaron los mensajes de estado y cortes intermedios: la respuesta es continua, clara y sin interrupciones.
- El sistema aprovecha la ventana de tokens extendida del modelo LLaMA-4 Scout.
- Mejor experiencia visual y de lectura para el usuario.

## 🛠️ Requisitos

- Python 3.9-3.12
- API Key de Groq (obtén una en [console.groq.com](https://console.groq.com))

## 🚀 Instalación

### Instalación con Docker (recomendada)

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/python-expert-llama4.git
   cd python-expert-llama4
   ```

2. Configura tu API key de Groq en el archivo `.env`:
   ```bash
   # Editar el archivo .env
   GROQ_API_KEY=tu_api_key_aqui
   ```

3. **Sigue estos pasos para ejecutar el chat interactivo:**

   ```bash
   # Paso 1: Inicia los servicios en segundo plano
   docker-compose up -d
   
   # Paso 2: Conéctate al contenedor en modo interactivo 
   docker-compose exec app python -m interactive
   ```

   > **Nota:** Este es el flujo de trabajo estándar. El comando `docker-compose up` sin `-d` solo mostrará logs pero no permitirá interacción directa.

   Cuando veas el mensaje de bienvenida como este, ya puedes interactuar:

   ```
   ╭─────────────────────────────────────────────────────────────────╮
   │                                                                 │
   │ 🤖 Asistente Experto con LLaMA-4 Scout | Groq API               │
   │ --------------------------------                                │
   │ - Ventana de contexto: 131,072 tokens                           │
   │ - Respuestas hasta: 8,192 tokens                                │
   │ - Modo: Interactivo optimizado                                  │
   │                                                                 │
   ╰─────────────────────────────────────────────────────────────────╯
   
   ╭─────────────────────────────────────────────────────────────────╮
   │                     ℹ️ INSTRUCCIONES                         │
   ╰─────────────────────────────────────────────────────────────────╯
   ¡Bienvenido al Chat! Puedes escribir directamente en esta terminal.
   
   Escribe /help para ver todos los comandos disponibles
   Para hacer una pregunta, solo escribe y presiona Enter
   ```
   
   **Nota importante:** Con `docker-compose up` normal (sin `-d`), verás los logs pero NO podrás interactuar con el chat. Esto se debe a que Docker no está conectando correctamente la entrada estándar (stdin) al contenedor en ese modo.

### Instalación local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/python-expert-llama4.git
   cd python-expert-llama4
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias (elige una opción):
   ```bash
   # Opción 1: Con uv (recomendado - más rápido)
   uv pip install -r requirements.txt
   
   # Opción 2: Con pip tradicional
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la raíz del proyecto:
   ```
   GROQ_API_KEY=tu_api_key_aquí
   DB_PATH=chat.db
   ```

### Instalación con Docker

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/python-expert-llama4.git
   cd python-expert-llama4
   ```

2. Crea un archivo `.env` como se indicó anteriormente.

3. Construye y ejecuta el contenedor:
   ```bash
   make up
   ```

## 💻 Uso

### Modo Interactivo (recomendado)

```bash
# Si usas Docker:
docker-compose up

# Si instalaste localmente:
python interactive.py
```

Una vez iniciado el modo interactivo, verás la interfaz del asistente. Para usar el chat:

1. **Hacer preguntas sobre Python**: Simplemente escribe tu consulta técnica y presiona Enter. Por ejemplo:
   ```
   ¿Cómo implementaría un patrón observer en Python?
   Explica las diferencias entre asyncio.gather() y asyncio.wait() con ejemplos
   ¿Cuál es la mejor forma de manejar múltiples excepciones en un bloque try/except?
   ```

2. **Comandos disponibles**:
   - `/help` - Mostrar lista de comandos disponibles
   - `/info` - Ver información sobre el modelo y configuración
   - `/clear` - Reiniciar la conversación actual
   - `/temp [0.0-1.0]` - Ajustar temperatura de respuestas
   - `/tokens [100-8192]` - Cambiar límite de tokens generados
   - `/export markdown [archivo]` - Exportar conversación a Markdown
   - `/export pdf [archivo]` - Exportar conversación a PDF
   - `/exit` o `/quit` - Salir del asistente

### Modo Comando

```bash
# Hacer una pregunta directa
python app.py ask "¿Podrías explicarme cómo aplicar el principio de responsabilidad única (SRP) en un servicio de autenticación en Python con ejemplos?"

# Ver historial de conversaciones
python app.py history

# Ver estadísticas de uso
python app.py stats
```

### Ejemplos de Exportación

```bash
# En modo interactivo
/export markdown mi_conversacion.md
/export pdf reporte_chat.pdf
```

Los archivos exportados se guardarán en el directorio actual, con formato profesional y toda la conversación estructurada.

## 🔐 Sistema de Separación de Contexto

La aplicación implementa un sistema avanzado de separación de contextos conversacionales que garantiza que cada sesión de chat comienza limpia, sin contaminación de conversaciones anteriores.

### Arquitectura de tres capas

1. **Separación en Base de Datos**:
   - Cada nueva sesión genera un separador especial en la base de datos
   - La función `create_new_conversation()` marca el inicio claro de cada conversación
   - Los separadores contienen timestamps para identificación precisa

2. **Filtrado al Recuperar Mensajes**:
   - La función `get_all_messages()` filtra automáticamente por conversación actual
   - Parámetro `current_conversation_only=True` asegura contexto limpio
   - Recuperación eficiente solo desde el último separador

3. **Verificación en Cliente API**:
   - Capa adicional de seguridad en `groq_client.py`
   - Detección y filtrado de separadores residuales
   - Protección contra inconsistencias en capas anteriores

### Beneficios

- **Contexto Limpio**: Cada conversación parte de cero sin arrastrar contexto anterior
- **Respuestas Precisas**: El modelo responde exactamente a la pregunta actual
- **Eficiencia de Recursos**: Envío al modelo solo del contexto relevante
- **Experiencia Mejorada**: Sin respuestas cruzadas o contaminadas


### Comandos básicos

- **Hacer una pregunta sobre Python**:
  ```bash
  python app.py ask "Muestra un ejemplo de decorador para medir el tiempo de ejecución de una función en Python"
  ```
  
  El asistente responderá con código de Python que puedes usar directamente en tus proyectos:

- **Ver historial de chat**:
  ```bash
  python app.py history --limit 10  # Muestra las últimas 10 interacciones
  python app.py history --search "decoradores"  # Busca conversaciones sobre decoradores
  ```

- **Exportar conversación**:
  ```bash
  python app.py export --md  # Exportar a Markdown
  python app.py export --pdf  # Exportar a PDF
  python app.py export --md --pdf  # Exportar ambos formatos
  ```

- **Limpiar historial**:
  ```bash
  python app.py clear
  ```

### Opciones avanzadas

- **Cambiar modelo**:
  ```bash
  python app.py ask "¿Cuál es la capital de Francia?" --model meta-llama/llama-4-scout-17b-16e-instruct
  ```

- **Ajustar temperatura**:
  ```bash
  python app.py ask "Escribe un poema sobre el mar" --temperature 0.8
  ```

- **Limitar tokens**:
  ```bash
  python app.py ask "Resume la Guerra Civil Española" --max-tokens 500
  ```

## 🧪 Desarrollo

### Configuración del entorno de desarrollo

1. Instala las dependencias de desarrollo:
   ```bash
   make install-dev
   ```

2. Configura los hooks de pre-commit:
   ```bash
   make init-dev
   ```

### Verificación de calidad

- **Ejecutar linting**:
  ```bash
  make lint
  ```

- **Verificar tipos**:
  ```bash
  make type-check
  ```

- **Ejecutar tests**:
  ```bash
  make test
  ```

- **Ejecutar todas las verificaciones**:
  ```bash
  make quality
  ```

## 📊 Estructura del proyecto

```
python-expert-llama4/
├── app.py              # CLI principal y punto de entrada
├── groq_client.py      # Cliente para la API de Groq
├── chat_db.py          # Manejo de base de datos para historial
├── tests/              # Tests unitarios
├── docs/               # Documentación generada
├── exports/            # Conversaciones exportadas
├── .env                # Variables de entorno (no incluido en repo)
├── makefile            # Comandos útiles
├── pyproject.toml      # Configuración de herramientas
└── README.md           # Este archivo
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, asegúrate de seguir estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## 🙏 Agradecimientos

- [Groq](https://groq.com) por proporcionar acceso a modelos Llama
- [Typer](https://typer.tiangolo.com/) para la interfaz CLI
- [Rich](https://rich.readthedocs.io/) para el formato en terminal
- [SQLAlchemy](https://www.sqlalchemy.org/) para el manejo de base de datos
