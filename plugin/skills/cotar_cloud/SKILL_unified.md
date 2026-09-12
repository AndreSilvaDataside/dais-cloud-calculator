---
description: Gera estimativas de custo em nuvem (AWS e Azure) a partir de uma conversa guiada com o arquiteto. Para AWS, retorna link oficial do calculator.aws. Para Azure, retorna estimativa detalhada de custo com preços públicos via Retail Prices API.
allowed-tools:
  - mcp__aws-pricing-calculator__search_services
  - mcp__aws-pricing-calculator__get_service_fields
  - mcp__aws-pricing-calculator__create_estimate
  - mcp__aws-pricing-calculator__add_service
  - mcp__aws-pricing-calculator__export_estimate
  - mcp__azure-pricing-mcp__azure_price_search
  - mcp__azure-pricing-mcp__azure_cost_estimate
  - mcp__azure-pricing-mcp__azure_price_compare
  - mcp__azure-pricing-mcp__azure_discover_skus
  - mcp__azure-pricing-mcp__azure_region_recommend
  - mcp__azure-pricing-mcp__azure_ri_pricing
  - mcp__azure-pricing-mcp__databricks_dbu_pricing
  - mcp__azure-pricing-mcp__databricks_cost_estimate
---

# /cotar_cloud — Cotação de Arquitetura Cloud (AWS e Azure)

Gera estimativas de custo a partir de uma conversa guiada com o arquiteto.

- **AWS** → link oficial `calculator.aws` pronto para enviar ao parceiro
- **Azure** → estimativa detalhada com preços públicos via Retail Prices API (sem link da calculadora)

---

## Arquiteturas padrão Dataside — AWS

Quando o SA descrever um problema de negócio em AWS, consulte esta seção antes de sugerir
serviços. Prefira sempre os padrões abaixo quando o cenário se encaixar.

#### Arquitetura 1 — Modern Data Platform / Lakehouse AWS (sem Databricks)

Casos de uso: centralização de dados de múltiplas origens (batch + streaming), analytics
corporativo, Big Data com processamento distribuído pesado. Indicada quando o cliente
não possui licença Databricks ou prefere permanecer em serviços nativos AWS.

Serviços:
- Ingestão (bancos):      AWS DMS — replicação contínua de Oracle, MongoDB, SQL
- Ingestão (SaaS/APIs):   AWS AppFlow — Google Analytics, Salesforce e outras APIs SaaS
- Ingestão (arquivos):    AWS Glue — catálogo + ingestão de arquivos planos e APIs REST
- Storage:                Amazon S3 — camadas Bronze (bruto), Silver (limpo), Gold (modelado)
- Processamento:          Amazon EMR + Apache Spark (SQL Notebooks) — transformações distribuídas
- Orquestração:           AWS Step Functions — coordenação do pipeline de ponta a ponta
- Serving (DW):           Amazon Redshift — Data Warehouse analítico de alta performance
- Serving (ad-hoc):       Amazon Athena — queries SQL serverless direto no S3
- BI & IA:                Power BI / Amazon QuickSight + ferramentas de IA (All Layer)
- Governança:             Lake Formation + Glue Data Catalog + DataBrew/Data Quality
- Segurança:              IAM, KMS, VPC com endpoints privados
- Monitoramento:          Amazon CloudWatch

Observações:
- EMR é o serviço mais custoso; validar se o volume justifica vs. alternativas menores
- Redshift tem custo fixo de instância — avaliar Serverless para cargas intermitentes
- Para clientes financeiros/saúde: confirmar região sa-east-1 (LGPD/BACEN)

---

#### Arquitetura 2 — Modern Data Platform / Lakehouse com Databricks

Casos de uso: centralização de dados com plataforma unificada, pipelines Delta Lake,
ML/IA sobre o Lakehouse. Indicada quando o cliente já possui ou quer adotar Databricks
como plataforma central.

Serviços:
- Ingestão (bancos):      AWS DMS — replicação contínua de Oracle, MongoDB, SQL
- Ingestão (SaaS/APIs):   Databricks Lakeflow — substitui AppFlow para ingestão nativa
- Ingestão (arquivos):    AWS Glue — catálogo + ingestão de arquivos planos
- Storage:                Amazon S3 (Delta Lake / Delta Open Sharing) — Bronze, Silver, Gold
- Processamento:          Databricks (clusters Apache Spark + SQL Notebooks) — substitui EMR
- Orquestração:           AWS Step Functions — coordenação serverless do pipeline
- Serving (DW):           Databricks SQL Warehouse — substitui Redshift
- Serving (ad-hoc):       Amazon Athena — queries serverless direto no S3
- BI & IA:                Power BI / Amazon QuickSight + ferramentas de IA (All Layer)
- Governança:             Lake Formation + Glue Data Catalog + Unity Catalog (Databricks)
- Segurança:              IAM, KMS, VPC/RAM
- Monitoramento:          Amazon CloudWatch

Observações:
- Calcular SEMPRE EC2 no estimate AWS + DBU separado — nunca somar duas vezes
- Lakeflow substitui AppFlow — verificar disponibilidade de conectores para o cliente
- Para clientes financeiros/saúde: confirmar região sa-east-1

---

#### Arquitetura 3 — Modern Data Platform / Cloud Data Warehouse com Snowflake

Casos de uso: centralização de dados com Snowflake como motor híbrido de armazenamento,
processamento e DW. Indicada quando o cliente já possui Snowflake.

