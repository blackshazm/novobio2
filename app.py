import gradio as gr
import asyncio
import io
import sys
from agent_src.main import Agent

# Função para capturar a saída de print e exibi-la em tempo real (simulado via yield)
async def run_agent_task(task: str, progress=gr.Progress()):
    """
    Executa a tarefa do agente e captura a saída do console para exibir na UI.
    """
    if not task:
        yield "Por favor, insira uma tarefa.", ""

    # Redireciona stdout para capturar os logs do agente
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    agent = Agent()

    # Gerador para fornecer feedback de progresso
    def log_generator():
        yield "Iniciando a tarefa do agente...\n"
        # O loop do agente é bloqueante, então executamos e depois pegamos a saída.
        # Uma implementação mais avançada usaria yields dentro do loop do agente.
        asyncio.run(agent.run(task))
        yield captured_output.getvalue()

    full_log = ""
    # Como a execução do agente é um processo longo, iteramos sobre um gerador
    # para manter a UI responsiva, embora o log só apareça no final aqui.
    for log_chunk in log_generator():
        full_log += log_chunk
        yield full_log

    # Restaura stdout
    sys.stdout = old_stdout

    # Retorna o log final
    return full_log

# Criação da Interface Gradio
with gr.Blocks(theme=gr.themes.Soft(), title="Agente Autônomo") as demo:
    gr.Markdown("# Agente Autônomo (Réplica do Manus)")
    gr.Markdown("Digite uma tarefa complexa e observe o agente trabalhar. Acompanhe os logs da execução abaixo.")

    with gr.Row():
        task_input = gr.Textbox(label="Tarefa do Agente", placeholder="Ex: Crie um script em python para calcular o n-ésimo número de Fibonacci e salve em um arquivo chamado 'fibonacci.py'.", lines=3)

    submit_button = gr.Button("Executar Tarefa", variant="primary")

    with gr.Accordion("Logs da Execução", open=True):
        output_log = gr.Textbox(label="Output", lines=20, interactive=False)

    submit_button.click(
        fn=run_agent_task,
        inputs=[task_input],
        outputs=[output_log]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
