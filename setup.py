from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="chat_llama_groq",
    version="0.1.0",
    author="Gonzalo Python",
    author_email="gonzalo@example.com",
    description="CLI para interactuar con modelos Llama a través de la API de Groq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gonzapython/Chat_llama_groq",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "chat-llama-groq=app:app",
        ],
    },
)
