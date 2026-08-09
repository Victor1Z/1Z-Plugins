# Cérebro Memória

Sistema de memória persistente em Obsidian. O vault é a única persistência — se não está escrito numa nota, não aconteceu.

## Estrutura

- `.claude-plugin/plugin.json` — metadados do plugin.
- `SKILL.md` — regras de uso e gatilhos de ativação.
- `references/` — estrutura do vault, regras de organização e templates de nota.
- `scripts/inicializar_vault.py` — cria a estrutura de pastas do vault (idempotente).
- `scripts/buscar_notas.py` — busca notas por frontmatter e texto livre, sem dependências externas.
- `cerebro-memoria.skill` — pacote original de onde o plugin foi extraído.

## Instalar

```shell
/plugin marketplace add .
/plugin install cerebro-memoria@1z-plugins
```

## Uso direto dos scripts

```bash
python plugins/cerebro-memoria/scripts/inicializar_vault.py --vault "C:\Users\Usuario\Documents\Obsidian\Cerebro"
python plugins/cerebro-memoria/scripts/buscar_notas.py --vault "C:\Users\Usuario\Documents\Obsidian\Cerebro" --query "sistema financeiro"
```
