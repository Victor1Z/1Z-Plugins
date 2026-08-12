#!/usr/bin/env python3
"""
Cria a nota de uma demanda a partir de references/demanda.template.md e liga as
duas pontas (demanda -> projeto e projeto -> demanda).

Valida o que costuma sair errado quando isso e feito a mao:

  - formato do ATD (ATD-000000, seis digitos) -- nome de arquivo errado quebra a
    rastreabilidade com o Agidesk e ninguem percebe na hora;
  - projeto inexistente -- criar projeto por conveniencia gera nota orfa que
    duplica um sistema ja documentado com outro nome;
  - demanda duplicada -- nunca sobrescreve; devolve o caminho existente.

O vault vem da mesma config do skill claude-memoria (~/.claude-memoria/
config.json) ou de --vault. Saida sempre em JSON.

Uso:
    python nova_demanda.py --atd ATD-282471 --projeto "Hub de Credito"
    python nova_demanda.py --atd ATD-282471 --projeto "Hub de Credito" \\
        --titulo "Consulta de propostas" --tipo Melhoria --solicitante "Fulano"
    python nova_demanda.py --atd ATD-282471 --projeto "Novo Sistema" --criar-projeto
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
# vault_config.py mora na skill irma, dentro do mesmo plugin. O plugin e copiado
# inteiro na instalacao, entao esse caminho existe no destino.
IRMA_SCRIPTS = SKILL_DIR.parent / "claude-memoria" / "scripts"
sys.path.insert(0, str(IRMA_SCRIPTS))

try:
    from vault_config import exigir_vault, saida_utf8  # noqa: E402
except ImportError:
    print(json.dumps({
        "erro": "Nao encontrei vault_config.py em " + str(IRMA_SCRIPTS),
        "sugestao": "A skill gestao-demandas depende da skill irma claude-memoria "
                    "no mesmo plugin. Reinstale o plugin completo.",
    }, ensure_ascii=False, indent=2))
    sys.exit(1)

TEMPLATE = SKILL_DIR / "references" / "demanda.template.md"
PROJETOS = "01 - Projetos"
ATD_RE = re.compile(r"^ATD-\d{6}$")
TIPOS = ("Melhoria", "Projeto", "Sustentação")
SECAO_DEMANDAS = "## Demandas"


def _sair(payload: dict, codigo: int = 0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(codigo)


def normalizar_atd(bruto: str):
    """Aceita variacao de caixa e espaco; recusa qualquer outro formato.

    Nao 'consertamos' 282471 ou ATD-2824 de proposito: o numero e o identificador
    da demanda, e adivinhar um digito faltando cria um vinculo errado que parece
    certo. Quem pede confirma o numero.
    """
    limpo = (bruto or "").strip().upper().replace(" ", "")
    return limpo if ATD_RE.match(limpo) else None


def listar_projetos(vault: Path):
    """Projetos existentes: pastas com projeto.md e notas soltas (formato antigo)."""
    raiz = vault / PROJETOS
    if not raiz.is_dir():
        return [], []
    pastas = sorted(p.name for p in raiz.iterdir() if p.is_dir())
    soltas = sorted(p.stem for p in raiz.glob("*.md"))
    return pastas, soltas


def achar_projeto(vault: Path, nome: str):
    """Devolve (pasta_do_projeto|None, motivo, candidatos).

    motivo: 'ok' | 'caixa' | 'nota_solta' | 'inexistente'

    O nome sempre vem do disco, nunca do que foi pedido. Confiar em
    (raiz / nome).is_dir() quebra dos dois lados: no Windows o filesystem e
    case-insensitive e devolveria a pasta certa com a caixa PEDIDA (frontmatter
    e link [[...]] saem com nome que nao existe); no Linux criaria uma segunda
    pasta para o mesmo projeto.
    """
    raiz = vault / PROJETOS
    if not raiz.is_dir():
        return None, "inexistente", []

    pastas, soltas = listar_projetos(vault)

    for p in pastas:
        if p == nome:
            return raiz / p, "ok", []

    # mesmo nome com caixa diferente: e o mesmo projeto, nao um novo
    for p in pastas:
        if p.lower() == nome.lower():
            return raiz / p, "caixa", [p]

    for s in soltas:
        if s.lower() == nome.lower():
            return None, "nota_solta", [s]

    # nomes parecidos ajudam quem chamou a perguntar em vez de criar duplicata
    chave = re.sub(r"[^a-z0-9]", "", nome.lower())
    parecidos = [
        p for p in pastas + soltas
        if chave and (chave in re.sub(r"[^a-z0-9]", "", p.lower())
                      or re.sub(r"[^a-z0-9]", "", p.lower()) in chave)
    ]
    return None, "inexistente", parecidos or pastas + soltas


TEMPLATE_PROJETO = """---
tipo: projeto
status: ativo
data_criacao: {data}
data_atualizacao: {data}
tags:
  - projeto
