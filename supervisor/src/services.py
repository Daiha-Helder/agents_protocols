import logging
import requests

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
from operator import add

from src.agents import classifique_intencao_do_usuario

logger = logging.getLogger(__name__)

class State(TypedDict):
    query: str
    responses: Annotated[list[str], add]

def request_agent(
        message: str,
        agent: str) -> str:

    url = f"http://{agent}:8000/send"
    payload = {"message": message}

    try:
        logger.info(
            f"Enviando requisição para {agent} em {url} com payload: {payload}"
        )

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        logger.info(f"Resposta recebida do {agent}: {data}")

        return data.get("resposta", "Resposta não encontrada.")

    except Exception as e:
        logger.exception(f"Erro ao enviar requisição para {agent}")

        return f"Erro ao consultar {agent}: {str(e)}"

def no_de_roteamento(state: State):

    query = state.get("query", "")
    classifications = classifique_intencao_do_usuario(query)

    return [
        Send(c["agent"], {"query": c["query"]})
        for c in classifications
    ]

def cartao_credito_node(state: State):
    query = state.get("query", "")
    logger.info("Executando agente CARTAO_CREDITO")

    resposta = request_agent(
        query,
        "cartao_credito_agent"
    )

    return {"responses": [resposta]}

# Minuto 10:55