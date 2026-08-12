#!/usr/bin/env python3
"""
Configura, uma vez por maquina, onde fica o vault do Claude Memoria.

A escolha e gravada em ~/.claude-memoria/config.json e passa a valer para todas
as conversas -- os outros scripts do skill leem esse arquivo sozinhos, sem
precisar de --vault. Fica fora do repositorio de proposito: e config da pessoa,
nao do plugin, e nunca deve entrar num commit.

Uso:
    python configurar_vault.py                             # status atual + vaults detectados
    python configurar_vault.py --detectar                  # so os vaults do Obsidian local
    python configurar_vault.py --vault "D:\\Obsidian\\Vault"
    python configurar_vault.py --vault "..." --criar       # grava e cria a estrutura de pastas
    python configurar_vault.py --limpar                    # esquece a configuracao

Saida sempre em JSON.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vault_config import (  # noqa: E402
    CONFIG_FILE,
    ENV_VAR,
    _expandir,
    detectar_vaults,
    escrever_config,
    ler_config,
    resolver_vault,
    saida_utf8,
)


def _status() -> dict:
    vault, origem = resolver_vault()
    status = {
        "configurado": vault is not None,
        "vault": str(vault) if vault else None,
        "origem": origem,
        "existe": bool(vault and vault.exists()),
        "arquivo_de_config": str(CONFIG_FILE),
        "variavel_de_ambiente": ENV_VAR,
    }
    if origem.endswith("legado") or origem.endswith("legada"):
        status["legado"] = (
            "Caminho vindo da config do nome anterior do plugin (cerebro-memoria). "
            "Continua funcionando; para migrar, regrave com "
            '--vault "<caminho>".'
        )
    return status


def _sair(payload: dict, codigo: int = 0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(codigo)


def main():
    saida_utf8()
    ap = argparse.ArgumentParser(
        description="Configura o caminho do vault do Claude Memoria para esta maquina",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--vault", help="caminho do vault a gravar como padrao")
    ap.add_argument("--criar", action="store_true",
                    help="com --vault: cria a pasta e a estrutura se ainda nao existir")
    ap.add_argument("--detectar", action="store_true",
                    help="lista os vaults registrados no Obsidian local")
    ap.add_argument("--limpar", action="store_true",
                    help="remove o vault gravado na config")
    args = ap.parse_args()

    if args.limpar:
        dados = ler_config()
        anterior = dados.pop("vault", None)
        dados.pop("configurado_em", None)
        escrever_config(dados)
        _sair({"acao": "limpar", "vault_anterior": anterior, "status": _status()})

    if args.vault:
        vault = _expandir(args.vault)
        if not vault.exists():
            if not args.criar:
                _sair({
                    "erro": f"{vault} nao existe.",
                    "sugestao": "Confira o caminho, ou repita com --criar para "
                                "criar a pasta e a estrutura do vault ali.",
                    "detectados": detectar_vaults(),
                }, 1)
            vault.mkdir(parents=True, exist_ok=True)
        elif not vault.is_dir():
            _sair({"erro": f"{vault} existe mas nao e uma pasta."}, 1)

        dados = ler_config()
        dados["vault"] = str(vault)
        dados["configurado_em"] = date.today().isoformat()
        escrever_config(dados)

        resultado = {"acao": "gravar", "status": _status()}

        if args.criar:
            # Reaproveita o inicializador em vez de duplicar a lista de pastas:
            # duas listas divergem na primeira vez que uma pasta muda de nome.
            import os
            import subprocess
            script = Path(__file__).resolve().parent / "inicializar_vault.py"
            # PYTHONIOENCODING + encoding='utf-8': sem os dois, os nomes de pasta
            # acentuados ("Reunioes", "Decisoes") voltam do subprocesso em
            # codepage do console e chegam aqui como lixo dentro do JSON.
            proc = subprocess.run(
                [sys.executable, str(script), "--vault", str(vault)],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            resultado["inicializacao"] = (proc.stdout + proc.stderr).strip()

        # Aviso: variavel de ambiente tem precedencia sobre a config gravada.
        # Sem isso, a pessoa grava o caminho novo e continua vendo o antigo.
        if resultado["status"]["origem"] == "ambiente":
            resultado["aviso"] = (
                f"A variavel {ENV_VAR} esta definida e tem precedencia sobre a "
                "config gravada. Remova-a para o valor gravado passar a valer."
            )
        _sair(resultado)

    if args.detectar:
        _sair({"detectados": detectar_vaults()})

    _sair({"status": _status(), "detectados": detectar_vaults()})


if __name__ == "__main__":
    main()
