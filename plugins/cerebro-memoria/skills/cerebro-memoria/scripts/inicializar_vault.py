#!/usr/bin/env python3
"""
Cria a estrutura de pastas do vault Cérebro, se ainda não existir, e o
_config/config.md com valores padrão conservadores.

Não apaga nem sobrescreve nada — é seguro rodar mais de uma vez.

O vault vem de configurar_vault.py (config do usuário) ou de --vault, que
sobrescreve. Veja vault_config.py para a ordem de precedência.

Uso:
    python inicializar_vault.py
    python inicializar_vault.py --vault "D:\\Obsidian\\Cerebro"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vault_config import exigir_vault, saida_utf8  # noqa: E402

PASTAS = [
    "00 - Inbox",
    "01 - Projetos",
    "02 - Trabalho/Reuniões",
    "02 - Trabalho/Tarefas",
    "02 - Trabalho/Decisões",
    "02 - Trabalho/Problemas",
    "02 - Trabalho/Incidentes",
    "02 - Trabalho/Documentação",
    "03 - Conhecimento",
    "04 - Pessoas",
    "05 - Empresas",
    "06 - Conceitos",
    "07 - Memórias",
    "99 - Arquivo",
    "_config",
]

CONFIG_PADRAO = """---
auto_context: false
auto_memory: false
confirm_delete: true
confirm_new_project: true
language: pt-BR
---

# Configuração do Cérebro

Esse arquivo controla o comportamento do skill `cerebro-memoria`.

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

Edite os valores acima livremente — o skill lê esse arquivo no início de
cada tarefa relevante.
"""


def main():
    saida_utf8()
    ap = argparse.ArgumentParser(description='Inicializa a estrutura do vault Cérebro')
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
    if not config_path.exists():
        config_path.write_text(CONFIG_PADRAO, encoding='utf-8')
        config_criado = True

    print(f"Pastas criadas: {len(criadas)}")
    for c in criadas:
        print(f"  + {c}")
    if not criadas:
        print("  (nenhuma — estrutura já existia)")
    print(f"Config criado em _config/config.md: {config_criado}")


if __name__ == '__main__':
    main()