Serviços:
- Ingestão (bancos):      AWS DMS — replicação contínua de Oracle, MongoDB, SQL
- Ingestão (SaaS/APIs):   Snowflake (conectores nativos) — substitui AppFlow/Lakeflow
- Ingestão (arquivos):    AWS Glue — catálogo + ingestão de arquivos planos
- Storage:                Amazon S3 + Snowflake (tabelas gerenciadas e externas)
- Processamento:          Snowflake (queries + pipelines + Snowpark) — substitui EMR
- Orquestração:           AWS Step Functions — coordenação serverless
- Serving (DW):           Snowflake Data Warehouse — motor analítico centralizado
- Serving (ad-hoc):       Amazon Athena — queries serverless no S3
- BI & IA:                Power BI / Amazon QuickSight + aplicações de IA (All Layer)
- Governança:             Lake Formation + Glue Data Catalog + Snowflake Access Control
- Segurança:              IAM, KMS, VPC/RAM
- Monitoramento:          Amazon CloudWatch

Observações:
- Custo Snowflake FORA da AWS Pricing Calculator — estimar à parte (créditos compute + storage)
- Para clientes financeiros/saúde: confirmar região sa-east-1

---

#### Arquitetura 4 — Lakehouse Otimizado com Databricks (sem AWS Glue)

Casos de uso: Lakehouse Databricks simplificado, com menor dependência de serviços AWS.
Variação mais enxuta da Arquitetura 2 — Lakeflow centraliza toda a ingestão.

Serviços:
- Ingestão (bancos):      AWS DMS — replicação direta de Oracle, MongoDB, SQL
- Ingestão (demais):      Databricks Lakeflow — streaming (Kafka), SaaS, APIs e arquivos
- Storage:                Amazon S3 (Delta Lake) — Bronze, Silver, Gold
- Processamento:          Databricks (clusters Apache Spark + SQL Notebooks) — único motor
- Orquestração:           AWS Step Functions — gerencia execuções e gatilhos
- Serving (DW):           Databricks SQL Warehouse — DW serverless de alta performance
- Serving (ad-hoc):       Amazon Athena — queries interativas direto no S3
- BI & IA:                Power BI / Amazon QuickSight + Machine Learning (All Layer)
- Governança:             Lake Formation + Glue Data Catalog + Unity Catalog (Databricks)
- Segurança:              IAM, KMS, VPC/RAM
- Monitoramento:          Amazon CloudWatch

Observações:
- AWS Glue REMOVIDO — Lakeflow cobre SaaS, APIs, arquivos e streaming
- Calcular SEMPRE EC2 no estimate AWS + DBU separado — nunca somar duas vezes
- Diferença da Arquitetura 2: sem AWS Glue, Lakeflow mais centralizado
- Para clientes financeiros/saúde: confirmar região sa-east-1

---

## Arquiteturas padrão Dataside — Azure

<!--
  COMO PREENCHER:
  Adicione uma entrada por arquitetura padrão Dataside para Azure, seguindo o formato
  das arquiteturas AWS acima. Quando preenchidas, têm prioridade sobre o conhecimento
  geral do Claude na sugestão de serviços — e devem ser sinalizadas ao arquiteto como
  padrão da empresa.

  FORMATO DE CADA ENTRADA:
  #### [Nome da arquitetura]
  Casos de uso: [quando usar]
  Serviços:
  - [camada]: [serviço] — [observação]
  Observações: [restrições, variações, pontos de atenção]
-->

<!-- ADICIONE AS ARQUITETURAS PADRÃO DATASIDE AZURE ABAIXO -->

<!-- FIM DAS ARQUITETURAS PADRÃO AZURE -->

---

## Resolução de preço Azure — regras obrigatórias

Esta seção vale para **toda** consulta de preço Azure. Leia antes de chamar
`azure_price_search`, `azure_discover_skus` ou `azure_cost_estimate`.

O MCP devolve o que a Retail Prices API devolve. A API não valida intenção: uma
busca mal formada devolve linha plausível com preço errado. Todos os casos abaixo
foram verificados contra a API em `brazilsouth`, sobre 12.637 meters de
`type = 'Consumption'`.

### Chave de resolução — cinco campos, não um

Um preço só está resolvido quando os cinco campos estão fixados:

```
serviceName + productName + meterName + skuName + tierMinimumUnits
```

Por que os cinco:

| Chave usada | Combinações ambíguas no snapshot |
| --- | ---: |
| `serviceName` + `productName` + `meterName` | 455 (1.620 linhas) |
| os três acima + `skuName` + `tierMinimumUnits` | 73 |
| dessas 73, com **preço divergente** | 4 |

As 4 divergentes são Azure Maps, Foundry Tools e Service Bus — nenhuma no catálogo
deste projeto. Para os serviços em escopo, a chave de cinco campos resolve preço de
forma única.

Se a busca devolver mais de uma linha com preço diferente, **não escolha a
primeira**. Estreite a busca até sobrar uma, ou pergunte ao arquiteto qual variante.

### Normalização antes de comparar

A própria Azure escreve o mesmo conceito de formas diferentes no mesmo
`productName`. Casos verificados:

- `Premium All-purpose Compute DBU` ao lado de `Premium All-Purpose Photon DBU`
- `OneLake BCDR Storage Hot Data Stored` ao lado de `Onelake BCDR Storage Cool Data Stored`

São 1.983 `meterName` com hífen no snapshot. Procedimento:

1. Normalize caixa e separadores (hífen, espaço, underscore) dos dois lados.
2. Compare o nome normalizado contra a allowlist abaixo.
3. Exija **correspondência exata** após a normalização. Nunca aceite
   correspondência parcial ou "contém".

### Allowlist por serviço

Só use meter que esteja nesta lista. Meter fora da lista é sinal de resolução
errada — volte um passo e estreite a busca.

**Microsoft Fabric** (`serviceFamily = "Data"`, não `Analytics`)

