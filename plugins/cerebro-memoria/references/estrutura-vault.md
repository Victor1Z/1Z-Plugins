# Estrutura do vault Cérebro

```
Cerebro/
│
├── 00 - Inbox/                  ← qualquer coisa sem classificação clara ainda
│
├── 01 - Projetos/                ← uma nota por projeto (não uma por decisão)
│
├── 02 - Trabalho/
│   ├── Reuniões/
│   ├── Tarefas/
│   ├── Decisões/
│   ├── Problemas/
│   ├── Incidentes/
│   └── Documentação/
│
├── 03 - Conhecimento/            ← conhecimento técnico não ligado a um projeto específico
│   ├── Programação/
│   ├── SAP/
│   ├── .NET/
│   ├── React/
│   ├── Git/
│   ├── DevOps/
│   └── Outros/
│
├── 04 - Pessoas/                 ← uma nota por pessoa relevante (colegas, contatos)
│
├── 05 - Empresas/                ← uma nota por empresa/fornecedor/cliente relevante
│
├── 06 - Conceitos/                ← conceitos que merecem existir como nota isolada e linkável
│
├── 07 - Memórias/                 ← registros pessoais que não são "trabalho" nem "conhecimento"
│
├── 99 - Arquivo/                  ← projetos/notas encerrados, fora do fluxo ativo
│
└── _config/
    └── config.md                  ← comportamento do skill (auto_context, auto_memory, etc.)
```

## O que vai em cada pasta

**00 - Inbox** — qualquer coisa que você não tem certeza de onde classificar: projeto ambíguo, pessoa não identificada, tarefa solta sem contexto suficiente. Nome do arquivo: `AAAA-MM-DD - descrição curta.md`. É normal ter itens aqui esperando o Victor organizar depois — não force uma classificação errada só para não deixar nada no Inbox.

**01 - Projetos** — uma nota por projeto, com seções internas (Visão Geral, Stack, Arquitetura, Decisões, Requisitos, Problemas, Tarefas, Histórico) que crescem ao longo do tempo. Ver `templates.md`.

**02 - Trabalho** — o dia a dia: reuniões, tarefas, decisões técnicas específicas (quando têm peso próprio, além do que já está resumido na nota do projeto), problemas e incidentes, documentação de processos.

**03 - Conhecimento** — coisas que você aprendeu ou documentou que não são sobre um projeto específico, e que valem para consulta futura independente do que estiver rodando no momento (ex: como funciona um Status 53 de IDoc, um padrão de arquitetura, um comando útil).

**04 - Pessoas / 05 - Empresas** — quando um nome de pessoa ou empresa aparece com frequência ou tem contexto que vale preservar (cargo, histórico de interações, combinados feitos), vira uma nota própria linkável com `[[Nome]]`.

**06 - Conceitos** — definições e explicações que fazem sentido existir isoladas e serem linkadas de várias notas diferentes, em vez de repetidas em cada uma.

**07 - Memórias** — categoria "coringa" para registros pessoais que não são nem trabalho nem conhecimento técnico, mas que o Victor quer preservar.

**99 - Arquivo** — projetos ou notas que saíram do fluxo ativo. Mover para cá em vez de apagar preserva o histórico (ver regra de não apagar sem autorização em `regras.md`).

**_config** — não é conteúdo do Victor, é configuração do próprio skill. Não deveria aparecer em buscas de contexto normais.
