# Claude Memória

Sistema de memória persistente em Obsidian. O vault é a única persistência — se não está escrito numa nota, não aconteceu.

Duas skills sobre o **mesmo vault**:

| Skill | Cuida de |
| --- | --- |
| `claude-memoria` | guardar e recuperar memória em geral: reuniões, conhecimento, empresas, contexto de projeto |
| `gestao-demandas` | a estrutura projeto × demanda × conhecimento, e o fluxo de análise de uma demanda (ATD) |

A segunda existe porque projeto e demanda são coisas diferentes — *projeto é onde o sistema existe, demanda é o que será alterado nele* — e confundir os dois é o jeito mais rápido de a base degradar.

## Estrutura

```text
.claude-plugin/plugin.json          metadados do plugin
skills/
├── claude-memoria/
│   ├── SKILL.md                    regras de uso e gatilhos de ativação
│   ├── references/
│   │   ├── estrutura-vault.md      árvore de pastas do vault
│   │   ├── regras.md               regras de organização, com o porquê de cada uma
│   │   └── templates.md            templates por tipo de nota (projeto, reunião, empresa...)
│   └── scripts/
│       ├── vault_config.py         resolve o caminho do vault (módulo compartilhado)
│       ├── configurar_vault.py     grava o caminho do vault desta máquina
│       ├── inicializar_vault.py    cria a estrutura de pastas (idempotente)
│       └── buscar_notas.py         busca por frontmatter e texto livre
└── gestao-demandas/
    ├── SKILL.md                    projeto × demanda, ATD, quando começar uma análise
    ├── references/
    │   ├── demanda.template.md     template literal da demanda (15 seções)
    │   ├── preenchimento-demanda.md como preencher sem inventar
    │   ├── fluxo-analise.md        gatilhos e as 5 etapas da análise
    │   └── projeto-e-demanda.md    regras de separação, links e não-duplicação
    └── scripts/
        ├── nova_demanda.py         cria a demanda validada e liga as duas pontas
        └── contexto_projeto.py     carrega projeto + demandas + notas relacionadas
```

`references/` e `scripts/` ficam dentro da pasta de cada skill de propósito: os caminhos que o `SKILL.md` documenta são resolvidos a partir dele.

Os scripts de `gestao-demandas` importam `vault_config.py` e `buscar_notas.py` da skill irmã por caminho relativo ao plugin — as duas skills moram no mesmo plugin justamente por isso: o plugin é copiado inteiro na instalação, então nenhuma delas precisa de uma cópia própria do resolvedor de vault.

## Instalar

```shell
/plugin marketplace add .
/plugin install claude-memoria@1z-plugins
```

## Configurar o vault (uma vez por máquina)

O caminho do vault não está escrito no plugin — cada pessoa informa o seu uma vez, e a escolha vale para todas as conversas seguintes.

```bash
cd plugins/claude-memoria/skills/claude-memoria

python scripts/configurar_vault.py --detectar               # lista os vaults do Obsidian local
python scripts/configurar_vault.py --vault "D:\Obsidian\Vault"
python scripts/configurar_vault.py --vault "D:\Obsidian\Vault" --criar   # cria a estrutura junto
python scripts/configurar_vault.py                          # mostra em qual vault você está
python scripts/configurar_vault.py --limpar                 # esquece a configuração
```

A escolha vai para `~/.claude-memoria/config.json` — fora do repositório, porque é config da pessoa e não do plugin. Trocar de vault é o mesmo comando com outro caminho.

Também dá para pedir isso em linguagem natural dentro do Claude Code ("configura o vault do Claude Memória"): a skill roda a detecção, pergunta qual vault usar e grava.

### Ordem de precedência

| Origem | Quando usar |
| --- | --- |
| `--vault "<caminho>"` | trabalhar num vault avulso, sem mexer no padrão |
| `CLAUDE_MEMORIA_VAULT` (variável de ambiente) | máquinas compartilhadas, CI, ou caminho por perfil de shell |
| `~/.claude-memoria/config.json` | o caso normal — gravado por `configurar_vault.py` |
| `CEREBRO_VAULT` / `~/.cerebro-memoria/config.json` | **legado**, só leitura — o plugin se chamava `cerebro-memoria`. Quem configurou antes do rename continua funcionando sem reconfigurar; regravar com `configurar_vault.py` migra para o caminho novo |

A detecção via Obsidian só **sugere** candidatos; ela nunca escolhe sozinha. Um vault escolhido por adivinhação recebe notas em silêncio, e o erro só aparece semanas depois.

## Estrutura do vault

```text
00 - Inbox/                     sem classificação clara ainda
01 - Projetos/<Projeto>/
├── projeto.md                  contexto permanente do sistema
└── demandas/ATD-000000.md      uma nota por atendimento
02 - Trabalho/                  Reuniões/, Documentação/
03 - Conhecimento/              Programação, SAP, .NET, React, Git, DevOps, Outros
05 - Empresas/                  uma nota por fornecedor/cliente
99 - Arquivo/                   encerrado, fora do fluxo ativo
_config/config.md               comportamento das skills
```

Essa é a organização definitiva — o que não se encaixa vai para `00 - Inbox/`, não para uma categoria nova.

Notas de projeto no formato antigo (arquivo solto em `01 - Projetos/`) continuam válidas e a busca continua achando; a conversão para o formato pasta é oferecida, nunca automática.

## Uso direto dos scripts

Com o vault já configurado, nenhum script precisa de `--vault`:

```bash
python claude-memoria/scripts/inicializar_vault.py
python claude-memoria/scripts/buscar_notas.py --query "sistema financeiro"
python claude-memoria/scripts/buscar_notas.py --tipo demanda --projeto "Hub de Crédito"
python claude-memoria/scripts/buscar_notas.py --tag sap --tag idoc

python gestao-demandas/scripts/nova_demanda.py --atd ATD-282471 --projeto "Hub de Crédito"
python gestao-demandas/scripts/contexto_projeto.py --atd ATD-282471
```

(a partir de `plugins/claude-memoria/skills/`). Dentro do plugin instalado, o `SKILL.md` usa `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/...`, porque o diretório atual não é o da skill.

`inicializar_vault.py` também completa um `config.md` que já existe, acrescentando só as chaves que faltam — valores que você ajustou não são tocados.

### Se `python` não for encontrado no Windows

`python` pode resolver para o stub da Microsoft Store (a mensagem é "Python não encontrado; execute sem argumentos para instalar na Microsoft Store"). Nesse caso use `py` no lugar de `python`, ou desative o alias em *Configurações > Aplicativos > Aliases de execução de aplicativo*.

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
