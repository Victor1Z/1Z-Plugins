# Estrutura do vault

```text
Vault/
│
├── 00 - Inbox/                     ← qualquer coisa sem classificação clara ainda
│
├── 01 - Projetos/
│   └── <Projeto>/
│       ├── projeto.md              ← contexto permanente do sistema
│       └── demandas/
│           ├── ATD-282471.md       ← uma nota por atendimento
│           └── ATD-291532.md
│
├── 02 - Trabalho/
│   ├── Reuniões/
│   └── Documentação/
│
├── 03 - Conhecimento/              ← boas práticas de desenvolvimento do time
│   ├── Programação/               ← conceitos e padrões de código
│   ├── Arquitetura/               ← conceitos de arquitetura de software
│   └── Outros/
│
├── 05 - Empresas/                  ← uma nota por empresa/fornecedor/cliente
│
├── 99 - Arquivo/                   ← encerrado, fora do fluxo ativo
│
└── _config/
    └── config.md                   ← comportamento do skill
```

Essa é a organização **definitiva**. Não crie categorias ou pastas de primeiro nível novas: o que não se encaixa claramente em nenhuma delas vai para `00 - Inbox/` e é triado depois. Uma pasta inventada para um caso isolado é como a estrutura deixa de ser navegável — a numeração existe justamente para que o conjunto seja pequeno e estável.

O `04` e o intervalo `06`–`98` estão livres de propósito. A numeração não é sequencial porque não precisa ser; renumerar pastas depois quebraria todo link já escrito.

## O que vai em cada pasta

**00 - Inbox** — o que continuou sem classificação **depois** de perguntar ao usuário (ver `regras.md`, regra 8). Nome do arquivo: `AAAA-MM-DD - descrição curta.md`. É normal ter itens aqui esperando triagem — não force uma classificação errada só para não deixar nada no Inbox. Errar por cautela é barato; uma nota mal classificada ninguém acha depois. O que o Inbox não é: atalho para evitar a pergunta.

**01 - Projetos** — uma pasta por projeto (um sistema, aplicação ou solução que **já existe e é funcional**), com `projeto.md` para o contexto permanente e `demandas/` para as alterações. Nunca `Hub de Crédito - APIs.md` ao lado de `Hub de Crédito - Arquitetura.md`: isso são seções dentro do `projeto.md`.

Projeto e demanda são coisas diferentes, e a distinção é o eixo da base inteira — ela é detalhada na skill irmã `gestao-demandas`, em `references/projeto-e-demanda.md`.

*Formato antigo:* notas de projeto como arquivo solto (`01 - Projetos/Hub de Crédito.md`) continuam válidas e a busca continua achando. Converter para o formato pasta é bem-vindo, mas nunca automático — ofereça quando a primeira demanda daquele projeto aparecer.

**02 - Trabalho** — reuniões (`Reuniões/AAAA-MM-DD - assunto.md`) e documentação de processo que não pertence a um projeto único. Note que aqui **não** há mais `Tarefas/`, `Decisões/`, `Problemas/` nem `Incidentes/`: decisão de uma alteração fica na demanda, decisão de arquitetura fica no `projeto.md`, e incidente ligado a um sistema é uma demanda tipo Sustentação. Pastas desse tipo que já existam no seu vault continuam funcionando — a estrutura acima é o que passa a ser criado e recomendado.

**03 - Conhecimento** — as **boas práticas de desenvolvimento adotadas pelo time**, que servem de base ao construir funcionalidade nova. Duas naturezas, uma subpasta cada:

| Subpasta | O que vai | Exemplos |
| --- | --- | --- |
| `Programação/` | conceitos e padrões de código: como se escreve, nomeia, testa e estrutura código aqui | tratamento de erro, padrão de nomenclatura, injeção de dependência, o que exige teste |
| `Arquitetura/` | conceitos de arquitetura de software: como as peças se organizam e conversam | camadas, contratos de API, padrão de integração entre serviços, idempotência, quando quebrar um serviço |
| `Outros/` | boa prática de desenvolvimento que não é claramente nenhuma das duas | escape, não depósito |

Dois testes, os dois precisam passar:

1. *"isso ainda seria útil se aquele projeto deixasse de existir?"* — se não, é do `projeto.md` ou da demanda.
2. *"isso orienta como a gente constrói?"* — se não, não é conhecimento aqui.

**O que não entra:** DevOps, infraestrutura, pipeline, configuração de ambiente e comando útil de ferramenta (`02 - Trabalho/Documentação/`); regra de negócio, processo e domínio (`projeto.md` ou a demanda); nota de "como resolvi este caso" sem prática generalizável (fica na demanda).

*Subpastas antigas.* Vaults criados antes desta definição têm `SAP/`, `.NET/`, `React/`, `Git/` e `DevOps/`. Elas continuam funcionando e a busca continua achando. Quando encontrar uma nota nelas durante uma tarefa, **ofereça** mover para a subpasta certa (ou para `02 - Trabalho/Documentação/`, no caso de DevOps) — nunca mova por conta própria. Tecnologia agora é tag (`#dotnet`, `#react`, `#sap`), não pasta: a mesma boa prática costuma valer em mais de um stack.

**05 - Empresas** — empresa, fornecedor ou cliente relevante: o que fornece, sistemas, integrações, APIs, contatos, problemas conhecidos, projetos relacionados. Projetos e demandas linkam `[[Sinqia]]` em vez de repetir o mesmo parágrafo sobre o fornecedor em cada nota. Contato de pessoa vinculado a um fornecedor mora aqui, na nota da empresa.

**99 - Arquivo** — o que saiu do fluxo ativo: projeto descontinuado, documentação obsoleta, histórico. Mover para cá em vez de apagar preserva o histórico (ver `regras.md`). Uma demanda **entregue** não é motivo para arquivar: ela é a resposta para "por que isso funciona assim?".

**_config** — configuração do próprio skill, não conteúdo. Não deveria aparecer em buscas de contexto (`buscar_notas.py` já ignora essa pasta).
