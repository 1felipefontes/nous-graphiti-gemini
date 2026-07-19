# Caixa customizada do Nous — Graphiti MCP + Google Gemini
# (1) instala o pacote do Gemini (google-genai);
# (2) patcha graphiti_core em tempo de build p/ o reranker usar Gemini
#     (o mcp server fixa o reranker no OpenAI e nao da config).
# Verificado no deploy real de 19/07/2026.
FROM zepai/knowledge-graph-mcp:standalone

RUN /app/mcp/.venv/bin/python -m ensurepip --upgrade || true \
 && /app/mcp/.venv/bin/python -m pip install --no-cache-dir --upgrade \
      "graphiti-core[falkordb,google-genai]>=0.29.2"

COPY patch_reranker.py /tmp/patch_reranker.py
RUN /app/mcp/.venv/bin/python /tmp/patch_reranker.py
