#!/usr/bin/env python3
"""
Cria a estrutura de um plugin novo a partir de templates/ e registra ele no
catalogo rodando a sincronizacao no fim.

Nao sobrescreve nada: se a pasta do plugin ja existir, o script para.

Sem dependencias externas -- Python 3 padrao.

Uso:
    python novo_plugin.py --nome meu-plugin --descricao "O que ele faz"
    python novo_plugin.py --nome meu-plugin --descricao "..." --com scripts references
    python novo_plugin.py --nome meu-plugin --descricao "..." --display "Meu Plugin"
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

SLUG_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Pastas opcionais e o arquivo .gitkeep-equivalente que explica para que servem.
EXTRAS = {
    "scripts": "Utilitarios chamados pelo SKILL.md. Sem dependencias externas,\nPython 3 padrao, para rodar em qualquer maquina.\n",
    "references": "Material que o SKILL.md carrega sob demanda (templates, regras,\ntabelas). Fica fora do SKILL.md para nao gastar contexto a toa.\n",
    "agents": "Definicoes de subagentes (.md com frontmatter). Uma por arquivo.\n",
    "hooks": "hooks.json com handlers de evento do Claude Code.\n",
}


def achar_raiz(inicio: Path) -> Path:
    """Sobe ate o dono do marketplace.json (cada plugin tem .claude-plugin/ propria)."""
    for candidato in [inicio, *inicio.parents]:
        if (candidato / ".claude-plugin" / "marketplace.json").is_file():
            return candidato
    raise SystemExit(
        f"nao achei .claude-plugin/marketplace.json subindo a partir de {inicio}.\n"
        "Rode dentro do repositorio do marketplace ou passe --raiz."
    )


def titulo(slug: str) -> str:
    return " ".join(p.capitalize() for p in slug.split("-"))


def renderizar(template: Path, valores: dict) -> str:
    texto = template.read_text(encoding="utf-8")
    for chave, valor in valores.items():
        texto = texto.replace("{{" + chave + "}}", valor)
    return texto


def autor_do_git(raiz: Path) -> str:
    try:
        saida = subprocess.run(
            ["git", "config", "user.name"],
            cwd=raiz, capture_output=True, text=True, timeout=5,
        )
        nome = saida.stdout.strip()
        if nome:
            return nome
    except (OSError, subprocess.SubprocessError):
        pass
    return "Victor Both"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--nome", required=True, help="slug do plugin em kebab-case (ex: revisor-sap)")
    parser.add_argument("--descricao", required=True, help="uma frase sobre o que o plugin faz")
    parser.add_argument("--display", default=None, help="nome legivel (padrao: derivado do slug)")
    parser.add_argument("--autor", default=None, help="autor (padrao: git config user.name)")
    parser.add_argument("--com", nargs="*", default=[], choices=sorted(EXTRAS), help="pastas extras a criar")
    parser.add_argument("--raiz", type=Path, default=None, help="raiz do marketplace (padrao: detecta automaticamente)")
    parser.add_argument("--sem-sync", action="store_true", help="nao rodar a sincronizacao do catalogo no fim")
    args = parser.parse_args()

    if not SLUG_VALIDO.match(args.nome):
        raise SystemExit(
            f"'{args.nome}' nao e um slug valido. Use minusculas, digitos e hifens "
            "(ex: revisor-sap) -- o nome vira namespace das skills."
        )

    raiz = args.raiz.resolve() if args.raiz else achar_raiz(Path(__file__).resolve().parent)
    templates = Path(__file__).resolve().parent.parent / "templates"
    destino = raiz / "plugins" / args.nome

    if destino.exists():
        raise SystemExit(f"{destino} ja existe -- nao vou sobrescrever. Apague ou escolha outro nome.")

    valores = {
        "NOME": args.nome,
        "DISPLAY": args.display or titulo(args.nome),
        "DESCRICAO": args.descricao,
        "AUTOR": args.autor or autor_do_git(raiz),
    }

    (destino / ".claude-plugin").mkdir(parents=True)
    (destino / ".claude-plugin" / "plugin.json").write_text(
        renderizar(templates / "plugin.json.tmpl", valores), encoding="utf-8"
    )
    (destino / "SKILL.md").write_text(
        renderizar(templates / "SKILL.md.tmpl", valores), encoding="utf-8"
    )
    (destino / "README.md").write_text(
        renderizar(templates / "README.md.tmpl", valores), encoding="utf-8"
    )

    for extra in args.com:
        pasta = destino / extra
        pasta.mkdir()
        (pasta / "LEIA-ME.md").write_text(f"# {extra}/\n\n{EXTRAS[extra]}", encoding="utf-8")

    rel = destino.relative_to(raiz).as_posix()
    print(f"[ok] plugin criado em {rel}/")
    print(f"     - {rel}/.claude-plugin/plugin.json")
    print(f"     - {rel}/SKILL.md   <- escreva o description real (e ele que ativa a skill)")
    print(f"     - {rel}/README.md")
    for extra in args.com:
        print(f"     - {rel}/{extra}/")

    if args.sem_sync:
        return 0

    print()
    # Sem o flush a saida do subprocesso sai antes da nossa e a ordem confunde.
    sys.stdout.flush()
    sync = Path(__file__).resolve().parent / "sincronizar_marketplace.py"
    return subprocess.run([sys.executable, str(sync), "--raiz", str(raiz)]).returncode


if __name__ == "__main__":
    sys.exit(main())