---

# {nome}

## Visão Geral

Não identificado

## Stack

## Arquitetura

## Sistemas e integrações

## Responsáveis

## Regras de negócio

## Decisões

## Links e documentação

## Demandas

## Histórico

### {data}

Projeto criado.
"""


def criar_projeto(pasta: Path, nome: str, hoje: str):
    (pasta / "demandas").mkdir(parents=True, exist_ok=True)
    nota = pasta / "projeto.md"
    if not nota.is_file():
        nota.write_text(TEMPLATE_PROJETO.format(nome=nome, data=hoje), encoding="utf-8")
    return nota


def registrar_no_projeto(nota_projeto: Path, atd: str):
    """Insere '- [[ATD]]' na secao ## Demandas do projeto.md.

    Sem isso o vinculo existe so numa direcao, e 'o que ja mexeram nesse
    sistema?' -- que se responde abrindo o projeto -- fica sem resposta.
    """
    if not nota_projeto.is_file():
        return "projeto.md ausente"

    texto = nota_projeto.read_text(encoding="utf-8")
    if f"[[{atd}]]" in texto:
        return "ja listado"

    linhas = texto.splitlines()
    item = f"- [[{atd}]]"

    idx = next((i for i, ln in enumerate(linhas)
                if ln.strip().lower() == SECAO_DEMANDAS.lower()), None)

    if idx is None:
        if linhas and linhas[-1].strip():
            linhas.append("")
        linhas += [SECAO_DEMANDAS, "", item, ""]
        nota_projeto.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return "secao criada"

    # fim da secao: proximo cabecalho de mesmo nivel ou superior
    fim = len(linhas)
    for i in range(idx + 1, len(linhas)):
        if re.match(r"^#{1,2} ", linhas[i]):
            fim = i
            break

    # insere depois do ultimo item da lista, ou logo abaixo do cabecalho
    ins = idx + 1
    for i in range(idx + 1, fim):
        if linhas[i].strip().startswith("- "):
            ins = i + 1
        elif linhas[i].strip():
            ins = i + 1
    if ins == idx + 1:
        linhas.insert(ins, "")
        ins += 1
    linhas.insert(ins, item)

    nota_projeto.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return "adicionado"


def main():
    saida_utf8()
    ap = argparse.ArgumentParser(description="Cria a nota de uma demanda no vault")
    ap.add_argument("--atd", required=True, help="numero de atendimento, formato ATD-000000")
    ap.add_argument("--projeto", required=True, help="nome do projeto existente")
    ap.add_argument("--titulo", default="", help="nome curto da demanda")
    ap.add_argument("--tipo", default="Melhoria", help="Melhoria / Projeto / Sustentação")
    ap.add_argument("--solicitante", default="")
    ap.add_argument("--analista", default="", help="quem esta conduzindo a analise")
    ap.add_argument("--sistemas", default="", help="sistemas envolvidos, texto livre")
    ap.add_argument("--agidesk", default="", help="numero do chamado, se diferente do ATD")
    ap.add_argument("--status", default="Rascunho")
    ap.add_argument("--criar-projeto", action="store_true", dest="criar_projeto",
                    help="cria o projeto se nao existir (use so com confirmacao explicita)")
    ap.add_argument("--vault", default="")
    args = ap.parse_args()

    atd = normalizar_atd(args.atd)
    if not atd:
        _sair({
            "erro": f"'{args.atd}' nao esta no formato ATD-000000 (prefixo ATD- e seis digitos).",
            "sugestao": "Confirme o numero do atendimento antes de criar a nota. "
                        "Nao invente numero nem use placeholder.",
        }, 1)

    vault = exigir_vault(args.vault, formato="json")
    hoje = date.today().isoformat()

    pasta, motivo, candidatos = achar_projeto(vault, args.projeto)

    if motivo == "nota_solta":
        _sair({
            "erro": f"O projeto '{candidatos[0]}' existe como nota solta "
                    f"({PROJETOS}/{candidatos[0]}.md), formato anterior a esta skill.",
            "sugestao": f"Converta para {PROJETOS}/{candidatos[0]}/projeto.md antes de "
                        "criar demandas nele. Nao faca isso sem confirmar com o usuario.",
        }, 1)

    if pasta is None:
        if not args.criar_projeto:
            _sair({
                "erro": f"Projeto '{args.projeto}' nao existe em {PROJETOS}/.",
                "sugestao": "Confirme a qual projeto a demanda pertence. Se for realmente "
                            "um projeto novo, repita com --criar-projeto.",
                "projetos_existentes": candidatos,
            }, 1)
        pasta = vault / PROJETOS / args.projeto

    nome_projeto = pasta.name
    demanda = pasta / "demandas" / f"{atd}.md"

    if demanda.is_file():
        _sair({
            "acao": "nenhuma",
            "aviso": f"{atd} ja existe. Nada foi sobrescrito.",
            "caminho": str(demanda.relative_to(vault)),
            "sugestao": "Atualize a nota existente e registre a mudanca na secao 15 "
                        "(Historico de revisao). Nao crie uma segunda demanda.",
        }, 0)

    if not TEMPLATE.is_file():
        _sair({"erro": f"Template nao encontrado em {TEMPLATE}"}, 1)

    projeto_criado = False
    if not (pasta / "projeto.md").is_file():
        criar_projeto(pasta, nome_projeto, hoje)
        projeto_criado = True
    (pasta / "demandas").mkdir(parents=True, exist_ok=True)

    tipo = args.tipo.strip() or "Melhoria"
    valores = {
        "{{ATD}}": atd,
        "{{TITULO}}": args.titulo.strip() or "Não identificado",
        "{{PROJETO}}": nome_projeto,
        "{{TIPO}}": tipo,
        "{{SOLICITANTE}}": args.solicitante.strip() or "Não identificado",
        "{{ANALISTA}}": args.analista.strip() or "Não identificado",
        "{{SISTEMAS}}": args.sistemas.strip() or "Não identificado",
        "{{AGIDESK}}": args.agidesk.strip() or atd.replace("ATD-", "#"),
        "{{STATUS}}": args.status.strip() or "Rascunho",
        "{{DATA}}": hoje,
    }
    conteudo = TEMPLATE.read_text(encoding="utf-8")
    for chave, valor in valores.items():
        conteudo = conteudo.replace(chave, valor)
    demanda.write_text(conteudo, encoding="utf-8")

    resultado = {
        "acao": "criada",
        "atd": atd,
        "projeto": nome_projeto,
        "caminho": str(demanda.relative_to(vault)),
        "projeto_criado": projeto_criado,
        "vinculo_no_projeto": registrar_no_projeto(pasta / "projeto.md", atd),
    }
    if motivo == "caixa":
        resultado["aviso"] = (
            f"Usei o projeto existente '{nome_projeto}' (voce escreveu "
            f"'{args.projeto}')."
        )
    if tipo not in TIPOS:
        resultado.setdefault("avisos", []).append(
            f"Tipo '{tipo}' fora dos previstos no template: {', '.join(TIPOS)}."
        )
    if projeto_criado:
        resultado["proximo_passo"] = (
            f"O projeto.md de '{nome_projeto}' nasceu vazio — preencha o contexto "
            "permanente do sistema antes de seguir com a analise."
        )
    _sair(resultado)


if __name__ == "__main__":
    main()
