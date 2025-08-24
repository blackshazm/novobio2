import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional

class KnowledgeBase:
    """
    Gerencia uma base de conhecimento vetorial usando FAISS e SentenceTransformers.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', knowledge_dir: str = './knowledge'):
        self.knowledge_dir = knowledge_dir
        self.model = SentenceTransformer(model_name)
        self.index: Optional[faiss.IndexFlatL2] = None
        self.documents: List[str] = []
        self._build_index()

    def _load_documents(self):
        """Carrega documentos de texto do diretório de conhecimento."""
        print(f"Carregando documentos de: {self.knowledge_dir}")
        if not os.path.exists(self.knowledge_dir):
            print(f"Diretório de conhecimento '{self.knowledge_dir}' não encontrado. A base de conhecimento estará vazia.")
            return

        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.knowledge_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Simplesmente adiciona o conteúdo do arquivo inteiro como um documento.
                    # Para textos longos, uma estratégia de "chunking" (divisão) seria melhor.
                    self.documents.append(f.read())
        print(f"Carregados {len(self.documents)} documentos.")

    def _build_index(self):
        """Constrói ou reconstrói o índice FAISS a partir dos documentos."""
        self._load_documents()
        if not self.documents:
            print("Nenhum documento para indexar.")
            return

        print("Codificando documentos e construindo índice FAISS...")
        embeddings = self.model.encode(self.documents, convert_to_tensor=False)

        # Assegurar que os embeddings são do tipo float32, que é o que o FAISS espera.
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        print(f"Índice construído com {self.index.ntotal} vetores.")

    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Busca na base de conhecimento por trechos relevantes para a consulta.
        Retorna os 'k' documentos mais relevantes.
        """
        if not self.index or self.index.ntotal == 0:
            return ["A base de conhecimento está vazia."]

        print(f"Buscando na base de conhecimento por: '{query}'")
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        distances, indices = self.index.search(query_embedding, k)

        results = [self.documents[i] for i in indices[0] if i < len(self.documents)]
        print(f"Encontrados {len(results)} resultados relevantes.")
        return results

# Exemplo de uso
if __name__ == '__main__':
    # Para testar, crie um diretório './knowledge' e adicione alguns arquivos .txt nele.
    # Ex: ./knowledge/ia.txt -> "Inteligência artificial é a simulação da inteligência humana em máquinas."
    # Ex: ./knowledge/python.txt -> "Python é uma linguagem de programação de alto nível."

    if not os.path.exists('./knowledge'):
        os.makedirs('./knowledge')
        with open('./knowledge/ia.txt', 'w') as f:
            f.write("Inteligência artificial é a simulação da inteligência humana em máquinas.")
        with open('./knowledge/python.txt', 'w') as f:
            f.write("Python é uma linguagem de programação de alto nível, interpretada, de script, imperativa, orientada a objetos, funcional, de tipagem dinâmica e forte.")

    kb = KnowledgeBase()

    if kb.index:
        search_results = kb.search("O que é IA?")
        print("\nResultados da busca por 'O que é IA?':")
        for res in search_results:
            print(f"- {res}")

        search_results_py = kb.search("Me fale sobre linguagens de programação")
        print("\nResultados da busca por 'Me fale sobre linguagens de programação':")
        for res in search_results_py:
            print(f"- {res}")
    else:
        print("\nNão foi possível testar a busca pois o índice não foi construído.")
