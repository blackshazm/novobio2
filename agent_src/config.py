import os

# URL para o servidor do LLM (serviço 'llm-server' no docker-compose, agora rodando Ollama)
# A porta padrão do Ollama é 11434.
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://llm-server:11434/v1")

# Nome do modelo que estamos usando, conforme registrado no Ollama.
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "xingyaow/codeact-agent-mistral")

# URL para o executor de código (serviço 'code-executor' no docker-compose)
JUPYTER_GATEWAY_URL = os.getenv("JUPYTER_GATEWAY_URL", "http://code-executor:8888")

# Chave de API (pode ser um valor fictício, pois estamos em um ambiente local)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")
