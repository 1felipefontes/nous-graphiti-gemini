# Nous: forca o cross-encoder (reranker) do Graphiti a usar Gemini.
#
# Esta versao do mcp server cria Graphiti() SEM passar um cross_encoder, entao
# graphiti_core cai no OpenAIRerankerClient() default -> exige OPENAI_API_KEY e
# quebra o startup. Aqui trocamos esse default por GeminiRerankerClient, que le
# a GOOGLE_API_KEY do ambiente. Carregado automaticamente pelo Python no arranque
# (sitecustomize esta no sys.path via site-packages).
import os


def _install_gemini_reranker():
    try:
        from graphiti_core.cross_encoder import openai_reranker_client as _orc
        from graphiti_core.cross_encoder.gemini_reranker_client import (
            GeminiRerankerClient,
        )
    except Exception:
        return  # graphiti_core indisponivel (ex.: durante o build) -> no-op

    api_key = os.environ.get("GOOGLE_API_KEY")
    model = os.environ.get("RERANKER_MODEL", "gemini-3.5-flash")

    def _factory(*args, **kwargs):
        try:
            from graphiti_core.llm_client.config import LLMConfig
            return GeminiRerankerClient(config=LLMConfig(api_key=api_key, model=model))
        except Exception:
            # fallback: GeminiRerankerClient() le GOOGLE_API_KEY do ambiente sozinho
            return GeminiRerankerClient()

    # substitui a classe no modulo; graphiti.py faz `from _orc import
    # OpenAIRerankerClient` no import (que roda depois deste sitecustomize),
    # entao passa a pegar a nossa factory Gemini.
    _orc.OpenAIRerankerClient = _factory
    try:
        import graphiti_core.cross_encoder as _cc_pkg
        if hasattr(_cc_pkg, "OpenAIRerankerClient"):
            _cc_pkg.OpenAIRerankerClient = _factory
    except Exception:
        pass


_install_gemini_reranker()
