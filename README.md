# nous-graphiti-gemini

Imagem Docker customizada do **Graphiti MCP server** com suporte a **Google Gemini**.

Parte da imagem oficial `zepai/knowledge-graph-mcp:standalone` e adiciona o pacote
`google-genai`, que nao vem instalado por padrao. Usada como motor da camada de
**Memoria** do projeto **Nous** (Graphaenus), rodando no EasyPanel/Hetzner.

Sem segredos aqui: chaves e senhas vivem so no EasyPanel (variaveis de ambiente).

Deploy: EasyPanel App -> Source: este repo -> Build: Dockerfile.
Runbook completo: repo interno graphaenus-maestro, `tech/sectors/core/hetzner/nous-graphiti.md`.
