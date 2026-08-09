# Templates de nota

Os nomes de campo do frontmatter abaixo (`tipo`, `projeto`, `tags`, `status`, `data`, `data_evento`, `data_criacao`, `data_atualizacao`) são os que `scripts/buscar_notas.py` reconhece para filtrar. Mantenha esses nomes exatos ao criar ou editar notas, mesmo que o conteúdo do resto da nota varie.

## Projeto — `01 - Projetos/Nome do Projeto.md`

```markdown
---
tipo: projeto
data_criacao: AAAA-MM-DD
data_atualizacao: AAAA-MM-DD
status: ativo
tags:
  - projeto
---

# Nome do Projeto

## Visão Geral

## Stack

## Arquitetura

## Decisões

## Requisitos

## Problemas

## Tarefas

## Histórico

### AAAA-MM-DD
```

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
```

## Decisão técnica — `02 - Trabalho/Decisões/Nome da Decisão.md`

Use isso quando a decisão tem peso próprio (vale a pena consultar "por que decidimos X" isoladamente). Decisões menores viram apenas uma entrada na seção `## Decisões` da nota do projeto.

```markdown
---
tipo: decisao_tecnica
data: AAAA-MM-DD
projeto:
status: ativa
tags:
  - decisao
---

# Decisão - Nome da Decisão

## Contexto

## Decisão

## Motivo

## Alternativas consideradas

-

## Consequências

## Histórico

### AAAA-MM-DD
Status: ativa / substituída / revertida.
```

## Incidente — `02 - Trabalho/Incidentes/AAAA-MM-DD - descrição curta.md`

```markdown
---
tipo: incidente
data_inicio: AAAA-MM-DD
data_fim:
sistema:
severidade:
status:
projeto:
tags:
  - incidente
---

# Incidente - Descrição curta

## Sintoma

## Causa

## Investigação

## Solução

## Impacto

## Prevenção

## Histórico
```

## Conhecimento técnico — `03 - Conhecimento/Área/Tecnologia/Título.md`

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
