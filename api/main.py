from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from .chain import (
    State,
    call_model,
    print_update,
    should_continue,
    summarize_history,
    summarize,
)

# uvicorn main:app --reload


app = FastAPI()
chain = None


@app.get("/")
async def root():
    print("hello from main.py")


@app.post("/summarize")
async def summarize_text(fich: UploadFile = File(...)):
    if fich.content_type != "text/plain":
        return {"error": "Only text files are suported"}
    content = await fich.read()
    texte = content.decode("utf-8")
    summary = summarize(texte)
    return {"summary": summary}


@app.post("/initialize")
async def initialize(fich: UploadFile = File(...)):
    global chain
    if fich.content_type != "text/plain":
        return {"error": "Only text files are suported"}
    content = await fich.read()
    texte = content.decode("utf-8")

    workflow = StateGraph(State)

    workflow.add_node(
        "conversation",
        lambda input: call_model(state=input, conversation_summary=summary),
    )

    workflow.add_node(summarize_history)

    workflow.add_edge(START, "conversation")

    workflow.add_conditional_edges(
        "conversation",
        should_continue,
    )

    workflow.add_edge("summarize_history", END)

    memory = MemorySaver()

    chain = workflow.compile(checkpointer=memory)

    summary = summarize(texte)

    return {"summarize": summary}


async def generate_stream(input_message, config, chain):
    for event in chain.stream(
        {"messages": [input_message]}, config, stream_mode="updates"
    ):
        yield event["conversation"]["messages"][0].content


@app.post("/update")
async def update(request: str = Form(...)):
    config = {"configurable": {"thread_id": "4"}}
    input_message = HumanMessage(content=request)
    return StreamingResponse(
        generate_stream(input_message, config, chain), media_type="text/plain"
    )
