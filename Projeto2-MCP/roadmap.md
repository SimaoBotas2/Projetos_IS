# Roadmap de Conformidade com o Enunciado

## Objetivo

Este ficheiro resume o que falta no projeto para ficar alinhado com o enunciado do Trabalho 2 de Integracao de Sistemas.

Conclusao atual: o projeto esta apenas parcialmente conforme. A arquitetura base existe, mas faltam varios requisitos obrigatorios do enunciado.

## Requisitos Obrigatorios em Falta

### 1. Criar uma segunda entidade de dominio relacionada com `Book`

O enunciado exige pelo menos duas entidades relacionadas entre si.

Neste momento, o projeto so implementa `Book`.

Opcoes simples e validas:

- `Author`
- `Category`
- `Loan`
- `Publisher`

Opcao recomendada para minimizar alteracoes: `Author`.

### 2. Modelar explicitamente a relacao entre as duas entidades

Nao basta criar uma segunda tabela isolada. E necessario haver relacao entre as entidades.

Exemplo recomendado:

- `Author` com `id`, `name`, `country`
- `Book` com `author_id` como chave estrangeira

Idealmente, a relacao deve existir tambem ao nivel do modelo, nao apenas como campo solto na base de dados.

### 3. Expor CRUD REST para a nova entidade

Atualmente, a API REST so expõe livros.

E necessario adicionar endpoints para a segunda entidade, por exemplo:

- `GET /authors`
- `GET /authors/{id}`
- `POST /authors`
- `PATCH /authors/{id}`
- `DELETE /authors/{id}`

### 4. Expor CRUD MCP para a nova entidade

Atualmente, o servidor MCP so disponibiliza tools para `Book`.

E necessario adicionar tools equivalentes para a segunda entidade, por exemplo:

- `list_authors_tool`
- `get_author_tool`
- `create_author_tool`
- `update_author_tool`
- `delete_author_tool`

### 5. Manter a logica partilhada entre REST e MCP

Este ponto esta bem encaminhado com a camada `app/services.py`, mas a mesma abordagem deve ser mantida para a nova entidade.

Regra pratica:

- a logica de negocio fica em `app/services.py`
- REST e MCP apenas chamam essa logica

### 6. Criar pelo menos um segundo resource MCP

O enunciado pede pelo menos dois resources.

Neste momento so existe um resource:

- `library://catalog-summary`

E necessario acrescentar pelo menos mais um.

Exemplos simples:

- `library://authors-summary`
- `library://inventory-report`
- `library://books-by-author`
- `library://database-schema`

### 7. Manter pelo menos um prompt MCP

Este requisito ja esta cumprido, porque o projeto ja tem um prompt MCP.

Mesmo assim, convem rever o texto para garantir que esta coerente com o dominio final e com os novos resources.

### 8. Implementar um caso explicito que devolva erro

O enunciado distingue claramente um caso que retorna erro de um caso que levanta excecao.

Sugestoes validas:

- tentar apagar um autor que ainda tem livros associados devolve erro
- tentar criar um livro com um ano invalido devolve erro
- tentar consultar uma entidade inexistente devolve erro estruturado

O importante aqui e devolver um erro controlado e justificavel.

### 9. Implementar um caso explicito que levante excecao

Tambem e necessario ter pelo menos uma operacao ou parametro que provoque excecao real e que nao possa ser concluido.

Neste momento, no MCP, varios erros sao convertidos em dicionarios `{"error": ...}` em vez de serem propagados como excecao.

Exemplos validos:

- `raise ValueError("Year cannot be in the future")`
- `raise RuntimeError("Cannot delete author with associated books")`

Convem que este caso seja facil de demonstrar na apresentacao.

### 10. Criar duas operacoes semelhantes com pequenas variacoes de input/output

Este requisito ainda nao esta implementado.

As duas operacoes devem:

- fazer algo muito parecido
- variar ligeiramente nos parametros de entrada
- variar ligeiramente no resultado devolvido

Exemplos simples para biblioteca:

- `create_book_simple(title: str, author_id: int)`
- `create_book_detailed(title: str, author_id: int, year: int, available: bool)`

Ou:

- `search_books_by_year(year: int)`
- `search_books_by_year_range(start_year: int, end_year: int)`

Ou:

- `set_book_price_float(price: float)`
- `set_book_price_text(price: str)`

O mais simples sera provavelmente criar duas variacoes de criacao ou pesquisa.

### 11. Garantir que o agente LangChain arranca no ambiente real

No estado atual, o agente nao arranca sem `.env` com chave Gemini.

E necessario:

- criar um `.env` real
- definir `GOOGLE_API_KEY` ou `GEMINI_API_KEY`
- arrancar `langchain_agent.py` sem erro
- testar `POST /chat`

Sem isto, a demo final fica bloqueada.

### 12. Limpar a interface web para o dominio correto

A interface web existe e serve para a arquitetura pedida, mas ainda contem textos residuais de outro exemplo.

Devem ser substituidos por conteudo coerente com o dominio biblioteca.

Exemplos a corrigir:

- referencias a BMI
- referencias a health tips
- sugestoes de exemplo que nao pertencem ao dominio atual

## Mudancas Minimas Recomendadas

Se o objetivo for cumprir o enunciado com o menor numero de alteracoes possivel, a sequencia recomendada e:

1. Adicionar a entidade `Author`.
2. Relacionar `Book.author_id -> Author.id`.
3. Adicionar CRUD REST para `Author`.
4. Adicionar CRUD MCP para `Author`.
5. Adicionar um segundo resource MCP, por exemplo `library://authors-summary`.
6. Adicionar uma tool que devolve erro controlado.
7. Adicionar uma tool que faz `raise` de excecao.
8. Adicionar duas tools semelhantes com pequenas variacoes de assinatura/resultado.
9. Corrigir os textos da webapp para o dominio biblioteca.
10. Criar `.env` e testar o fluxo completo.

## Estado Final Esperado

Quando o projeto estiver corretamente alinhado com o enunciado, deve ser possivel demonstrar que:

1. A pagina web envia mensagens para o agente.
2. O agente usa tools MCP para gerir duas entidades relacionadas.
3. O MCP expoe pelo menos dois resources e pelo menos um prompt.
4. Existe CRUD via REST e MCP para as entidades do dominio.
5. Existe pelo menos um caso de erro e pelo menos um caso de excecao.
6. Existem duas operacoes semelhantes com pequenas diferencas de entrada e saida.
7. Todos os componentes arrancam localmente sem ajustes de ultima hora.

## Prioridade Recomendada

### Alta prioridade

- segunda entidade relacionada
- CRUD REST da nova entidade
- CRUD MCP da nova entidade
- segundo resource MCP
- caso de erro
- caso de excecao
- duas operacoes semelhantes

### Media prioridade

- atualizacao do prompt MCP para refletir o novo dominio completo
- limpeza da interface web

### Essencial para demonstracao

- `.env` valido
- agente LangChain funcional
- fluxo completo web -> agente -> MCP -> base de dados

## Nota Final

O projeto ja tem uma base util e funcional:

- API REST operacional para livros
- servidor MCP operacional para livros
- prompt MCP criado
- interface web existente
- agente LangChain implementado

O principal problema nao e falta de estrutura, mas sim falta de cobertura completa dos requisitos do enunciado.
