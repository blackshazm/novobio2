import os

# URL para o servidor do LLM (serviço 'llm-server' no docker-compose)
# A porta interna do container é 8000, conforme o comando no docker-compose.yml.
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://llm-server:8000/v1")

# Nome do modelo que estamos usando, conforme servido pelo vLLM.
# O nome do modelo pode ser diferente dependendo de como o vLLM o registra.
# Usamos o nome do diretório como um padrão razoável.
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "CodeActAgent-Mistral-7b-v0.1")

# URL para o executor de código (serviço 'code-executor' no docker-compose)
JUPYTER_GATEWAY_URL = os.getenv("JUPYTER_GATEWAY_URL", "http://code-executor:8888")

# Chave de API (pode ser um valor fictício, pois estamos em um ambiente local)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")
