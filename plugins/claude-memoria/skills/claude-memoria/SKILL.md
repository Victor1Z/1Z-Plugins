---
name: claude-memoria
description: Sistema de memória persistente pessoal, usando um vault do Obsidian (configurado uma vez por máquina) como única fonte de verdade — sem banco vetorial, sem SQLite. Ative sempre que o usuário pedir para guardar algo ("se lembre disso", "lembra disso", "guarda isso", "salva isso", "anota isso", "não esquece disso", "memoriza isso"), sempre que pedir para recuperar contexto ("busca o contexto", "lembra do projeto X", "como ficou aquela decisão sobre Y", "vamos continuar aquele projeto Z"), e sempre que a conversa envolver registrar reuniões, decisões técnicas, incidentes de TI/SAP, conhecimento técnico ou andamento de projetos que deveriam virar registro permanente no Claude Memória. Ative também quando pedirem para configurar/trocar o caminho do vault do Claude Memória. Ative mesmo sem essas frases exatas — a intenção de persistir ou recuperar informação é o que importa.
---

# Claude Memória — memória persistente em Obsidian

## Skill irmã: projetos e demandas

Este plugin tem duas skills sobre o mesmo vault. Esta cuida de **guardar e recuperar memória em geral**. A irmã, `gestao-demandas`, cuida da estrutura **projeto × demanda × conhecimento** e do fluxo de análise de uma demanda (ATD).

Se a conversa envolve um projeto, um número `ATD-000000`, ou levantar requisitos/regras/casos de uso, o dono do assunto é a `gestao-demandas` — as regras dela estão em `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/SKILL.md`. Em particular: **análise de demanda nunca começa sozinha**, só com pedido explícito.

## Ideia central

O Obsidian é a única persistência. Você (Claude) é a camada de inteligência por cima dela. Isso significa: nada de inventar um banco de dados paralelo, nada de "lembrar" coisas que não estão escritas em uma nota — se não está no vault, não aconteceu. Isso é o que torna a memória confiável: o usuário pode abrir o Obsidian a qualquer momento e ver exatamente o que você sabe sobre cada assunto.

## Onde fica o vault

O caminho do vault **não** está escrito nesta skill: ele é de cada pessoa e é configurado uma única vez por máquina, ficando em `~/.claude-memoria/config.json` (fora do repositório do plugin). Os scripts leem esse arquivo sozinhos — **não passe `--vault`** a menos que a pessoa peça explicitamente para trabalhar num vault diferente do padrão dela.

A ordem de precedência é: `--vault` > variável de ambiente `CLAUDE_MEMORIA_VAULT` > config gravada > config do nome anterior do plugin (`~/.cerebro-memoria/config.json` ou `CEREBRO_VAULT`), que ainda é lida para quem configurou antes do rename. Se o status vier com `origem` legada, vale sugerir regravar com `configurar_vault.py --vault "<caminho>"` — a escrita sempre vai para o caminho novo.

Este skill assume que você tem acesso de arquivo a esse caminho na conversa atual — normalmente porque está rodando via Claude Code ou Claude Desktop na máquina da pessoa, com ferramentas de arquivo (bash/view/create_file/str_replace) ou um conector MCP de filesystem/Obsidian apontando para essa pasta. Se você perceber que não tem esse acesso nesta conversa (por exemplo, está rodando num ambiente sandbox sem esse caminho montado), diga isso claramente em vez de simular ou inventar o conteúdo do vault.

Os scripts esperam Python 3 disponível no ambiente onde você está rodando.

Esta skill fica em `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/` — use esse prefixo ao chamar os scripts e ao ler os arquivos de `references/`. Caminho relativo simples (`scripts/buscar_notas.py`) só funcionaria se o diretório atual fosse o da skill, o que normalmente não é o caso.

## Passo 0 — primeira vez nesta máquina

Se qualquer script responder que o vault não está configurado (`"erro": "Vault do Claude Memoria nao configurado..."`), faça o setup **antes** de continuar a tarefa, e só então volte para o que a pessoa pediu:

