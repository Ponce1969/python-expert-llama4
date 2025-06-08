# Contribuyendo a Chat Llama-Groq

¡Gracias por tu interés en contribuir a Chat Llama-Groq! Este documento proporciona directrices para contribuir al proyecto.

## Flujo de trabajo de desarrollo

1. **Fork** el repositorio en GitHub.
2. **Clona** tu fork localmente:
   ```bash
   git clone https://github.com/tu-usuario/Chat_llama_groq.git
   cd Chat_llama_groq
   ```
3. **Configura** el entorno de desarrollo:
   ```bash
   make install-dev
   make init-dev  # Instala pre-commit hooks
   ```
4. **Crea una rama** para tu contribución:
   ```bash
   git checkout -b feature/nombre-de-tu-caracteristica
   ```
5. **Realiza tus cambios** siguiendo las convenciones de código.
6. **Ejecuta las pruebas** para asegurarte de que todo funciona:
   ```bash
   make quality  # Ejecuta linting, verificación de tipos y tests
   ```
7. **Commit** tus cambios:
   ```bash
   git commit -m "Descripción clara del cambio"
   ```
8. **Push** a tu fork:
   ```bash
   git push origin feature/nombre-de-tu-caracteristica
   ```
9. **Crea un Pull Request** desde tu fork a la rama principal del repositorio original.

## Convenciones de código

- Sigue [PEP 8](https://www.python.org/dev/peps/pep-0008/) para el estilo de código.
- Usa [type hints](https://docs.python.org/3/library/typing.html) para anotaciones de tipo.
- Escribe docstrings en formato [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Mantén el código limpio y bien documentado.

## Pruebas

- Añade pruebas para cualquier nueva funcionalidad o corrección de errores.
- Asegúrate de que todas las pruebas existentes pasen antes de enviar un PR.
- Apunta a una cobertura de código de al menos 80%.

## Proceso de revisión

1. Los mantenedores revisarán tu PR tan pronto como sea posible.
2. Es posible que se soliciten cambios o mejoras.
3. Una vez aprobado, tu PR será fusionado en la rama principal.

## Informes de errores

Si encuentras un error, por favor crea un issue en GitHub incluyendo:

- Una descripción clara del problema
- Pasos para reproducir el error
- Comportamiento esperado vs. comportamiento actual
- Capturas de pantalla si es aplicable
- Información sobre tu entorno (OS, versión de Python, etc.)

## Solicitudes de características

Las solicitudes de características son bienvenidas. Por favor, proporciona:

- Una descripción clara de la característica
- Justificación de por qué sería útil
- Ejemplos de cómo funcionaría

## Licencia

Al contribuir a este proyecto, aceptas que tus contribuciones estarán bajo la misma licencia que el proyecto (MIT).
