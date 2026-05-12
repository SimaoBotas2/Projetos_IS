Library MCP Scaffold

Estrutura
- main.py: API REST com CRUD de livros
- mcp_server.py: servidor MCP com tools, resource e prompt
- langchain_agent.py: agente FastAPI que consome o servidor MCP
- webapp.html: interface web simples
- app/: camada partilhada entre REST e MCP

Preparacao
1. Ativar a virtual environment.
2. Instalar dependencias com `pip install -r requirements.txt`.
3. Criar `.env` com `GOOGLE_API_KEY=...` ou `GEMINI_API_KEY=...`.

Execucao
1. `python main.py`
2. `python mcp_server.py`
3. `python langchain_agent.py`
4. Abrir `webapp.html` no browser.

REST
- GET /
- GET /books
- GET /books/{id}
- POST /books
- PATCH /books/{id}
- DELETE /books/{id}

MCP
- Tools: list_books_tool, get_book_tool, create_book_tool, update_book_tool, delete_book_tool
- Resource: library://catalog-summary
- Prompt: library_assistant_prompt