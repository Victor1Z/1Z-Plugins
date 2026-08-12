---
name: gestao-demandas
description: Organiza projetos, demandas (ATD), conhecimento técnico e empresas dentro do vault do Claude Memória, e conduz a análise/levantamento de uma demanda quando pedido. Ative sempre que a conversa envolver um projeto ("o Hub de Crédito", "o Supera", "essa API"), um número de atendimento no formato ATD-000000, uma melhoria/correção/ajuste a fazer num sistema existente, documentar um projeto novo, registrar uma empresa/fornecedor (Sinqia, Dremio, Emarsys), ou levantar requisitos, regras de negócio, casos de uso e critérios de aceite. Ative também quando pedirem para iniciar uma análise ("vamos analisar essa demanda", "inicia o levantamento da ATD-282471", "começa a análise"). Ativar a skill não significa começar uma análise — o levantamento só começa com pedido explícito.
---

# Gestão de projetos, demandas e conhecimento

## Ideia central

Três coisas diferentes, que o vault mantém separadas de propósito:

> **Projeto** é onde o sistema existe. **Demanda** é o que será alterado nele. **Conhecimento** é a boa prática de desenvolvimento que orienta como a próxima funcionalidade é construída.

Confundir os três é o jeito mais rápido de degradar a base. Uma demanda tratada como projeto vira uma cópia da arquitetura inteira que envelhece sozinha; conhecimento preso dentro de uma demanda nunca é achado de novo quando outro projeto precisa dele.

Isso é uma skill irmã de `claude-memoria`, no mesmo plugin e no **mesmo vault** — mesma config (`~/.claude-memoria/config.json`), mesmos scripts de busca. `claude-memoria` cuida de guardar e recuperar memória em geral; esta aqui cuida da estrutura projeto/demanda e do fluxo de análise.

## A regra que mais importa: não comece uma análise sozinho

Mencionar uma demanda **não** é pedir uma análise.

> "Essa demanda ATD-282471 pertence ao Hub de Crédito." → isso é informação. Registre o vínculo se fizer sentido, e siga a conversa.

> "Vamos iniciar uma análise da ATD-282471." → aí sim, execute o fluxo de análise.

`auto_analysis` é `false` em `_config/config.md` e deve continuar assim. Os gatilhos que valem como pedido explícito, e o fluxo completo das cinco etapas, estão em `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/fluxo-analise.md` — leia esse arquivo antes de conduzir a primeira análise da conversa.

Uma análise iniciada sem pedido custa caro nos dois sentidos: gera um documento de 15 seções cheio de "Não identificado" que ninguém pediu, e interrompe a conversa que a pessoa estava tendo.

## Onde cada coisa mora

```text
00 - Inbox/                     ← ainda sem classificação clara
01 - Projetos/
└── <Projeto>/
    ├── projeto.md              ← contexto permanente do sistema
    └── demandas/
        └── ATD-282471.md       ← contexto específico de uma alteração
02 - Trabalho/
├── Reuniões/
└── Documentação/
03 - Conhecimento/              ← boas práticas do time: Programação, Arquitetura, Outros
05 - Empresas/                  ← uma nota por empresa/fornecedor/cliente
99 - Arquivo/                   ← encerrado, fora do fluxo ativo
_config/config.md
```

Essa é a organização **definitiva**. Não crie categorias ou pastas de primeiro nível novas. Se uma informação não se encaixa claramente em nenhuma delas, ela vai para `00 - Inbox/` — inventar uma sétima pasta para um caso isolado é como a estrutura vira irrecuperável.

Detalhes de cada pasta: `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/estrutura-vault.md`.

## Projeto

Um projeto é uma estrutura que **já existe e é funcional**: Hub de Crédito, Supera, Front-Hub-Credito, a API de propostas, um sistema interno. Ele tem uma nota principal, `01 - Projetos/<Projeto>/projeto.md`, que guarda o contexto permanente — objetivo, arquitetura, stack, sistemas envolvidos, integrações, bancos, APIs, responsáveis, regras de negócio relevantes, decisões arquiteturais, links e a lista de demandas.

Nunca crie uma nota de projeto nova para cada demanda. E não crie um projeto só porque uma demanda ainda não está vinculada a nenhum — nesse caso, pergunte.

Antes de criar qualquer projeto, procure: `buscar_notas.py --pasta "01 - Projetos"`. Nome parecido mas não idêntico ao que a pessoa falou é motivo para perguntar, não para assumir que é outro sistema.

