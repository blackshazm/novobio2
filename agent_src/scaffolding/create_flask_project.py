import os
import argparse

# Template para o arquivo principal da aplicação Flask
FLASK_APP_TEMPLATE = """
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Rodando em 0.0.0.0 torna acessível fora do container
    # O agente deve rodar isso em background com `&`
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

# Template para a página HTML inicial
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Bem-vindo ao {project_name}!</h1>
    <p>Seu app Flask está funcionando.</p>
</body>
</html>
"""

# Template para a folha de estilos CSS
CSS_TEMPLATE = """
body {{
    font-family: sans-serif;
    background-color: #f4f4f4;
    color: #333;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}}

h1 {{
    color: #0056b3;
}}
"""

def create_flask_project(project_name: str):
    """
    Cria uma estrutura de diretórios e arquivos para um projeto Flask básico
    dentro do diretório 'workspace'.
    """
    base_path = os.path.join("workspace", project_name)
    templates_path = os.path.join(base_path, "templates")
    static_path = os.path.join(base_path, "static")

    # Cria os diretórios
    os.makedirs(templates_path, exist_ok=True)
    os.makedirs(static_path, exist_ok=True)
    print(f"Diretórios criados em: {base_path}")

    # Cria os arquivos
    with open(os.path.join(base_path, "app.py"), "w") as f:
        f.write(FLASK_APP_TEMPLATE)
    print("app.py criado.")

    with open(os.path.join(templates_path, "index.html"), "w") as f:
        f.write(HTML_TEMPLATE.format(project_name=project_name))
    print("templates/index.html criado.")

    with open(os.path.join(static_path, "style.css"), "w") as f:
        f.write(CSS_TEMPLATE)
    print("static/style.css criado.")

    print(f"\nProjeto Flask '{project_name}' criado com sucesso em '{base_path}'.")
    print("Para rodar o projeto, navegue até o diretório e execute: python app.py")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gera uma estrutura básica de projeto Flask.")
    parser.add_argument("--name", type=str, required=True, help="O nome do projeto a ser criado.")

    args = parser.parse_args()

    create_flask_project(args.name)
