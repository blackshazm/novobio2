# Baseado na imagem do Jupyter para ter um ambiente Python robusto.
# https://hub.docker.com/r/jupyter/base-notebook
FROM jupyter/base-notebook:python-3.10

# Mudar para o usuário root para instalar pacotes de sistema
USER root

# Instalar dependências do sistema, como Node.js, npm e outras utilidades
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    wget \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Voltar para o usuário padrão do contêiner Jupyter
USER ${NB_UID}

# Criar um diretório de trabalho para o agente
WORKDIR /home/jovyan/work

# Instalar as bibliotecas Python necessárias para automação e manipulação de dados
COPY --chown=${NB_UID}:${NB_GID} requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar o Playwright e seus navegadores
RUN playwright install --with-deps

# O `start-notebook.sh` do `jupyter/base-notebook` é o CMD padrão.
# Vamos precisar sobrescrevê-lo no docker-compose.yml para iniciar o Jupyter Kernel Gateway.
# Expondo a porta padrão do Kernel Gateway.
EXPOSE 8888