| productName | meterName | preço |
| --- | --- | ---: |
| `Fabric Capacity` | qualquer `* Capacity Usage CU` | 0,28 / CU-hora |
| `Fabric Capacity` | `Capacity Overage Capacity Usage CU` | 0,84 / CU-hora |
| `Fabric Capacity Reservation` | `Fabric Capacity CU` | 1458,00 (1 ano) / 4374,00 (3 anos) |
| `OneLake` | `OneLake Storage Hot Data Stored` | 0,0407 / GB-mês |
| `OneLake` | `OneLake Storage Cool Data Stored` | 0,0221 / GB-mês |
| `OneLake` | `OneLake Storage Cold Data Stored` | 0,0083 / GB-mês |

**Azure Databricks** — ver a seção própria na Fase 7. `productName` decide o
modelo de cobrança:

| productName | modelo | somar VM? |
| --- | --- | --- |
| `Azure Databricks` | clássico | **sim**, DBU + VM do cluster |
| `Azure Databricks Regional` | serverless | **não**, o DBU já inclui compute |

**ADLS Gen2** — `serviceName = "Storage"`,
`productName = "Azure Data Lake Storage Gen2 Hierarchical Namespace"`.

São 33 meters só de `Data Stored`, um por combinação de camada e redundância. O
`skuName` é a chave (`Hot GRS`, `Cool LRS`, `Archive LRS`, …). Amplitude
verificada: `Archive LRS` a 0,002 contra `Hot RA-GZRS` a 0,091688 — fator 46.
Camada e redundância **têm que ser premissa declarada**.

Referência (primeira faixa, `tierMinimumUnits = 0`):

| skuName | preço / GB-mês |
| --- | ---: |
| `Hot LRS` | 0,0326 |
| `Hot ZRS` | 0,0407 |
| `Hot GRS` | 0,0652 |
| `Cool LRS` | 0,0177 |
| `Cool GRS` | 0,0354 |
| `Archive LRS` | 0,002 |

As camadas `Hot *` são escalonadas em três faixas: `tierMinimumUnits` 0, 51.200 e
512.000 GB. Para volume acima de 50 TB, some por faixa — não aplique a primeira
faixa ao volume inteiro.

**Key Vault** — `serviceName = "Key Vault"`, 16 meters.
`productName = "Key Vault"` para o comum; `Key Vault HSM Pool` /
`Standard B1 Instance` custa 3,20 por hora (2.336,00/mês). Não ofereça HSM Pool sem
o arquiteto ter pedido HSM dedicado.

**Egress** — `serviceName = "Bandwidth"`. Duas séries paralelas por roteamento, o
`productName` desambigua:

| productName | preço após os 100 GB |
| --- | ---: |
| `Bandwidth - Routing Preference: Internet` | 0,12 / GB |
| `Rtn Preference: MGN` | 0,181 / GB |

Os primeiros 100 GB/mês são gratuitos (`tierMinimumUnits = 0` a 0,0 — este é um
zero legítimo). Na falta de informação, use `Routing Preference: Internet` e
declare como premissa. Transferência entre zonas de disponibilidade custa 0,01/GB
em cada direção; entre regiões, 0,16/GB.

**Private Link e Private Endpoint** — **não existem** na Retail Prices API, nem em
`brazilsouth` nem em `eastus`. A varredura completa devolveu só dois falsos
positivos (`Notification Hubs / Private Link Unit` a 35,00/mês e
`Azure Container Apps / Environment Private Endpoint` a 0,20/hora) — nenhum dos
dois serve. Entram como **premissa declarada sem valor**:

```
📌 Private Endpoint / Private Link: incluído na arquitetura, sem valor na
   estimativa — não há meter público na Retail Prices API. Confirmar com o
   parceiro Microsoft antes de fechar a proposta.
```

### Gates de validação — checar antes de somar

Sete falhas verificadas. Cada uma produz número plausível e errado.

**1. Nome de serviço enganoso entre gerações e produtos.** Seis pares
confirmados no snapshot:

| Devolvido pela busca | O que o arquiteto pediu |
| --- | --- |
| `Data Lake Store` (Gen1) | `Azure Data Lake Storage Gen2` |
| `... Flat Namespace` | `... Hierarchical Namespace` |
| `Azure Purview` | `Microsoft Purview` |
| `SQL database in Microsoft Fabric` | `SQL Database` |
| `Azure Cloud HSM` | `Key Vault HSM Pool` |
| `Private Mobile Network` (Azure Private 5G) | qualquer busca por "private" |

**2. `meterName` não é chave.** Em 8% das linhas (1.005 de 12.637) o mesmo
`meterName` aponta para preços diferentes. Caso verificado — `Key Vault` /
`Premium HSM-protected Advanced Key`, quatro linhas:

| `tierMinimumUnits` | preço |
| ---: | ---: |
| 0 | 5,00 |
| 250 | 2,50 |
| 1.500 | 0,90 |
| 4.000 | 0,40 |

Fator 12 entre a primeira e a última. Sem `tierMinimumUnits` a resposta é sorteio.

**3. Preço 0,0 é falha de resolução até prova em contrário.** Dos 478 zeros do
snapshot, só **153** são primeira faixa gratuita — reconhecíveis por terem meter
irmão com `tierMinimumUnits` maior. Os outros **325** (68%) são `Free Trial`,
`POC Non-Billable`, variantes gratuitas de meter pago e operações sem custo —
casos verificados:
`Premium - Free Trial All-purpose Compute DBU`,
`POC Non-Billable Serverless SQL DBU`, `Storage Mirroring Free Data Stored`.

Só aceite 0,0 se **uma** destas for verdadeira:
- existe meter irmão com `tierMinimumUnits` maior (é faixa gratuita — ex.: egress
  até 100 GB);
- o meter está explicitamente na allowlist como gratuito.

