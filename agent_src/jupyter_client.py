import requests
import json
import uuid
import asyncio
import websockets
from typing import Tuple

from .config import JUPYTER_GATEWAY_URL

class JupyterClient:
    """
    Um cliente assíncrono para interagir com um Jupyter Kernel Gateway usando WebSockets.
    """
    def __init__(self, gateway_url: str = JUPYTER_GATEWAY_URL):
        self.gateway_url = gateway_url
        self.http_url = gateway_url
        self.ws_url = "ws://" + gateway_url.split("://")[1]
        self.kernel_id = None
        self.session = requests.Session()

    def start_kernel(self) -> str:
        """Inicia um novo kernel via REST API e armazena seu ID."""
        if self.kernel_id:
            print(f"Kernel {self.kernel_id} já está em execução.")
            return self.kernel_id

        url = f"{self.http_url}/api/kernels"
        response = self.session.post(url, json={})
        response.raise_for_status()
        kernel_data = response.json()
        self.kernel_id = kernel_data['id']
        print(f"Jupyter Kernel iniciado com ID: {self.kernel_id}")
        return self.kernel_id

    async def execute_code(self, code: str) -> Tuple[str, str]:
        """
        Executa um bloco de código no kernel ativo usando WebSockets.
        Retorna uma tupla contendo (stdout, stderr).
        """
        if not self.kernel_id:
            raise Exception("Kernel não iniciado. Chame start_kernel() primeiro.")

        ws_connection_url = f"{self.ws_url}/api/kernels/{self.kernel_id}/channels"

        stdout_parts = []
        stderr_parts = []

        async with websockets.connect(ws_connection_url) as websocket:
            # Construir a mensagem de execução de código padrão do Jupyter
            msg_id = uuid.uuid4().hex
            msg = {
                "header": {
                    "msg_id": msg_id,
                    "username": "agent",
                    "session": uuid.uuid4().hex,
                    "msg_type": "execute_request",
                    "version": "5.3",
                },
                "metadata": {},
                "content": {
                    "code": code,
                    "silent": False,
                    "store_history": True,
                    "user_expressions": {},
                    "allow_stdin": False,
                },
                "buffers": [],
                "parent_header": {},
                "channel": "shell",
            }

            await websocket.send(json.dumps(msg))

            while True:
                try:
                    message_str = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    message = json.loads(message_str)

                    # Verificar se a mensagem é uma resposta à nossa requisição
                    if message.get("parent_header", {}).get("msg_id") == msg_id:
                        msg_type = message["header"]["msg_type"]
                        content = message["content"]

                        if msg_type == "stream":
                            if content["name"] == "stdout":
                                stdout_parts.append(content["text"])
                            elif content["name"] == "stderr":
                                stderr_parts.append(content["text"])
                        elif msg_type == "error":
                            stderr_parts.append(f"{content['ename']}: {content['evalue']}")
                        elif msg_type == "status" and content["execution_state"] == "idle":
                            # A execução terminou
                            break
                except asyncio.TimeoutError:
                    print("Timeout esperando pela resposta do kernel. A execução pode ter travado.")
                    break

        return "".join(stdout_parts), "".join(stderr_parts)

    def shutdown_kernel(self):
        """Desliga o kernel ativo via REST API."""
        if not self.kernel_id:
            print("Nenhum kernel para desligar.")
            return

        url = f"{self.http_url}/api/kernels/{self.kernel_id}"
        response = self.session.delete(url)
        if response.status_code == 204:
            print(f"Kernel {self.kernel_id} desligado com sucesso.")
        else:
            print(f"Falha ao desligar o kernel {self.kernel_id}. Status: {response.status_code}")
        self.kernel_id = None

# Exemplo de uso assíncrono
async def main():
    client = JupyterClient()
    try:
        client.start_kernel()

        print("\n--- Teste 1: Executando código simples ---")
        stdout, stderr = await client.execute_code("print('Olá do Jupyter real!')\nimport platform\nprint(platform.python_version())")
        print(f"Saída Padrão:\n{stdout}")
        print(f"Saída de Erro:\n{stderr}")

        print("\n--- Teste 2: Executando código com erro ---")
        stdout, stderr = await client.execute_code("print(1/0)")
        print(f"Saída Padrão:\n{stdout}")
        print(f"Saída de Erro:\n{stderr}")

    finally:
        client.shutdown_kernel()

if __name__ == '__main__':
    # Este script precisa de um loop de eventos asyncio para rodar.
    # Para testar diretamente, você pode usar:
    # python -c "import asyncio; from agent_src.jupyter_client import main; asyncio.run(main())"
    # desde que o Jupyter Gateway esteja rodando.
    pass
