import subprocess


def export_markdown(messages):
    lines = []
    for m in messages:
        prefix = "**Usuario**:" if m.role == "user" else "**Asistente:**"
        lines.append(f"{prefix}  \n{m.content}")
    return "\n\n".join(lines)

def convert_md_to_pdf(md_file: str, pdf_file: str):
    subprocess.run(["pandoc", md_file, "-o", pdf_file], check=True)