Caso contrário, trate como resolução falhada e busque de novo. **Nunca** entregue
linha a 0,0 na proposta sem dizer por quê.

**4. Em linha de reserva, `unitOfMeasure` mente.** Verificado ao vivo: Fabric
devolve `unitOfMeasure = "1 Hour"` com `retailPrice = 1458.00`. Lido
literalmente, dá 1458/hora — erro de mais de cinco mil vezes.

O divisor vem do campo **`reservationTerm`**, não do `unitOfMeasure`:

```
reservationTerm = "1 Year"   → retailPrice é o compromisso anual por unidade
                               mensal = retailPrice / 12
reservationTerm = "3 Years"  → retailPrice é o compromisso de 36 meses
                               mensal = retailPrice / 36
```

Em qualquer linha com `type = "Reservation"`, ignore `unitOfMeasure` e use
`reservationTerm`.

**5. Fabric não tem meter de F SKU.** `skuName = "F64 Capacity"` devolve **vazio** —
verificado. Buscar só por "F64" devolve 14 máquinas virtuais da série F, entre
3.060,16 e 8.166,51/mês, contra 13.081,60/mês do Fabric F64 real. O valor errado
cabe numa proposta sem levantar suspeita. Fabric é **calculado**, não consultado —
ver a seção própria na Fase 6.

**6. Databricks clássico é DBU + VM; serverless é só DBU.** Misturar os dois conta
o compute duas vezes ou subestima. `productName` decide — ver a Fase 7.

**7. Colisão de preço entre meters diferentes.** **Seis** meters distintos custam
exatamente **0,0407** por GB-mês:

| productName | meterName |
| --- | --- |
| `OneLake` | `OneLake Storage Hot Data Stored` |
| `OneLake` | `Storage Mirroring Data Stored` |
| `Azure Databricks Regional` | `Premium Databricks Storage Unit DSU` |
| `Azure Data Lake Storage Gen2 Hierarchical Namespace` | `Hot ZRS Data Stored` |
| `Azure Data Lake Storage Gen2 Flat Namespace` | `Hot ZRS Data Stored` |
| `General Block Blob v2 Hierarchical Namespace` | `Hot ZRS Data Stored` |

Escolher o errado **não muda o total** e não é detectável revisando valores. Pior:
as três últimas linhas combinam esta armadilha com a armadilha 1 — `Flat Namespace`
e `Hierarchical Namespace` custam o mesmo em `Hot ZRS`, então escolher a geração
errada de ADLS passa batido nessa camada e só aparece em outra.

A única defesa é fixar o meter pelos cinco campos na hora da busca, não conferir o
número depois.

### Premissa de data do preço

Preço público da Retail Prices API muda sem aviso. Toda saída tem que declarar a
data da consulta:

```
📌 Preços: Azure Retail Prices API, consulta de [DD/MM/AAAA], região [região],
   moeda USD, preço público sem desconto negociado.
```

Se a API demorar ou falhar durante a conversa, **diga isso ao arquiteto** e não
preencha com valor de memória. Número não verificado não entra em proposta.

---

## Comportamento central: modo conversa obrigatório

**Nunca peça tudo de uma vez. Nunca gere a estimativa sem ter as informações
mínimas. Aja como um arquiteto sênior conversando com o colega.**

O arquiteto pode invocar `/cotar_cloud` com muito pouco contexto. Isso é esperado.
Sua responsabilidade é conduzir a conversa fazendo perguntas curtas, uma ou duas
por vez, até ter o suficiente para gerar a estimativa.

---

## Fluxo de conversa

### Fase 1 — Identificar o provider

Ao ser invocado, verifique se o provider foi informado:

**Se o provider foi informado** (ex: "quero cotar um lakehouse na AWS", "cliente Azure")
→ siga para a **Fase 2** com o provider identificado.

**Se não foi informado** → pergunte antes de qualquer outra coisa:

```
Antes de começar: esse cliente usa AWS ou Azure?
```

Só avance após a resposta.

---

### Fase 2 — Abertura (o que você já tem?)

Com o provider definido, avalie o que foi passado:

**Se o SA listou serviços específicos** → pule a Fase 3 e vá direto para a
Fase 4 (dimensionamento).

**Se o SA descreveu um problema de negócio** (sem listar serviços) → siga para a
**Fase 3** (sugestão de arquitetura).

**Se o SA passou muito pouco ou nada** → lance no máximo 2 perguntas:
1. Qual o contexto / cenário do cliente?
2. Quais serviços está pensando? (se não listou)

---

### Fase 3 — Sugestão de arquitetura

Se o SA descreveu o problema do cliente sem listar serviços:

**1. Verifique primeiro as arquiteturas padrão Dataside** do provider identificado
(seções no topo). Se houver match, use esse padrão como base e sinalize:

```
Com base no que você descreveu, sugiro a arquitetura padrão Dataside
para [Nome da arquitetura]:

🗄️  Storage:       [serviço] — [motivo]
⚙️  Processamento: [serviço] — [motivo]
📊  Serving:       [serviço] — [motivo]
🔐  Segurança:     [serviço] — [motivo]

Faz sentido para esse cliente? Posso ajustar antes de dimensionar.
```

**2. Se não houver match**, use seu conhecimento geral de padrões para o provider
sem mencionar "padrão Dataside":

```
Com base no que você descreveu, sugiro essa arquitetura:

🗄️  Storage:       [serviço] — [motivo]
⚙️  Processamento: [serviço] — [motivo]
📊  Serving:       [serviço] — [motivo]
🔐  Segurança:     [serviço] — [motivo]

Faz sentido? Posso ajustar antes de partir para o dimensionamento.
```

Aguarde confirmação antes de avançar.

---

### Fase 4 — Dimensionamento progressivo

