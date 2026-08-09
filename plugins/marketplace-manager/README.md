# Marketplace Manager

Cria, valida e registra os plugins deste marketplace. O `.claude-plugin/marketplace.json` da raiz é **gerado** a partir dos `plugin.json` de cada plugin — não edite ele à mão.

## Estrutura

- `.claude-plugin/plugin.json` — metadados deste plugin.
- `SKILL.md` — instruções que o Claude segue ao mexer no marketplace.
- `scripts/sincronizar_marketplace.py` — regenera e valida o catálogo.
- `scripts/novo_plugin.py` — cria um plugin novo a partir de `templates/`.
- `templates/` — esqueleto de `plugin.json`, `SKILL.md` e `README.md`.

## Comandos

```bash
# criar um plugin novo (já registra no catálogo)
python plugins/marketplace-manager/scripts/novo_plugin.py \
  --nome revisor-sap --descricao "Revisa chamados de SAP" --com scripts references

# regenerar o catálogo depois de mexer em qualquer plugin.json
python plugins/marketplace-manager/scripts/sincronizar_marketplace.py

# verificar sem escrever (bom antes de commitar)
python plugins/marketplace-manager/scripts/sincronizar_marketplace.py --check
```

## O que a validação pega

- `plugin.json` ausente, mal formado ou gravado fora de UTF-8.
- `name` que não é kebab-case ou que não bate com o nome da pasta.
- `version` ausente ou fora de semver — sem ela, quem instalou nunca recebe update.
- Plugin sem componente algum (`SKILL.md`, `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`): instala e não faz nada.
- `SKILL.md` na raiz sem `name:` no frontmatter — o Claude Code cairia no nome do diretório de instalação, que muda a cada atualização.
- Referência a caminho fora da pasta do plugin: na instalação ele é copiado isolado e esse caminho não existe no destino.

## Campos preservados na sincronização

O catálogo é regenerado, mas estes campos são mantidos como você escreveu: `name` e `owner` do marketplace, e por plugin `source`, `category`, `tags`, `strict` e `relevance`. O resto (`description`, `version`, `author`, `keywords`, `displayName`) vem sempre do `plugin.json`.
