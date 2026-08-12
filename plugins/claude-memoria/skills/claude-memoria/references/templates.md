# Templates de nota

Os nomes de campo do frontmatter abaixo (`tipo`, `projeto`, `tags`, `status`, `data`, `data_evento`, `data_criacao`, `data_atualizacao`) são os que `scripts/buscar_notas.py` reconhece para filtrar. Mantenha esses nomes exatos ao criar ou editar notas, mesmo que o conteúdo do resto da nota varie.

O template de **demanda** não está aqui: ele é grande e tem estrutura própria, em `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/demanda.template.md` (com o guia de preenchimento em `preenchimento-demanda.md`, na mesma pasta).

## Projeto — `01 - Projetos/<Projeto>/projeto.md`

Um projeto é um sistema que **já existe e é funcional**. Esta nota guarda o contexto permanente dele; o que vai ser alterado mora nas demandas.

```markdown
---
tipo: projeto
status: ativo
data_criacao: AAAA-MM-DD
data_atualizacao: AAAA-MM-DD
tags:
  - projeto
---

# Nome do Projeto

## Visão Geral

Objetivo e finalidade do sistema.

## Stack

## Arquitetura

## Sistemas e integrações

APIs, bancos, filas, ambientes. Fornecedor envolvido linka para [[Empresa]].

## Responsáveis

## Regras de negócio

Regras permanentes do domínio — não as que uma demanda específica introduz.

## Decisões

Decisões arquiteturais que valem para o sistema todo, com data.

## Links e documentação

## Demandas

- [[ATD-000000]]

## Histórico

### AAAA-MM-DD
```

A seção `## Demandas` é obrigatória e tem que ficar em dia: sem ela, "o que já mexeram nesse sistema?" só se responde varrendo o vault. `nova_demanda.py` mantém essa lista sozinho.

## Reunião — `02 - Trabalho/Reuniões/AAAA-MM-DD - assunto.md`

```markdown
---
tipo: reuniao
data: AAAA-MM-DD
hora_inicio:
hora_fim:
projeto:
participantes:
  -
local:
origem: conversa-claude
status: concluida
tags:
  - reuniao
---

# Reunião - Assunto

## Objetivo

## Discussões

## Decisões

## Pendências

## Problemas

## Próximos passos

## Relacionamentos

- Projeto: [[Nome do Projeto]]
- Demanda: [[ATD-000000]]
```

## Conhecimento técnico — `03 - Conhecimento/<Área>/Título.md`

Use quando a informação **não depende** de um projeto específico. O teste: *"isso ainda seria útil se aquele projeto deixasse de existir?"*.

```markdown
---
tipo: conhecimento
area:
tecnologia:
tags:
  -
---

# Título

## Significado

## Quando ocorre / quando se aplica

## Problemas comuns

## Exemplos

## Referências
```

## Empresa — `05 - Empresas/Nome.md`

```markdown
---
tipo: empresa
status: ativa
data_criacao: AAAA-MM-DD
data_atualizacao: AAAA-MM-DD
tags:
  - empresa
---

# Nome

## O que fornece

## Sistemas e produtos

## Integrações

APIs, protocolos, limites, credenciais (onde ficam — nunca o valor delas).

## Contatos

## Problemas conhecidos

## Documentação

## Projetos relacionados

- [[Nome do Projeto]]
```

Uma nota por empresa. Sem isso, "o Sinqia tem limite de 100 req/min" acaba escrito em quatro demandas, três delas com o número errado.

## Documentação de processo — `02 - Trabalho/Documentação/Título.md`

Para processo, procedimento ou registro de trabalho que não pertence a um projeto único (inclui incidente sem sistema identificado — incidente ligado a um projeto é uma demanda tipo Sustentação).

```markdown
---
tipo: documentacao
data_criacao: AAAA-MM-DD
data_atualizacao: AAAA-MM-DD
projeto:
tags:
  -
---

# Título

## Contexto

## Procedimento

## Observações
```

## Item de Inbox — `00 - Inbox/AAAA-MM-DD - descrição curta.md`

Sem frontmatter rígido é aceitável aqui — o objetivo é capturar rápido, não classificar perfeitamente. Mesmo assim, inclua `origem` e a data se souber, para facilitar a triagem depois:

```markdown
---
tipo: inbox
data_criacao: AAAA-MM-DD
origem: conversa-claude
---

# Descrição curta

Conteúdo capturado, o mais fiel possível ao que o Victor disse.
```

## Tipos que não têm mais template próprio

`decisao_tecnica` e `incidente` existiam como nota isolada em `02 - Trabalho/Decisões/` e `02 - Trabalho/Incidentes/`. Notas antigas desses tipos continuam válidas e a busca continua achando (`--tipo decisao_tecnica`), mas notas novas seguem outro caminho:

- decisão de uma alteração → seção `## Decisões` da **demanda**;
- decisão que vale para o sistema todo → seção `## Decisões` do **`projeto.md`**, com data;
- incidente num sistema conhecido → **demanda** tipo Sustentação, com o ATD do atendimento;
- incidente sem sistema identificado → `02 - Trabalho/Documentação/`.

O motivo é o da regra 6 de `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/projeto-e-demanda.md`: contexto espalhado em sete arquivos não se reconstrói depois.
