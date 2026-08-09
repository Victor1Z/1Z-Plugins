# Cérebro Memória

Sistema de memória persistente em Obsidian. O vault é a única persistência — se não está escrito numa nota, não aconteceu.

## Estrutura

```text
.claude-plugin/plugin.json          metadados do plugin
skills/cerebro-memoria/
├── SKILL.md                        regras de uso e gatilhos de ativação
├── references/
│   ├── estrutura-vault.md          árvore de pastas do vault
│   ├── regras.md                   regras de organização, com o porquê de cada uma
│   └── templates.md                templates de frontmatter + corpo por tipo de nota
└── scripts/
    ├── inicializar_vault.py        cria a estrutura de pastas (idempotente)
    └── buscar_notas.py             busca por frontmatter e texto livre
```

`references/` e `scripts/` ficam dentro da pasta da skill de propósito: os caminhos que o `SKILL.md` documenta são resolvidos a partir dele.

## Instalar

```shell
/plugin marketplace add .
/plugin install cerebro-memoria@1z-plugins
```

## Uso direto dos scripts

Fora do plugin instalado, a partir da raiz do repositório:

```bash
cd plugins/cerebro-memoria/skills/cerebro-memoria

python scripts/inicializar_vault.py --vault "C:\Users\Usuario\Documents\Obsidian\Cerebro"
python scripts/buscar_notas.py --vault "C:\Users\Usuario\Documents\Obsidian\Cerebro" --query "sistema financeiro"
python scripts/buscar_notas.py --vault "..." --tipo decisao_tecnica --projeto "Sistema Financeiro"
python scripts/buscar_notas.py --vault "..." --tag sap --tag idoc
```

Dentro do plugin instalado, o `SKILL.md` usa `${CLAUDE_PLUGIN_ROOT}/skills/cerebro-memoria/scripts/...`, porque o diretório atual não é o da skill.

## Campos de frontmatter reconhecidos

`buscar_notas.py` filtra por `tipo`, `projeto`, `tags` e `status`, e lê a data de `data`, `data_evento` ou `data_criacao` (nessa ordem). Use os nomes exatos ao criar notas — estão em `references/templates.md`.

Tags funcionam nos dois formatos YAML:

```yaml
tags: [sap, idoc]     # inline
tags:                 # em bloco
  - sap
  - idoc
```

O prefixo `#` é ignorado na comparação, então `--tag sap` acha `#sap`.
