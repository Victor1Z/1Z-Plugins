# Fluxo de análise de uma demanda

## Quando começar

Uma análise começa **só** com pedido explícito. Duas formas valem:

1. a skill foi chamada diretamente (`/claude-memoria:gestao-demandas`);
2. o Victor usou uma expressão equivalente a "iniciar uma análise":

- "iniciar uma análise" / "iniciar análise" / "inicie a análise"
- "começar análise" / "comece a análise"
- "vamos analisar essa demanda" / "analise essa demanda"
- "quero analisar essa ATD"
- "iniciar o levantamento" / "iniciar levantamento da demanda"

Variações naturais dessas frases também valem — "bora levantar essa ATD", "monta a análise da 282471", "vamos especificar isso". O que importa é a intenção de **começar o levantamento**, não a frase literal.

## Quando não começar

Falar de uma demanda não é pedir análise. Estes casos **não** disparam o fluxo:

- "Essa demanda ATD-282471 pertence ao Hub de Crédito." → informação; registre o vínculo se fizer sentido.
- "Abriram a ATD-291532 hoje." → informação.
- "O que a gente já tem sobre a ATD-282471?" → é recuperação de contexto, não análise. Busque e resuma.
- "Como funciona a integração com o Sinqia?" → é pergunta técnica. Responda com o contexto do vault.

Na dúvida entre informar e analisar, pergunte numa linha: *"quer que eu abra a análise dessa ATD ou só registro isso?"*. Uma pergunta curta custa muito menos que um documento de 15 seções que ninguém pediu.

## Etapa 1 — identificar a demanda

Localize o número ATD e valide o formato `ATD-000000` (prefixo `ATD-`, seis dígitos).

- Sem número → **peça o número**. Não invente, não use placeholder, não crie a nota "para preencher depois".
- Formato diferente (`ATD-2824`, `282471`, `atd282471`) → confirme com o Victor qual é o número certo antes de criar qualquer arquivo. Provavelmente é só forma de escrever, mas o nome do arquivo é o identificador — errar ali quebra a rastreabilidade com o Agidesk.

## Etapa 2 — identificar o projeto

Nesta ordem de prioridade:

1. informação já na própria demanda (se a nota existe, o frontmatter `projeto` e a seção `## Projeto`);
2. informação nos projetos existentes (algum `projeto.md` já lista essa ATD?);
3. contexto que o Victor deu na conversa;
4. **perguntar**.

Não crie um projeto novo só porque a demanda ainda não está vinculada a nenhum. Um projeto criado por conveniência agora é uma nota órfã que duplica um sistema que já estava documentado com outro nome.

Se o nome do projeto for parecido mas não idêntico a um existente ("Hub Crédito" vs "Hub de Crédito"), pergunte antes de assumir que são dois.

## Etapa 3 — carregar contexto antes de analisar

Este é o passo que decide se a análise vale algo. Analisar sem ler o que já foi documentado produz uma spec que contradiz decisões já tomadas.

Uma chamada resolve a maior parte:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/scripts/contexto_projeto.py" --atd ATD-282471
```

Isso traz o `projeto.md`, as demandas irmãs e as notas que linkam para o projeto. Complemente quando fizer sentido:

- `03 - Conhecimento/` — a área técnica envolvida (SAP, .NET, React...) já tem nota sobre isso?
- `05 - Empresas/` — a demanda envolve fornecedor? Tem problema conhecido registrado?
- `02 - Trabalho/Documentação/` e `02 - Trabalho/Reuniões/` — teve reunião sobre isso?

Vale procurar por demandas anteriores parecidas: se a ATD-291532 mexeu na mesma rota há três meses, o levantamento dela já responde metade das perguntas desta.

## Etapa 4 — criar ou atualizar a nota da demanda

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/gestao-demandas/scripts/nova_demanda.py" \
  --atd ATD-282471 --projeto "Hub de Crédito" --titulo "Consulta de propostas"
```

Se a demanda **já existe**, não crie uma segunda em lugar nenhum — atualize a existente. O script se recusa a sobrescrever e devolve o caminho do arquivo; a partir daí é edição.

Ao atualizar uma demanda que já tinha conteúdo, registre a mudança na seção 15 (Histórico de revisão) com data e versão, em vez de trocar o texto em silêncio.

## Etapa 5 — conduzir a análise

Preencha o template com o que existe de fato:

- o que o Victor contou na conversa;
- o que está no `projeto.md` e nas demandas relacionadas;
- documentação técnica e notas de conhecimento;
- informação de empresa/fornecedor, quando relevante.

E marque explicitamente o que não é fato:

- requisito que você deduziu → `Presumido`;
- regra de negócio inferida do comportamento atual → origem `a validar`;
- o que não deu para determinar → `Não identificado`, ou vira item da seção 14 (Dúvidas e gaps em aberto).

**Trabalhe como co-analista, não como gerador de documento.** Faça as perguntas que faltam em vez de preencher tudo com o palpite mais plausível — um campo preenchido com suposição apresentada como fato é pior que um campo vazio, porque ninguém vai revisá-lo.

No fim, confirme numa ou duas linhas o que foi criado/atualizado, onde, e o que ficou em aberto. Se a análise gerou conhecimento reutilizável, ofereça extrair para `03 - Conhecimento/` e linkar de volta.

## Checagem final

Antes de considerar a análise entregue:

- [ ] Todo RF tem pelo menos um CU
- [ ] Todo CU referencia um RF
- [ ] Todo CA referencia um CU
- [ ] Casos de borda da seção 9 respondidos ou marcados `Não identificado`
- [ ] `## Projeto` linka para o projeto **e** o `projeto.md` lista esta ATD
- [ ] Seção 14 lista o que precisa ser confirmado com o solicitante
- [ ] Seção 15 tem a entrada desta revisão

Para uma revisão mais dura do documento antes de entregar, existe a skill `herval-analise:entrega-revisao` — ela roda seis verificações estruturadas em cima do que foi gerado.
