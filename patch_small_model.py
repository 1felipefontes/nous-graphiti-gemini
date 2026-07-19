# Nous: patcha mcp_server/src/services/factories.py em tempo de BUILD para o
# branch do Gemini passar `small_model` ao GraphitiLLMConfig.
#
# POR QUE: o graphiti-core tem DOIS slots de LLM -- o principal e um "small"
# usado em tarefas baratas (dedup de nos, resumo de arestas). O branch gemini da
# factory nao preenche o small, entao ele cai no default hardcoded do
# graphiti_core (`DEFAULT_SMALL_MODEL = 'gemini-2.5-flash-lite'`), que o Google
# fechou para contas novas -> 404 -> o episodio morre na fila DEPOIS de o modelo
# principal ter respondido 200. A leitura segue funcionando (so usa embedding),
# o que faz a falha parecer inexistente.
#
# NAO da para resolver por YAML: o LLMConfig do mcp_server nao tem o campo, e o
# GraphitiConfig usa extra='ignore' -- escrever `small_model:` no config.yaml e
# descartado em silencio.
#
# O QUE FAZ: `small_model=config.model`, exatamente o que o upstream ja faz no
# branch do OpenAI (factories.py: "# Use the same model for both main and small
# model slots"). Se um dia quiser um modelo menor/mais barato no slot small,
# troque a linha injetada aqui.
#
# Deterministico e verificavel: se o padrao nao existir (versao mudou), o build
# FALHA aqui com mensagem clara -- mesma politica dos outros patches.
import sys
import pathlib
import re

MARK = "# NOUS_SMALL_MODEL_PATCH"

# O caminho canonico na imagem :standalone. Se mudar, procuramos abaixo de /app.
CANDIDATES = [
    pathlib.Path("/app/mcp/src/services/factories.py"),
    pathlib.Path("/app/mcp/services/factories.py"),
    pathlib.Path("/app/src/services/factories.py"),
]

target = next((p for p in CANDIDATES if p.exists()), None)
if target is None:
    found = sorted(pathlib.Path("/app").rglob("services/factories.py"))
    if len(found) == 1:
        target = found[0]
    elif len(found) > 1:
        sys.stderr.write(
            "NOUS PATCH ERROR: mais de um services/factories.py em /app:\n  "
            + "\n  ".join(str(p) for p in found)
            + "\nAjustar CANDIDATES em patch_small_model.py.\n"
        )
        sys.exit(1)

if target is None:
    sys.stderr.write(
        "NOUS PATCH ERROR: services/factories.py nao encontrado em /app.\n"
        "O layout da imagem mudou -- ajustar patch_small_model.py.\n"
    )
    sys.exit(1)

src = target.read_text(encoding="utf-8")

if MARK in src:
    print(f"NOUS: {target} ja estava patchado (small_model)")
    sys.exit(0)

# Ancora no branch do GEMINI. O arquivo tem varios blocos GraphitiLLMConfig(
# (openai, anthropic, gemini, groq) e so podemos tocar UM: achamos a construcao
# do GeminiClient e andamos para tras ate o GraphitiLLMConfig( mais proximo.
anchor = src.find("GeminiClient(config=llm_config)")
if anchor == -1:
    anchor = src.find("GeminiClient(")
if anchor == -1:
    sys.stderr.write(
        "NOUS PATCH ERROR: 'GeminiClient(' nao encontrado em factories.py.\n"
        "A estrutura da factory mudou -- ajustar patch_small_model.py.\n"
    )
    sys.exit(1)

start = src.rfind("GraphitiLLMConfig(", 0, anchor)
if start == -1:
    sys.stderr.write(
        "NOUS PATCH ERROR: nenhum 'GraphitiLLMConfig(' antes do GeminiClient.\n"
        "A estrutura da factory mudou -- ajustar patch_small_model.py.\n"
    )
    sys.exit(1)

block = src[start:anchor]

if "small_model" in block:
    print("NOUS: branch gemini ja passa small_model -- upstream corrigiu, nada a fazer")
    sys.exit(0)

# Injeta logo apos 'model=config.model,' preservando a indentacao encontrada.
m = re.search(r"([ \t]*)model=config\.model,\n", block)
if not m:
    sys.stderr.write(
        "NOUS PATCH ERROR: 'model=config.model,' nao encontrado no bloco gemini.\n"
        f"Bloco inspecionado:\n{block}\n"
        "Ajustar patch_small_model.py.\n"
    )
    sys.exit(1)

indent = m.group(1)
injection = f"{indent}small_model=config.model,  {MARK}\n"
new_block = block[: m.end()] + injection + block[m.end() :]

target.write_text(src[:start] + new_block + src[anchor:], encoding="utf-8")
print(f"NOUS: {target} -- small_model=config.model injetado no branch gemini OK")
