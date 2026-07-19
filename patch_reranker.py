# Nous: patcha graphiti_core/graphiti.py em tempo de BUILD para o reranker usar
# Gemini em vez do OpenAI default. Deterministico e verificavel: se o padrao nao
# existir (versao do graphiti-core mudou), o build FALHA aqui com mensagem clara.
import sys
import pathlib
import graphiti_core

gp = pathlib.Path(graphiti_core.__file__).parent / "graphiti.py"
src = gp.read_text(encoding="utf-8")

MARK = "# NOUS_GEMINI_RERANKER_PATCH"
if MARK in src:
    print("NOUS: graphiti.py ja estava patchado")
    sys.exit(0)

if "OpenAIRerankerClient()" not in src:
    sys.stderr.write(
        "NOUS PATCH ERROR: 'OpenAIRerankerClient()' nao encontrado em graphiti.py.\n"
        "A versao do graphiti-core mudou -- ajustar patch_reranker.py.\n"
    )
    sys.exit(1)

# troca as chamadas do reranker OpenAI pela nossa factory Gemini (a linha de
# import 'OpenAIRerankerClient' -- sem parenteses -- fica intacta, so nao e usada)
src = src.replace("OpenAIRerankerClient()", "_nous_gemini_reranker()")

# helper anexado ao fim do modulo (imports deferidos p/ evitar problema de ordem)
src += '''

# NOUS_GEMINI_RERANKER_PATCH
def _nous_gemini_reranker():
    import os
    from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
    try:
        from graphiti_core.llm_client.config import LLMConfig
    except Exception:
        from graphiti_core.llm_client import LLMConfig
    return GeminiRerankerClient(
        config=LLMConfig(
            api_key=os.environ.get("GOOGLE_API_KEY"),
            model=os.environ.get("RERANKER_MODEL", "gemini-3.5-flash"),
        )
    )
'''

gp.write_text(src, encoding="utf-8")
print("NOUS: graphiti.py reranker patchado para Gemini OK")
