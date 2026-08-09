#!/usr/bin/env python3
"""
Regenera .claude-plugin/marketplace.json a partir dos manifestos reais de cada
plugin em plugins/<slug>/.claude-plugin/plugin.json.

O catalogo da raiz e derivado: quem manda e o plugin.json. Assim catalogo e
manifesto nao tem como divergir (versao bumpada num lugar e nao no outro e o
bug mais comum, e o sintoma nunca aponta para a causa).

Sem dependencias externas -- Python 3 padrao, como os outros scripts do repo.

Uso:
    python sincronizar_marketplace.py                # regenera o catalogo
    python sincronizar_marketplace.py --check        # so verifica, nao escreve
    python sincronizar_marketplace.py --raiz "C:\\...\\1Z Plugin"
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Campos que pertencem ao catalogo e nao ao manifesto: a sincronizacao preserva
# o que ja estiver escrito neles em vez de sobrescrever.
CAMPOS_SO_DO_CATALOGO = ("source", "category", "tags", "strict", "relevance")

# Campos copiados do plugin.json para a entrada do catalogo, nessa ordem.
CAMPOS_HERDADOS = (
    "displayName",
    "description",
    "version",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
)

# Diretorios/arquivos que fazem um plugin ter algum componente de verdade.
COMPONENTES = ("SKILL.md", "skills", "commands", "agents", "hooks", ".mcp.json")

SLUG_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Nomes reservados pela Anthropic: um marketplace com um desses para de carregar.
NOMES_RESERVADOS = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "claude-plugins-community", "claude-community", "anthropic-marketplace",
    "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
    "knowledge-work-plugins", "life-sciences", "claude-for-legal",
    "claude-for-financial-services", "financial-services-plugins",
    "first-party-plugins", "healthcare",
}


def achar_raiz(inicio: Path) -> Path:
    """Sobe a arvore ate achar o dono do .claude-plugin/marketplace.json.

    Procura o marketplace.json e nao so a pasta .claude-plugin/: cada plugin
    tem uma .claude-plugin/ propria, entao parar na primeira acharia a pasta
    do plugin em vez da raiz do repositorio.
    """
    for candidato in [inicio, *inicio.parents]:
        if (candidato / ".claude-plugin" / "marketplace.json").is_file():
            return candidato
    raise SystemExit(
        f"nao achei .claude-plugin/marketplace.json subindo a partir de {inicio}.\n"
        "Rode dentro do repositorio do marketplace ou passe --raiz."
    )


def ler_json(caminho: Path) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        raise SystemExit(
            f"{caminho} nao esta em UTF-8. Reescreva o arquivo em UTF-8 "
            "(acentos gravados em Latin-1 quebram o parser do Claude Code)."
        )
    except json.JSONDecodeError as e:
        raise SystemExit(f"{caminho} nao e JSON valido: {e}")


def validar_plugin(pasta: Path, manifesto: dict) -> list:
    """Devolve a lista de problemas que impedem o plugin de entrar no catalogo."""
    problemas = []
    nome = manifesto.get("name")

    if not nome:
        problemas.append("plugin.json sem campo 'name' (obrigatorio)")
    elif not SLUG_VALIDO.match(nome):
        problemas.append(f"nome '{nome}' nao e kebab-case (use minusculas e hifens)")
    elif nome != pasta.name:
        problemas.append(
            f"nome '{nome}' diferente da pasta '{pasta.name}' -- "
            "o Claude Code usa o nome para namespacing, mantenha os dois iguais"
        )

    if not manifesto.get("description"):
        problemas.append("sem 'description' (aparece no /plugin, vale preencher)")

    versao = manifesto.get("version")
    if not versao:
        problemas.append(
            "sem 'version' -- sem ela o plugin nao fica fixado e o controle "
            "de atualizacao passa a depender de outras fontes"
        )
    elif not re.match(r"^\d+\.\d+\.\d+", str(versao)):
        problemas.append(f"version '{versao}' nao parece semver (ex: 1.0.0)")

    if not any((pasta / c).exists() for c in COMPONENTES):
        problemas.append(
            "nenhum componente encontrado (SKILL.md, skills/, commands/, "
            "agents/, hooks/ ou .mcp.json) -- o plugin instalaria sem fazer nada"
        )

    skill_raiz = pasta / "SKILL.md"
    if skill_raiz.is_file() and not (pasta / "skills").is_dir():
        cabecalho = skill_raiz.read_text(encoding="utf-8", errors="replace")[:2000]
        if not re.search(r"^name:\s*\S", cabecalho, re.MULTILINE):
            problemas.append(
                "SKILL.md na raiz sem 'name:' no frontmatter -- o Claude Code cairia "
                "no nome do diretorio de instalacao, que muda a cada atualizacao"
            )

    for ref in pasta.rglob("*"):
        if ref.is_file() and ref.suffix in (".md", ".json") and "node_modules" not in ref.parts:
            texto = ref.read_text(encoding="utf-8", errors="replace")
            if re.search(r"[\"'(\s]\.\./", texto):
                problemas.append(
                    f"{ref.relative_to(pasta).as_posix()} referencia '../' -- "
                    "na instalacao o plugin e copiado isolado e esse caminho nao existe"
                )
                break

    return problemas


def coletar_plugins(raiz: Path) -> tuple:
    """Le todos os plugins de plugins/*/ e devolve (entradas, erros)."""
    dir_plugins = raiz / "plugins"
    if not dir_plugins.is_dir():
        raise SystemExit(f"nao achei {dir_plugins}")

    entradas, erros = [], []
    for pasta in sorted(p for p in dir_plugins.iterdir() if p.is_dir()):
        manifesto_path = pasta / ".claude-plugin" / "plugin.json"
        if not manifesto_path.is_file():
            erros.append((pasta.name, [f"falta {manifesto_path.relative_to(raiz).as_posix()}"]))
            continue

        manifesto = ler_json(manifesto_path)
        problemas = validar_plugin(pasta, manifesto)
        if problemas:
            erros.append((pasta.name, problemas))
            continue

        entrada = {"name": manifesto["name"], "source": f"./{pasta.name}"}
        for campo in CAMPOS_HERDADOS:
            if campo in manifesto:
                entrada[campo] = manifesto[campo]
        entradas.append(entrada)

    return entradas, erros


def mesclar(catalogo_antigo: dict, entradas: list) -> dict:
    """Aplica as entradas novas preservando o que so existe no catalogo."""
    antigas = {e.get("name"): e for e in catalogo_antigo.get("plugins", []) if isinstance(e, dict)}

    novas = []
    for entrada in entradas:
        anterior = antigas.get(entrada["name"], {})
        preservado = {c: anterior[c] for c in CAMPOS_SO_DO_CATALOGO if c in anterior}
        # 'source' customizado no catalogo vence o padrao ./<pasta>.
        entrada = {**entrada, **preservado}
        # 'name' e 'source' primeiro, para o arquivo ficar legivel.
        novas.append({
            "name": entrada.pop("name"),
            "source": entrada.pop("source"),
            **entrada,
        })

    novo = dict(catalogo_antigo)
    novo["plugins"] = novas
    return novo


def formatar(catalogo: dict) -> str:
    return json.dumps(catalogo, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raiz", type=Path, default=None, help="raiz do marketplace (padrao: detecta automaticamente)")
    parser.add_argument("--check", action="store_true", help="so verifica se o catalogo esta em dia; nao escreve")
    args = parser.parse_args()

    raiz = args.raiz.resolve() if args.raiz else achar_raiz(Path(__file__).resolve().parent)
    catalogo_path = raiz / ".claude-plugin" / "marketplace.json"

    if not catalogo_path.is_file():
        raise SystemExit(
            f"nao achei {catalogo_path}.\n"
            "Crie o catalogo com ao menos 'name', 'owner' e 'plugins': []."
        )

    catalogo_antigo = ler_json(catalogo_path)

    nome_mkt = catalogo_antigo.get("name")
    if not nome_mkt:
        raise SystemExit("marketplace.json sem 'name' (obrigatorio)")
    if nome_mkt in NOMES_RESERVADOS:
        raise SystemExit(
            f"'{nome_mkt}' e um nome reservado pela Anthropic; o marketplace nao carrega. "
            "Escolha outro nome."
        )
    if not SLUG_VALIDO.match(nome_mkt):
        raise SystemExit(f"nome do marketplace '{nome_mkt}' nao e kebab-case")
    if not isinstance(catalogo_antigo.get("owner"), dict) or not catalogo_antigo["owner"].get("name"):
        raise SystemExit("marketplace.json precisa de 'owner' com ao menos 'name'")

    entradas, erros = coletar_plugins(raiz)

    for nome, problemas in erros:
        print(f"[erro] {nome}:", file=sys.stderr)
        for p in problemas:
            print(f"        - {p}", file=sys.stderr)

    conteudo_novo = formatar(mesclar(catalogo_antigo, entradas))
    conteudo_atual = catalogo_path.read_text(encoding="utf-8")

    if args.check:
        if conteudo_novo != conteudo_atual:
            print(f"[check] {catalogo_path.name} esta desatualizado -- rode sem --check", file=sys.stderr)
            return 1
        if erros:
            return 1
        print(f"[check] ok: {len(entradas)} plugin(s) em dia")
        return 0

    if conteudo_novo != conteudo_atual:
        catalogo_path.write_text(conteudo_novo, encoding="utf-8")
        print(f"[ok] {catalogo_path.relative_to(raiz).as_posix()} atualizado")
    else:
        print(f"[ok] {catalogo_path.relative_to(raiz).as_posix()} ja estava em dia")

    for e in entradas:
        print(f"     - {e['name']} {e.get('version', '(sem versao)')}")

    if erros:
        print(f"\n{len(erros)} plugin(s) ficaram fora do catalogo (veja os erros acima).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