1. Rode `configurar_vault.py --detectar` para listar os vaults que o Obsidian conhece nesta máquina.
2. **Pergunte qual usar** — mostre os candidatos com o caminho completo. Não escolha sozinho, mesmo que só apareça um candidato óbvio: escrever no vault errado é um estrago que só aparece semanas depois. Se a lista vier vazia (Obsidian não instalado, ou vault nunca aberto aqui), peça o caminho.
3. Grave com `configurar_vault.py --vault "<caminho escolhido>"`. Se a pasta ainda não existir e a pessoa quiser um vault novo, use `--vault "<caminho>" --criar`, que já cria a estrutura de pastas.
4. Confirme numa linha onde ficou gravado e que isso vale para as próximas conversas.

Trocar de vault depois é o mesmo comando com outro caminho; `--limpar` esquece a configuração.

## Antes de qualquer coisa: checar a config do vault

Resolvido o caminho, o vault tem (ou deveria ter) um arquivo `_config/config.md` com o comportamento desejado. Esse arquivo mora *dentro* do vault e controla o comportamento; não confunda com `~/.claude-memoria/config.json`, que só guarda **onde** o vault fica.

```yaml
auto_context: false      # buscar contexto sozinho, sem pedirem?
auto_memory: false        # salvar informação relevante sem o gatilho "se lembre disso"?
auto_analysis: false      # NUNCA true — análise de demanda só com pedido explícito
auto_linking: true        # criar/sugerir links [[...]] quando a relação é clara?
confirm_delete: true      # confirmar antes de apagar qualquer coisa?
confirm_new_project: true # confirmar antes de criar nota de projeto nova?
```

Se esse arquivo ainda não existir, rode `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/inicializar_vault.py` (veja abaixo) para criar a estrutura de pastas e a config com valores padrão conservadores, e avise que criou. Não pergunte permissão pra isso — criar a estrutura de pastas e um arquivo de config é a própria função deste skill, não uma ação destrutiva. Se a config já existir mas estiver sem alguma dessas chaves, o mesmo script acrescenta só as que faltam, sem tocar nos valores que você já ajustou.

Leia esse arquivo mentalmente no início de cada tarefa relevante e respeite os valores. Por padrão (`auto_context: false`, `auto_memory: false`), você só busca ou salva quando pedirem explicitamente ou disparar um dos gatilhos abaixo — isso evita registrar lixo ou recuperar contexto que não vem ao caso.

## Fluxo 1 — guardar uma informação ("remember")

Quando o usuário disparar um gatilho de persistência:

1. **Classifique** o que está sendo dito: é contexto permanente de um projeto, algo específico de uma demanda (ATD), uma reunião, conhecimento técnico geral, informação sobre uma empresa/fornecedor, ou algo sem categoria clara ainda?
2. **Identifique o projeto/assunto relacionado**, se houver um. Se o que está sendo dito é sobre uma alteração num sistema com número de atendimento, o lugar é a demanda — veja a skill `gestao-demandas`.
3. **Procure antes de criar.** Rode `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py` filtrando por tipo/projeto/tags para ver se já existe uma nota sobre esse mesmo assunto. Isso é o passo mais importante do fluxo — pular ele é a causa nº 1 de vault bagunçado.
4. **Decida atualizar vs. criar:**
   - Achou uma nota que claramente é sobre o mesmo projeto/assunto → **atualize** ela (veja "preservar histórico" abaixo). Nunca crie `Sistema Financeiro - Docker.md`, `Sistema Financeiro - API.md` etc. quando já existe `Sistema Financeiro.md` — tudo isso é uma seção dentro da nota do projeto, não notas separadas.
   - Não achou nada e a classificação está clara → **crie** a nota usando o template correspondente (`${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/templates.md`).
   - Não tem certeza de projeto/categoria → **vai para o Inbox** (`00 - Inbox/AAAA-MM-DD - descrição curta.md`), sem tentar forçar uma classificação. É mais fácil organizar depois do que desfazer uma classificação errada.
   - Se o match com um projeto existente não for óbvio (nome parecido mas não idêntico), **pergunte** em vez de assumir — a menos que `confirm_new_project: false` na config.
5. **Preserve histórico.** Ao atualizar uma nota, não sobrescreva informação antiga — adicione à seção `## Histórico` com a data, e só então atualize o corpo principal se o fato mudou (ex: decisão trocada). Um exemplo do padrão está em `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/regras.md`.
6. **Registre a data certa.** Distinga a data do evento (quando aconteceu) da data de criação da nota e da última atualização — os três campos existem no frontmatter por esse motivo.
7. **Confirme de forma breve** o que foi salvo e onde (uma ou duas linhas — "Registrado no Sistema Financeiro: decisão de usar .NET 10 no backend"). Não é preciso pedir permissão para escrever a nota em si; escrever no vault é a função do skill.

