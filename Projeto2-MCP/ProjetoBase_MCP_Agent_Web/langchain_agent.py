import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# LangChain & LangGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent          
from langgraph.checkpoint.memory import InMemorySaver

# MCP Adapters
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from contextlib import asynccontextmanager


import traceback

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Define GOOGLE_API_KEY ou GEMINI_API_KEY no ficheiro .env")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=GOOGLE_API_KEY)

# ── MEMORY (persists across requests for the same thread_id) ──────────────────
memory = InMemorySaver()


class ChatRequest(BaseModel):
    message: str


def extract_text(content) -> str:
    """Safely extract a plain string from an AI message's content field.
    content can be:
      - a plain string  →  return as-is
      - a list of dicts →  join the text blocks
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
        ]
        return " ".join(parts)
    return str(content)


def build_user_error_message(error: Exception) -> str:
    message = str(error).strip() or error.__class__.__name__
    normalized = message.upper()

    if "RESOURCE_EXHAUSTED" in normalized or "429" in normalized or "QUOTA" in normalized:
        return (
            "A quota da API Gemini foi esgotada. "
            "Tenta novamente mais tarde ou usa uma chave com quota disponível."
        )

    service_error_terms = (
        "CONNECTION REFUSED",
        "ALL CONNECTION ATTEMPTS FAILED",
        "FAILED TO CONNECT",
        "SERVICE UNAVAILABLE",
        "SESSION IS CLOSED",
        "TIMEOUT",
        "CONNECTERROR",
        "UNAVAILABLE",
        "INDISPONÍVEL",
    )
    if any(term in normalized for term in service_error_terms):
        return (
            "O serviço da biblioteca está indisponível neste momento. "
            "Verifica se o MCP Server e os restantes serviços estão ativos e tenta novamente."
        )

    return f"Ocorreu um erro ao processar o pedido. Detalhe: {message}"


@asynccontextmanager
async def lifespan(application: FastAPI):
    url = "http://127.0.0.1:8002/sse"
    application.state.agent = None
    application.state.thread_config = None
    application.state.startup_error = None

    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                prompt_data = await session.get_prompt(
                    "library_assistant_prompt", arguments={"user_name": "Visitante"}
                )
                system_instruction = prompt_data.messages[0].content.text

                resource_data = await session.read_resource("library://catalog-summary")
                resource_text = resource_data.contents[0].text
                print(f"\nRESOURCE LIDO [library://catalog-summary]:\n{resource_text}")
                system_instruction += f"\n\nServer context:\n{resource_text}"

                tools = await load_mcp_tools(session)
                print("\n=== TOOLS CARREGADAS ===", tools)

                application.state.agent = create_agent(
                    model=llm,
                    tools=tools,
                    system_prompt=system_instruction,
                    checkpointer=memory,
                )
                application.state.thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
                print("Agente da biblioteca inicializado com sucesso.")

                yield
    except Exception as e:
        traceback.print_exc()
        application.state.startup_error = (
            "Ligação ao serviço MCP indisponível. "
            f"Detalhe: {str(e).strip() or e.__class__.__name__}"
        )
        print(application.state.startup_error)
        yield

    print("A encerrar o servidor.")

app = FastAPI(title="Library Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(req: ChatRequest):
    agent = getattr(app.state, "agent", None)
    thread_config = getattr(app.state, "thread_config", None)

    if agent is None or thread_config is None:
        startup_error = getattr(app.state, "startup_error", None)
        if startup_error:
            return {"reply": build_user_error_message(RuntimeError(startup_error))}
        raise HTTPException(status_code=503, detail="Agente ainda não inicializado.")
    try:
        inputs = {"messages": [HumanMessage(content=req.message)]}
        final_response = ""

        async for event in agent.astream(
            inputs, config=thread_config, stream_mode="values"
        ):
            msg = event["messages"][-1]

            if msg.type == "ai" and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"\nTOOL CALL: {tool_call['name']}")
                    print(f"   Args: {tool_call['args']}")
            elif msg.type == "tool":
                print(f"\nTOOL RESULT [{msg.name}]: {msg.content}")
            elif msg.type == "ai" and msg.content:
                final_response = extract_text(msg.content)
                print(f"\nAI RESPONSE: {final_response}")

        return {"reply": final_response}

    except ChatGoogleGenerativeAIError as e:
        traceback.print_exc()
        return {"reply": build_user_error_message(e)}

    except Exception as e:
        traceback.print_exc()
        message = build_user_error_message(e)
        if "quota" in message.lower() or "indisponível" in message.lower():
            return {"reply": message}
        raise HTTPException(status_code=500, detail=message) from e


@app.post("/reset")
async def reset():
    """Generate a new thread_id — effectively clears conversation history."""
    app.state.thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    return {"status": "Histórico limpo com sucesso"}


@app.get("/health")
async def health():
    startup_error = getattr(app.state, "startup_error", None)
    return {
        "status": "ok" if startup_error is None else "degraded",
        "agent_ready": startup_error is None,
        "detail": startup_error,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)