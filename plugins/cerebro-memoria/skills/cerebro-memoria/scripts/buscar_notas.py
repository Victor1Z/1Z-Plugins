#!/usr/bin/env python3
"""
Busca notas no vault do Cérebro (Obsidian) por frontmatter e/ou texto livre.
Sem dependências externas (não requer PyYAML) para funcionar em qualquer
Python 3 padrão na máquina do Victor.

Uso:
    python buscar_notas.py --vault "C:\\Users\\Usuario\\Documents\\Obsidian\\Cerebro" --query "sistema financeiro"
    python buscar_notas.py --vault "..." --tipo decisao_tecnica --projeto "Sistema Financeiro"
    python buscar_notas.py --vault "..." --tag sap --tag idoc
    python buscar_notas.py --vault "..." --pasta "01 - Projetos"

Sem nenhum filtro, retorna todas as notas do vault (inventário geral).
Saída sempre em JSON.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n?', re.DOTALL)

# Pastas internas do Obsidian que nunca devem virar resultado de busca.
# '.trash' importa em particular: sem isso uma nota apagada volta a aparecer
# na recuperacao de contexto, que e exatamente o oposto de apagar.
PASTAS_IGNORADAS = {'_config', '.obsidian', '.trash'}


def _limpar(valor):
    return valor.strip().strip('"').strip("'")


def parse_frontmatter(text):
    """Parser simples de YAML frontmatter.

    Entende 'chave: valor', listas em bloco ('- item') e listas inline
    ('tags: [a, b]'). A forma inline e a que o Obsidian escreve e a que
    qualquer um digita a mao -- sem ela o valor virava a string bruta
    '[a, b]' e o filtro --tag falhava em silencio, retornando zero
    resultados numa nota que tem a tag.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    data = {}
    current_key = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if stripped.startswith('- '):
            if current_key:
                data.setdefault(current_key, [])
                if isinstance(data[current_key], list):
                    data[current_key].append(_limpar(stripped[2:]))
            continue
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip()
            if val == '':
                data[key] = []
                current_key = key
            elif val.startswith('[') and val.endswith(']'):
                itens = [_limpar(p) for p in val[1:-1].split(',')]
                data[key] = [p for p in itens if p]
                current_key = None
            else:
                data[key] = _limpar(val)
                current_key = None
    return data, body


def normalizar_tags(valor):
    """Devolve as tags como lista minuscula, sem o '#' que o Obsidian aceita."""
    if isinstance(valor, list):
        brutas = valor
    elif valor in (None, ''):
        brutas = []
    else:
        brutas = [valor]
    return [str(t).strip().lstrip('#').lower() for t in brutas if str(t).strip()]


def load_notes(vault):
    notes = []
    for path in vault.rglob('*.md'):
        # ignora config do proprio skill e pastas internas do Obsidian
        if PASTAS_IGNORADAS & set(path.relative_to(vault).parts):
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        fm, body = parse_frontmatter(text)
        notes.append({
            'path': str(path.relative_to(vault)),
            'fm': fm,
            'body': body,
            'raw': text,
        })
    return notes


def matches(note, args):
    fm = note['fm']
    if args.tipo and str(fm.get('tipo', '')).lower() != args.tipo.lower():
        return False
    if args.projeto and args.projeto.lower() not in str(fm.get('projeto', '')).lower():
        return False
    if args.tags:
        note_tags = normalizar_tags(fm.get('tags', []))
        if not all(t in note_tags for t in normalizar_tags(args.tags)):
            return False
    if args.query:
        q = args.query.lower()
        haystack = (note['path'] + '\n' + note['raw']).lower()
        if q not in haystack:
            return False
    return True


def primeira_linha_util(body, width):
    """Primeira linha de conteudo real: pula titulo markdown e linhas vazias."""
    for linha in body.splitlines():
        linha = linha.strip()
        if linha and not linha.startswith('#'):
            return linha[:width]
    return ''


def snippet(note, query, width=160):
    """Trecho do CORPO da nota, nunca do frontmatter.

    A busca casa contra a nota inteira (frontmatter incluso, o que e util para
    achar por projeto/tag), mas o trecho vindo do frontmatter so mostrava
    'tipo: projeto status: ativo ...' -- ruido, nao conteudo.
    """
    body = note['body']
    if query:
        idx = body.lower().find(query.lower())
        if idx != -1:
            start = max(0, idx - width // 2)
            end = min(len(body), idx + width // 2)
            return ' '.join(body[start:end].split())
    return primeira_linha_util(body, width)


def main():
    ap = argparse.ArgumentParser(description='Busca notas no vault Cérebro')
    ap.add_argument('--vault', required=True, help='Caminho do vault do Obsidian')
    ap.add_argument('--query', default='', help='Texto livre a buscar em qualquer parte da nota')
    ap.add_argument('--tipo', default='', help='Filtra pelo campo "tipo" do frontmatter')
    ap.add_argument('--projeto', default='', help='Filtra pelo campo "projeto" do frontmatter (substring)')
    ap.add_argument('--tag', dest='tags', action='append', default=[], help='Filtra por tag (pode repetir)')
    ap.add_argument('--pasta', default='', help='Filtra por subpasta relativa ao vault, ex: "01 - Projetos"')
    ap.add_argument('--limit', type=int, default=25)
    args = ap.parse_args()

    vault = Path(args.vault)
    if not vault.exists():
        print(json.dumps({'erro': f'Vault não encontrado em {vault}'}, ensure_ascii=False))
        sys.exit(1)

    notes = load_notes(vault)

    if args.pasta:
        alvo = args.pasta.replace('\\', '/')
        notes = [n for n in notes if n['path'].replace('\\', '/').startswith(alvo)]

    results = [n for n in notes if matches(n, args)]
    total_encontrado = len(results)
    results = results[:args.limit]

    output = []
    for n in results:
        fm = n['fm']
        output.append({
            'path': n['path'],
            'titulo': fm.get('titulo') or Path(n['path']).stem,
            'tipo': fm.get('tipo', ''),
            'projeto': fm.get('projeto', ''),
            'status': fm.get('status', ''),
            'tags': normalizar_tags(fm.get('tags', [])),
            'data': fm.get('data') or fm.get('data_evento') or fm.get('data_criacao', ''),
            'trecho': snippet(n, args.query),
        })

    print(json.dumps({
        'total_encontrado': total_encontrado,
        'total_no_vault': len(notes),
        'resultados': output,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
