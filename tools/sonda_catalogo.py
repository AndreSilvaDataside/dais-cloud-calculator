#!/usr/bin/env python3
"""
Sondagem da Azure Retail Prices API.

Modos:
  discover  ->  quais serviceName existem numa serviceFamily
  sweep     ->  varre a regiao inteira e lista serviceFamily -> serviceName
  probe     ->  um serviceName especifico tem meter? quais? qual unidade?

Sem dependencia externa: usa apenas a stdlib.

Uso:
    python sonda_catalogo.py sweep --region brazilsouth
    python sonda_catalogo.py discover --family Data --region brazilsouth
    python sonda_catalogo.py probe --region brazilsouth
    python sonda_catalogo.py probe --service "Private Link" --region any
    python sonda_catalogo.py probe --service "Microsoft Fabric" --price-type Reservation
    python sonda_catalogo.py probe --json saida.json

Notas de uso:
    --region any        omite o filtro de regiao (pega meter Global, Zone 1 etc)
    --price-type all    omite o filtro de priceType (traz Consumption e Reservation)
    --family aceita qualquer texto: a lista de familias da Azure muda com o tempo.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

API = "https://prices.azure.com/api/retail/prices"

# Candidatos do catalogo real da Dataside. Grafia confirmada pela sondagem
# de 10/09 em brazilsouth, exceto os marcados como a confirmar.
CANDIDATOS = [
    "Microsoft Fabric",
    "Azure Databricks",
    "Storage",
    "Key Vault",
    "Virtual Machines",
    "Virtual Network",
    "Bandwidth",
    "SQL Database",
    "Private Link",           # a confirmar: rodar com --region any
    "Azure Kubernetes Service",
]

# A Azure muda essa lista com o tempo. Use o modo sweep para descobrir o
# que existe de fato em vez de confiar nisto.
FAMILIAS = [
    "AI + Machine Learning", "Analytics", "Compute", "Containers", "Data",
    "Databases", "Developer Tools", "DevOps", "Identity", "Integration",
    "Internet of Things", "Management and Governance", "Media", "Migration",
    "Mixed Reality", "Mobile", "Networking", "Other", "Security", "Storage",
    "Web",
]

PRICE_TYPES = ["Consumption", "Reservation", "DevTestConsumption", "all"]


def log(msg: str) -> None:
    """Progresso vai para stderr, para nao sujar a saida em markdown."""
    print(msg, file=sys.stderr, flush=True)


def montar_filtro(
    service: str | None = None,
    family: str | None = None,
    region: str = "eastus",
    price_type: str = "Consumption",
) -> str:
    partes = []
    if service:
        partes.append(f"serviceName eq '{service}'")
    if family:
        partes.append(f"serviceFamily eq '{family}'")
    if region and region.lower() not in ("any", "all", "todas"):
        partes.append(f"armRegionName eq '{region}'")
    if price_type and price_type.lower() != "all":
        partes.append(f"priceType eq '{price_type}'")
    return " and ".join(partes)


def _get(url: str, timeout: int, tentativas: int = 3) -> dict:
    ultimo = None
    for n in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            ultimo = e
            if n < tentativas - 1:
                espera = 2 ** n
                log(f"    falhou ({type(e).__name__}), nova tentativa em {espera}s")
                time.sleep(espera)
    raise ultimo  # type: ignore[misc]


def buscar(
    filtro: str,
    max_paginas: int = 1,
    currency: str = "USD",
    timeout: int = 60,
    rotulo: str = "",
) -> tuple[list[dict], bool, str | None]:
    """Devolve (itens, tem_mais_paginas, erro)."""
    params = {"currencyCode": currency}
    if filtro:
        params["$filter"] = filtro
    url = f"{API}?{urllib.parse.urlencode(params)}"
    itens: list[dict] = []
    paginas = 0
    try:
        while url and paginas < max_paginas:
            dados = _get(url, timeout=timeout)
            itens.extend(dados.get("Items") or [])
            url = dados.get("NextPageLink")
            paginas += 1
            if rotulo and paginas % 20 == 0:
                log(f"  {rotulo}: {paginas} paginas, {len(itens)} itens")
        return itens, bool(url), None
    except urllib.error.HTTPError as e:
        return itens, False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return itens, False, f"rede: {e.reason}"
    except Exception as e:  # noqa: BLE001
        return itens, False, f"{type(e).__name__}: {e}"


def _cabecalho(args: argparse.Namespace, titulo: str) -> None:
    regiao = "todas" if args.region.lower() in ("any", "all", "todas") else args.region
    extra = getattr(args, "price_type", None)
    sufixo = f", priceType: {extra}" if extra else ""
    print(f"# {titulo} (regiao: {regiao}{sufixo})\n")


def cmd_sweep(args: argparse.Namespace) -> int:
    _cabecalho(args, "Varredura completa")
    log("Varredura sem filtro de familia. Pode levar minutos.")
    filtro = montar_filtro(region=args.region, price_type=args.price_type)
    itens, tem_mais, erro = buscar(
        filtro, max_paginas=args.max_pages, timeout=args.timeout, rotulo="sweep"
    )
    if erro and not itens:
        print(f"Falha na consulta: {erro}")
        return 1
    if not itens:
        print("Nenhum item. Confira a regiao.")
        return 1

    mapa: dict[str, Counter] = defaultdict(Counter)
    for i in itens:
        mapa[i.get("serviceFamily", "?")][i.get("serviceName", "?")] += 1

    if tem_mais:
        print("> Amostra truncada: aumente --max-pages para varredura completa.\n")
    if erro:
        print(f"> Interrompida por erro apos {len(itens)} itens: {erro}\n")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(itens, f, ensure_ascii=False)
        log(f"snapshot salvo em {args.json} ({len(itens)} meters)")

    print(f"Total de meters na amostra: {len(itens)}\n")
    for familia in sorted(mapa):
        print(f"## {familia}\n")
        print("| serviceName | meters |")
        print("| --- | ---: |")
        for nome, qtd in sorted(mapa[familia].items()):
            print(f"| {nome} | {qtd} |")
        print()
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    _cabecalho(args, "Descoberta de serviceName")
    achou_algo = False
    for familia in args.family:
        log(f"consultando familia {familia}")
        filtro = montar_filtro(
            family=familia, region=args.region, price_type=args.price_type
        )
        itens, tem_mais, erro = buscar(
            filtro, max_paginas=args.max_pages, timeout=args.timeout, rotulo=familia
        )
        if erro and not itens:
            print(f"## {familia}\nFalha na consulta: {erro}\n")
            continue
        if not itens:
            print(f"## {familia}\nNenhum item. Confira a grafia da familia ou da regiao.\n")
            continue
        achou_algo = True
        nomes = Counter(i.get("serviceName", "?") for i in itens)
        aviso = "  (amostra truncada, aumente --max-pages)" if tem_mais else ""
        print(f"## {familia}{aviso}\n")
        print("| serviceName | meters na amostra |")
        print("| --- | ---: |")
        for nome, qtd in sorted(nomes.items()):
            print(f"| {nome} | {qtd} |")
        print()
    return 0 if achou_algo else 1


def cmd_probe(args: argparse.Namespace) -> int:
    servicos = args.service or CANDIDATOS
    _cabecalho(args, "Sondagem por servico")
    print("| servico | status | meters | unidades |")
    print("| --- | --- | ---: | --- |")

    detalhes: dict[str, list[dict]] = {}
    algum_ok = False

    for servico in servicos:
        log(f"consultando {servico}")
        filtro = montar_filtro(
            service=servico, region=args.region, price_type=args.price_type
        )
        itens, tem_mais, erro = buscar(
            filtro, max_paginas=args.max_pages, timeout=args.timeout, rotulo=servico
        )
        if erro and not itens:
            print(f"| {servico} | erro: {erro} | | |")
            continue
        if not itens:
            print(f"| {servico} | VAZIO | 0 | |")
            continue
        detalhes[servico] = itens
        algum_ok = True
        unidades = sorted({i.get("unitOfMeasure", "?") for i in itens})
        marca = "+" if tem_mais else ""
        print(f"| {servico} | ok | {len(itens)}{marca} | {', '.join(unidades[:4])} |")

    print("\n> VAZIO nao prova que o servico nao existe. Pode ser grafia errada do")
    print("> serviceName, ou meter fora da regiao filtrada (use --region any), ou")
    print("> priceType diferente (use --price-type all). Rode sweep antes de concluir.\n")

    for servico, itens in detalhes.items():
        print(f"\n## {servico}\n")
        por_produto: dict[str, list[dict]] = defaultdict(list)
        for i in itens:
            por_produto[i.get("productName", "?")].append(i)
        print("| productName | meters | meterName (amostra) | unidade | preco |")
        print("| --- | ---: | --- | --- | ---: |")
        for produto in sorted(por_produto)[: args.max_produtos]:
            grupo = por_produto[produto]
            amostra = grupo[0]
            print(
                f"| {produto} "
                f"| {len(grupo)} "
                f"| {amostra.get('meterName', '?')} "
                f"| {amostra.get('unitOfMeasure', '?')} "
                f"| {amostra.get('retailPrice', '?')} |"
            )
        if len(por_produto) > args.max_produtos:
            print(f"| ... | | mais {len(por_produto) - args.max_produtos} productName | | |")
        print()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(detalhes, f, ensure_ascii=False, indent=2)
        print(f"\nBruto salvo em {args.json}")

    return 0 if algum_ok else 1


CAMPOS_BUSCA = [
    "serviceName", "serviceFamily", "productName", "meterName",
    "skuName", "armSkuName",
]


def normalizar(texto: str) -> str:
    """Deixa a busca imune a hifen, sublinhado, barra e caixa.

    A Azure escreve 'All-purpose Compute DBU' com hifen e 'Onelake' e
    'OneLake' no mesmo productName. Busca literal perde os dois casos.
    """
    t = texto.lower()
    for c in "-_/":
        t = t.replace(c, " ")
    return " ".join(t.split())


def cmd_grep(args: argparse.Namespace) -> int:
    """Procura um termo em qualquer campo textual do snapshot do sweep."""
    try:
        with open(args.file, encoding="utf-8") as f:
            itens = json.load(f)
    except FileNotFoundError:
        print(f"Arquivo nao encontrado: {args.file}")
        print("Gere primeiro com: sonda_catalogo.py sweep --region <regiao> --json <arquivo>")
        return 1
    except json.JSONDecodeError as e:
        print(f"JSON invalido em {args.file}: {e}")
        return 1

    if isinstance(itens, dict):  # aceita tambem o json do modo probe
        itens = [x for lista in itens.values() for x in lista]

    termos = [normalizar(t) for t in args.term]
    achados = []
    for i in itens:
        alvo = normalizar(" ".join(str(i.get(c, "")) for c in CAMPOS_BUSCA))
        if all(t in alvo for t in termos) if args.all_terms else any(t in alvo for t in termos):
            achados.append(i)

    modo = "todos os termos" if args.all_terms else "qualquer termo"
    print(f"# Busca por {args.term} ({modo}) em {len(itens)} meters\n")
    if not achados:
        print("Nenhum resultado. O termo nao aparece em nenhum campo do snapshot.")
        print("Isso e evidencia forte de que o servico nao esta exposto nesta regiao.")
        return 1

    print(f"{len(achados)} resultados\n")
    print("| serviceFamily | serviceName | productName | meterName | unidade | preco |")
    print("| --- | --- | --- | --- | --- | ---: |")
    for i in achados[: args.limite]:
        print(
            f"| {i.get('serviceFamily','?')} | {i.get('serviceName','?')} "
            f"| {i.get('productName','?')} | {i.get('meterName','?')} "
            f"| {i.get('unitOfMeasure','?')} | {i.get('retailPrice','?')} |"
        )
    if len(achados) > args.limite:
        print(f"| ... | mais {len(achados) - args.limite} | | | | |")
    return 0


def _comuns(p: argparse.ArgumentParser, paginas: int) -> None:
    p.add_argument("--region", default="eastus", help="regiao ARM, ou 'any' para todas")
    p.add_argument("--price-type", default="Consumption", choices=PRICE_TYPES,
                   dest="price_type")
    p.add_argument("--max-pages", type=int, default=paginas, dest="max_pages")
    p.add_argument("--timeout", type=int, default=60)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sondagem da Azure Retail Prices API")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sweep", help="varre a regiao e lista familia -> servico")
    s.add_argument("--json", default=None, help="salva o snapshot completo da regiao")
    _comuns(s, 400)
    s.set_defaults(func=cmd_sweep)

    g = sub.add_parser("grep", help="procura um termo no snapshot salvo pelo sweep")
    g.add_argument("--file", required=True, help="arquivo gerado por sweep --json")
    g.add_argument("--term", action="append", required=True, help="repetivel")
    g.add_argument("--all-terms", action="store_true", dest="all_terms",
                   help="exige todos os termos em vez de qualquer um")
    g.add_argument("--limite", type=int, default=40)
    g.set_defaults(func=cmd_grep)

    d = sub.add_parser("discover", help="lista os serviceName de uma familia")
    d.add_argument("--family", action="append", default=None,
                   help="nome da familia; aceita qualquer texto, repetivel")
    _comuns(d, 40)
    d.set_defaults(func=cmd_discover)

    b = sub.add_parser("probe", help="testa serviceName especificos")
    b.add_argument("--service", action="append", default=None)
    b.add_argument("--max-produtos", type=int, default=15, dest="max_produtos")
    b.add_argument("--json", default=None)
    _comuns(b, 60)
    b.set_defaults(func=cmd_probe)

    args = p.parse_args(argv)
    if args.cmd == "discover" and not args.family:
        args.family = FAMILIAS
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())