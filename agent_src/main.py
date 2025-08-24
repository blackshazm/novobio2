import openai
import re
from typing import List, Dict

from .config import LLM_API_BASE, LLM_MODEL_NAME, OPENAI_API_KEY
from .jupyter_client import JupyterClient
from .knowledge_base import KnowledgeBase

# 1. Definição do Prompt do Sistema (Versão com RAG)
SYSTEM_PROMPT = """
Você é Manus, um agente de IA autônomo e competente. Sua principal forma de interagir com o mundo é através da execução de código Python no ambiente de trabalho (`/home/jovyan/work`).

<princípios_gerais>
1.  **Analise e Planeje:** Antes de agir, sempre analise a tarefa. Para tarefas complexas, seu primeiro passo deve ser criar um plano detalhado e salvá-lo em `todo.md`.
2.  **Aja com Código:** Sua única forma de ação é gerar um bloco de código Python. Responda SEMPRE com um único bloco de código formatado como ```python\n# seu código\n```. Não inclua texto fora do bloco.
3.  **Use o Filesystem:** Use o diretório de trabalho para salvar arquivos, rascunhos, e resultados intermediários. Isso é sua memória de longo prazo.
4.  **Consulte a Base de Conhecimento:** Antes de responder a uma pergunta, considere as informações de contexto fornecidas. Se o histórico contiver uma mensagem do tipo "[CONTEXTO DA BASE DE CONHECIMENTO]", use essa informação para formular sua resposta ou plano.
5.  **Observe e Adapte:** Após cada execução, você receberá o resultado (STDOUT/STDERR). Use essa observação para decidir seu próximo passo e para depurar seu código se necessário.
6.  **Conclusão:** Ao concluir todos os passos do plano, sua última ação deve ser `print("TASK_COMPLETE")`.
</princípios_gerais>

<regras_de_planejamento>
- O plano deve ser salvo em `workspace/todo.md`.
- O formato do plano deve ser uma lista de tarefas em markdown (ex: `- [ ] Passo 1: Fazer X.`).
- Conforme você completa os passos, sua primeira ação no ciclo seguinte deve ser ler o `todo.md`, e a ação seguinte deve ser reescrevê-lo com o passo correspondente marcado como concluído (ex: `- [x] Passo 1: Fazer X.`).
</regras_de_planejamento>

<regras_de_erro>
- Se a execução de um código resultar em um erro (STDERR não vazio), sua primeira prioridade é depurar.
- Analise a mensagem de erro no STDERR.
- Gere um novo bloco de código que corrija o erro anterior. Não repita o código que falhou.
- Se o mesmo tipo de erro persistir por 3 tentativas, abandone a abordagem atual e tente uma estratégia completamente diferente para alcançar o objetivo.
</regras_de_erro>
"""

PLANNER_PROMPT_TEMPLATE = """
Você é um assistente de planejamento de IA. Sua tarefa é decompor um objetivo complexo em uma lista de passos simples e acionáveis em formato markdown.

Objetivo do Usuário: "{task}"

Analise o objetivo e gere um plano detalhado. Cada passo deve ser uma ação clara que o agente pode executar.

Responda APENAS com o plano em formato markdown, e nada mais.
"""