Com a arquitetura confirmada, colete o dimensionamento **uma ou duas perguntas
por vez**. Use tom consultivo:

- *"Entendido. Para o storage, qual o volume de dados esperado — em GB ou TB?"*
- *"Legal. O processamento vai rodar quantas horas por dia, em média?"*
- *"Você mencionou banco relacional — qual engine e tamanho de instância?"*

Se o arquiteto não souber, **sugira um valor razoável com justificativa curta**
e siga em frente.

Ordem de prioridade:
1. Região (AWS: padrão `sa-east-1` | Azure: padrão `brazilsouth`)
2. Volume de dados (GB/TB em storage)
3. Tipo de processamento e instância
4. Horas por dia e dias por mês em Produção
5. Banco de dados (engine, tamanho)
6. Serving layer (DW, tipo e tamanho)
7. Serviços de suporte (segurança, orquestração, monitoramento)

---

### Fase 5 — Confirmação antes de gerar

Quando tiver as informações mínimas, faça um resumo e confirme:

```
Ok, tenho o suficiente para gerar. Deixa eu confirmar o que vou cotar:

📋 Cenário: [nome do cliente / projeto]
☁️  Provider: [AWS | Azure]
🌎 Região: [região]

Produção:
  - [serviço 1]: [parâmetros]
  - [serviço 2]: [parâmetros]

Homologação e Desenvolvimento: sizing proporcional automático.

Gero assim ou quer ajustar algo?
```

---

### Fase 6 — Gerar a estimativa

#### Se provider = AWS

Use as tools na sequência:

```
create_estimate → description: "Cotação [Cliente/Projeto] — [data]"
add_service (grupo: "Produção")
add_service (grupo: "Homologação")
add_service (grupo: "Desenvolvimento")
export_estimate
```

**Regras de sizing por ambiente:**

| Ambiente        | Horas de uso    | Hardware         |
|-----------------|-----------------|------------------|
| Produção        | 100% (730h/mês) | Tamanho definido |
| Homologação     | ~30% (200h/mês) | Mesmo hardware   |
| Desenvolvimento | ~50% horas prod | 1 tier abaixo    |

Exemplos de "1 tier abaixo": `m5.xlarge` → `m5.large`, `r5.2xlarge` → `r5.xlarge`.

**Sempre usar preços on-demand.** Nunca Reserved Instances, Savings Plans ou Spot.

Serviços compartilhados entre ambientes (Secrets Manager, Route 53) são adicionados
uma única vez, fora dos grupos.

#### Se provider = Azure

**Antes de qualquer busca, aplique a seção
"Resolução de preço Azure — regras obrigatórias"** (chave de cinco campos,
allowlist e os sete gates de validação). O MCP não valida intenção: busca mal
formada devolve preço plausível e errado.

Use as tools na sequência para cada serviço da arquitetura:

```
azure_discover_skus    → encontrar o SKU correto para o serviço
azure_cost_estimate    → calcular custo mensal (Produção)
azure_cost_estimate    → calcular custo mensal (Homologação: ~30% de uso)
azure_cost_estimate    → calcular custo mensal (Desenvolvimento: ~50% de uso, 1 tier abaixo)
```

**Regras de sizing por ambiente — padrão:**

| Ambiente        | Horas de uso    | Hardware         |
|-----------------|-----------------|------------------|
| Produção        | 100% (730h/mês) | Tamanho definido |
| Homologação     | ~30% (200h/mês) | Mesmo hardware   |
| Desenvolvimento | ~50% horas prod | 1 tier abaixo    |

Para Azure, "1 tier abaixo" é o tamanho imediatamente menor da **mesma** série
(`Standard_D4s_v5` → `Standard_D2s_v5`), nunca troca de série — trocar de série
muda a relação vCPU/memória e invalida a comparação.

**Três serviços não seguem esta tabela.** Use a regra da seção própria, que
prevalece sobre esta:

| Serviço | Por quê | Onde |
| --- | --- | --- |
| Microsoft Fabric | não tem "tier de hardware"; reserva é 730h fixas | seção Fabric, abaixo |
| Azure Databricks | horas dependem de autoterminação; serverless não tem VM | Fase 7 |
| Armazenamento (ADLS, OneLake) | cobra por volume, não por hora — não reduza por horas | ver abaixo |

**Armazenamento não escala por horas.** ADLS Gen2 e OneLake cobram pelo volume
armazenado o mês inteiro, nos três ambientes. Reduza o **volume** em HML e Dev
(~30% e ~10% do volume de produção é ponto de partida razoável), nunca as horas.
Aplicar 200h/mês a uma linha de storage subestima em ~3,6×.

**Modelo de compra — regra por serviço, não global:**

- **Padrão: on-demand / retail público.** Nunca Spot, nunca desconto negociado.
- **Exceção — Microsoft Fabric:** apresente **os dois** modelos (sob demanda e
  reserva). A reserva é 40,6% mais barata e é o que o cliente efetivamente compra;
  omiti-la superestima a proposta em quase o dobro. Mostrar os dois e deixar o
  arquiteto escolher — nunca escolher em silêncio.
- **Exceção — VM de longa permanência:** se o arquiteto pedir explicitamente
  comparação com Reserved Instance, apresente como linha adicional, nunca
  substituindo o on-demand.

Em qualquer caso, o modelo usado entra nas premissas declaradas.

Use `azure_region_recommend` se o arquiteto não tiver preferência de região e quiser
a opção mais barata para o serviço principal.

#### Microsoft Fabric on Azure

**Não existe meter de F SKU na Retail Prices API.** `skuName = "F64 Capacity"`
devolve vazio. O preço do Fabric é **calculado a partir do CU**, não consultado.
Ver armadilha 5 na seção de resolução de preço.

