# nous-graphiti-gemini

Imagem Docker customizada do **Graphiti MCP server** com suporte a **Google Gemini**.

Parte da imagem oficial `zepai/knowledge-graph-mcp:standalone` e adiciona o pacote
`google-genai`, que nao vem instalado por padrao. Usada como motor da camada de
**Memoria** do projeto **Nous** (Graphaenus), rodando no EasyPanel/Hetzner.

Sem segredos aqui: chaves e senhas vivem so no EasyPanel (variaveis de ambiente).

Deploy: EasyPanel App -> Source: este repo -> Build: Dockerfile.
Runbook completo: repo interno graphaenus-maestro, `tech/sectors/core/hetzner/nous-graphiti.md`.

## Os 4 patches

Todos sao de **build**, deterministicos, e **falham ruidosamente**: se o upstream
mudar e o padrao esperado sumir, o build quebra com mensagem clara em vez de gerar
uma imagem silenciosamente errada.

| # | Arquivo | Corrige |
|---|---|---|
| 1 | (no `Dockerfile`) | instala `google-genai` -- nao vem na imagem oficial |
| 2 | `patch_reranker.py` | reranker fixado em OpenAI, sem opcao de config -> Gemini |
| 3 | `patch_host.py` | anti-DNS-rebinding do FastMCP barra acesso por dominio (getzep/graphiti#1205) |
| 4 | `patch_small_model.py` | branch gemini nao preenche o slot do "modelo pequeno" -> cai no default `gemini-2.5-flash-lite`, fechado pelo Google (404) |

## O padrao de falha que se repetiu 3 vezes

Os patches 2 e 4, mais o gotcha do embedder, sao **a mesma armadilha**: um default
da biblioteca apontando para um modelo ou provider que nao serve -- e que **nao
aparece em lugar nenhum do `config.yaml`**. Ler a configuracao nao revela o
problema; so o log revela.

| Quando | Sintoma | Causa |
|---|---|---|
| Deploy inicial | tudo 404 (leitura e escrita) | `text-embedding-004`, desligado pelo Google em 14/01/2026 -> usar `gemini-embedding-001` |
| Busca | reranking chamava OpenAI | default do mcp_server ignora o provider configurado |
| 19/07/2026 | `add_memory` responde "queued" e o episodio **some**; leitura normal | `small_model` nao preenchido -> default `gemini-2.5-flash-lite` (404) |

O terceiro foi o mais traicoeiro: o modelo principal responde **200**, a leitura
funciona (so usa embedding), e a falha so aparece no log do worker da fila.

**Regra pratica:** depois de qualquer deploy, conferir no log **quais modelos
foram de fato chamados** -- e nao so o que esta escrito no `config.yaml`.

```
grep -E "generateContent|EmbedContents|ERROR" <logs>
```

Todos devem ser modelos que voce escolheu. Qualquer nome que voce nao reconhecer
e um default vazando.

## Upstream

O patch 4 e um bug do upstream que atinge **anthropic, gemini e groq** -- so o
branch `openai` de `mcp_server/src/services/factories.py` faz
`small_model = config.model`. Bom candidato a PR.

Nao da para corrigir por YAML: `LLMConfig` do mcp_server nao tem o campo
`small_model`, e `GraphitiConfig` usa `extra='ignore'` -- a chave seria
**descartada em silencio**.
