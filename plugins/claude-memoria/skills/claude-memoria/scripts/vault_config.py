#!/usr/bin/env python3
"""
Resolucao do caminho do vault, compartilhada pelos scripts do skill.

O caminho do vault e de cada pessoa, nao do plugin. Deixar ele escrito no
SKILL.md fazia o plugin so funcionar na maquina de quem escreveu. Aqui ele vem,
nesta ordem de precedencia:

    1. --vault na linha de comando   (ganha de tudo; util para vault secundario)
    2. variavel de ambiente CLAUDE_MEMORIA_VAULT
    3. ~/.claude-memoria/config.json  (gravado uma vez por configurar_vault.py)
    4. config legada do nome anterior do plugin (ver LEGADO abaixo)

A deteccao dos vaults do Obsidian (obsidian.json) NAO entra nessa cadeia de
proposito: ela so sugere candidatos durante a configuracao. Escolher sozinho um
vault entre varios levaria a escrever notas no vault errado em silencio -- o
tipo de erro que so aparece semanas depois.

Sem dependencias externas: Python 3 padrao.
"""
import json
import os
from pathlib import Path

ENV_VAR = "CLAUDE_MEMORIA_VAULT"
CONFIG_DIR = Path.home() / ".claude-memoria"
CONFIG_FILE = CONFIG_DIR / "config.json"

# LEGADO: o plugin se chamava "cerebro-memoria" e gravava a config aqui. Quem
# configurou o vault antes do rename continua funcionando sem reconfigurar --
# em maquina que voce nao esta olhando, o sintoma seria um "vault nao
# configurado" que parece bug do plugin. Somente leitura: escrita sempre vai
# para o caminho novo, entao a legada morre sozinha no primeiro configurar_vault.
ENV_VAR_LEGADO = "CEREBRO_VAULT"
CONFIG_FILE_LEGADO = Path.home() / ".cerebro-memoria" / "config.json"


def saida_utf8():
    """Faz stdout/stderr aceitarem acentos em qualquer console.

    No Windows o console usa a codepage local (cp1252, cp850...) e imprimir um
    caminho ou trecho de nota com acento fora dela levanta UnicodeEncodeError --
    o script morre por causa do 'print', nao da tarefa. Chame no inicio de cada
    script que imprime conteudo do vault.
    """
    import sys

    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass  # Python < 3.7 ou fluxo substituido: segue com o padrao


def _expandir(caminho) -> Path:
    """Aceita ~, $VAR e %VAR% no caminho gravado ou vindo do ambiente."""
    return Path(os.path.expandvars(str(caminho))).expanduser()


def ler_config() -> dict:
    """Config do usuario. Arquivo ausente ou corrompido => dict vazio."""
    return _ler_json(CONFIG_FILE)


def escrever_config(dados: dict) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return CONFIG_FILE


def _ler_json(caminho: Path) -> dict:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return dados if isinstance(dados, dict) else {}


def resolver_vault(arg=None):
    """Devolve (Path|None, origem). origem: 'argumento', 'ambiente', 'config',
    'ambiente-legado', 'config-legada' ou 'nenhuma'."""
    if arg:
        return _expandir(arg), "argumento"

    do_ambiente = os.environ.get(ENV_VAR, "").strip()
    if do_ambiente:
        return _expandir(do_ambiente), "ambiente"

    do_config = str(ler_config().get("vault", "")).strip()
    if do_config:
        return _expandir(do_config), "config"

    # LEGADO por ultimo: so vale quando nao ha config nova nenhuma, entao nunca
    # sobrepoe uma escolha atual.
    legado_ambiente = os.environ.get(ENV_VAR_LEGADO, "").strip()
    if legado_ambiente:
        return _expandir(legado_ambiente), "ambiente-legado"

    legado_config = str(_ler_json(CONFIG_FILE_LEGADO).get("vault", "")).strip()
    if legado_config:
        return _expandir(legado_config), "config-legada"

    return None, "nenhuma"


MSG_SEM_VAULT = (
    "Vault do Claude Memoria nao configurado nesta maquina.\n"
    "Configure uma vez com:\n"
    "    python configurar_vault.py --detectar          # lista os vaults do Obsidian\n"
    '    python configurar_vault.py --vault "<caminho>"  # grava a escolha\n'
    f"A escolha fica em {CONFIG_FILE} e vale para todas as conversas.\n"
    f"Alternativa: definir a variavel de ambiente {ENV_VAR}."
)


def _msg_inexistente(vault: Path, origem: str) -> str:
    de_onde = {
        "argumento": "passado em --vault",
        "ambiente": f"vindo de {ENV_VAR}",
        "config": f"gravado em {CONFIG_FILE}",
        "ambiente-legado": f"vindo de {ENV_VAR_LEGADO}, do nome anterior do plugin",
        "config-legada": f"gravado em {CONFIG_FILE_LEGADO}, do nome anterior do plugin",
    }.get(origem, origem)
    return (
        f"Vault nao encontrado em {vault} ({de_onde}).\n"
        "Corrija com: python configurar_vault.py --vault \"<caminho>\"\n"
        "Ou crie a pasta com: python inicializar_vault.py --vault \"<caminho>\""
    )


def exigir_vault(arg=None, formato="texto", exigir_existente=True) -> Path:
    """Resolve o vault ou encerra com uma mensagem que diz como configurar.

    formato='json' para scripts cuja saida e consumida como JSON -- um erro em
    texto puro no meio de um pipeline JSON vira 'falha de parse' e esconde a
    causa real, que e so falta de configuracao.
    """
    import sys

    vault, origem = resolver_vault(arg)

    erro = None
    if vault is None:
        erro = MSG_SEM_VAULT
    elif exigir_existente and not vault.exists():
        erro = _msg_inexistente(vault, origem)

    if erro:
        if formato == "json":
            print(json.dumps({"erro": erro}, ensure_ascii=False, indent=2))
        else:
            print(erro, file=sys.stderr)
        sys.exit(1)

    return vault


def caminhos_obsidian_json() -> list:
    """Onde o Obsidian guarda a lista de vaults, por plataforma."""
    home = Path.home()
    candidatos = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidatos.append(Path(appdata) / "obsidian" / "obsidian.json")
    candidatos += [
        home / "AppData" / "Roaming" / "obsidian" / "obsidian.json",
        home / "Library" / "Application Support" / "obsidian" / "obsidian.json",
        home / ".config" / "obsidian" / "obsidian.json",
        # instalacao via Flatpak
        home / ".var" / "app" / "md.obsidian.Obsidian" / "config" / "obsidian" / "obsidian.json",
    ]
    vistos, unicos = set(), []
    for c in candidatos:
        chave = str(c).lower()
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(c)
    return unicos


def detectar_vaults() -> list:
    """Vaults registrados no Obsidian local, mais recentes primeiro.

    Lista vazia nao significa 'nao tem vault' -- pode ser Obsidian nao
    instalado, ou vault que nunca foi aberto nesta maquina.
    """
    encontrados = {}
    for caminho in caminhos_obsidian_json():
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        vaults = dados.get("vaults")
        if not isinstance(vaults, dict):
            continue
        for info in vaults.values():
            if not isinstance(info, dict) or not info.get("path"):
                continue
            p = _expandir(info["path"])
            encontrados[str(p).lower()] = {
                "path": str(p),
                "nome": p.name,
                "existe": p.exists(),
                "aberto": bool(info.get("open")),
                "ts": info.get("ts", 0) or 0,
            }
    return sorted(encontrados.values(), key=lambda v: v["ts"], reverse=True)
