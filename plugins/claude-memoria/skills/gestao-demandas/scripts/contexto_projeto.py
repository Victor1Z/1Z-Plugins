#!/usr/bin/env python3
"""
Carrega de uma vez o contexto de um projeto: projeto.md, demandas dele e notas do
vault que apontam para ele.

E a Etapa 3 do fluxo de analise em uma chamada, em vez de cinco buscas soltas.
Analisar sem ler o que ja foi documentado produz spec que contradiz decisao ja
tomada -- esse script existe para tirar a desculpa de pular esse passo.

Reaproveita o parser de frontmatter de buscar_notas.py (skill irma) em vez de
duplicar: duas implementacoes divergem na primeira vez que uma delas ganha um
caso novo.

Uso:
    python contexto_projeto.py --projeto "Hub de Credito"
    python contexto_projeto.py --atd ATD-282471
    python contexto_projeto.py --projeto "Hub de Credito" --sem-conteudo
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
IRMA_SCRIPTS = SKILL_DIR.parent / "claude-memoria" / "scripts"
sys.path.insert(0, str(IRMA_SCRIPTS))

try:
    from buscar_notas import parse_frontmatter, primeira_linha_util  # noqa: E402
    from vault_config import exigir_vault, saida_utf8  # noqa: E402
except ImportError:
    print(json.dumps({
        "erro": "Nao encontrei os modulos da skill irma em " + str(IRMA_SCRIPTS),
        "sugestao": "A skill gestao-demandas depende da skill claude-memoria no "
                    "mesmo plugin. Reinstale o plugin completo.",
    }, ensure_ascii=False, indent=2))
    sys.exit(1)

PROJETOS = "01 - Projetos"
PASTAS_IGNORADAS = {"_config", ".obsidian", ".trash"}
ATD_RE = re.compile(r"^ATD-\d{6}$")


def _sair(payload: dict, codigo: int = 0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(codigo)


def titulo_da_nota(corpo: str, padrao: str = "") -> str:
    """Texto do H1, sem o 'ATD-000000 — ' na frente.

    O indice de demandas precisa mostrar do que cada uma trata; a primeira linha
    util do corpo e sempre o link do projeto, que e igual em todas.
    """
    for linha in corpo.splitlines():
        if linha.startswith("# "):
            titulo = linha[2:].strip()
            return titulo.split("—", 1)[-1].strip() if "—" in titulo else titulo
    return padrao


def notas_do_vault(vault: Path):
    for path in vault.rglob("*.md"):
        rel = path.relative_to(vault)
        if PASTAS_IGNORADAS & set(rel.parts):
            continue
        try:
            yield rel, path.read_text(encoding="utf-8")
        except OSError:
            continue


def achar_por_atd(vault: Path, atd: str):
    """Devolve (nome_do_projeto|None, caminho_relativo_da_demanda|None)."""
    raiz = vault / PROJETOS
    if raiz.is_dir():
        for demanda in raiz.glob(f"*/demandas/{atd}.md"):
            return demanda.parent.parent.name, demanda.relative_to(vault)
    # fallback: demanda fora do lugar esperado, ou projeto declarado no frontmatter
    for rel, texto in notas_do_vault(vault):
        if rel.stem.upper() == atd:
            fm, _ = parse_frontmatter(texto)
            return (str(fm.get("projeto", "")) or None), rel
    return None, None


def resolver_pasta(vault: Path, nome: str):
    """Nome sempre vindo do disco, nunca do que foi pedido.

    Importa aqui porque as notas relacionadas sao achadas por substring '[[Nome]]'
    no texto -- e comparacao de string em Python e case-sensitive mesmo quando o
    filesystem nao e. Pedir "hub de credito" acharia a pasta no Windows e depois
    nao acharia nenhuma nota linkando '[[Hub de Credito]]'.
    """
    raiz = vault / PROJETOS
    if not raiz.is_dir():
        return None, []
    pastas = sorted(p.name for p in raiz.iterdir() if p.is_dir())
    for p in pastas:
        if p == nome:
            return raiz / p, []
    for p in pastas:
        if p.lower() == nome.lower():
            return raiz / p, []
    return None, pastas + sorted(p.stem for p in raiz.glob("*.md"))


def main():
    saida_utf8()
    ap = argparse.ArgumentParser(description="Carrega o contexto de um projeto do vault")
    ap.add_argument("--projeto", default="", help="nome do projeto")
    ap.add_argument("--atd", default="", help="descobre o projeto a partir da demanda")
    ap.add_argument("--sem-conteudo", action="store_true", dest="sem_conteudo",
                    help="omite o corpo das notas; devolve so o indice")
    ap.add_argument("--limit", type=int, default=30, help="maximo de notas relacionadas")
    ap.add_argument("--vault", default="")
    args = ap.parse_args()

    if not args.projeto and not args.atd:
        _sair({"erro": "Informe --projeto ou --atd."}, 1)

    vault = exigir_vault(args.vault, formato="json")

    demanda_rel = None
    nome = args.projeto.strip()

    if args.atd:
        atd = args.atd.strip().upper().replace(" ", "")
        if not ATD_RE.match(atd):
            _sair({"erro": f"'{args.atd}' nao esta no formato ATD-000000."}, 1)
        achado, demanda_rel = achar_por_atd(vault, atd)
        if not nome:
            nome = achado or ""
        if not nome:
            _sair({
                "erro": f"{atd} nao encontrada no vault e nenhum projeto informado.",
                "sugestao": "Passe --projeto, ou crie a demanda com nova_demanda.py.",
            }, 1)

    pasta, candidatos = resolver_pasta(vault, nome)
    if pasta is None:
        _sair({
            "erro": f"Projeto '{nome}' nao encontrado em {PROJETOS}/.",
            "projetos_existentes": candidatos,
        }, 1)

    nome = pasta.name
    saida = {"projeto": nome, "pasta": str(pasta.relative_to(vault))}

    nota_projeto = pasta / "projeto.md"
    if nota_projeto.is_file():
        texto = nota_projeto.read_text(encoding="utf-8")
        fm, corpo = parse_frontmatter(texto)
        saida["projeto_md"] = {
            "caminho": str(nota_projeto.relative_to(vault)),
            "status": fm.get("status", ""),
            "conteudo": None if args.sem_conteudo else corpo.strip(),
        }
    else:
        saida["projeto_md"] = None
        saida["aviso"] = ("Projeto sem projeto.md — o contexto permanente do sistema "
                          "nao esta documentado.")

    demandas = []
    for path in sorted((pasta / "demandas").glob("*.md")) if (pasta / "demandas").is_dir() else []:
        fm, corpo = parse_frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(vault)
        item = {
            "atd": fm.get("atd") or path.stem,
            "titulo": titulo_da_nota(corpo, path.stem),
            "caminho": str(rel),
            "tipo_demanda": fm.get("tipo_demanda", ""),
            "status": fm.get("status", ""),
            "data": fm.get("data_atualizacao") or fm.get("data_criacao", ""),
        }
        if demanda_rel and rel == demanda_rel:
            item["conteudo"] = None if args.sem_conteudo else corpo.strip()
            item["e_a_demanda_pedida"] = True
        demandas.append(item)
    saida["demandas"] = demandas

    if demanda_rel and not any(d.get("e_a_demanda_pedida") for d in demandas):
        # demanda existe, mas fora de 01 - Projetos/<Projeto>/demandas/
        fm, corpo = parse_frontmatter((vault / demanda_rel).read_text(encoding="utf-8"))
        saida["demanda_fora_do_lugar"] = {
            "caminho": str(demanda_rel),
            "conteudo": None if args.sem_conteudo else corpo.strip(),
            "sugestao": f"Esperado em {PROJETOS}/{nome}/demandas/.",
        }

    # notas que citam o projeto ou uma de suas demandas, fora da pasta do projeto
    alvos = [f"[[{nome}]]", nome] + [f"[[{d['atd']}]]" for d in demandas]
    prefixo = str(pasta.relative_to(vault)).replace("\\", "/")
    relacionadas = []
    for rel, texto in notas_do_vault(vault):
        if str(rel).replace("\\", "/").startswith(prefixo):
            continue
        if not any(a in texto for a in alvos):
            continue
        fm, corpo = parse_frontmatter(texto)
        relacionadas.append({
            "caminho": str(rel),
            "tipo": fm.get("tipo", ""),
            "trecho": primeira_linha_util(corpo, 200),
        })
    saida["total_relacionadas"] = len(relacionadas)
    saida["relacionadas"] = sorted(relacionadas, key=lambda n: n["caminho"])[:args.limit]

    _sair(saida)


if __name__ == "__main__":
    main()
