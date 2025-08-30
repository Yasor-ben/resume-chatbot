import os
from typing import Literal

from prompts import SUMMARIZE_PROMPT, SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import MessagesState, END

# pour du streaming
from langchain_core.output_parsers import StrOutputParser

# pour localiser le fichier .env
from dotenv import load_dotenv

load_dotenv()


class State(MessagesState):
    history: str


def summarize(conversation: str) -> str:

    prompt_template = SUMMARIZE_PROMPT
    prompt = PromptTemplate(template=prompt_template, input_variables=["text_complet"])

    llm = ChatOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        model=os.environ["MODEL_ID"],
        temperature=0.2,
    )
    chain = prompt | llm | StrOutputParser()

    return chain.invoke(conversation)


def call_model(state: State, conversation_summary: str) -> dict:

    llm = ChatOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        model=os.environ["MODEL_ID"],
        temperature=0.2,
    )
    history = state.get("history", "")
    if history:
        system_message = f"summary of conversation earlier : {history}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        system_message = SYSTEM_PROMPT.format(conversation=conversation_summary)
        messages = [SystemMessage(content=system_message)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def summarize_history(state: State) -> dict:

    llm = ChatOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        model=os.environ["MODEL_ID"],
        temperature=0.2,
    )
    history = state.get("history", "")
    if history:
        history_message = f"summary of conversation earlier : {history}"
    else:
        history_message = f"No conversation history aviable"

    message = [state(message)] + [HumanMessage(content=history_message)]
    response = summarize.invoke(message)
    delete_message = [RemoveMessage(id=m.id) for m in state["message"][:-2]]
    return {"history": response.content, "messages": delete_message}


def print_update(update: dict) -> None:
    for k, v in update.items():
        for m in v["messages"]:
            m.pretty_print()
        if "history" in v:
            print(v["history"])


def should_continue(state: State) -> Literal["summarize_history", END]:
    message = state["messages"]
    if len(message) > 6:
        return "summarize_history"
    return END


# https://github.com/Yasor-ben/resume-chatbot.git
# git remote add origin https://github.com/ton_user/mon-projet.git
# git branch -M main            # renomme la branche locale en main (si ce n’est pas déjà fait)
# git push -u origin main       # envoie le code vers GitHub

# 183972828+Yasor-ben@users.noreply.github.com
# git config --global user.email "183972828+Yasor-ben@users.noreply.github.com"
# git config --global user.name  "yasor-ben"
# git commit --amend --reset-author --no-edit
# git push --force-with-lease origin main
# git commit --amend --reset-author --no-edit
