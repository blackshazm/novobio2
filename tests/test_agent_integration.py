import pytest
import os
import asyncio
from agent_src.main import Agent

# Marcador para indicar que estes são testes de integração
# e requerem que todo o ambiente Docker (LLM, Jupyter) esteja em execução.
# Para executar apenas estes testes: `pytest -m integration`
@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_creates_flask_app_e2e():
    """
    Testa um fluxo de ponta a ponta onde o agente recebe a tarefa de criar
    uma aplicação web Flask simples.
    O teste verifica se o agente usa a ferramenta de scaffolding para criar
    a estrutura de arquivos esperada.
    """
    # Definição da Tarefa
    project_name = "meu_site_teste"
    task = f"Crie um site Flask 'hello world' chamado '{project_name}'. Use a ferramenta de scaffolding."

    # Caminhos para os arquivos que esperamos que o agente crie
    base_path = os.path.join("workspace", project_name)
    app_py_path = os.path.join(base_path, "app.py")
    index_html_path = os.path.join(base_path, "templates", "index.html")

    # Garantir que o diretório não existe antes do teste
    if os.path.exists(base_path):
        import shutil
        shutil.rmtree(base_path)

    # Instanciar e executar o agente
    agent = Agent()
    await agent.run(task)

    # Verificações (Asserts)
    # Verificar se os arquivos principais foram criados pela ferramenta de scaffolding
    assert os.path.isdir(base_path), f"O diretório do projeto '{base_path}' não foi criado."
    assert os.path.exists(app_py_path), f"O agente falhou em criar o arquivo principal '{app_py_path}'."
    assert os.path.exists(index_html_path), f"O agente falhou em criar o template inicial '{index_html_path}'."

    # Verificar o conteúdo do app.py para garantir que é um app Flask
    with open(app_py_path, 'r') as f:
        content = f.read()
    assert "from flask import Flask" in content, "O arquivo app.py não parece ser uma aplicação Flask."

    print(f"\nTeste de integração concluído com sucesso. Projeto '{project_name}' foi criado.")

# Para executar este teste:
# 1. Certifique-se de que o ambiente Docker está em execução com `docker-compose up -d`.
# 2. Instale as dependências de teste: `pip install pytest pytest-asyncio`
# 3. Execute o pytest a partir do diretório raiz do projeto: `pytest`
