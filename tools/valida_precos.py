#!/usr/bin/env python3
"""
Confere os precos afirmados na SKILL contra a Azure Retail Prices API.

Toda tabela de preco da Skill e uma afirmacao sobre a API. Esta ferramenta
reconfere cada uma. Serve para rodar antes de apresentacao e antes de aprovar
PR que mexa em numero.

Sem dependencia externa: usa apenas a stdlib e o sonda_catalogo.py ao lado.

Uso:
    python valida_precos.py                          # busca ao vivo na API
    python valida_precos.py --snapshot brazilsouth-2026-09-11.json
    python valida_precos.py --snapshot arquivo.json --verbose

Saida: uma linha por conferencia, e o total de falhas no fim.
Codigo de saida 0 se tudo passou, 1 se houve falha.

FALHA NAO E NECESSARIAMENTE BUG.
    Se a Azure mudou um preco, a conferencia falha e esta certa em falhar: o
    aviso e de que uma tabela da Skill envelheceu. Leia a falha, confirme na
    API, e corrija a Skill. Nao ajuste o numero esperado aqui sem corrigir
    a Skill tambem, senao a ferramenta para de servir para nada.

    Por isso esta ferramenta nao serve como teste de CI que tem que passar
    sempre. Ela serve como conferencia deliberada.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sonda_catalogo import buscar, montar_filtro, normalizar  # noqa: E402

# O console do Windows usa cp1252 e nao aceita os acentos e setas desta saida.
# Sem isto a ferramenta quebra justamente ao imprimir uma FALHA, que e a unica
# hora em que ela precisa ser lida.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REGIAO = "brazilsouth"

SKILL = Path(__file__).resolve().parents[1] / "plugin" / "skills" / "cotar_cloud" / "SKILL_unified.md"

# Servicos que a Skill cota. Define o que buscar quando nao ha snapshot.
SERVICOS = [
    "Microsoft Fabric",
    "Azure Databricks",
    "Storage",
    "Key Vault",
    "Bandwidth",
    "Virtual Machines",
    "Log Analytics",
    "Azure Monitor",
    "Azure Data Factory v2",
    "Microsoft Purview",
    "Azure Purview",          # geracao anterior: o par da armadilha 1
    "ExpressRoute",
    "Microsoft Copilot Studio",
    "IoT Hub",
    "Stream Analytics",
    "Functions",
    "Foundry Models",
]

# ---------------------------------------------------------------------------
# Precos de meter afirmados na Skill: (productName, meterName, preco esperado)
# Primeira faixa (tierMinimumUnits = 0) salvo onde indicado.
# ---------------------------------------------------------------------------
PRECOS = [
    # --- Microsoft Fabric: capacidade ---
    ("Fabric Capacity", "Data Warehouse Capacity Usage CU", 0.28),
    ("Fabric Capacity", "Power BI Capacity Usage CU", 0.28),
    ("Fabric Capacity", "Spark Memory Optimized Capacity Usage CU", 0.28),
    ("Fabric Capacity", "Eventhouse Capacity Usage CU", 0.28),
    ("Fabric Capacity", "Capacity Overage Capacity Usage CU", 0.84),
    # --- Microsoft Fabric: armazenamento OneLake ---
    ("OneLake", "OneLake Storage Hot Data Stored", 0.0407),
    ("OneLake", "OneLake Storage Cool Data Stored", 0.0221),
    ("OneLake", "OneLake Storage Cold Data Stored", 0.0083),
    ("OneLake", "Storage Mirroring Data Stored", 0.0407),
    # --- Databricks classico (DBU + VM) ---
    ("Azure Databricks", "Premium All-purpose Compute DBU", 0.55),
    ("Azure Databricks", "Premium All-Purpose Photon DBU", 0.55),
    ("Azure Databricks", "Standard All-purpose Compute DBU", 0.40),
    ("Azure Databricks", "Standard All-Purpose Photon DBU", 0.40),
    ("Azure Databricks", "Premium Jobs Compute DBU", 0.30),
    ("Azure Databricks", "Premium Jobs Compute Photon DBU", 0.30),
    ("Azure Databricks", "Standard Jobs Compute DBU", 0.15),
    ("Azure Databricks", "Premium Jobs Light Compute DBU", 0.22),
    ("Azure Databricks", "Standard Jobs Light Compute DBU", 0.07),
    ("Azure Databricks", "Premium SQL Analytics DBU", 0.22),
    ("Azure Databricks", "Premium Core Compute Delta Live Tables DBU", 0.30),
    ("Azure Databricks", "Premium Pro Compute Delta Live Tables DBU", 0.38),
    ("Azure Databricks", "Premium Advanced Compute Delta Live Tables DBU", 0.54),
    ("Azure Databricks", "Premium Enhanced Security and Compliance DBU", 0.10),
    # --- Databricks serverless (so DBU) ---
    ("Azure Databricks Regional", "Premium Serverless SQL DBU", 1.09),
    ("Azure Databricks Regional", "Premium Interactive Serverless Compute DBU", 1.09),
    ("Azure Databricks Regional", "Premium SQL Compute Pro DBU", 0.85),
    ("Azure Databricks Regional", "Premium Automated Serverless Compute DBU", 0.59),
    ("Azure Databricks Regional", "Premium Database Serverless Compute DBU", 0.42),
    ("Azure Databricks Regional", "Premium Model Training DBU", 1.11),
    ("Azure Databricks Regional", "Premium Serverless Realtime Inferencing DBU", 0.112),
    ("Azure Databricks Regional", "Premium Databricks Storage Unit DSU", 0.0407),
    # --- ADLS Gen2 ---
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot LRS Data Stored", 0.0326),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot ZRS Data Stored", 0.0407),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot GRS Data Stored", 0.0652),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Cool LRS Data Stored", 0.0177),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Cool GRS Data Stored", 0.0354),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Archive LRS Data Stored", 0.002),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot RA-GZRS Data Stored", 0.091688),
    # --- Key Vault ---
    ("Key Vault HSM Pool", "Standard B1 Instance", 3.2),
    # --- Key Vault: operacoes (allowlist completa) ---
    ("Key Vault", "Operations", 0.03),
    ("Key Vault", "Advanced Key Operations", 0.15),
    ("Key Vault", "Automated Key Rotation", 1.0),
    ("Key Vault", "Secret Renewal", 1.0),
    ("Key Vault", "Certificate Renewal Request", 3.0),
    ("Key Vault", "Premium HSM-protected RSA 2048-bit key", 1.0),
    # --- ADLS Gen2: operacoes ---
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot Write Operations", 0.091),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot GRS Write Operations", 0.182),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot Read Operations", 0.0073),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot Other Operations", 0.00728),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot Iterative Write Operations", 0.091),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot GRS Iterative Write Operations", 0.182),
    # --- Discos gerenciados ---
    ("Premium SSD Managed Disks", "P10 LRS Disk", 34.05),
    ("Premium SSD Managed Disks", "P10 LRS Disk Mount", 1.82),
    ("Premium SSD Managed Disks", "P10 ZRS Disk", 51.075),
    # --- Log Analytics / Azure Monitor ---
    ("Log Analytics", "Analytics Logs Data Analyzed", 2.3),
    ("Log Analytics", "Analytics Logs Data Retention", 0.2),
    ("Azure Monitor", "Basic Logs Data Ingestion", 1.0),
    ("Azure Monitor", "Auxiliary Logs Data Ingestion", 0.1),
    ("Azure Monitor", "Alerts Resource Monitored at 1 Minute Frequency", 0.3),
    # --- Azure Data Factory v2 ---
    ("Azure Data Factory v2", "Cloud Orchestration Activity Run", 1.0),
    ("Azure Data Factory v2", "Cloud Data Movement", 0.25),
    ("Azure Data Factory v2", "Cloud Pipeline Activity", 0.005),
    ("Azure Data Factory v2", "Self Hosted Orchestration Activity Run", 1.5),
    ("Azure Data Factory v2", "Self Hosted Data Movement", 0.1),
    # --- Purview ---
    ("Microsoft Purview Data Governance", "Data Management Basic Data Governance Processing Unit", 15.0),
    ("Microsoft Purview Data Governance", "Data Management Advanced Data Governance Processing Unit", 240.0),
    ("Microsoft Purview Data Governance", "Data Catalog Standard Asset", 0.0165),
    ("Azure Purview Data Map", "Standard Capacity Unit", 0.411),
    # --- ExpressRoute (gateway) ---
    ("ExpressRoute Standard Gateway", "Standard Gateway", 0.19),
    ("ExpressRoute High Performance Gateway", "High Performance Gateway", 0.49),
    ("Microsoft Purview Data Governance", "Data Management Standard Data Governance Processing Unit", 60.0),
    ("ExpressRoute Gateway", "ErGw1AZ Gateway", 0.361),
    ("ExpressRoute Gateway", "ErGw3AZ Gateway", 2.151),
    # --- Copilot Studio ---
    ("Microsoft Copilot Studio", "Pay As You Go Message", 0.01),
    ("Microsoft Copilot Studio", "Pay As You Go Copilot Credit", 0.01),
    # --- IoT Hub (por unidade/mes) ---
    ("IoT Hub", "B1 Unit", 20.0),
    ("IoT Hub", "S1 Unit", 50.0),
    ("IoT Hub", "S2 Unit", 500.0),
    ("IoT Hub", "S3 Unit", 5000.0),
    # --- Stream Analytics ---
    ("Stream Analytics", "Standard Streaming Unit", 0.125),
    ("Stream Analytics", "Dedicated Streaming Unit", 0.125),
    ("Stream Analytics", "Standard V2 Streaming Unit/Job", 0.6733),
    # --- Azure OpenAI: serviceName e "Foundry Models" ---
    ("Azure OpenAI GPT5", "GPT 5 Chat Inpt Glbl 1M Tokens", 1.25),
    ("Azure OpenAI GPT5", "GPT 5 Chat outpt Glbl 1M Tokens", 10.0),
    ("Azure OpenAI GPT5", "GPT 5 Chat cchd Inpt Glbl 1M Tokens", 0.125),
    # --- Egress ---
    ("Bandwidth - Routing Preference: Internet", "Standard Data Transfer Out", 0.0),
    ("Rtn Preference: MGN", "Standard Inter-Region Data Transfer", 0.16),
]

# Faixas escalonadas: (productName, meterName, tierMinimumUnits, preco)
FAIXAS = [
    ("Bandwidth - Routing Preference: Internet", "Standard Data Transfer Out", 100.0, 0.12),
    ("Rtn Preference: MGN", "Standard Data Transfer Out", 100.0, 0.181),
    ("Key Vault", "Premium HSM-protected Advanced Key", 0.0, 5.0),
    ("Key Vault", "Premium HSM-protected Advanced Key", 250.0, 2.5),
    ("Key Vault", "Premium HSM-protected Advanced Key", 1500.0, 0.9),
    ("Key Vault", "Premium HSM-protected Advanced Key", 4000.0, 0.4),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot GRS Data Stored", 51200.0, 0.0626),
    ("Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot GRS Data Stored", 512000.0, 0.06),
    # Log Analytics: a faixa 0 e a MAIS BARATA (0,0) e a faixa 5 custa 4,60.
    # E o contraexemplo da heuristica "maior preco = tier 0" que a Skill proibe.
    ("Log Analytics", "Analytics Logs Data Ingestion", 0.0, 0.0),
    ("Log Analytics", "Analytics Logs Data Ingestion", 5.0, 4.6),
    ("Stream Analytics", "Dedicated V2 Streaming Unit/Job", 730.0, 0.288307),
    ("Functions", "Standard Execution Time", 400000.0, 0.000016),
]

# Tabela de F SKU da Skill: (CUs, sob demanda/mes, reserva/mes, compromisso anual)
FSKU = [
    (2, 408.80, 243.00, 2916.00),
    (4, 817.60, 486.00, 5832.00),
    (8, 1635.20, 972.00, 11664.00),
    (16, 3270.40, 1944.00, 23328.00),
    (32, 6540.80, 3888.00, 46656.00),
    (64, 13081.60, 7776.00, 93312.00),
    (128, 26163.20, 15552.00, 186624.00),
    (256, 52326.40, 31104.00, 373248.00),
]

CU_HORA = 0.28        # Fabric Capacity, qualquer Capacity Usage CU
CU_ANO = 1458.00      # Fabric Capacity Reservation, 1 Year
CU_3ANOS = 4374.00    # Fabric Capacity Reservation, 3 Years
HORAS_MES = 730

# Trechos que a Skill precisa conter, e trechos que nao pode mais conter.
EXIGE = [
    "Resolução de preço Azure",
    "Chave de resolução",
    "Allowlist por serviço",
    "Gates de validação",
    "reservationTerm",
    "Azure Databricks Regional",
    "Capacity Overage Capacity Usage CU",
    "Fabric Capacity Reservation",
    "OneLake Storage Hot Data Stored",
    "oito gates de validação",
    "Mesmo preço, unidade diferente",
    "Serviços que não estão na Retail Prices API",
    "Nenhuma linha some em silêncio",
    "Todo número declarado vale o mesmo",
    "Hot GRS Iterative Write Operations",
    "Standard_D2s_v5",
    "P10 LRS Disk Mount",
    "CENÁRIO A",
    "O que o MCP devolve, e o que ele não devolve",
    "discounted_price",
    "Não deduza a faixa pelo preço",
    "Serviço que não está na allowlist",
    "Foundry Models",
    "Azure Data Factory v2",
    "Microsoft Purview Data Governance",
    "S2` | 500,00",
    "A allowlist inteira é de `brazilsouth`",
    "Não existe fator de correção regional",
    "Os preços desta tabela não são verificados",
    "Allowlist por serviço — `brazilsouth`",
]
PROIBE = [
    # A instrucao que nao funciona: esse skuName nao existe na API.
    'skuName: "F[N] Capacity"',
    "F[N] Capacity",
    # Contradizia o Fabric, onde a reserva e 40,6% mais barata.
    "Nunca Reserved Instances ou Spot",
    "sete gates de validação",
]


class Relatorio:
    def __init__(self, verbose: bool) -> None:
        self.falhas: list[str] = []
        self.ok = 0
        self.verbose = verbose

    def chk(self, rotulo: str, cond: bool, detalhe: str = "") -> None:
        if cond:
            self.ok += 1
            if self.verbose:
                print(f"  ok     {rotulo}")
        else:
            self.falhas.append(rotulo + (f"  ({detalhe})" if detalhe else ""))
            print(f"  FALHA  {rotulo}" + (f"  → {detalhe}" if detalhe else ""))

    def secao(self, titulo: str) -> None:
        print(f"\n=== {titulo} ===")


def carregar(snapshot: str | None, timeout: int) -> tuple[list[dict], str]:
    """Devolve (linhas de Consumption, descricao da fonte)."""
    if snapshot:
        caminho = Path(snapshot)
        if not caminho.is_absolute():
            caminho = Path.cwd() / caminho
        with open(caminho, encoding="utf-8") as f:
            linhas = json.load(f)
        return linhas, f"snapshot {caminho.name} ({len(linhas)} meters)"

    linhas: list[dict] = []
    for servico in SERVICOS:
        filtro = montar_filtro(service=servico, region=REGIAO, price_type="Consumption")
        itens, tem_mais, erro = buscar(filtro, max_paginas=200, timeout=timeout, rotulo=servico)
        if erro:
            print(f"  AVISO  falha ao buscar {servico}: {erro}", file=sys.stderr)
        if tem_mais:
            print(f"  AVISO  {servico} tem mais paginas que o limite", file=sys.stderr)
        linhas.extend(itens)
    return linhas, f"API ao vivo, {REGIAO} ({len(linhas)} meters dos servicos em escopo)"


def indexar(linhas: list[dict]) -> dict:
    idx = collections.defaultdict(list)
    for r in linhas:
        idx[(r.get("productName"), r.get("meterName"))].append(r)
    return idx


def preco(idx: dict, pn: str, mn: str, tier: float = 0.0) -> float | None:
    for r in idx[(pn, mn)]:
        if r.get("tierMinimumUnits") == tier:
            return r.get("retailPrice")
    return None


def conferir_precos(rel: Relatorio, idx: dict) -> None:
    rel.secao("precos de meter afirmados na Skill")
    for pn, mn, esperado in PRECOS:
        obtido = preco(idx, pn, mn)
        rel.chk(f"{pn} / {mn} = {esperado}", obtido == esperado,
                "nao encontrado" if obtido is None else f"API devolve {obtido}")

    rel.secao("faixas escalonadas (tierMinimumUnits)")
    for pn, mn, tier, esperado in FAIXAS:
        obtido = preco(idx, pn, mn, tier)
        rel.chk(f"{mn} @ tier {tier:.0f} = {esperado}", obtido == esperado,
                "nao encontrado" if obtido is None else f"API devolve {obtido}")


def conferir_fabric(rel: Relatorio, idx: dict, timeout: int) -> None:
    rel.secao("Fabric: nao existe meter de F SKU (armadilha 5)")
    cu = [r for k, v in idx.items() for r in v
          if k[0] == "Fabric Capacity" and (k[1] or "").endswith("Capacity Usage CU")]
    taxas = {r["retailPrice"] for r in cu if "Overage" not in (r.get("meterName") or "")}
    rel.chk(f"todo Capacity Usage CU custa {CU_HORA} ({len(cu)} meters)", taxas == {CU_HORA},
            f"taxas distintas: {sorted(taxas)}")

    rel.secao("Fabric: reserva na API (priceType = Reservation)")
    filtro = montar_filtro(service="Microsoft Fabric", region=REGIAO, price_type="Reservation")
    itens, _, erro = buscar(filtro, max_paginas=5, timeout=timeout)
    if erro:
        rel.chk("buscar reserva do Fabric", False, erro)
        return
    por_termo = {i.get("reservationTerm"): i for i in itens}
    rel.chk(f"1 Year = {CU_ANO}", (por_termo.get("1 Year") or {}).get("retailPrice") == CU_ANO)
    rel.chk(f"3 Years = {CU_3ANOS}", (por_termo.get("3 Years") or {}).get("retailPrice") == CU_3ANOS)
    rel.chk("productName = 'Fabric Capacity Reservation'",
            all(i.get("productName") == "Fabric Capacity Reservation" for i in itens))
    rel.chk("meterName = 'Fabric Capacity CU'",
            all(i.get("meterName") == "Fabric Capacity CU" for i in itens))
    # Armadilha 4: a linha de reserva diz "1 Hour" e nao e por hora.
    rel.chk("unitOfMeasure diz '1 Hour' na linha de reserva (armadilha 4 continua valida)",
            all(i.get("unitOfMeasure") == "1 Hour" for i in itens),
            "a API mudou: reveja o gate 4 da Skill")

    rel.secao("Fabric: aritmetica da tabela de F SKU")
    for cus, od, rsv, anual in FSKU:
        calc_od = round(cus * CU_HORA * HORAS_MES, 2)
        calc_rsv = round(cus * CU_ANO / 12, 2)
        calc_anual = round(cus * CU_ANO, 2)
        rel.chk(f"F{cus}: {od} sob demanda / {rsv} reserva / {anual} anual",
                (calc_od, calc_rsv, calc_anual) == (od, rsv, anual),
                f"calculado {calc_od} / {calc_rsv} / {calc_anual}")
    rel.chk("reserva de 3 anos tem a mesma taxa/CU-mes que a de 1 ano",
            round(CU_3ANOS / 36, 2) == round(CU_ANO / 12, 2))
    desconto = round((1 - (CU_ANO / 12) / (CU_HORA * HORAS_MES)) * 100, 1)
    rel.chk("desconto da reserva = 40,6% (valor afirmado na Skill)", desconto == 40.6,
            f"calculado {desconto}%")


def conferir_armadilhas(rel: Relatorio, idx: dict, linhas: list[dict], completo: bool) -> None:
    rel.secao("armadilha 1: nome de servico enganoso")
    produtos = {r.get("productName") for r in linhas}
    for a, b in [("Azure Data Lake Storage Gen2 Flat Namespace",
                  "Azure Data Lake Storage Gen2 Hierarchical Namespace")]:
        rel.chk(f"'{a}' e '{b}' coexistem", a in produtos and b in produtos)

    rel.secao("armadilha 2: meterName nao e chave")
    por_meter = collections.defaultdict(set)
    for r in linhas:
        por_meter[(r.get("serviceName"), r.get("productName"), r.get("meterName"))].add(r.get("retailPrice"))
    divergentes = [k for k, v in por_meter.items() if len(v) > 1]
    afetadas = [r for r in linhas
                if len(por_meter[(r.get("serviceName"), r.get("productName"), r.get("meterName"))]) > 1]
    rel.chk(f"existe meterName com preco divergente ({len(divergentes)} combinacoes, "
            f"{len(afetadas)} linhas)", bool(divergentes))
    kv = sorted((r.get("tierMinimumUnits"), r.get("retailPrice"))
                for r in idx[("Key Vault", "Premium HSM-protected Advanced Key")])
    rel.chk("Key Vault / Premium HSM-protected Advanced Key tem 4 faixas de 5,00 a 0,40",
            kv == [(0.0, 5.0), (250.0, 2.5), (1500.0, 0.9), (4000.0, 0.4)], str(kv))

    rel.secao("armadilha 3: preco 0,0 nem sempre e faixa gratuita")
    zeros = [r for r in linhas if r.get("retailPrice") == 0.0]
    com_irmao = [r for r in zeros
                 if any(o.get("tierMinimumUnits", 0) > 0
                        for o in idx[(r.get("productName"), r.get("meterName"))])]
    sem_irmao = len(zeros) - len(com_irmao)
    pct = round(sem_irmao / len(zeros) * 100) if zeros else 0
    print(f"         {len(zeros)} zeros: {len(com_irmao)} com irmao de tier maior "
          f"(faixa gratuita), {sem_irmao} sem ({pct}%)")
    rel.chk("a maioria dos zeros NAO e faixa gratuita", pct > 50, f"{pct}%")
    for pn, mn in [("Azure Databricks", "Premium - Free Trial All-purpose Compute DBU"),
                   ("Azure Databricks Regional", "POC Non-Billable Serverless SQL DBU")]:
        rel.chk(f"meter proibido existe e custa 0,0: {mn}", preco(idx, pn, mn) == 0.0)

    rel.secao("armadilha 7: grafia inconsistente e colisao de preco")
    rel.chk("'All-purpose' e 'All-Purpose' coexistem no mesmo productName",
            preco(idx, "Azure Databricks", "Premium All-purpose Compute DBU") is not None
            and preco(idx, "Azure Databricks", "Premium All-Purpose Photon DBU") is not None)
    rel.chk("normalizar() iguala as duas grafias",
            normalizar("Premium All-purpose Compute") == normalizar("Premium All-Purpose Compute"))
    rel.chk("'OneLake' e 'Onelake' coexistem no productName OneLake",
            preco(idx, "OneLake", "OneLake BCDR Storage Hot Data Stored") is not None
            and preco(idx, "OneLake", "Onelake BCDR Storage Cool Data Stored") is not None)
    colisao = [r for r in linhas if r.get("retailPrice") == 0.0407]
    nomes = sorted({(r.get("productName"), r.get("meterName")) for r in colisao})
    print(f"         {len(nomes)} meters distintos a 0,0407:")
    for pn, mn in nomes:
        print(f"           {pn} / {mn}")
    rel.chk("meters distintos colidem em 0,0407 (a Skill afirma 6)", len(nomes) >= 2,
            f"encontrados {len(nomes)}")

    if not completo:
        print("\n         (contagens sobre a regiao inteira exigem --snapshot de sweep)")
        return

    rel.secao("contagens sobre a regiao inteira")
    rel.chk("snapshot e so de Consumption",
            all(r.get("type") == "Consumption" for r in linhas))
    chave5 = collections.Counter()
    precos5 = collections.defaultdict(set)
    for r in linhas:
        k = (r.get("serviceName"), r.get("productName"), r.get("meterName"),
             r.get("skuName"), r.get("tierMinimumUnits"))
        chave5[k] += 1
        precos5[k].add(r.get("retailPrice"))
    amb5 = [k for k, v in chave5.items() if v > 1]
    div5 = [k for k in amb5 if len(precos5[k]) > 1]
    print(f"         chave de 5 campos: {len(amb5)} combinacoes ambiguas, "
          f"{len(div5)} com preco divergente")
    for k in div5:
        print(f"           divergente: {k[0]} / {k[2]}")
    rel.chk("a chave de 5 campos resolve preco para os servicos em escopo",
            not [k for k in div5 if k[0] in SERVICOS],
            "ha divergencia em servico do catalogo: reveja a chave na Skill")

    rel.secao("Fabric F SKU: o que uma busca por 'F64' devolve (armadilha 5)")
    vazio = [r for r in linhas if "f64 capacity" in (r.get("skuName") or "").lower()]
    rel.chk("skuName 'F64 Capacity' nao existe", not vazio, f"{len(vazio)} linhas")
    vms = [r for r in linhas
           if r.get("serviceName") == "Virtual Machines"
           and (r.get("skuName") or "").startswith("F64")
           and "Spot" not in (r.get("skuName") or "")
           and "Low Priority" not in (r.get("skuName") or "")
           and "Windows" not in (r.get("productName") or "")]
    if vms:
        lo = round(min(r["retailPrice"] for r in vms) * HORAS_MES, 2)
        hi = round(max(r["retailPrice"] for r in vms) * HORAS_MES, 2)
        real = round(64 * CU_HORA * HORAS_MES, 2)
        print(f"         {len(vms)} VMs F64 Linux pagas: {lo} a {hi}/mes")
        print(f"         Fabric F64 real (sob demanda):  {real}/mes")
        rel.chk("as VMs F64 sao mais baratas que o Fabric F64 — valor errado parece plausivel",
                hi < real)


def conferir_unidades(rel: Relatorio, idx: dict, linhas: list[dict]) -> None:
    """Gate 8: mesmo retailPrice, unitOfMeasure diferente — erro de 100x."""
    rel.secao("gate 8: mesmo preco, unidade diferente")
    P = "Azure Data Lake Storage Gen2 Hierarchical Namespace"
    for normal, iterativo, preco in [
        ("Hot Write Operations", "Hot Iterative Write Operations", 0.091),
        ("Hot GRS Write Operations", "Hot GRS Iterative Write Operations", 0.182),
    ]:
        a = [r for r in idx[(P, normal)]]
        b = [r for r in idx[(P, iterativo)]]
        if not a or not b:
            rel.chk(f"{normal} vs {iterativo}", False, "meter nao encontrado")
            continue
        rel.chk(f"'{normal}' e '{iterativo}' custam os dois {preco}",
                a[0]["retailPrice"] == preco and b[0]["retailPrice"] == preco)
        rel.chk(f"...mas a unidade difere: {a[0]['unitOfMeasure']} vs {b[0]['unitOfMeasure']}",
                a[0]["unitOfMeasure"] != b[0]["unitOfMeasure"],
                "a API igualou as unidades: o gate 8 perdeu o sentido, reveja a Skill")
    dl = [r for r in idx[(P, "Delete Operations")]]
    if dl:
        rel.chk("'Delete Operations' custa 0,0 e nao tem irmao de tier maior (gate 3)",
                dl[0]["retailPrice"] == 0.0 and not any(r["tierMinimumUnits"] > 0 for r in dl))

    rel.secao("Virtual Machines: quanto do catalogo e armadilha")
    vm = [r for r in linhas if r.get("serviceName") == "Virtual Machines"]
    if not vm:
        print("         (sem VMs na fonte — use --snapshot para esta conferencia)")
        return
    spot = len([r for r in vm if "Spot" in (r.get("skuName") or "")])
    low = len([r for r in vm if "Low Priority" in (r.get("skuName") or "")])
    win = len([r for r in vm if "Windows" in (r.get("productName") or "")])
    ok = [r for r in vm if "Spot" not in (r.get("skuName") or "")
          and "Low Priority" not in (r.get("skuName") or "")
          and "Windows" not in (r.get("productName") or "")]
    print(f"         {len(vm)} meters: {spot} Spot, {low} Low Priority, {win} Windows, "
          f"{len(ok)} Linux pago ({round(len(ok)/len(vm)*100)}%)")
    rel.chk("a maioria dos meters de VM nao serve para cotacao paga em Linux",
            len(ok) / len(vm) < 0.5)
    d2 = {r.get("skuName"): r["retailPrice"] for r in vm
          if r.get("armSkuName") == "Standard_D2s_v5"
          and "Windows" not in (r.get("productName") or "")}
    rel.chk("Standard_D2s_v5 Linux pago = 0,153", d2.get("Standard_D2s_v5") == 0.153)
    rel.chk("Standard_D2s_v5 Spot = 0,028274 (proibido pela regra de modelo de compra)",
            d2.get("Standard_D2s_v5 Spot") == 0.028274)


# Comparacao regional afirmada na Skill: (serviceName, productName, meterName,
# brazilsouth, eastus, westeurope). None = nao conferido nessa regiao.
REGIONAL = [
    ("Microsoft Fabric", "Fabric Capacity", "Data Warehouse Capacity Usage CU", 0.28, 0.18, 0.22),
    ("Microsoft Fabric", "OneLake", "OneLake Storage Hot Data Stored", 0.0407, 0.026, 0.024),
    ("Storage", "Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot LRS Data Stored", 0.0326, 0.0208, 0.0196),
    ("Storage", "Azure Data Lake Storage Gen2 Hierarchical Namespace", "Hot Write Operations", 0.091, 0.065, 0.0702),
    ("Azure Databricks", "Azure Databricks Regional", "Premium Serverless SQL DBU", 1.09, 0.7, 0.91),
    ("Azure Databricks", "Azure Databricks", "Premium Jobs Compute DBU", 0.3, 0.3, 0.3),
    ("Azure Databricks", "Azure Databricks", "Premium All-purpose Compute DBU", 0.55, 0.55, 0.55),
    ("Key Vault", "Key Vault", "Operations", 0.03, 0.03, 0.03),
    ("Key Vault", "Key Vault HSM Pool", "Standard B1 Instance", 3.2, 3.2, 3.2),
]


def conferir_regioes(rel: Relatorio, timeout: int) -> None:
    """A allowlist e de brazilsouth. Confere a tabela de comparacao regional.

    Se a Azure equalizar os precos entre regioes, estas conferencias falham e a
    Skill precisa ser revista: o aviso de 56% deixaria de ser verdade.
    """
    rel.secao("comparacao regional (a allowlist vale so em brazilsouth)")
    cache = {}
    for svc in {r[0] for r in REGIONAL}:
        for rg in ("eastus", "westeurope"):
            itens, _, erro = buscar(montar_filtro(service=svc, region=rg, price_type="Consumption"),
                                    max_paginas=30, timeout=timeout)
            if erro:
                print(f"  AVISO  {svc}/{rg}: {erro}", file=sys.stderr)
            cache[(svc, rg)] = itens

    def preco_em(svc, pn, mn, rg):
        for r in cache[(svc, rg)]:
            if (r.get("productName") == pn and r.get("meterName") == mn
                    and r.get("tierMinimumUnits") == 0):
                return r.get("retailPrice")
        return None

    iguais, variam = 0, 0
    for svc, pn, mn, br, us, eu in REGIONAL:
        g_us, g_eu = preco_em(svc, pn, mn, "eastus"), preco_em(svc, pn, mn, "westeurope")
        rel.chk(f"{mn} em eastus = {us}", g_us == us,
                "nao encontrado" if g_us is None else f"API devolve {g_us}")
        rel.chk(f"{mn} em westeurope = {eu}", g_eu == eu,
                "nao encontrado" if g_eu is None else f"API devolve {g_eu}")
        if br == us == eu:
            iguais += 1
        else:
            variam += 1
    print(f"         {variam} meters variam por regiao, {iguais} sao iguais no mundo todo")
    rel.chk("existem meters que variam E meters que nao variam (nao ha fator unico)",
            variam > 0 and iguais > 0,
            "o padrao mudou: a regra de regiao da Skill precisa ser revista")
    fab_br = 0.28
    fab_us = preco_em("Microsoft Fabric", "Fabric Capacity", "Data Warehouse Capacity Usage CU", "eastus")
    if fab_us:
        delta = round((fab_br / fab_us - 1) * 100)
        print(f"         Fabric: brazilsouth e {delta}% mais caro que eastus")
        rel.chk("Skill afirma que Fabric custa 56% mais em brazilsouth", delta == 56,
                f"calculado {delta}%")
        f64_br, f64_us = round(64 * fab_br * 730, 2), round(64 * fab_us * 730, 2)
        rel.chk(f"F64: {f64_br} em brazilsouth contra {f64_us} em eastus",
                f64_br == 13081.6 and f64_us == 8409.6)


def conferir_skill(rel: Relatorio) -> None:
    rel.secao("consistencia da SKILL_unified.md")
    if not SKILL.exists():
        rel.chk(f"encontrar {SKILL.name}", False, str(SKILL))
        return
    texto = SKILL.read_text(encoding="utf-8")
    for t in EXIGE:
        rel.chk(f"a Skill contem: {t}", t in texto)
    for t in PROIBE:
        rel.chk(f"a Skill NAO contem: {t}", t not in texto,
                "instrucao que nao funciona voltou ao arquivo")


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    p = argparse.ArgumentParser(
        description="Confere os precos afirmados na SKILL contra a Retail Prices API",
        epilog="Falha nao e necessariamente bug: pode ser preco que a Azure mudou. "
               "Leia a falha e corrija a Skill, nao o numero esperado aqui.")
    p.add_argument("--snapshot", default=None,
                   help="JSON gerado por 'sonda_catalogo.py sweep --json'. "
                        "Sem isso, busca ao vivo apenas os servicos em escopo.")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--verbose", "-v", action="store_true",
                   help="mostra tambem as conferencias que passaram")
    args = p.parse_args(argv)

    try:
        linhas, fonte = carregar(args.snapshot, args.timeout)
    except FileNotFoundError:
        print(f"snapshot nao encontrado: {args.snapshot}", file=sys.stderr)
        print("gere um com: python sonda_catalogo.py sweep --region brazilsouth "
              "--max-pages 400 --json brazilsouth-AAAA-MM-DD.json", file=sys.stderr)
        return 2
    if not linhas:
        print("nenhuma linha carregada — API fora do ar ou snapshot vazio", file=sys.stderr)
        return 2

    completo = bool(args.snapshot)
    print(f"fonte: {fonte}")
    print(f"skill: {SKILL}")
    if not completo:
        print("modo parcial: contagens sobre a regiao inteira precisam de --snapshot")

    rel = Relatorio(args.verbose)
    idx = indexar(linhas)
    conferir_precos(rel, idx)
    conferir_fabric(rel, idx, args.timeout)
    conferir_armadilhas(rel, idx, linhas, completo)
    conferir_unidades(rel, idx, linhas)
    conferir_regioes(rel, args.timeout)
    conferir_skill(rel)

    print("\n" + "=" * 68)
    print(f"{rel.ok} conferencias passaram, {len(rel.falhas)} falharam")
    for f in rel.falhas:
        print(f"  - {f}")
    if rel.falhas:
        print("\nAntes de ajustar numero esperado aqui: confirme na API e corrija a Skill.")
        print("  python sonda_catalogo.py probe --service \"<servico>\" --region brazilsouth")
    return 1 if rel.falhas else 0


if __name__ == "__main__":
    sys.exit(main())
