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


def parse_frontmatter(text):
    """Parser simples de YAML frontmatter: chave: valor e listas com '- item'."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    data = {}
    current_key = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('- '):
            if current_key:
                data.setdefault(current_key, [])
                if isinstance(data[current_key], list):
                    data[current_key].append(stripped[2:].strip())
            continue
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip()
            if val == '':
                data[key] = []
                current_key = key
            else:
                data[key] = val.strip('"').strip("'")
                current_key = None
    return data, body


def load_notes(vault):
    notes = []
    for path in vault.rglob('*.md'):
        # ignora arquivos de config do próprio skill
        if '_config' in path.relative_to(vault).parts:
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
        raw_tags = fm.get('tags', [])
        note_tags = [t.lower() for t in raw_tags] if isinstance(raw_tags, list) else [str(raw_tags).lower()]
        if not all(t.lower() in note_tags for t in args.tags):
            return False
    if args.query:
        q = args.query.lower()
        haystack = (note['path'] + '\n' + note['raw']).lower()
        if q not in haystack:
            return False
    return True


def snippet(note, query, width=160):
    raw = note['raw']
    if not query:
        body = note['body'].strip()
        return body.splitlines()[0][:width] if body else ''
    idx = raw.lower().find(query.lower())
    if idx == -1:
        return ''
    start = max(0, idx - width // 2)
    end = min(len(raw), idx + width // 2)
    return raw[start:end].replace('\n', ' ').strip()


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
            'tags': fm.get('tags', []) if isinstance(fm.get('tags', []), list) else [fm.get('tags')],
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
