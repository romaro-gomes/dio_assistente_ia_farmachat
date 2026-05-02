from pathlib import Path
from util.use_retriever import create_retrievers

EXTENSOES = {".pdf", ".docx", ".html", ".pptx"}

def collect_files_from_folder(root_folder: str) -> dict[str, list[Path]]:
    root = Path(root_folder)
    resultado = {}

    subpastas = [root] + [p for p in root.rglob("*") if p.is_dir()]  # ✅ link removido

    for pasta in subpastas:
        arquivos = [
            f for f in pasta.iterdir()
            if f.is_file() and f.suffix.lower() in EXTENSOES  # ✅ link removido
        ]
        if arquivos:
            nome_pasta = str(pasta.relative_to(root)) or root.name  # ✅ link removido
            resultado[nome_pasta] = arquivos
            print(f"📂 {nome_pasta} → {len(arquivos)} arquivo(s)")

    if not resultado:
        print("Nenhum arquivo encontrado.")


    return resultado


def ingest_retriever():
    resultado = collect_files_from_folder(
        root_folder="/home/romario/projetos/Pessoal/farma_chat/data/raw/"
    )

    # ✅ Achata o dicionário em lista antes de passar
    todos_arquivos = [
        arquivo
        for arquivos in resultado.values()
        for arquivo in arquivos
    ]
    
    create_retrievers(todos_arquivos)
    
if __name__ == '__main__':
	ingest_retriever()