**Projetos antigos em formato antigo.** Se você encontrar `01 - Projetos/Hub de Crédito.md` como arquivo solto (formato anterior a esta skill), ele continua válido e a busca continua achando. Quando a primeira demanda daquele projeto aparecer, ofereça converter para `01 - Projetos/Hub de Crédito/projeto.md` — mas não mexa por conta própria.

## Demanda

Uma demanda é uma melhoria, correção, alteração, ajuste, nova funcionalidade ou mudança de comportamento **dentro de um projeto existente**. Ela nunca é um projeto independente.

Toda demanda tem um número de atendimento, no formato exato:

```text
ATD-000000
```

Seis dígitos, com o hífen. `ATD-282471` é o identificador único da demanda — é o nome do arquivo e o valor do campo `atd` no frontmatter.

**Se a pessoa pedir para criar uma demanda sem informar o número, peça o número.** Não invente, não use placeholder, não crie com `ATD-000000` "para preencher depois". Um número inventado vira o identificador de verdade em minutos e ninguém consegue mais cruzar com o Agidesk.

A demanda vive em `01 - Projetos/<Projeto>/demandas/ATD-282471.md` e segue o template literal de `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/demanda.template.md` — 15 seções, com IDs rastreáveis (RF, RNF, RN, CU, CA). Essa é a fonte de verdade da estrutura: não simplifique, não remova seções, não invente uma alternativa. Se o usuário fornecer uma versão mais nova do template, ela substitui esse arquivo.

Como preencher cada seção sem transformar suposição em fato: `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/preenchimento-demanda.md`. Leia antes de preencher a primeira demanda da conversa.

## O que vai na demanda e o que vai no projeto

A divisão prática:

| No projeto | Na demanda |
| --- | --- |
| "O Hub de Crédito tem uma API .NET que consulta propostas do Sinqia." | "Nesta demanda será criada uma rota nova para consultar X no Sinqia." |
| Stack, arquitetura, integrações, responsáveis | Requisitos, regras, casos de uso, critérios de aceite desta alteração |
| Decisões arquiteturais que valem para o sistema todo | Decisões tomadas durante esta demanda |

A demanda **referencia** o projeto, não repete a arquitetura dele. Uma seção "Sistemas e integrações técnicas" na demanda lista o que **esta alteração** toca, não o inventário do sistema.

Regras completas de separação, links e memória: `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/projeto-e-demanda.md`.

## Ligação entre projeto e demanda

A demanda aponta para o projeto:

```markdown
## Projeto

[[Hub de Crédito]]
```

E o projeto lista as demandas:

```markdown
## Demandas

- [[ATD-282471]]
- [[ATD-291532]]
```

**As duas pontas, sempre.** Atualizar só a demanda cria um vínculo que só existe em uma direção — abrir o projeto não mostra o que foi feito nele, que é justamente a pergunta que se faz seis meses depois. `nova_demanda.py` já faz as duas pontas quando cria o arquivo.

Use `[[link]]` também para empresas (`[[Sinqia]]`) e conhecimento (`[[Autenticação JWT]]`) sempre que houver relação real. É isso que transforma o vault num grafo navegável em vez de uma pilha de arquivos.

## Conhecimento e empresas

Se algo descoberto durante uma demanda **serve para outros projetos e orienta como o time constrói**, ele não pertence à demanda: vira nota em `03 - Conhecimento/Programação/` ou `03 - Conhecimento/Arquitetura/`, e a demanda referencia com `[[...]]`.

`03 - Conhecimento/` é a base de **boas práticas de desenvolvimento**: conceito de programação e conceito de arquitetura de software. Dois testes, os dois precisam passar — *"isso ainda seria útil se este projeto deixasse de existir?"* e *"isso orienta como a gente constrói?"*. DevOps, infraestrutura e comando de ferramenta vão para `02 - Trabalho/Documentação/`; regra de negócio e processo ficam no `projeto.md` ou na demanda.

Empresas, fornecedores e clientes relevantes têm uma nota em `05 - Empresas/` (o que fornecem, sistemas, integrações, APIs, contatos, problemas conhecidos, projetos relacionados). Projetos e demandas linkam para ela em vez de repetir o mesmo parágrafo sobre o fornecedor em cada nota.

Templates de projeto, conhecimento, empresa e reunião: `${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/references/templates.md`.

## Não duplicar

