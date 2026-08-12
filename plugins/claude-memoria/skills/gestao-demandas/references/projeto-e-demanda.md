# Projeto, demanda e conhecimento — regras de organização

Cada regra aqui existe para evitar um jeito específico da base degradar. Vale entender o motivo, não só seguir a lista.

## 1. Demanda nunca é projeto

Um projeto é um sistema que existe e continua existindo depois que a demanda acaba. Uma demanda é uma alteração com começo e fim.

O sintoma de ter errado isso: `01 - Projetos/Nova consulta de propostas/` — isso não é um sistema, é uma mudança no Hub de Crédito. Vira `01 - Projetos/Hub de Crédito/demandas/ATD-282471.md`.

Consequência de errar: a arquitetura do sistema passa a existir em cinco cópias, uma por "projeto" que na verdade era demanda, e cada uma envelhece por conta própria. Seis meses depois ninguém sabe qual está certa.

## 2. Toda demanda tem número de atendimento, e ele nunca é inventado

`ATD-000000`, seis dígitos. É o nome do arquivo e o campo `atd` do frontmatter.

Sem número, peça. Um número inventado ou um placeholder `ATD-000000` vira o identificador real em questão de minutos — alguém copia para um commit, uma mensagem, um card — e aí não dá mais para cruzar com o Agidesk.

## 3. Contexto permanente no projeto, contexto da alteração na demanda

| Vai no `projeto.md` | Vai na demanda |
| --- | --- |
| "A API é .NET 8 e consulta propostas no Sinqia via REST." | "Será criado o endpoint `GET /propostas/{id}/parcelas`." |
| Bancos, filas, integrações, ambientes, responsáveis | Requisitos, regras, casos de uso e critérios **desta** alteração |
| Decisões arquiteturais do sistema | Decisões tomadas durante esta demanda |
| Regras de negócio permanentes do domínio | Regras novas ou alteradas por esta demanda |

Teste rápido: *"isso continua verdade depois que a demanda for para produção e for esquecida?"*. Se sim, é do projeto.

A demanda **referencia** o projeto. Não copie a arquitetura para dentro dela — a seção 10 do template lista só o que esta alteração toca.

O caminho inverso também vale: se durante a demanda você descobriu algo permanente sobre o sistema ("na verdade a fila é Kafka, não RabbitMQ"), isso sobe para o `projeto.md`, não fica enterrado numa demanda que ninguém vai reler.

## 4. Um projeto, uma nota principal

`01 - Projetos/<Projeto>/projeto.md`. Nunca `Hub de Crédito - Arquitetura.md`, `Hub de Crédito - APIs.md`, `Hub de Crédito - Integrações.md`. Tudo isso é **seção** dentro do `projeto.md`.

Antes de criar um projeto, procure. `buscar_notas.py --pasta "01 - Projetos"`. Nome parecido não é nome diferente — pergunte.

## 5. O vínculo é sempre nas duas pontas

Demanda → projeto (`## Projeto` com `[[Nome do Projeto]]`) **e** projeto → demanda (item em `## Demandas`).

Só uma ponta parece suficiente na hora, mas a pergunta que se faz depois é "o que já mexeram nesse sistema?" — e essa pergunta se responde abrindo o projeto. Sem a lista lá, a resposta exige varrer o vault inteiro.

## 6. Decisão de demanda fica dentro da demanda

Na seção `## Decisões` da própria nota:

```markdown
## Decisões

- A API será criada no serviço X, não no Y — o Y não tem acesso à base de propostas.
- A consulta usa o endpoint de parcelas do Sinqia em vez da view local (dado desatualizado).
```

Nunca `decisao-1.md`, `decisao-2.md`, `decisao-3.md`. O contexto de uma demanda tem que caber num arquivo só, senão reconstruir o raciocínio depois exige abrir sete notas na ordem certa.

Decisão que vale para o sistema inteiro (não só para esta demanda) sobe para `## Decisões` do `projeto.md`, com a data.

## 7. Conhecimento reutilizável sai da demanda

Teste: *"isso ainda seria útil se este projeto deixasse de existir?"*

- "Como configurar autenticação JWT num serviço .NET" → sim → `03 - Conhecimento/.NET/Configuração de autenticação JWT.md`, e a demanda linka `[[Configuração de autenticação JWT]]`.
- "O endpoint de propostas exige o header X-Origem" → não, é do Hub de Crédito → vai para o `projeto.md`.
- "Nesta demanda decidimos usar cache de 5 minutos" → não → fica na demanda.

Conhecimento preso dentro de uma demanda é conhecimento perdido: ninguém procura solução de JWT dentro da ATD-282471.

## 8. Empresa é nota própria, não parágrafo repetido

`05 - Empresas/Sinqia.md` guarda o que a empresa fornece, sistemas, integrações, APIs, contatos, problemas conhecidos e projetos relacionados. Projetos e demandas linkam `[[Sinqia]]`.

Sem isso, "o Sinqia tem limite de 100 req/min" acaba escrito em quatro demandas, três delas com o número errado.

## 9. Não duplicar — procurar antes de criar

Antes de qualquer arquivo novo: verifique se já existe; verifique se existe informação equivalente com outro nome; atualize o existente quando for o caso; só crie quando for entidade nova de verdade.

- um projeto → uma `projeto.md`
- uma demanda → uma nota por ATD
- uma empresa → uma nota
- conhecimento → uma nota por assunto reutilizável

## 10. O que é permanente vira nota; o que é do momento, não

- "Estou verificando essa API agora" → temporário, não registre.
- "O Hub de Crédito usa a API X para consultar propostas" → permanente → `projeto.md`.
- "Para configurar o serviço .NET assim, precisa daquela config" → reutilizável → `03 - Conhecimento/.NET/`.

Registrar o temporário polui a base com frases que ninguém consegue interpretar duas semanas depois.

## 11. Sem classificação clara → `00 - Inbox/`

Não force uma pasta e não invente categoria nova de primeiro nível. `00 - Inbox/AAAA-MM-DD - descrição curta.md` e triagem depois.

Errar por cautela aqui é barato. Uma nota mal classificada é cara: ninguém mais a encontra, e ela é redigitada do zero meses depois.

## 12. Encerrado vai para `99 - Arquivo/`, não para a lixeira

Projeto descontinuado, demanda antiga, documentação obsoleta: mova, não apague. Informação histórica só é excluída com autorização explícita na conversa.

Uma demanda entregue **não** é motivo para arquivar — ela é a resposta para "por que isso funciona assim?". Arquive o projeto inteiro quando o sistema sair do ar, com as demandas junto.
