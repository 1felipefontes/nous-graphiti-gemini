# Caixa customizada do Nous — Graphiti MCP + suporte a Google Gemini
# Parte da imagem oficial e adiciona o pacote do Gemini (google-genai),
# que nao vem instalado por padrao no zepai/knowledge-graph-mcp:standalone.
# Extra verificado em 19/07/2026 (mcp_server/pyproject.toml -> optional-deps "providers").
FROM zepai/knowledge-graph-mcp:standalone

RUN /app/mcp/.venv/bin/python -m ensurepip --upgrade || true \
 && /app/mcp/.venv/bin/python -m pip install --no-cache-dir --upgrade \
      "graphiti-core[falkordb,google-genai]>=0.29.2"
