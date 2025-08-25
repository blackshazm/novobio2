# Usa a imagem oficial do Ollama como base.
FROM ollama/ollama

# Durante a construção da imagem, baixa o modelo CodeActAgent.
# Isso garante que o modelo esteja disponível assim que o container iniciar,
# evitando a necessidade de baixá-lo no primeiro uso.
RUN ollama pull xingyaow/codeact-agent-mistral

# O comando padrão da imagem base (`ollama serve`) será usado para iniciar o servidor.
