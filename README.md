# Projeto Agente Autônomo (Réplica do Manus)

Este projeto implementa um agente de IA autônomo inspirado na arquitetura do "Manus", utilizando o `CodeActAgent` e outras ferramentas de código aberto. O ambiente é totalmente orquestrado com Docker e Docker Compose.

## Estrutura do Projeto

- `docker-compose.yml`: O arquivo principal que define e orquestra todos os serviços.
- `code-executor.Dockerfile`: As instruções para construir a imagem Docker para os serviços Python.
- `requirements.txt`: Lista de dependências Python.
- `app.py`: A interface de usuário principal, construída com Gradio.
- `agent_src/`: O código-fonte do agente.
- `README.md`: Este manual de instruções.

## Pré-requisitos

Antes de começar, garanta que você tem os seguintes softwares instalados:
1.  **Docker:** [Instruções de instalação](https://docs.docker.com/engine/install/)
2.  **Docker Compose:** Geralmente vem com o Docker Desktop. [Instruções](https://docs.docker.com/compose/install/)
3.  **Git:** Para clonar os repositórios necessários.
4.  **GPU NVIDIA & NVIDIA Container Toolkit:** **Obrigatório** para o serviço `llm-server`. O `vLLM` requer uma GPU NVIDIA para funcionar. [Instruções de instalação](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Passo a Passo para Configuração e Execução

### Passo 1: Preparar os Diretórios

Clone este repositório e, dentro dele, crie os diretórios para o modelo e para a interface de chat.

```bash
# (Assumindo que você já clonou este projeto)
mkdir model
mkdir chat-ui
mkdir workspace
mkdir -p data/mongodb
```

### Passo 2: Baixar o Modelo LLM

O serviço `llm-server` precisa dos arquivos do modelo. Vamos usar o `CodeActAgent-Mistral-7b-v0.1`.

```bash
# Navegue até o diretório do modelo que você criou
cd model

# Clone o repositório do modelo
git lfs install
git clone https://huggingface.co/xingyaoww/CodeActAgent-Mistral-7b-v0.1 .

# Volte para a raiz do projeto
cd ..
```

### Passo 3: Obter o Código da Interface (Chat-UI)

A interface de chat recomendada é a `chat-ui` do Hugging Face.

```bash
# Navegue até o diretório da UI que você criou
cd chat-ui

# Clone o repositório da interface de chat
git clone https://github.com/huggingface/chat-ui .

# Volte para a raiz do projeto
cd ..
```

### Passo 4: Configurar a Interface (Chat-UI)

A interface de chat precisa ser configurada para se comunicar com os outros serviços.

1.  **Copie o template de configuração:**
    ```bash
    cp chat-ui/.env.template chat-ui/.env.local
    ```
2.  **Edite o arquivo `chat-ui/.env.local`:**
    Você precisará modificar/adicionar as seguintes linhas para apontar para os nossos serviços Docker. Use um editor de texto para fazer as alterações.

    ```env
    # Exemplo de configuração para .env.local

    # Conexão com o MongoDB
    MONGODB_URL=mongodb://mongo:27017

    # Configuração do Modelo (LLM)
    MODELS=`[
      {
        "name": "CodeActAgent-Mistral-7b-v0.1",
        "dataset": "CodeActAgent",
        "websiteUrl": "https://huggingface.co/xingyaoww/CodeActAgent-Mistral-7b-v0.1",
        "preprompt": "Você é um agente de IA prestativo e autônomo.",
        "chatPromptTemplate" : "...",
        "parameters": {
          "temperature": 0.1,
          "top_p": 0.95,
          "max_new_tokens": 4096
        },
        "endpoints": [{
          "url": "http://llm-server:8000/v1/chat/completions",
          "type": "openai"
        }]
      }
    ]`

    # Adicione a URL para o nosso executor de código
    JUPYTER_API_URL=http://code-executor:8888
    ```

    **Nota:** A configuração exata de `MODELS` pode variar. Consulte a documentação da `chat-ui` para detalhes, mas o `endpoints.url` deve apontar para `http://llm-server:8000/v1/chat/completions`.

### Passo 5: Iniciar Todos os Serviços

Com tudo configurado, você pode iniciar o ambiente completo com um único comando a partir do diretório raiz do projeto.

```bash
# O --build é importante na primeira vez para construir as imagens customizadas
docker-compose up -d --build
```

### Passo 6: Iniciar e Acessar a Aplicação

Com tudo configurado, você pode iniciar o ambiente completo com um único comando a partir do diretório raiz do projeto.

```bash
# O --build é importante na primeira vez para construir as imagens customizadas
docker-compose up -d --build
```

Após alguns minutos (o `llm-server` pode demorar para carregar o modelo), os serviços estarão prontos.

#### **Acessando a Interface Principal (Recomendado)**
Abra seu navegador e acesse a nossa interface Gradio:
- **URL:** `http://localhost:7860`

Esta é a forma mais simples e direta de interagir com o agente.

#### **Logs dos Serviços**
Para verificar o status ou depurar qualquer um dos serviços em segundo plano, use:
```bash
docker-compose logs -f <nome_do_servico>
# Ex: docker-compose logs -f llm-server
# Ex: docker-compose logs -f code-executor
```

#### **Parando a Aplicação**
Para parar todos os serviços, execute:
```bash
docker-compose down
```

## Testando o Agente

Adicionamos uma suíte de testes de integração para verificar o comportamento do agente de ponta a ponta.

**Pré-requisito:** O ambiente Docker completo deve estar em execução (`docker-compose up`).

**Como executar os testes:**

1.  **Instale as dependências de teste:**
    ```bash
    pip install pytest pytest-asyncio
    ```

2.  **Execute o Pytest:**
    A partir do diretório raiz do projeto, execute o seguinte comando:
    ```bash
    pytest
    ```
    Isso descobrirá e executará automaticamente os testes no diretório `tests/`. Você verá a saída do teste no seu console.

---
*Nota sobre a `chat-ui` externa:* A configuração para a `chat-ui` (porta 5173) ainda está presente no `docker-compose.yml`, mas seu uso é opcional e requer a configuração manual do `.env.local` conforme descrito anteriormente. A interface Gradio é a maneira recomendada de usar este projeto.