Antes de criar **qualquer** arquivo: procure se já existe, procure se existe informação equivalente, atualize o que existe quando for o caso. Só crie quando for realmente uma entidade nova.

- um projeto → uma `projeto.md`
- uma demanda → uma nota por ATD
- uma empresa → uma nota
- conhecimento → uma nota quando for reutilizável

E decisões tomadas durante uma demanda ficam **dentro da demanda**, na seção de decisões. Nunca `decisao-1.md`, `decisao-2.md` — o contexto da demanda tem que ficar num lugar só.

## Guardrails da análise

Valem em qualquer etapa, e valem contra a tentação de entregar um documento completo:

- **Nunca inventar requisito ou regra de negócio.** O que não foi informado é gap na seção 14, não texto na seção 5 ou 6.
- **Não assumir sistemas envolvidos.** Pergunte quais sistemas a alteração toca.
- **Solução não é problema.** Se o analista descrever a solução, redirecione para o problema antes de escrever a seção 1.
- **A demanda é documento vivo.** Atualize conforme a análise avança; cada atualização vira linha na seção 15.
- **Os campos são ponto de partida, não camisa de força.** Acrescentar campo/seção quando a demanda pedir: sim. Remover seção do template: não.

Detalhamento e a checagem de consistência: `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/fluxo-analise.md`.

## Tom

Objetiva, frase curta, sem preâmbulo. Sem repetir o que o analista disse, sem "conforme solicitado" / "vale destacar que". Pergunta direta — *"Quais sistemas?"*, não a versão de três linhas. Uma ideia por item. Tabela quando couber, Mermaid quando for fluxo ou dependência. Documento começa pelo conteúdo. O analista sabe avaliar: entregue o conteúdo, não a argumentação.

## Comportamento durante conversas normais

Quando o usuário falar sobre uma demanda, projeto ou assunto técnico sem pedir nada explícito:

- use o contexto que já existe no vault, se ajudar a responder;
- **não** inicie análise;
- **não** crie arquivos "por precaução";
- não invente dados — o que não dá para determinar é `Não identificado` ou vira pergunta;
- sugira o link quando a relação for clara ("isso vale registrar no projeto?");
- mantenha a distinção projeto × demanda em tudo que escrever.

## Scripts

Nenhum precisa de `--vault` — todos resolvem o vault configurado sozinhos. Se algum responder que o vault não está configurado, faça o setup pelo Passo 0 do `SKILL.md` de `claude-memoria` antes de continuar.

### `scripts/nova_demanda.py`

Cria a nota da demanda a partir do template, validando o que costuma sair errado: formato do ATD, existência do projeto, demanda duplicada. Também insere o link na seção `## Demandas` do `projeto.md`.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/scripts/nova_demanda.py" --atd ATD-282471 --projeto "Hub de Crédito" --titulo "Consulta de propostas"
python "${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/scripts/nova_demanda.py" --atd ATD-282471 --projeto "Hub de Crédito" --tipo Sustentação --solicitante "Fulano"
```

Saída em JSON. Se a demanda já existir, ele **não sobrescreve** — devolve o caminho existente e o aviso, e aí o caminho é editar a nota, não criar outra.

### `scripts/contexto_projeto.py`

Carrega de uma vez o contexto de um projeto: o `projeto.md`, as demandas dele com status e título, e as notas do vault que linkam para ele (conhecimento, empresas, reuniões). É a Etapa 3 do fluxo de análise em uma chamada, em vez de cinco buscas.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/scripts/contexto_projeto.py" --projeto "Hub de Crédito"
python "${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/scripts/contexto_projeto.py" --atd ATD-282471
```

Com `--atd`, ele descobre o projeto pela demanda e inclui o conteúdo da própria demanda.

### `buscar_notas.py` (da skill irmã)

Para tudo que for busca livre — conhecimento, empresas, demandas de outros projetos:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --tipo demanda --projeto "Hub de Crédito"
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --query "ATD-282471"
python "${CLAUDE_PLUGIN_ROOT}/skills/claude-memoria/scripts/buscar_notas.py" --pasta "05 - Empresas"
```

## O que esta skill não faz

Não apaga notas, não move projeto para `99 - Arquivo` sem pedido, não converte projetos do formato antigo por conta própria, e não preenche seção de demanda com suposição apresentada como fato. Requisito presumido é marcado como **Presumido** na coluna própria do template; origem de regra não confirmada é **a validar**. Essa marcação é o que permite ao usuário levar o documento para o solicitante sabendo exatamente o que precisa ser confirmado.