Custo de Fabric tem **duas parcelas obrigatórias**: capacidade + armazenamento
OneLake. Nunca entregue só uma.

**Parcela 1 — capacidade (CU)**

O F SKU é uma quantidade de Capacity Units. O número no nome é o número de CUs:
F2 = 2 CU, F64 = 64 CU. Duas formas de compra, e o cliente costuma comprar a
segunda:

```
sob demanda:   CUs × 0,28 × horas do mês
reserva 1 ano: CUs × 1458,00 ÷ 12   (por mês)
reserva 3 anos: CUs × 4374,00 ÷ 36  (por mês)
```

A reserva de 3 anos tem a **mesma** taxa por CU-hora da de 1 ano (121,50 por
CU/mês nas duas). Não há desconto adicional — só travamento de preço por mais
tempo. Não apresente 3 anos como economia maior que 1 ano.

Tabela de referência, `brazilsouth`, 730 h/mês:

| F SKU | CUs | Sob demanda/mês | Reserva/mês | Compromisso anual |
| --- | ---: | ---: | ---: | ---: |
| F2 | 2 | 408,80 | 243,00 | 2.916,00 |
| F4 | 4 | 817,60 | 486,00 | 5.832,00 |
| F8 | 8 | 1.635,20 | 972,00 | 11.664,00 |
| F16 | 16 | 3.270,40 | 1.944,00 | 23.328,00 |
| F32 | 32 | 6.540,80 | 3.888,00 | 46.656,00 |
| F64 | 64 | 13.081,60 | 7.776,00 | 93.312,00 |
| F128 | 128 | 26.163,20 | 15.552,00 | 186.624,00 |
| F256 | 256 | 52.326,40 | 31.104,00 | 373.248,00 |

A reserva é **40,6% mais barata** que sob demanda. Esse desconto é grande demais
para ser escolhido em silêncio: **apresente os dois modelos** e deixe o arquiteto
decidir. Ver a regra de modelo de compra na Fase 6.

Meters para confirmar o preço unitário quando quiser validar na API:

```
capacidade: productName = "Fabric Capacity"
            meterName   = qualquer "* Capacity Usage CU"   → 0,28 / CU-hora
reserva:    productName = "Fabric Capacity Reservation"
            meterName   = "Fabric Capacity CU"
            skuName     = "Fabric Capacity"
            type        = "Reservation"  → 1458,00 (1 Year) / 4374,00 (3 Years)
```

Todos os ~100 meters de workload (`Data Warehouse Capacity Usage CU`,
`Eventhouse Capacity Usage CU`, `Spark Memory Optimized Capacity Usage CU`,
`Power BI Capacity Usage CU`, …) custam **o mesmo 0,28**. Não existe workload mais
caro que outro por CU — o que varia é quantos CUs cada um consome, e isso a API não
informa. **Não** tente cotar por workload individual: dimensione o F SKU total.

**Parcela 2 — armazenamento OneLake**

```
productName = "OneLake"
meterName   = "OneLake Storage Hot Data Stored"   → 0,0407 / GB-mês
```

Cuidado: `Storage Mirroring Data Stored` custa exatamente o mesmo 0,0407 e não é
a mesma coisa (armadilha 7). Fixe o meter pelo nome completo.

Camadas frias, se o arquiteto mencionar arquivamento:

| meterName | preço / GB-mês |
| --- | ---: |
| `OneLake Storage Hot Data Stored` | 0,0407 |
| `OneLake Storage Cool Data Stored` | 0,0221 |
| `OneLake Storage Cold Data Stored` | 0,0083 |

Na falta de informação, use **Hot** e declare como premissa.

**Excedente de capacidade**

`Capacity Overage Capacity Usage CU` custa **0,84** — o triplo de 0,28. Não inclua
excedente na estimativa; inclua a premissa:

```
📌 Fabric: premissa de que a carga cabe na capacidade F[N] contratada.
   Excedente (overage) é cobrado a 0,84/CU-hora, 3× a taxa normal.
```

**Dimensionamento do F SKU**

Pergunte qual F SKU o cliente pretende usar. Se o arquiteto não souber, sugira e
siga:

- Carga leve (notebooks exploratórios, DW pequeno, 1 equipe): **F8–F16**
- Carga média (pipelines diários, DW corporativo, 2–3 equipes): **F32–F64**
- Carga pesada (processamento contínuo, múltiplas equipes): **F128+**

Declare o sizing como premissa — ele é estimativa, não medição.

**Ambientes em Fabric**

Fabric não tem "1 tier abaixo de hardware" como VM. A dimensão que varia é o F SKU
e, em não-produção, geralmente **não se compra reserva**:

| Ambiente | Capacidade | Modelo de compra | OneLake |
| --- | --- | --- | --- |
| Produção | F[N] definido | reserva **e** sob demanda (mostrar os dois) | volume total |
| Homologação | F[N] dois tiers abaixo (mín. F2) | sob demanda, capacidade pausável | ~30% do volume |
| Desenvolvimento | F2 ou F4 | sob demanda, capacidade pausável | ~10% do volume |

Duas diferenças em relação à regra genérica de ambientes, e elas são
intencionais:

1. **Não aplique a redução de horas (200h/mês) ao F SKU reservado.** Reserva é
   compromisso de 730 h/mês independente de uso. Redução de horas só faz sentido em
   capacidade sob demanda, que pode ser pausada.
2. Capacidade Fabric sob demanda **pode ser pausada** — se o arquiteto confirmar
   que HML e Dev ficam pausados fora do horário comercial, use 200 h/mês e declare
   a premissa. Se não confirmar, use 730 h/mês.

Armazenamento OneLake **não pausa**: cobra pelo volume o mês inteiro nos três
ambientes.

**Saída de Fabric**