class Agent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=LLM_API_BASE)
        self.jupyter_client = JupyterClient()
        self.knowledge_base = KnowledgeBase()
        self.event_stream: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.error_count = 0
        self.last_error = None

    def _extract_python_code(self, text: str) -> str:
        """Extrai o bloco de código Python de uma resposta do LLM."""
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _create_plan(self, task: str, context: str = "") -> str:
        """Gera um plano de execução para uma tarefa complexa, usando contexto se disponível."""
        print("Gerando plano de execução...")
        planner_task = f"{task}\n\nContexto relevante:\n{context}" if context else task
        planner_prompt = PLANNER_PROMPT_TEMPLATE.format(task=planner_task)

        response = self.client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": planner_prompt}],
            temperature=0.0,
        )
        plan = response.choices[0].message.content
        print(f"Plano gerado:\n---\n{plan}\n---")
        return plan

    def _inject_knowledge(self, task: str):
        """Busca na base de conhecimento e injeta contexto no event stream se a tarefa for uma pergunta."""
        # Heurística simples: se a tarefa contém 'o que é', 'quem é', 'me fale sobre', etc.
        question_triggers = ['o que é', 'quem é', 'me fale sobre', 'qual é', 'como funciona']
        if any(trigger in task.lower() for trigger in question_triggers):
            print("Tarefa parece ser uma pergunta. Buscando na base de conhecimento...")
            results = self.knowledge_base.search(task)
            if results:
                context_str = "\n".join(f"- {res}" for res in results)
                knowledge_prompt = f"[CONTEXTO DA BASE DE CONHECIMENTO]\n{context_str}\n[FIM DO CONTEXTO]"
                self.event_stream.append({"role": "system", "content": knowledge_prompt})
                print("Contexto injetado no event stream.")
                return context_str
        return ""

    async def run(self, user_task: str):
        """Executa o loop principal do agente de forma assíncrona."""
        print(f"Iniciando tarefa: {user_task}")
        self.jupyter_client.start_kernel()

        # Passo -1: Injetar conhecimento se for uma pergunta
        knowledge_context = self._inject_knowledge(user_task)

        # Passo 0: Gerar o plano
        plan = self._create_plan(user_task, context=knowledge_context)

        initial_action_code = f'with open("workspace/todo.md", "w") as f:\n    f.write("""{plan}""")'

        self.event_stream.append({"role": "user", "content": f"O objetivo é: {user_task}."})

        code_to_execute = initial_action_code

        try:
            while True:
                print("\n==================== NOVO CICLO ====================")

                print(f"Executando código:\n---\n{code_to_execute}\n---")
                # A chamada para execute_code agora é assíncrona
                stdout, stderr = await self.jupyter_client.execute_code(code_to_execute)
                observation = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                print(f"Observação da Execução:\n---\n{observation}\n---")

                # Lógica de contagem de erro
                if stderr:
                    if stderr == self.last_error:
                        self.error_count += 1
                    else:
                        self.last_error = stderr
                        self.error_count = 1

                    if self.error_count >= 3:
                        print("O mesmo erro ocorreu 3 vezes. Injetando instrução para mudar de estratégia.")
                        observation += "\n\nAVISO DO SISTEMA: Você tentou a mesma operação várias vezes e falhou. Tente uma abordagem completamente diferente."
                        self.error_count = 0 # Reseta o contador
                else:
                    self.error_count = 0
                    self.last_error = None

                self.event_stream.append({"role": "assistant", "content": f"```python\n{code_to_execute}\n```"})
                self.event_stream.append({"role": "user", "content": f"Resultado da execução:\n{observation}"})

                if "TASK_COMPLETE" in code_to_execute:
                    print("\nSinal de 'TASK_COMPLETE' detectado. Finalizando a tarefa.")
                    break

                print(f"Conteúdo do Event Stream enviado ao LLM (últimos 4 eventos): {self.event_stream[-4:]}")
                response = self.client.chat.completions.create(
                    model=LLM_MODEL_NAME,
                    messages=self.event_stream,
                    temperature=0.1,
                )
                llm_response_text = response.choices[0].message.content
                print(f"Resposta do LLM:\n---\n{llm_response_text}\n---")

                code_to_execute = self._extract_python_code(llm_response_text)

                if not code_to_execute:
                    print("Nenhum código encontrado na resposta. A tarefa pode ter terminado de forma inesperada.")
                    break

        finally:
            self.jupyter_client.shutdown_kernel()
            print("\nLoop do agente finalizado.")

if __name__ == '__main__':
    import asyncio
    import os

    # Crie o diretório 'knowledge' e um arquivo de exemplo para o teste de RAG
    if not os.path.exists('./knowledge'):
        os.makedirs('./knowledge')
        with open('./knowledge/ia.txt', 'w') as f:
            f.write("A Inteligência Artificial (IA) é um campo da ciência da computação dedicado a criar sistemas que podem realizar tarefas que normalmente exigiriam inteligência humana.")

    agent = Agent()
    # Tarefa que pode usar a base de conhecimento
    task = "Me fale sobre o que é Inteligência Artificial e salve a explicação em um arquivo 'ia_explicação.txt' no workspace."

    # Executa o loop assíncrono do agente
    asyncio.run(agent.run(task))
