# Regras de organização do Claude Memória

Cada regra aqui existe para evitar um jeito específico do vault degradar com o tempo. Vale entender o motivo, não só seguir a lista.

## 1. Nunca criar uma nota de projeto sem antes procurar se já existe

Sem essa checagem, é fácil acabar com `Sistema Financeiro/`, `Gerenciamento Financeiro/` e `Carteira de Investimentos/` todas descrevendo a mesma coisa. Rode `buscar_notas.py --pasta "01 - Projetos"` (ou filtrando por `--tipo projeto`) antes de criar. Se o nome for parecido mas não idêntico ao que o Victor mencionou, pergunte antes de assumir que é outro projeto — a menos que a config diga para não confirmar.

Um projeto é uma pasta com `projeto.md` dentro (`01 - Projetos/<Projeto>/projeto.md`). Notas de projeto como arquivo solto são do formato antigo: continuam válidas, mas não crie novas assim.

## 2. Pesquisar entidades semelhantes antes de criar qualquer nota nova

Vale para empresas e assuntos de conhecimento também, não só projetos. Uma empresa mencionada duas vezes com grafias levemente diferentes do nome não deveria virar duas notas.

## 3. Gatilhos explícitos de persistência sempre são respeitados

Se o Victor disser "se lembre disso" (ou uma variação clara da mesma intenção), a informação é registrada — não é opcional nem depende de você achar que é relevante o suficiente.

## 4. Não duplicar informação existente

Se a informação já está registrada e o que o Victor disse é só uma reafirmação, não crie uma entrada nova redundante — no máximo atualize a data de última confirmação, se isso importar.

## 5. Preservar histórico ao atualizar uma decisão

Quando algo muda (ex: `.NET 9` vira `.NET 10`), não apague o registro anterior. Adicione ao histórico com a data, e marque o status do que foi substituído. Isso é o que permite responder "por que a gente tinha decidido X antes" meses depois.

## 6. Registrar a data do evento, não só a data em que você está escrevendo

Se o Victor descreve algo que aconteceu ontem ou na semana passada, `data_evento` reflete isso — `data_criacao`/`data_atualizacao` refletem quando a nota foi escrita/editada. As duas coisas divergem com frequência e ambas importam.

## 7. Distinguir as três datas

`data_criacao` (quando a nota nasceu), `data_evento` (quando o fato aconteceu, se aplicável) e `data_atualizacao` (última edição). Nem toda nota precisa das três — conhecimento técnico geral normalmente não tem `data_evento`.

## 8. Informação sem classificação clara vai para o Inbox, não para uma pasta "chutada"

É preferível ter algo no Inbox esperando triagem do que uma nota mal classificada que ninguém mais vai achar depois. Errar por excesso de cautela aqui é barato; errar classificando errado é caro.

## 9. Não apagar informação histórica sem autorização explícita na conversa

Isso vale mesmo que `confirm_delete` esteja `false` na config para outras ações — apagar histórico é sempre uma decisão consciente do Victor, nunca automática. "Mover para 99 - Arquivo" é quase sempre a opção certa em vez de apagar.

## 10. Usar links `[[Nota]]` para relacionar entidades

Uma reunião linka para o projeto discutido, uma demanda linka para o projeto ao qual pertence e para o conhecimento que usou, um fornecedor citado linka para a nota dele em `05 - Empresas`. Isso é o que transforma o vault de uma pilha de arquivos em um grafo navegável dentro do próprio Obsidian.

Vínculo entre projeto e demanda é **nas duas pontas**: a demanda aponta para o projeto e o projeto lista a demanda. Só uma direção parece suficiente na hora, mas "o que já mexeram nesse sistema?" se responde abrindo o projeto.

## 11. Projeto, demanda e conhecimento são três coisas diferentes

Projeto é onde o sistema existe; demanda é o que será alterado nele; conhecimento é o que se reutiliza em outros contextos. Nunca tratar uma demanda como projeto independente, nunca criar nota de projeto nova por demanda.

As regras completas dessa separação — incluindo formato obrigatório do ATD, onde cada informação mora e por quê — estão na skill irmã: `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/projeto-e-demanda.md`.

## 12. Análise de demanda só começa com pedido explícito

`auto_analysis` é `false` e deve continuar assim. Mencionar uma demanda ou um número ATD é informação, não pedido de levantamento. Os gatilhos que valem estão em `${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/references/fluxo-analise.md`.
