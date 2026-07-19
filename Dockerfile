# Caixa customizada do Nous — Graphiti MCP + suporte a Google Gemini
# Parte da imagem oficial e:
#   (1) instala o pacote do Gemini (google-genai), que nao vem por padrao;
#   (2) forca o reranker a usar Gemini via sitecustomize (o mcp server desta
#       versao fixa o reranker no OpenAI e nao da opcao de config).
# Verificado no deploy real de 19/07/2026.
FROM zepai/knowledge-graph-mcp:standalone

RUN /app/mcp/.venv/bin/python -m ensurepip --upgrade || true \
 && /app/mcp/.venv/bin/python -m pip install --no-cache-dir --upgrade \
      "graphiti-core[falkordb,google-genai]>=0.29.2"

COPY sitecustomize.py /app/mcp/.venv/lib/python3.11/site-packages/sitecustomize.py
