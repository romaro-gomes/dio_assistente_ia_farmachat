from docling.document_converter import DocumentConverter
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import pickle
from rank_bm25 import BM25Okapi
import streamlit as st
EXTENSOES = {".pdf", ".docx", ".html", ".pptx"}

def ingest_folder(folder_path: str):
    print(folder_path)
    folder = Path(folder_path)
    files = [
        file for file in folder.rglob("*")
        if file.is_file() and file.suffix.lower() in EXTENSOES
    ]
    if not files:
        print("Nenhum arquivo encontrado.")
        return []
    print(f"📁 {len(files)} arquivos encontrados")
    return files


def create_chunks_for_files(
    files,
    splitter=None,
    converter=None
):
    # Instancia aqui dentro para evitar problemas com defaults mutáveis
    if splitter is None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=100
        )
    if converter is None:
        converter = DocumentConverter()

    all_chunks = []
    for file in files:
        try:
            result = converter.convert(str(file))
            content = result.document.export_to_markdown()
            chunks = splitter.create_documents(          # ✅ plural
                texts=[content],
                metadatas=[{
                    "source": file.name,
                    "subject": str(file.parent)
                }]
            )
            all_chunks.extend(chunks)
            print(f"  ✅ {file.name} → {len(chunks)} chunks")

        except Exception as e:
            print(f"  ❌ Erro em {file.name}: {e}")
            continue

    return all_chunks


def create_vector_store(
    all_chunks,                                          # ✅ posicional
    persist_dir: str = "./chroma_db",
    embeddings=None
):
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large",
        )
    vectorstore = Chroma.from_documents(
        all_chunks,
        embeddings,
        persist_directory=persist_dir                   # ✅ nome correto
    )
    print(f"\n✅ {len(all_chunks)} chunks indexados no Chroma")
    return vectorstore                                   # ✅ retorna


def build_and_save_bm25(
    all_chunks,                                         # ✅ recebe Documents
    path: str = "./bm25_index/bm25okapi.pkl"
):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    docs_text = [doc.page_content for doc in all_chunks]
    tokenized = [doc.lower().split() for doc in docs_text]
    bm25 = BM25Okapi(tokenized)
    with open(path, "wb") as f:
        pickle.dump({"bm25": bm25, "docs": docs_text}, f)
    print("✅ BM25 salvo em disco")
    return bm25


def create_retrievers(files: str):
    '''
    files = ingest_folder(folder_path)
    if not files:
        return None
    '''    

    all_chunks = create_chunks_for_files(files)
    vectorstore = create_vector_store(all_chunks)       # ✅ usa o retorno
    build_and_save_bm25(all_chunks)                     # ✅ passa Documents

    # Hybrid retriever: BM25 + ChromaDB
    bm25_retriever = BM25Retriever.from_documents(all_chunks, k=6)
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    print('Bancos criados')
    return None
        
@st.cache_resource
def load_retrievers(
    persist_dir: str = "./chroma_db",
    bm25_path: str = "./bm25_index/bm25okapi.pkl",
    embeddings=None
):
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large", model_kwargs={"device": "cpu"}
        )

    # 1. Carrega ChromaDB
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    print("✅ ChromaDB carregado")

    # 2. Carrega BM25
    with open(bm25_path, "rb") as f:
        data = pickle.load(f)

    docs_text = data["docs"]
    docs = [Document(page_content=text) for text in docs_text]
    bm25_retriever = BM25Retriever.from_documents(docs, k=6)
    print("✅ BM25 carregado")
    
    return dense_retriever, bm25_retriever


def get_retrievers(folder_path: str):
    chroma_exists = Path("./chroma_db").exists()
    bm25_exists   = Path("./bm25_index/bm25okapi.pkl").exists()

    if chroma_exists and bm25_exists:
        print("📂 Índices encontrados — carregando...")
        return load_retrievers()
    else:
        print("🔨 Índices não encontrados — criando...")
        return create_retrievers(folder_path)

