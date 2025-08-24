import pytest
import os
import asyncio
from agent_src.main import Agent

# Marcador para indicar que estes são testes de integração
# e requerem que todo o ambiente Docker (LLM, Jupyter) esteja em execução.
# Para executar apenas estes testes: `pytest -m integration`
@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_creates_file_e2e():
    """
    Testa um fluxo de ponta a ponta onde o agente recebe a tarefa de criar
    um arquivo com conteúdo específico.
    """
    # Definição da Tarefa
    task = "Crie um arquivo chamado 'test_output.txt' no diretório 'workspace' com o conteúdo exato 'hello from test'."

    # Caminho para o arquivo que esperamos que o agente crie
    output_filepath = "workspace/test_output.txt"

    # Garantir que o arquivo não existe antes do teste
    if os.path.exists(output_filepath):
        os.remove(output_filepath)

    # Instanciar e executar o agente
    agent = Agent()
    await agent.run(task)

    # Verificações (Asserts)
    # 1. Verificar se o arquivo foi criado
    assert os.path.exists(output_filepath), f"O agente falhou em criar o arquivo em {output_filepath}"

    # 2. Verificar se o conteúdo do arquivo está correto
    with open(output_filepath, 'r') as f:
        content = f.read()
    assert content == "hello from test", f"O conteúdo do arquivo é '{content}', mas esperávamos 'hello from test'"

    # Limpeza
    # Deixar o arquivo para inspeção manual, se desejado, ou remover.
    # print(f"Teste concluído. O arquivo de saída '{output_filepath}' foi criado com sucesso.")
    # os.remove(output_filepath)

# Para executar este teste:
# 1. Certifique-se de que o ambiente Docker está em execução com `docker-compose up -d`.
# 2. Instale as dependências de teste: `pip install pytest pytest-asyncio`
# 3. Execute o pytest a partir do diretório raiz do projeto: `pytest`
