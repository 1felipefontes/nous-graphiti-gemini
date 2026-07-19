# Nous: desliga a protecao anti-DNS-rebinding do FastMCP, que bloqueia acesso
# via dominio ("Invalid Host header" / 421). Bug conhecido do graphiti (issue
# #1205): o FastMCP nasce com host 127.0.0.1 -> protecao travada em localhost.
# Nosso endpoint ja esta protegido por Basic Auth + HTTPS no proxy, entao essa
# camada e redundante. Patch de BUILD, deterministico e verificavel.
import sys
import pathlib

p = pathlib.Path("/app/mcp/src/graphiti_mcp_server.py")
src = p.read_text(encoding="utf-8")

MARK = "# NOUS_HOST_PATCH"
if MARK in src:
    print("NOUS: host patch ja aplicado")
    sys.exit(0)

if "mcp = FastMCP(" not in src or "instructions=GRAPHITI_MCP_INSTRUCTIONS," not in src:
    sys.stderr.write(
        "NOUS HOST PATCH ERROR: ancoras nao encontradas em graphiti_mcp_server.py "
        "(versao mudou) -- ajustar patch_host.py.\n"
    )
    sys.exit(1)

helper = (
    "# NOUS_HOST_PATCH\n"
    "def _nous_transport_security():\n"
    "    try:\n"
    "        from mcp.server.fastmcp.server import TransportSecuritySettings\n"
    "    except Exception:\n"
    "        from mcp.server.transport_security import TransportSecuritySettings\n"
    "    return TransportSecuritySettings(enable_dns_rebinding_protection=False)\n\n\n"
)

# define o helper logo antes da construcao do FastMCP (que roda no import)
src = src.replace("mcp = FastMCP(", helper + "mcp = FastMCP(", 1)
# injeta o argumento transport_security na construcao
src = src.replace(
    "instructions=GRAPHITI_MCP_INSTRUCTIONS,",
    "instructions=GRAPHITI_MCP_INSTRUCTIONS,\n        transport_security=_nous_transport_security(),",
    1,
)

p.write_text(src, encoding="utf-8")
print("NOUS: DNS-rebinding/host patch OK")
