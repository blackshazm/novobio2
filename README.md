# Projeto Agente Autônomo (v2 - com Ollama)

Este projeto implementa um agente de IA autônomo inspirado na arquitetura do "Manus", utilizando o `CodeActAgent` e outras ferramentas de código aberto. O ambiente é totalmente orquestrado com Docker e Docker Compose e agora usa **Ollama** para servir o modelo, removendo a necessidade de uma GPU NVIDIA.

## Estrutura do Projeto

- `docker-compose.yml`: O arquivo principal que define e orquestra todos os serviços.
- `ollama.Dockerfile`: Constrói a imagem do Ollama e baixa o modelo `CodeActAgent` automaticamente.
- `code-executor.Dockerfile`: Constrói a imagem Docker para os serviços Python (Gradio UI e Jupyter).
- `requirements.txt`: Lista de dependências Python.
- `app.py`: A interface de usuário principal, construída com Gradio.
- `agent_src/`: O código-fonte do agente.
- `tests/`: Testes de integração para o agente.
- `README.md`: Este manual de instruções.

## Pré-requisitos

Antes de começar, garanta que você tem os seguintes softwares instalados:
1.  **Docker:** [Instruções de instalação](https://docs.docker.com/engine/install/)
2.  **Docker Compose:** Geralmente vem com o Docker Desktop. [Instruções](https://docs.docker.com/compose/install/)

É isso! A necessidade de uma GPU NVIDIA foi removida.

## Passo a Passo para Configuração e Execução

### Passo 1: Preparar os Diretórios

Clone este repositório e, dentro dele, crie os diretórios necessários para o workspace do agente.

```bash
# (Assumindo que você já clonou este projeto)
mkdir workspace
mkdir -p data/mongodb
mkdir knowledge
```
O download do modelo e da UI externa (`chat-ui`) não são mais passos necessários para a execução principal.

### Passo 2: Iniciar a Aplicação

Com o Docker em execução, inicie o ambiente completo com um único comando a partir do diretório raiz do projeto.

```bash
# O --build é importante na primeira vez para construir as imagens customizadas
# e para o Ollama baixar o modelo. Isso pode levar alguns minutos.
docker-compose up -d --build
```
Na primeira vez que você executar este comando, o Ollama fará o download do modelo `xingyaow/codeact-agent-mistral`, que tem vários gigabytes. Por favor, seja paciente. O progresso será exibido nos logs.

### Passo 3: Acessar a Interface do Agente

Após os containers estarem em execução, acesse a interface Gradio no seu navegador:
- **URL:** `http://localhost:7860`

Esta é a forma principal e recomendada de interagir com o agente.

### Monitoramento e Gerenciamento

**Logs dos Serviços:**
Para verificar o status ou depurar qualquer um dos serviços em segundo plano (especialmente para ver o progresso do download do Ollama), use:
```bash
docker-compose logs -f <nome_do_servico>
# Ex: docker-compose logs -f llm-server
```

**Parando a Aplicação:**
Para parar todos os serviços, execute:
```bash
docker-compose down
```

## Testando o Agente

Adicionamos uma suíte de testes de integração para verificar o comportamento do agente de ponta a ponta.

**Pré-requisito:** O ambiente Docker completo deve estar em execução (`docker-compose up`).

**Como executar os testes:**

1.  **Instale as dependências de teste (em seu ambiente local, não no Docker):**
    ```bash
    pip install pytest pytest-asyncio
    ```

2.  **Execute o Pytest:**
    A partir do diretório raiz do projeto, execute o seguinte comando:
    ```bash
    pytest
    ```
    Isso descobrirá e executará automaticamente os testes no diretório `tests/`. Você verá a saída do teste no seu console.