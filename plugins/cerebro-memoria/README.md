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
    ├── vault_config.py             resolve o caminho do vault (módulo compartilhado)
    ├── configurar_vault.py         grava o caminho do vault desta máquina
    ├── inicializar_vault.py        cria a estrutura de pastas (idempotente)
    └── buscar_notas.py             busca por frontmatter e texto livre
```

`references/` e `scripts/` ficam dentro da pasta da skill de propósito: os caminhos que o `SKILL.md` documenta são resolvidos a partir dele.

## Instalar

```shell
/plugin marketplace add .
/plugin install cerebro-memoria@1z-plugins
```

## Configurar o vault (uma vez por máquina)

O caminho do vault não está escrito no plugin — cada pessoa informa o seu uma vez, e a escolha vale para todas as conversas seguintes.

```bash
cd plugins/cerebro-memoria/skills/cerebro-memoria

python scripts/configurar_vault.py --detectar               # lista os vaults do Obsidian local
python scripts/configurar_vault.py --vault "D:\Obsidian\Cerebro"
python scripts/configurar_vault.py --vault "D:\Obsidian\Cerebro" --criar   # cria a estrutura junto
python scripts/configurar_vault.py                          # mostra em qual vault você está
python scripts/configurar_vault.py --limpar                 # esquece a configuração
```

A escolha vai para `~/.cerebro-memoria/config.json` — fora do repositório, porque é config da pessoa e não do plugin. Trocar de vault é o mesmo comando com outro caminho.

Também dá para pedir isso em linguagem natural dentro do Claude Code ("configura o vault do Cérebro"): a skill roda a detecção, pergunta qual vault usar e grava.

### Ordem de precedência

| Origem | Quando usar |
| --- | --- |
| `--vault "<caminho>"` | trabalhar num vault avulso, sem mexer no padrão |
| `CEREBRO_VAULT` (variável de ambiente) | máquinas compartilhadas, CI, ou caminho por perfil de shell |
| `~/.cerebro-memoria/config.json` | o caso normal — gravado por `configurar_vault.py` |

A detecção via Obsidian só **sugere** candidatos; ela nunca escolhe sozinha. Um vault escolhido por adivinhação recebe notas em silêncio, e o erro só aparece semanas depois.

## Uso direto dos scripts

Com o vault já configurado, nenhum script precisa de `--vault`:

```bash
python scripts/inicializar_vault.py
python scripts/buscar_notas.py --query "sistema financeiro"
python scripts/buscar_notas.py --tipo decisao_tecnica --projeto "Sistema Financeiro"
python scripts/buscar_notas.py --tag sap --tag idoc
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
