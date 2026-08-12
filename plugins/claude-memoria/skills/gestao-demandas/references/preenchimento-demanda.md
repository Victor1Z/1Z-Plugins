# Como preencher a nota de uma demanda

O template literal — o arquivo que `nova_demanda.py` copia e que define a estrutura obrigatória — é `demanda.template.md`, nesta mesma pasta. Leia ele para ver as 15 seções na ordem. Este documento explica **como preenchê-las** sem transformar suposição em fato.

O template é a fonte de verdade da estrutura. Não simplifique, não remova seções, não invente uma estrutura alternativa. Seção sem informação continua presente, com `Não identificado` — uma seção ausente é indistinguível de uma seção esquecida, e é exatamente o que precisa ficar visível para o Victor saber o que ainda falta levantar.

Se o Victor fornecer uma versão mais nova do template, ela substitui `demanda.template.md`.

## As três marcações que sustentam o documento

| Marcação | Onde | Significa |
| --- | --- | --- |
| `Confirmado` / `Presumido` | requisitos funcionais (seção 5) | `Confirmado` **só** quando o solicitante ou um documento disse aquilo. O que você deduziu do contexto é `Presumido`, mesmo quando parece obviamente certo. |
| origem `confirmada` / `a validar` | regras de negócio (seção 6) | Regra inferida do comportamento atual do sistema é `a validar`, não `confirmada`. |
| `Não identificado` | qualquer campo | Não deu para determinar. Melhor que branco (que parece esquecimento) e muito melhor que um palpite escrito como fato. |

Um campo preenchido com suposição apresentada como fato é pior que um campo vazio: ninguém volta para revisá-lo. É assim que uma spec chega ao desenvolvedor com uma regra de negócio que nunca existiu.

Tudo que for `Presumido`, `a validar` ou `Não identificado` deveria ter um item correspondente na seção 14 (Dúvidas e gaps em aberto). É essa seção que o Victor leva para a conversa com o solicitante.

## Rastreabilidade entre os IDs

```text
RF-01 ──> CU-01 ──> CA-01
  │         │
  │         └──> CU-02 ──> CA-02
  └──> CU-03 ──> CA-03
```

- Todo requisito funcional precisa de **pelo menos um** caso de uso.
- Todo caso de uso referencia **um** requisito (campo "Requisito relacionado").
- Todo critério de aceite referencia **um** caso de uso.

Requisito que ficou sem caso de uso é um de dois problemas: ou não era requisito (era desejo, contexto ou solução), ou falta levantamento. Nos dois casos vira item da seção 14 — não invente um caso de uso só para a tabela fechar.

## Seção por seção, o que costuma sair errado

**1. Problema** — a maioria das demandas chega já como solução ("criar um botão de exportar"). O problema é o que está atrás disso ("o time exporta manualmente e leva 2h por semana"). Se você só souber a solução, escreva-a e registre na seção 14 que o problema real não foi confirmado.

**2. Objetivo** — precisa dizer como saberemos que foi resolvido. "Melhorar o processo" não é objetivo; "reduzir o fechamento de 2h para minutos" é.

**3. Contexto atual** — como funciona **hoje**. Se a funcionalidade é nova, descreva o cenário sem ela (o que o usuário faz no lugar). Essa seção é o que impede o desenvolvedor de quebrar um fluxo que ninguém mencionou.

**4. Escopo** — "Fora do escopo" costuma ficar vazio e é a metade mais valiosa. O que o solicitante provavelmente espera mas não vai vir nesta demanda? Escreva.

**5. Requisitos** — funcional é o que o sistema faz; não-funcional é performance, segurança, volumetria. "A tela tem que ser bonita" não é requisito — ou vira critério de aceite concreto, ou vira pergunta.

**9. Casos de borda** — as seis linhas do template são fixas de propósito: são as que mais aparecem em produção e menos aparecem na conversa inicial. Responder `Não identificado` nelas é aceitável; apagar a linha não é.

**10. Sistemas e integrações** — só o que **esta** demanda toca. O inventário do sistema é do `projeto.md`. A coluna "Validado via sap-adt" existe porque objeto SAP citado de memória frequentemente não existe com aquele nome — `não` ali é um risco explícito.

**11. Fluxo** — o bloco `mermaid` renderiza direto no Obsidian. Um fluxo com três caixas e uma decisão vale mais que três parágrafos; se não houver fluxo com ramificação, apague o bloco em vez de deixar o exemplo.

**15. Histórico de revisão** — toda alteração posterior na demanda ganha uma linha aqui, com data e versão. Sem isso, "isso mudou quando?" não tem resposta.

## Seções fora do template original

`## Projeto`, `## Decisões` e `## Relacionados` não existem no template do Agidesk. Foram acrescentadas porque o vault precisa delas: o link de volta ao projeto, o lugar onde decisões param de virar arquivos soltos, e as arestas do grafo. As seções 1 a 15 são o template original, na ordem original.
