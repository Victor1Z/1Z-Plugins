---
name: marketplace-manager
description: Gerencia o marketplace de plugins do Victor no repositório 1Z Plugin. Ative sempre que a conversa envolver criar um plugin novo ("cria um plugin pra...", "quero uma skill nova pra..."), registrar/publicar um plugin existente no marketplace, corrigir metadados de plugin (nome, versão, descrição, autor), entender por que um plugin não aparece no /plugin, ou revisar/atualizar o .claude-plugin/marketplace.json. Ative também quando o pedido for "instala esse plugin" ou "atualiza o marketplace" dentro deste repositório.
---

# Marketplace Manager

## Ideia central

O `.claude-plugin/marketplace.json` é **derivado**, nunca escrito à mão. A fonte de verdade de cada plugin é o `plugins/<slug>/.claude-plugin/plugin.json` dele. O catálogo da raiz é só um índice gerado a partir desses manifestos.

Isso importa porque o erro mais comum aqui é o catálogo e o manifesto discordarem — versão bumpada num lugar e não no outro, plugin renomeado na pasta mas não no catálogo. Quando isso acontece o Claude Code instala metadado velho e o sintoma (skill que não aparece, versão que não atualiza) não aponta para a causa. Gerando o catálogo, essa classe inteira de bug some.

## Estrutura que o Claude Code espera

```text
1Z Plugin/
├── .claude-plugin/
│   └── marketplace.json              ← catálogo (GERADO — não editar à mão)
└── plugins/
    └── <slug>/
        ├── .claude-plugin/
        │   └── plugin.json           ← fonte de verdade do plugin
        └── skills/
            └── <nome-da-skill>/
                ├── SKILL.md          ← frontmatter com `name` e `description`
                ├── references/
                └── scripts/
```

Três regras que não são óbvias e quebram na prática:

- **Nunca `SKILL.md` na raiz do plugin.** Os docs dizem que a raiz funciona como fallback quando não existe `skills/`, mas nem toda superfície que lista as habilidades de um plugin instalado enumera a partir dela — o sintoma é o plugin aparecer instalado e "sem habilidades ou agentes". `skills/<slug>/SKILL.md` funciona em todas.
- **`references/` e `scripts/` vão junto do `SKILL.md`, dentro da pasta da skill.** Os caminhos que o `SKILL.md` documenta (`scripts/buscar_notas.py`) são relativos a ele. Se o `SKILL.md` desce um nível e as pastas ficam para trás, todo comando documentado aponta para o lugar errado.
- **Nada de `../` dentro do plugin.** Na instalação a pasta é copiada isolada para o cache; caminho para fora dela não existe no destino. Se dois plugins precisam do mesmo arquivo, duplique ou use symlink.

O `name:` do frontmatter também é obrigatório: sem ele o Claude Code usa o nome do diretório de instalação, que para plugin vindo de marketplace é uma string de versão que muda a cada update — a skill troca de nome sozinha.

## Fluxo: criar um plugin novo

```bash
python plugins/marketplace-manager/scripts/novo_plugin.py \
  --nome meu-plugin \
  --descricao "O que ele faz, em uma frase" \
  --com scripts references
```

O script cria a pasta a partir de `templates/`, já no layout `skills/<slug>/`, com `plugin.json` e `SKILL.md` válidos, e roda a sincronização no fim. Depois disso só falta escrever o conteúdo real do `SKILL.md`.

O `description` do frontmatter é o que decide se a skill é ativada — escreva os gatilhos reais (frases que o Victor diria), não um resumo genérico do que o plugin faz. Compare com o `cerebro-memoria`: ele lista as frases literais de guardar e de recuperar.

## Fluxo: registrar / atualizar o catálogo

```bash
# regenera .claude-plugin/marketplace.json a partir dos manifestos
python plugins/marketplace-manager/scripts/sincronizar_marketplace.py

# só verifica, sem escrever (útil antes de commitar)
python plugins/marketplace-manager/scripts/sincronizar_marketplace.py --check
```

A sincronização preserva o que é do catálogo e não do manifesto: `name` e `owner` do marketplace, e por plugin os campos `category`, `tags`, `strict` e um `source` customizado, se você tiver escrito algum. Todo o resto (`description`, `version`, `author`, `keywords`, `displayName`) é sobrescrito pelo `plugin.json`.

Se o script reclamar de um plugin, ele não entra no catálogo — a mensagem diz qual campo está errado. Um plugin sem componente algum (sem `SKILL.md`, sem `skills/`, sem `agents/`, sem `commands/`, sem `hooks/`) instala mas não faz nada, então isso também vira erro.

## Fluxo: instalar localmente

```shell
/plugin marketplace add .
/plugin install cerebro-memoria@1z-plugins
```

O `marketplace add` aponta para a raiz do repositório (onde está `.claude-plugin/`), não para `plugins/`. Depois de instalar, se a saída pedir, rode `/reload-plugins`.

Skills de plugin ficam com namespace: a skill `cerebro-memoria` do plugin `cerebro-memoria` é invocada como `/cerebro-memoria:cerebro-memoria`.

Para validar antes de publicar:

```bash
claude plugin validate ./plugins/meu-plugin --strict
```

## Versionamento

Só bumpe o `version` no `plugin.json` — o catálogo pega de lá. Enquanto o `version` não muda, quem já instalou **não recebe atualização**, mesmo com o código novo no repositório. É a causa mais comum de "editei o plugin e nada mudou".
