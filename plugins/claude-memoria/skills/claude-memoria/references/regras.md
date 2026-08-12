# Regras de organização do Claude Memória

Cada regra aqui existe para evitar um jeito específico do vault degradar com o tempo. Vale entender o motivo, não só seguir a lista.

## 1. Nunca criar uma nota de projeto sem antes procurar se já existe

Sem essa checagem, é fácil acabar com `Sistema Financeiro/`, `Gerenciamento Financeiro/` e `Carteira de Investimentos/` todas descrevendo a mesma coisa. Rode `buscar_notas.py --pasta "01 - Projetos"` (ou filtrando por `--tipo projeto`) antes de criar. Se o nome for parecido mas não idêntico ao que o usuário mencionou, pergunte antes de assumir que é outro projeto — a menos que a config diga para não confirmar.

Um projeto é uma pasta com `projeto.md` dentro (`01 - Projetos/<Projeto>/projeto.md`). Notas de projeto como arquivo solto são do formato antigo: continuam válidas, mas não crie novas assim.

## 2. Pesquisar entidades semelhantes antes de criar qualquer nota nova

Vale para empresas e assuntos de conhecimento também, não só projetos. Uma empresa mencionada duas vezes com grafias levemente diferentes do nome não deveria virar duas notas.

## 3. Gatilhos explícitos de persistência sempre são respeitados

Se o usuário disser "se lembre disso" (ou uma variação clara da mesma intenção), a informação é registrada — não é opcional nem depende de você achar que é relevante o suficiente.

## 4. Não duplicar informação existente

Se a informação já está registrada e o que o usuário disse é só uma reafirmação, não crie uma entrada nova redundante — no máximo atualize a data de última confirmação, se isso importar.

## 5. Preservar histórico ao atualizar uma decisão

Quando algo muda (ex: `.NET 9` vira `.NET 10`), não apague o registro anterior. Adicione ao histórico com a data, e marque o status do que foi substituído. Isso é o que permite responder "por que a gente tinha decidido X antes" meses depois.

## 6. Registrar a data do evento, não só a data em que você está escrevendo

Se o usuário descreve algo que aconteceu ontem ou na semana passada, `data_evento` reflete isso — `data_criacao`/`data_atualizacao` refletem quando a nota foi escrita/editada. As duas coisas divergem com frequência e ambas importam.

## 7. Distinguir as três datas

`data_criacao` (quando a nota nasceu), `data_evento` (quando o fato aconteceu, se aplicável) e `data_atualizacao` (última edição). Nem toda nota precisa das três — conhecimento técnico geral normalmente não tem `data_evento`.

## 8. Na dúvida de classificação, perguntar primeiro; Inbox é o destino de quem perguntou e continuou sem resposta

Quando não dá para decidir *o que* a informação é — que tipo de nota, de que projeto, se é o mesmo assunto de uma nota que já existe —, a primeira saída é perguntar ao usuário, numa mensagem só, com as opções concretas que a busca já levantou. Quem pediu tem o contexto que falta e responde em dez segundos; adivinhar custa uma nota que ninguém acha depois.

O Inbox (`00 - Inbox/AAAA-MM-DD - descrição curta.md`) entra quando a pergunta não resolveu: ele não sabe ainda, não quis classificar agora, ou pediu para só guardar. Aí é melhor ter algo no Inbox esperando triagem do que uma nota mal classificada. Errar por excesso de cautela é barato; errar classificando errado é caro.

O que não vale é usar o Inbox como atalho para não perguntar — o roteiro de quando e como perguntar está no `SKILL.md`, em "Perguntar antes de classificar".

## 9. Não apagar informação histórica sem autorização explícita na conversa

Isso vale mesmo que `confirm_delete` esteja `false` na config para outras ações — apagar histórico é sempre uma decisão consciente do usuário, nunca automática. "Mover para 99 - Arquivo" é quase sempre a opção certa em vez de apagar.

## 10. Usar links `[[Nota]]` para relacionar entidades

Uma reunião linka para o projeto discutido, uma demanda linka para o projeto ao qual pertence e para o conhecimento que usou, um fornecedor citado linka para a nota dele em `05 - Empresas`. Isso é o que transforma o vault de uma pilha de arquivos em um grafo navegável dentro do próprio Obsidian.

Vínculo entre projeto e demanda é **nas duas pontas**: a demanda aponta para o projeto e o projeto lista a demanda. Só uma direção parece suficiente na hora, mas "o que já mexeram nesse sistema?" se responde abrindo o projeto.

## 11. Projeto, demanda e conhecimento são três coisas diferentes

Projeto é onde o sistema existe; demanda é o que será alterado nele; conhecimento é o que se reutiliza em outros contextos. Nunca tratar uma demanda como projeto independente, nunca criar nota de projeto nova por demanda.

As regras completas dessa separação — incluindo formato obrigatório do ATD, onde cada informação mora e por quê — estão na skill irmã: `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/projeto-e-demanda.md`.

## 12. `03 - Conhecimento/` é boa prática de desenvolvimento — não é depósito de tudo que é técnico

A pasta guarda o que o time adotou como padrão para **construir**: conceito de programação (`Programação/`) e conceito de arquitetura de software (`Arquitetura/`). Os dois testes precisam passar — *"isso ainda seria útil se aquele projeto deixasse de existir?"* e *"isso orienta como a gente constrói?"*.

Fora dali: DevOps, infraestrutura, pipeline e comando de ferramenta vão para `02 - Trabalho/Documentação/`; regra de negócio, processo e domínio ficam no `projeto.md` ou na demanda.

O motivo é uso, não estética: essa pasta é lida antes de construir funcionalidade nova. Misturar receita de pipeline e regra de negócio ali faz o time parar de abrir a pasta, e aí ela deixa de ser base de nada.

Subpasta antiga (`SAP/`, `.NET/`, `React/`, `Git/`, `DevOps/`) continua funcionando. Ao encontrar nota nelas, **ofereça** mover para a subpasta certa — ou para `02 - Trabalho/Documentação/`, no caso de DevOps. Nunca mova por conta própria. Tecnologia virou tag/campo `tecnologia`, não pasta: a mesma prática costuma valer em mais de um stack.

## 13. Análise de demanda só começa com pedido explícito

`auto_analysis` é `false` e deve continuar assim. Mencionar uma demanda ou um número ATD é informação, não pedido de levantamento. Os gatilhos que valem estão em `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/fluxo-analise.md`.
