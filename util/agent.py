import os
from util.use_retriever import load_retrievers

from langchain.messages import HumanMessage,SystemMessage
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.pretty import pprint

console = Console()

model_name = "BAAI/bge-reranker-base"
model_kwargs = {'device': 'cpu'} 
hf = HuggingFaceCrossEncoder( model_name=model_name, model_kwargs=model_kwargs )

chromadb, bm25 = load_retrievers()
llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0
)


@tool
def retrieve_context(messages: str) -> str:
    """Retrieve information to help answer a query."""
    retrieved_chroma = chromadb.invoke(messages)
    retrieved_bm25 = bm25.invoke(messages)
    serialized_chroma = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_chroma
    )
    serialized_bm25 = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_bm25
    )

    context = serialized_bm25 + '\n' + serialized_chroma

    return context

@tool 
def recreate_query(messages: str,context: str) -> str:
    """ Create a fictional document beased in original query and retrieved"""
    agent = create_agent(
                model=llm,
                system_prompt=SystemMessage("Create a fictional document beased in original query and retrieved, to improve retriever in BM25 and Chroma Vectorstores. The fictional document must response the original query.")
            )
    result= agent.invoke({'messages':HumanMessage([f'{messages},{context}'])})
    content = result.content

    return content 



@tool
def final_retriver(content: str) -> str:
    """ Use the fictional document to improve the retrieve aswer to correct the original query"""

    retrieved_chroma = chromadb.invoke(content)
    retrieved_bm25 = bm25.invoke(content)
    serialized_chroma = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_chroma
    )
    serialized_bm25 = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_bm25
    )
    final_context= serialized_bm25 + '\n' + serialized_chroma
    return final_context  






agent = create_agent(
                model=llm,
                system_prompt=SystemMessage([
                """
                Você é um especialista em legislação farmâceuticas, que ajuda farmacêuticos a tirarem duvidas sobre a legislação farmaceutica.
                Utilize s ferramentas de retrieves para conseguir as respostas baseadas nas documentaçõe fornecidas.
                A sua resposta final deve ser baseadas no contexto fornecido no retreiver.
                Não responda o que você não acahar respostas.

                Pense um resposta final  que responda a pergunta inicial do farmaceutico. 

                Sempre a pergunta for sobre um prática sempre comece a resposta como o seguinte:

                "Baseado na legislação X....."

                Se for sobre uma lei, portaria ou regulamentação comece com:
                "Esta X, define e abordar os seguintes temas ...."

                A resposta não deve conter mais de 200 palavras. 



                                             """]),
                tools=[retrieve_context,recreate_query,final_retriver])

if __name__=='__main__':
    resposta= agent.invoke({'messages':HumanMessage('Eu posso vender um antibiótico com um receita de 20 dias?')})
    pprint(resposta)

    print('*************************************************************************************************')
    
    conteudo = resposta['messages'][-1].content
    
    console.print(Panel(
        Markdown(conteudo),
        title="[bold green]Assistente Farmacêutico[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
        
    