Apresente a conta aberta, as duas parcelas separadas, os dois modelos de compra:

```
🔶 Microsoft Fabric — Produção (F64)
   Capacidade sob demanda: 64 CU × 0,28 × 730h    = 13.081,60/mês
   Capacidade com reserva: 64 CU × 1458,00 ÷ 12   =  7.776,00/mês  (−40,6%)
   OneLake (Hot):          [N] GB × 0,0407        =    [X]/mês
   ─────────────────────────────────────────────────────────────
   Total sob demanda: [X]/mês   |   Total com reserva: [X]/mês
   Compromisso anual da reserva: 93.312,00
```

---

### Fase 7 — Databricks (se aplicável)

#### Databricks on AWS

O custo é composto por duas partes:
- **Instância EC2** → já incluída no estimate AWS (Fase 6)
- **DBU** → calculado abaixo, separado

**Sempre forneça a estimativa de DBU.** Apresente a conta aberta.

| Tipo de cluster     | DBU/hora por nó | Preço/DBU (sa-east-1) |
|---------------------|-----------------|------------------------|
| Jobs Compute        | 1.0 DBU         | ~$0.20                 |
| All-Purpose Compute | 1.0 DBU         | ~$0.40                 |
| Jobs Compute Light  | 0.5 DBU         | ~$0.20                 |

Fórmula: `DBU/hora × nº de nós × horas/mês × preço/DBU`

Aplique regras de ambiente (30%/50%) para Homologação e Desenvolvimento.

#### Databricks on Azure

**Antes de calcular, decida o modelo de cobrança. Ele muda o que entra na soma.**

Na Retail Prices API o `productName` separa dois modelos que **não** se somam:

| productName | modelo | o que cobrar |
| --- | --- | --- |
| `Azure Databricks` | **clássico** | DBU **+** a VM do cluster, separadamente |
| `Azure Databricks Regional` | **serverless** | **só** o DBU — já inclui o compute |

Pergunte ao arquiteto qual dos dois, ou infira:

- Cluster com tipo de VM definido, pool, autoscale de nós → **clássico**
- SQL Warehouse serverless, Serverless Jobs, Model Serving → **serverless**
- Na dúvida, pergunte. Errar aqui erra o total em ~2×, para cima ou para baixo.

**Clássico — DBU + VM**

Duas parcelas, ambas obrigatórias:

```
DBU: DBU/hora por nó × nº de nós × horas/mês × preço do DBU
VM:  preço/hora da VM × nº de nós × horas/mês
```

A VM é cotada como `serviceName = "Virtual Machines"` normal, no mesmo cluster.
`productName = "Azure Databricks"`, preços verificados em `brazilsouth`:

| meterName | preço / DBU-hora |
| --- | ---: |
| `Premium All-purpose Compute DBU` | 0,55 |
| `Premium All-Purpose Photon DBU` | 0,55 |
| `Standard All-purpose Compute DBU` | 0,40 |
| `Standard All-Purpose Photon DBU` | 0,40 |
| `Premium Jobs Compute DBU` | 0,30 |
| `Premium Jobs Compute Photon DBU` | 0,30 |
| `Standard Jobs Compute DBU` | 0,15 |
| `Premium Jobs Light Compute DBU` | 0,22 |
| `Standard Jobs Light Compute DBU` | 0,07 |
| `Premium SQL Analytics DBU` | 0,22 |
| `Premium Core Compute Delta Live Tables DBU` | 0,30 |
| `Premium Pro Compute Delta Live Tables DBU` | 0,38 |
| `Premium Advanced Compute Delta Live Tables DBU` | 0,54 |

Repare em `All-purpose` e `All-Purpose` convivendo no mesmo `productName`
(armadilha 7) — normalize antes de comparar.

Add-ons de segurança somam por cima do DBU quando o cliente os contrata:
`Premium Enhanced Security and Compliance DBU` a 0,10 e
`... Mission Critical Add-on DBU` a 0,15. Só inclua se o arquiteto pedir.

**Serverless — só DBU**

`productName = "Azure Databricks Regional"`. **Não some VM.** Preços verificados:

| meterName | preço / DBU-hora |
| --- | ---: |
| `Premium Serverless SQL DBU` | 1,09 |
| `Premium Interactive Serverless Compute DBU` | 1,09 |
| `Premium SQL Compute Pro DBU` | 0,85 |
| `Premium Automated Serverless Compute DBU` | 0,59 |
| `Premium Database Serverless Compute DBU` | 0,42 |
| `Premium Model Training DBU` | 1,11 |
| `Premium Serverless Realtime Inferencing DBU` | 0,112 |

O DBU serverless é mais caro por hora justamente porque embute o compute —
comparar 1,09 serverless contra 0,55 clássico sem contar a VM do clássico dá
conclusão invertida.

Armazenamento serverless: `Premium Databricks Storage Unit DSU` a **0,0407** — o
mesmo valor de três outros meters (armadilha 7). Fixe pelo nome completo.

**Meters proibidos**

Nunca use na estimativa, mesmo que a busca os devolva primeiro — todos custam 0,0
e não são gratuitos de verdade (armadilha 3):

- `Premium - Free Trial All-purpose Compute DBU`, `Standard - Free Trial ...`
- `Premium - Free Trial SQL Compute Pro DBU`
- qualquer `POC Non-Billable ... DBU`

**Tools do MCP**

```
databricks_dbu_pricing    → confirmar o preço do DBU do tipo de cluster
databricks_cost_estimate  → estimativa mensal
```

Se `databricks_cost_estimate` devolver "compute + DBU" para um cenário
**serverless**, o compute está duplicado — descarte a parcela de compute e use só o
DBU. A tool não distingue os dois `productName`.

**Ambientes**

