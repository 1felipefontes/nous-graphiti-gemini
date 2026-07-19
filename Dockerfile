# Caixa customizada do Nous — Graphiti MCP + Google Gemini
# (1) instala o Gemini (google-genai);
# (2) patch reranker -> Gemini (mcp server fixa OpenAI);
# (3) patch host -> desliga anti-DNS-rebinding do FastMCP (bloqueia dominio;
#     issue getzep/graphiti #1205). Endpoint ja protegido por Basic Auth+HTTPS.
# Verificado no deploy real de 19/07/2026.
FROM zepai/knowledge-graph-mcp:standalone

RUN /app/mcp/.venv/bin/python -m ensurepip --upgrade || true \
 && /app/mcp/.venv/bin/python -m pip install --no-cache-dir --upgrade \
      "graphiti-core[falkordb,google-genai]>=0.29.2"

COPY patch_reranker.py /tmp/patch_reranker.py
COPY patch_host.py /tmp/patch_host.py
RUN /app/mcp/.venv/bin/python /tmp/patch_reranker.py \
 && /app/mcp/.venv/bin/python /tmp/patch_host.py
