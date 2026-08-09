# Regras de organização do Cérebro

Cada regra aqui existe para evitar um jeito específico do vault degradar com o tempo. Vale entender o motivo, não só seguir a lista.

## 1. Nunca criar uma nota de projeto sem antes procurar se já existe

Sem essa checagem, é fácil acabar com `Sistema Financeiro.md`, `Gerenciamento Financeiro.md` e `Carteira de Investimentos.md` todas descrevendo a mesma coisa. Rode `buscar_notas.py --pasta "01 - Projetos"` (ou filtrando por `--tipo projeto`) antes de criar. Se o nome for parecido mas não idêntico ao que o Victor mencionou, pergunte antes de assumir que é outro projeto — a menos que a config diga para não confirmar.

## 2. Pesquisar entidades semelhantes antes de criar qualquer nota nova

Vale para pessoas, empresas e conceitos também, não só projetos. Uma pessoa mencionada duas vezes com grafias levemente diferentes do nome não deveria virar duas notas.

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

Uma reunião linka para o projeto discutido, uma decisão linka para o projeto ao qual pertence, uma pessoa mencionada em uma reunião pode linkar para a nota dela em `04 - Pessoas`. Isso é o que transforma o vault de uma pilha de arquivos em um grafo navegável dentro do próprio Obsidian.