Aplique a regra geral (Produção 730h, HML ~200h, Dev ~50% das horas de produção).
Duas diferenças para Databricks:

1. Em **Dev**, "1 tier abaixo" reduz a **VM** do cluster no clássico, e reduz o
   **número de nós** no serverless (onde não há VM a reduzir).
2. Clusters com autoterminação não rodam 730 h/mês. Se o arquiteto confirmar
   autoterminação, use as horas reais de job e declare a premissa.

**Saída de Databricks**

```
🔷 Azure Databricks — Produção (clássico, Premium Jobs Compute)
   DBU: [N] DBU/h × [N] nós × [N]h × 0,30  = [X]/mês
   VM:  [tipo] × [N] nós × [N]h × [preço]  = [X]/mês
   ─────────────────────────────────────────────────
   Total Databricks: [X]/mês
```

```
🔷 Azure Databricks — Produção (serverless, Premium Serverless SQL)
   DBU: [N] DBU/h × [N]h × 1,09 = [X]/mês  (compute incluído — sem VM)
   ─────────────────────────────────────────────────
   Total Databricks: [X]/mês
```

---

### Fase 8 — Serviços fora do escopo

Se um serviço necessário não puder ser estimado:

```
⚠️ [Nome do Serviço] não está coberto pela estimativa automática.
Preço disponível em: [URL da pricing page]
Estimativa manual: [regra de cobrança + valor estimado se possível]
Informar separadamente ao parceiro.
```

Exemplos: Snowflake (AWS ou Azure — valores via PDF da calculadora oficial, sem API),
Vector Search, serviços em preview.

---

## Formato de saída final

### AWS

```
✅ Estimate gerado

🔗 Link oficial (AWS): https://calculator.aws/...
   → Enviar este link ao parceiro AWS

📊 Custos mensais estimados:
   Produção:        $X.XXX/mês
   Homologação:     $X.XXX/mês
   Desenvolvimento: $X.XXX/mês
   ──────────────────────────────
   Total AWS:       $X.XXX/mês

[Se houver Databricks:]
🔷 Databricks (DBU — separado do estimate AWS):
   DBU: [N] DBU/h × [N] nós × [N]h × $[X] = ~$XXX/mês (Produção)
   Homologação e Dev: proporcional
   → Confirmar em databricks.com/product/pricing e anexar print à proposta
   Total estimado (AWS + Databricks): ~$X.XXX/mês

📋 Serviços incluídos: [lista]
📌 Premissas assumidas: [lista]

💡 Próximos passos:
   1. Revisar o link e ajustar parâmetros se necessário
   2. Anexar o link à proposta no sistema interno
   [3. Print da calculadora Databricks, se aplicável]
```

### Azure

```
✅ Estimativa gerada (Azure Retail Prices — preço público on-demand)

⚠️ Não há geração automática de link para a Azure Pricing Calculator.
   Recomendado: abrir calculator.microsoft.com e preencher manualmente
   para gerar o link oficial caso o parceiro exija.

📊 Custos mensais estimados:
   Produção:        $X.XXX/mês
   Homologação:     $X.XXX/mês
   Desenvolvimento: $X.XXX/mês
   ──────────────────────────────
   Total Azure:     $X.XXX/mês

[Se houver Databricks:]
🔷 Databricks on Azure (incluído no total acima):
   Compute: $XXX/mês | DBU: $XXX/mês
   Total Databricks: ~$XXX/mês (Produção)

📋 Serviços incluídos: [lista]
📌 Premissas assumidas: [lista]
   Região: [região] | Moeda: USD | Preço: retail público, sem desconto negociado
   Fonte: Azure Retail Prices API, consulta de [DD/MM/AAAA]
   [Fabric: modelo de compra apresentado — sob demanda e reserva de 1 ano]
   [ADLS Gen2: camada e redundância assumidas — ex. Hot GRS]
   [Private Endpoint / Private Link: sem valor, não há meter público na API]

💡 Próximos passos:
   1. Validar preços em prices.azure.com se necessário
   2. Preencher calculator.microsoft.com para gerar link oficial ao parceiro
   [3. Ajustar preços se o cliente tiver desconto negociado]
```

---

## Erros comuns a evitar

- **Não começar sem saber o provider** — sempre confirmar AWS ou Azure primeiro
- **Não fazer um formulário** — a conversa deve ser fluida, não um checklist
- **Não travar por falta de informação** — sugerir valor razoável e seguir
- **Não pular a sugestão de arquitetura** — quando o SA descreve problema sem listar serviços
- **Não ignorar padrões Dataside cadastrados** — se houver match, prefira sempre o padrão
- **Não usar preços com desconto negociado** — sempre retail público
- **Não escolher modelo de compra em silêncio** — em Fabric, mostrar sob demanda
  E reserva; a diferença é 40,6%
- **Não somar EC2 do Databricks (AWS) duas vezes** — já está no estimate AWS
- **Não somar VM do Databricks serverless (Azure)** — `Azure Databricks Regional`
  já inclui compute no DBU
- **Não buscar F SKU do Fabric na API** — não existe meter de F SKU; o preço é
  calculado a partir do CU
- **Não aceitar preço 0,0 sem justificar** — 68% dos zeros (325 de 478) não são
  faixa gratuita
- **Não resolver preço por `meterName` sozinho** — a chave tem cinco campos;
  faltando `tierMinimumUnits` o erro chega a 12×
- **Não ler `unitOfMeasure` em linha de reserva** — o divisor vem de
  `reservationTerm`
- **Não entregar Fabric sem OneLake** — capacidade e armazenamento são duas
  parcelas obrigatórias
- **Não assumir região sem confirmar** — especialmente para clientes de setores regulados
- **Não gerar sem confirmar (Fase 5)** — o resumo evita retrabalho
