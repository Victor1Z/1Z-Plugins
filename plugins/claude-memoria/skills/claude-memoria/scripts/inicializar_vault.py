#!/usr/bin/env python3
"""
Cria a estrutura de pastas do vault Claude Memória, se ainda não existir, e o
_config/config.md com valores padrão conservadores.

Não apaga nem sobrescreve nada — é seguro rodar mais de uma vez.

O vault vem de configurar_vault.py (config do usuário) ou de --vault, que
sobrescreve. Veja vault_config.py para a ordem de precedência.

Uso:
    python inicializar_vault.py
    python inicializar_vault.py --vault "D:\\Obsidian\\Vault"
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vault_config import exigir_vault, saida_utf8  # noqa: E402

# Estrutura definitiva. Categoria nova de primeiro nivel nao entra aqui: o que
# nao se encaixa vai para "00 - Inbox" e e triado depois. Uma pasta criada para
# um caso isolado e como a organizacao vira irrecuperavel.
PASTAS = [
    "00 - Inbox",
    "01 - Projetos",
    "02 - Trabalho/Reuniões",
    "02 - Trabalho/Documentação",
    "03 - Conhecimento/Programação",
    "03 - Conhecimento/SAP",
    "03 - Conhecimento/.NET",
    "03 - Conhecimento/React",
    "03 - Conhecimento/Git",
    "03 - Conhecimento/DevOps",
    "03 - Conhecimento/Outros",
    "05 - Empresas",
    "99 - Arquivo",
    "_config",
]

# Chave -> valor padrao. Usado tanto no config novo quanto para completar um
# config existente que nasceu antes de uma chave passar a existir.
CHAVES_CONFIG = [
    ("auto_context", "false"),
    ("auto_memory", "false"),
    ("auto_analysis", "false"),
    ("auto_linking", "true"),
    ("confirm_delete", "true"),
    ("confirm_new_project", "true"),
    ("language", "pt-BR"),
]

CONFIG_PADRAO = """---
auto_context: false
auto_memory: false
auto_analysis: false
auto_linking: true
confirm_delete: true
confirm_new_project: true
language: pt-BR
---

# Configuração do Claude Memória

Esse arquivo controla o comportamento do skill `claude-memoria`.

- `auto_context`: se `true`, Claude tenta buscar contexto relacionado
  automaticamente quando você menciona algo que parece já ter sido
  registrado antes. Se `false` (padrão), Claude só busca quando você pedir
  explicitamente ("busca o contexto", "lembra do projeto X").
- `auto_memory`: se `true`, Claude pode registrar informação relevante
  mesmo sem o gatilho "se lembre disso". Recomendo manter `false` até você
  confiar no comportamento.
- `confirm_delete`: se `true`, Claude sempre confirma antes de apagar
  qualquer nota ou trecho de nota.
- `confirm_new_project`: se `true`, Claude confirma antes de criar uma nota
  de projeto nova em vez de assumir que é diferente de um já existente.
- `auto_analysis`: **mantenha `false`.** Com `false`, a análise de uma
  demanda só começa quando você pedir explicitamente ("vamos analisar essa
  demanda", "inicia o levantamento da ATD-000000"). Mencionar uma demanda
  não dispara análise.
- `auto_linking`: se `true` (padrão), Claude cria e sugere links `[[...]]`
  entre projeto, demanda, conhecimento e empresa quando a relação é clara.

Edite os valores acima livremente — o skill lê esse arquivo no início de
cada tarefa relevante.
"""


FRONTMATTER_RE = re.compile(r'^(---\s*\n)(.*?)(\n---\s*)$', re.DOTALL | re.MULTILINE)


def completar_config(config_path):
    """Acrescenta ao config existente as chaves que ainda nao existem nele.

    Um config criado antes de uma chave passar a existir nao ganha a chave
    sozinho, e o skill acaba lendo um comportamento que nao esta escrito em
    lugar nenhum -- que e pior do que o padrao explicito.

    Nunca altera nem remove valor existente: so acrescenta o que falta.
    Devolve (chaves_adicionadas, erro).
    """
    texto = config_path.read_text(encoding='utf-8')
    m = FRONTMATTER_RE.search(texto)
    if not m:
        return [], 'config.md sem bloco de frontmatter — não mexi nele'

    bloco = m.group(2)
    faltando = [
        (chave, padrao) for chave, padrao in CHAVES_CONFIG
        if not re.search(rf'^\s*{re.escape(chave)}\s*:', bloco, re.MULTILINE)
    ]
    if not faltando:
        return [], None

    novas = '\n'.join(f'{chave}: {padrao}' for chave, padrao in faltando)
    fim = m.end(2)
    atualizado = texto[:fim] + '\n' + novas + texto[fim:]
    config_path.write_text(atualizado, encoding='utf-8')
    return [chave for chave, _ in faltando], None


def main():
    saida_utf8()
    ap = argparse.ArgumentParser(description='Inicializa a estrutura do vault Claude Memória')
    ap.add_argument('--vault', default='', help='Caminho do vault do Obsidian (padrão: o configurado)')
    args = ap.parse_args()

    # exigir_existente=False: criar a pasta é justamente a função deste script.
    vault = exigir_vault(args.vault, exigir_existente=False)
    vault.mkdir(parents=True, exist_ok=True)

    criadas = []
    for pasta in PASTAS:
        p = vault / pasta
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            criadas.append(str(p.relative_to(vault)))

    config_path = vault / "_config" / "config.md"
    config_criado = False
    chaves_novas, erro_config = [], None
    if not config_path.exists():
        config_path.write_text(CONFIG_PADRAO, encoding='utf-8')
        config_criado = True
    else:
        chaves_novas, erro_config = completar_config(config_path)

    print(f"Pastas criadas: {len(criadas)}")
    for c in criadas:
        print(f"  + {c}")
    if not criadas:
        print("  (nenhuma — estrutura já existia)")
    print(f"Config criado em _config/config.md: {config_criado}")
    if chaves_novas:
        print(f"Chaves acrescentadas ao config existente: {', '.join(chaves_novas)}")
    if erro_config:
        print(f"Aviso: {erro_config}")


if __name__ == '__main__':
    main()
