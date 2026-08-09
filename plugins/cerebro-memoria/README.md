# Cérebro Memória

Plugin extraído do arquivo cerebro-memoria.skill. Esta skill implementa um sistema de memória persistente em Obsidian.

## Estrutura

- SKILL.md: descrição e regras de uso do plugin.
- eferences/: templates e regras do vault.
- scripts/: utilitários Python para inicializar e buscar notas.
- cerebro-memoria.skill: pacote original.
- manifest.json: metadados do plugin.

## Uso

1. Execute python scripts/inicializar_vault.py --vault C:\Users\Usuario\Documents\Obsidian\Cerebro para criar a estrutura do vault.
2. Use python scripts/buscar_notas.py --vault C:\Users\Usuario\Documents\Obsidian\Cerebro --query ... para pesquisar notas.

