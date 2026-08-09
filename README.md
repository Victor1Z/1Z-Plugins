# 1Z Plugin Marketplace

Marketplace pessoal de plugins do Claude Code. Cada plugin fica em `plugins/<slug>/`.

## Plugins

- **cerebro-memoria** — memória persistente em Obsidian, com o vault como única fonte de verdade. Cada pessoa configura o caminho do próprio vault uma vez (`configurar_vault.py`).
- **marketplace-manager** — cria, valida e registra os plugins deste repositório.

## Instalar

No Claude Code, a partir da raiz deste repositório:

```shell
/plugin marketplace add .
/plugin install cerebro-memoria@1z-plugins
```

Se a saída da instalação pedir, rode `/reload-plugins`. As skills ficam com namespace do plugin — por exemplo `/cerebro-memoria:cerebro-memoria`.

## Adicionar um plugin

```bash
python plugins/marketplace-manager/scripts/novo_plugin.py \
  --nome meu-plugin --descricao "O que ele faz"
```

Depois escreva o `SKILL.md` de verdade e rode a sincronização:

```bash
python plugins/marketplace-manager/scripts/sincronizar_marketplace.py
```

## Estrutura

```text
.claude-plugin/
└── marketplace.json              ← catálogo (GERADO — não editar à mão)
plugins/
└── <slug>/
    ├── .claude-plugin/
    │   └── plugin.json           ← fonte de verdade do plugin
    └── skills/
        └── <nome-da-skill>/
            ├── SKILL.md
            ├── references/
            └── scripts/
```

O catálogo é derivado dos `plugin.json`. Editar ele à mão faz catálogo e manifesto divergirem, e o sintoma disso (skill que não aparece, versão que não atualiza) nunca aponta para a causa.

O `SKILL.md` nunca vai na raiz do plugin: os docs listam a raiz como fallback, mas nem toda superfície enumera a skill a partir dela — o plugin instala e aparece "sem habilidades". A validação do `marketplace-manager` recusa esse layout.