## Fluxo 2 — recuperar contexto ("recall")

Quando o usuário pedir contexto ou perguntar algo que soa como referência a algo já registrado:

1. Rode `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py` com a query e, se souber, filtros de tipo/projeto/tag.
2. Monte um resumo organizado a partir do que foi encontrado — não repita o conteúdo bruto das notas, sintetize (stack, decisões, pendências, reuniões relacionadas, data da última atualização).
3. Se nada for encontrado, diga isso claramente. Não invente contexto para parecer útil.
4. Se `auto_context: false` (padrão), só faça essa busca quando pedirem. Se `auto_context: true`, você pode tentar isso proativamente quando o usuário referenciar algo como "aquele projeto financeiro" — mas ainda assim é melhor confirmar rapidamente o que encontrou do que assumir silenciosamente.

## Regra de ouro: uma nota por assunto, não uma nota por frase

Um projeto, decisão recorrente ou área de conhecimento tem **uma nota**, com seções internas que crescem ao longo do tempo. Notas novas e separadas só fazem sentido para: uma reunião específica, um incidente específico, uma decisão técnica específica com peso próprio, ou um conceito que merece existir isolado (aí sim linkado de volta com `[[Nome da Nota]]`). Na dúvida, prefira atualizar uma nota existente a criar uma nova.

## Estrutura do vault, templates e regras completas

- `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/estrutura-vault.md` — árvore de pastas completa e o que vai em cada uma.
- `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/templates.md` — template de frontmatter + corpo para projeto, reunião, decisão técnica, incidente e conhecimento técnico. Use como base ao criar notas novas; os nomes dos campos de frontmatter aqui são os que `buscar_notas.py` espera para filtrar (`tipo`, `projeto`, `tags`, `status`, `data`/`data_evento`/`data_criacao`).
- `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/regras.md` — as regras completas de organização, com o porquê de cada uma (duplicação, exclusão, Inbox, etc.).

Leia esses arquivos quando for criar um tipo de nota que ainda não usou na conversa atual, ou quando tiver dúvida sobre onde algo deveria ir.

## Scripts

Nenhum deles precisa de `--vault`: todos resolvem o vault configurado sozinhos.

### `scripts/configurar_vault.py`

Descobre, grava e mostra o caminho do vault desta máquina. Saída sempre em JSON.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/configurar_vault.py"
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/configurar_vault.py" --detectar
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/configurar_vault.py" --vault "D:\Obsidian\Vault"
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/configurar_vault.py" --vault "D:\Obsidian\Vault" --criar
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/configurar_vault.py" --limpar
```

Sem argumentos, mostra o status (`vault`, `origem`, `existe`) e os vaults detectados — use isso quando quiser saber em qual vault você está escrevendo.

### `scripts/buscar_notas.py`

Busca notas por texto livre e/ou filtros de frontmatter. Sempre prefira isso a tentar adivinhar ou a ler o vault inteiro nota por nota — é mais rápido e mais confiável.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --query "sistema financeiro"
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --tipo decisao_tecnica --projeto "Sistema Financeiro"
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --tag sap --tag idoc
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --pasta "01 - Projetos"
```

Retorna JSON com `total_encontrado`, `total_no_vault` e a lista de `resultados` (path, título, tipo, projeto, status, tags, data, trecho). Sem nenhum filtro, lista o vault inteiro — útil para um inventário geral, mas use `--limit` se o vault já estiver grande.

### `scripts/inicializar_vault.py`

Cria a estrutura de pastas padrão e o `_config/config.md`, se ainda não existirem. Não apaga nem sobrescreve nada — é seguro rodar mais de uma vez.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/inicializar_vault.py"
```

## O que este skill não faz (por enquanto)

Não apaga notas automaticamente, não reorganiza pastas em massa, e não decide sozinho mudar `confirm_delete`/`confirm_new_project` para `false` — essas são decisões que o usuário toma editando `_config/config.md` diretamente, ou pedindo explicitamente para você editar. Exclusão de conteúdo histórico só acontece com autorização explícita na conversa, mesmo que `confirm_delete` esteja `false` para outras coisas.
