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

#### Arquitetura 1 — Modern Data Platform / Lakehouse com Databricks e Fabric Integration

Casos de uso: plataforma de dados em nuvem Azure estruturada em camadas Medallion (Bronze,
Silver, Gold), combinando Azure Databricks para processamento analítico com suporte a IA
generativa e conectividade ao Microsoft Fabric (Direct Lake / Shortcuts).

Serviços:
- Ingestão (batch/pipelines): Azure Data Factory (ADF) — orquestração e ingestão principal
- Ingestão (on-premise):    ExpressRoute / VM Self-Hosted Integration Runtime — conectividade
  privada, segura e de alta velocidade para ambientes on-premise e sistemas legados
- Ingestão (fontes modernas): Databricks Ingestion / Lakeflow — APIs, Google Analytics, Excel
  e streaming de bancos SQL/NoSQL
- Storage:                Azure Data Lake Storage Gen2 (ADLS Gen2) — Delta Lake nas camadas
  Bronze (brutos), Silver (enriquecidos) e Gold (modelados)
- Processamento:          Azure Databricks (Core Processing) — motor unificado Spark para
  limpeza, transformação e regras de negócio via SQL Notebooks
- Orquestração:           Unity Catalog / ADF — gerenciamento do ciclo de vida e agendamento
  de jobs do pipeline
- IA (All Layer):         Azure OpenAI Service & Databricks AI — integração de LLMs e IA
                          (na API: `serviceName = "Foundry Models"`, não "Azure OpenAI Service")
  generativa consumindo dados tratados da camada Gold
- Serving (DW):           Databricks (SQL Warehouse) — data warehousing serverless
- Serving (BI direto):    Direct Lake / Shortcuts (Microsoft Fabric integration) — conectividade
  direta de baixíssima latência para o Power BI sem cópia de dados
- BI & IA:                Power BI + Databricks Genie (assistente de BI conversacional)
- Governança:             Unity Catalog — governança centralizada, auditoria, controle de
  acesso refinado e data lineage para todos os ativos no Data Lake
- Segurança:              Azure Key Vault — gestão segura de segredos, chaves e credenciais
- Monitoramento:          Azure Monitor / Log Analytics
- Gestão de custos:       Microsoft Cost Management

Observações:
- Calcular SEMPRE VM/compute do Databricks no estimate Azure + DBU separado — nunca somar
  duas vezes
- ExpressRoute só entra na estimativa quando há integração on-premise real
- Direct Lake evita duplicação de dados entre Databricks e Fabric — validar se o cliente já
  possui licença Fabric antes de incluir no escopo
- Para clientes financeiros/saúde: confirmar região Brazil South (LGPD/BACEN)

---

#### Arquitetura 2 — Lakehouse Puramente Databricks

Casos de uso: versão simplificada e focada exclusivamente no ecossistema Databricks,
reduzindo componentes adicionais da Azure ao utilizar o Databricks como motor unificado de
ingestão, processamento, governança e serving.

Serviços:
- Ingestão (todas as fontes): Databricks (Auto Loader / Lakeflow) — principal motor de
  ingestão para Oracle, MongoDB, Google Analytics, APIs, Excel e SQL
- Ingestão (on-premise):    VMs Runtime On-Premise — ponte de conexão com ambientes e bancos
  de dados locais/privados
- Storage:                Azure Data Lake Storage Gen2 (ADLS Gen2) — Delta Lake nas camadas
  Bronze (bruto), Silver (limpo) e Gold (pronto para consumo)
- Processamento:          Azure Databricks (Core Processing) — Apache Spark + SQL Notebooks
  para transformação e movimentação entre as camadas Medallion
- Orquestração:           Unity Catalog / Databricks Workflows — orquestração de tarefas e
  controle do pipeline
- IA (All Layer):         Azure OpenAI Service & Databricks AI — IA generativa e machine
                          (na API: `serviceName = "Foundry Models"`, não "Azure OpenAI Service")
  learning sobre as camadas de dados tratadas
- Serving (DW):           Databricks (SQL Warehouse) — motor analítico para consultas de
  alta performance
- BI & IA:                Power BI — ferramenta única de visualização consumindo diretamente
  os dados do Databricks
- Governança:             Unity Catalog — gerenciamento de acesso, catálogo de dados e
  linhagem
- Segurança:              Azure Key Vault — gestão de credenciais e segredos
- Monitoramento:          Azure Monitor — telemetria e métricas de desempenho
- Gestão de custos:       Microsoft Cost Management

Observações:
- Azure Data Factory entra apenas como gerenciamento complementar do ambiente — não é o
  motor de ingestão principal (diferença da Arquitetura 1)
- Calcular SEMPRE VM/compute do Databricks no estimate Azure + DBU separado — nunca somar
  duas vezes
- Sem integração com Microsoft Fabric (Direct Lake/Shortcuts) — diferença da Arquitetura 1
- Para clientes financeiros/saúde: confirmar região Brazil South (LGPD/BACEN)

---

#### Arquitetura 3 — Modern Data Platform / Lakehouse com Copilot Studio e Conectores de Consumo Ampliados

Casos de uso: arquitetura Lakehouse centrada no Azure Databricks e no Unity Catalog, que
expande as capacidades de consumo e IA integrando o Microsoft Copilot Studio e plataformas
externas de automação/mensageria.

Serviços:
- Ingestão (batch/pipelines): Azure Data Factory (ADF) — ingestão e orquestração dos fluxos
  principais
- Ingestão (on-premise):    ExpressRoute / VM Self-Hosted Integration Runtime — conectividade
  privada e segura para sistemas on-premise e bancos legados
- Ingestão (SaaS/APIs/arquivos): Databricks (Lakeflow / Ingestion) — Google Analytics, APIs,
  arquivos planos (Excel) e bancos relacionais/NoSQL
- Storage:                Azure Data Lake Storage Gen2 (ADLS Gen2) — Delta Lake nas camadas
  Medallion (Bronze, Silver e Gold)
- Processamento:          Azure Databricks (Core Processing) — Apache Spark + SQL Notebooks
  para transformação e limpeza dos dados
- Orquestração:           Unity Catalog / ADF — agendamento e controle de execução das
  rotinas de ETL/ELT
- IA (All Layer):         Microsoft Copilot Studio & Databricks AI — substitui a camada
  OpenAI para criar agentes de IA conversacionais personalizados e modelos avançados
  alimentados pelos dados da camada Gold
- Serving (DW):           Databricks (SQL Warehouse) — processamento analítico para queries
  de alta performance
- BI & IA (consumo ampliado): Power BI (dashboards e relatórios corporativos) + Lovable /
  Belake.ai (plataformas web/low-code acionadas por dados) + WhatsApp (mensageria para
  alertas, notificações e interação via bots)
- Governança:             Unity Catalog — controle de acesso refinado, auditoria e linhagem
  de dados
- Segurança:              Azure Key Vault — gerenciamento de chaves e segredos
- Monitoramento:          Azure Monitor — telemetria, logs e métricas de desempenho
- Gestão de custos:       Microsoft Cost Management

Observações:
- Copilot Studio substitui o Azure OpenAI Service da Arquitetura 1 como camada de IA
  conversacional — validar licenciamento do cliente antes de incluir no escopo
- Lovable/Belake.ai e integração WhatsApp são custos FORA do Azure Pricing — estimar à parte
  (licenças/assinaturas de terceiros)
- Calcular SEMPRE VM/compute do Databricks no estimate Azure + DBU separado — nunca somar
  duas vezes
- Para clientes financeiros/saúde: confirmar região Brazil South (LGPD/BACEN)

---

#### Arquitetura 4 — Microsoft Fabric End-to-End Platform

Casos de uso: plataforma moderna de dados 100% baseada no ecossistema nativo Microsoft
Fabric, substituindo o Databricks pelo Fabric Data Engineering e OneLake para
processamento, governança unificada via Purview e integração com IA.

Serviços:
- Ingestão (batch/pipelines): Fabric Data Factory — orquestração e ingestão totalmente
  integradas à experiência do Microsoft Fabric
- Ingestão (on-premise):    ExpressRoute / VMs Runtime On-Premise — conexão privada para
  transferência segura de dados de ambientes locais e legados
- Ingestão (fontes heterogêneas): Fabric Data Factory — Oracle, MongoDB, Google Analytics,
  APIs, Excel e SQL
- Storage:                OneLake / Delta Lake — repositório centralizado nativo do Fabric
  com as camadas Medallion (Bronze, Silver e Gold) sob padrão Delta Lake
- Processamento:          Data Engineering Fabric (Core Processing) — motor unificado
  baseado em Apache Spark e SQL Notebooks para tratamento, limpeza e transformação
- Orquestração:           Fabric Pipelines / Purview — controle de execução do ciclo de
  vida dos dados
- IA (All Layer):         Azure OpenAI Service & Fabric Copilot — IA generativa e
                          (na API: `serviceName = "Foundry Models"`, não "Azure OpenAI Service")
  assistentes inteligentes consumindo dados refinados da camada Gold
- Serving (DW):           Fabric Lakehouse / Synapse Data Warehouse — motor analítico
  nativo para servir dados de alta performance
- Serving (BI direto):    Direct Lake / Shortcuts — conectividade em tempo real para o
  Power BI sem cópia de dados (zero-ETL/zero-duplication)
- BI & IA:                Power BI — ferramenta central de relatórios e visualização
  analítica
- Governança:             Microsoft Purview — catálogo, compliance, auditoria e linhagem
  integrados nativamente
- Segurança:              Azure Key Vault — gestão de credenciais e chaves
- Monitoramento:          Azure Monitor — monitoramento e telemetria
- Gestão de custos:       Microsoft Cost Management — governança e controle de custos do
  ambiente Azure/Fabric

Observações:
- Sem Databricks — Fabric Data Engineering substitui processamento, Unity Catalog é
  substituído por Purview (diferença das Arquiteturas 1-3)
- Capacidade Fabric (F SKUs) é o item de custo central — dimensionar pela carga de
  processamento/consumo, não por VM individual
- Direct Lake evita duplicação de dados para o Power BI nativamente, sem depender de
  integração externa (diferença da Arquitetura 1, que integra Databricks ao Fabric)
- Para clientes financeiros/saúde: confirmar região Brazil South (LGPD/BACEN)

---

#### Arquitetura 5 — Híbrida Databricks + Microsoft Fabric para ERP/SQL Enterprise

Casos de uso: arquitetura corporativa voltada para ingestão intensiva de sistemas core (SAP
e SQL Server), combinando o poder de processamento do Databricks com a ponte de integração
nativa do Microsoft Fabric (Direct Lake / Shortcuts) para relatórios e IA.

Serviços:
- Ingestão (batch/pipelines): Fabric Data Factory — orquestrador principal dos fluxos e
  conectores corporativos
- Ingestão (on-premise):    ExpressRoute / VMs Runtime On-Premise — infraestrutura dedicada
  para extração de alto volume e baixa latência de dados de sistemas SAP e SQL Server
- Storage:                Azure Databricks (Delta Lake) — camadas Medallion (Bronze, Silver
  e Gold) em formato Delta Lake
- Processamento:          Azure Databricks (Core Processing) — processamento das camadas
  Medallion
- Integração Fabric:      Direct Lake / Shortcut (Connect Databricks to Microsoft Fabric) —
  ponte que conecta o armazenamento gerenciado pelo Databricks diretamente ao OneLake do
  Microsoft Fabric sem necessidade de mover ou duplicar dados
- Orquestração:           Unity Catalog / Purview — controle central de acesso, governança e
  orquestração dos pipelines
- IA (All Layer):         Azure OpenAI Service & Microsoft Fabric AI — LLMs e IA generativa
                          (na API: `serviceName = "Foundry Models"`, não "Azure OpenAI Service")
  atuando sobre os dados refinados corporativos
- Serving (BI direto):    Direct Lake / Shortcuts — entrega analítica de ultra-baixa
  latência para ferramentas de visualização
- BI & IA (consumo):      Power BI (visualização via Direct Lake) + Belake.ai (integração
  com aplicações web e plataformas personalizadas) + Genie / Copilot Studio (assistentes
  virtuais e bots de IA conversacional treinados nos dados do negócio)
- Governança:             Unity Catalog (Databricks) + Microsoft Purview — governança dupla,
  integração entre as duas ferramentas para rastreabilidade de linhagem e controle de
  acesso unificado
- Segurança:              Azure Key Vault — gerenciamento seguro de credenciais e segredos
- Monitoramento:          Azure Monitor — telemetria e métricas operacionais
- Gestão de custos:       Microsoft Cost Management — monitoramento e alocação de custos
  Azure/Fabric

Observações:
- Governança dupla (Unity Catalog + Purview) — validar com o cliente se ambas as
  ferramentas serão realmente usadas em paralelo ou se uma substitui a outra, para não
  gerar custo/esforço redundante
- Indicada para clientes com ingestão pesada de SAP/SQL Server on-premise — dimensionar
  ExpressRoute e Self-Hosted Integration Runtime pelo volume real de extração
- Calcular SEMPRE VM/compute do Databricks no estimate Azure + DBU separado — nunca somar
  duas vezes
- Belake.ai e Copilot Studio podem envolver custos FORA do Azure Pricing — estimar à parte
  (licenças/assinaturas de terceiros)
- Para clientes financeiros/saúde: confirmar região Brazil South (LGPD/BACEN)

---

---

## Resolução de preço Azure — regras obrigatórias

Esta seção vale para **toda** consulta de preço Azure. Leia antes de chamar
`azure_price_search`, `azure_discover_skus` ou `azure_cost_estimate`.

O MCP devolve o que a Retail Prices API devolve. A API não valida intenção: uma
busca mal formada devolve linha plausível com preço errado. Todos os casos abaixo
foram verificados contra a API em `brazilsouth`, sobre 12.637 meters de
`type = 'Consumption'`.

### O que o MCP devolve, e o que ele não devolve

**Leia isto antes da chave de cinco campos.** A Retail Prices API tem 20 campos por
linha. O `azure-pricing-mcp` devolve oito, e os que faltam são justamente os que
desambiguam preço:

| Campo | Na API | No MCP |
| --- | :-: | :-: |
| `serviceName` | ✓ | ✓ como `service` |
| `productName` | ✓ | ✓ como `product` |
| `skuName` | ✓ | ✓ como `sku` |
| `unitOfMeasure` | ✓ | ✓ como `unit` |
| `retailPrice` | ✓ | ✓ como **`discounted_price`** |
| **`meterName`** | ✓ | ✗ **não volta, e não é filtrável** |
| **`tierMinimumUnits`** | ✓ | ✗ **não volta** |
| `reservationTerm` | ✓ | ✗ |

Consequência direta, verificada em `brazilsouth`: buscar `Key Vault` devolve estas
quatro linhas, entre outras:

```
product="Key Vault"  sku="Premium"  unit="1"  discounted_price=5.0
product="Key Vault"  sku="Premium"  unit="1"  discounted_price=2.5
product="Key Vault"  sku="Premium"  unit="1"  discounted_price=0.9
product="Key Vault"  sku="Premium"  unit="1"  discounted_price=0.4
```

São `Premium HSM-protected Advanced Key` nas faixas 0 / 250 / 1.500 / 4.000.
Idênticas em todo campo devolvido, exceto o preço. **Não há como distinguir.**

Mesma coisa em `Log Analytics` / `Analytics Logs`: três linhas na unidade `1 GB` a
0,0 / 2,3 / 4,6, que são `Data Ingestion` na faixa 0, `Data Analyzed` e
`Data Ingestion` a partir de 5 GB. Pelo MCP, indecidível.

**Portanto: a allowlist desta seção é a fonte de preço. O MCP serve para descobrir
o que existe e confirmar ordem de grandeza — não para resolver preço.**

Isso não é uma concessão: a allowlist foi construída lendo a API diretamente, com
os cinco campos à vista, e é reconferível a qualquer momento com
`python tools/valida_precos.py`.

### Serviço que não está na allowlist

Você **não consegue** resolver preço dele com as tools disponíveis. Não tente.

```
⚠️ [Serviço] — faz parte da arquitetura, sem valor nesta estimativa.
   Não está no catálogo de meters verificados desta Skill, e o MCP não
   devolve os campos necessários para resolver o preço com segurança.
   Levantar em prices.azure.com ou confirmar com o parceiro Microsoft.
```

Nunca improvise. Nunca use "o primeiro resultado". Nunca estime de memória. Uma
linha sem valor e declarada é honesta; uma linha com número errado vira proposta.

Se o serviço aparecer com frequência, ele merece entrar na allowlist — o caminho é
`python tools/sonda_catalogo.py probe --service "<nome>" --region brazilsouth`,
conferir os cinco campos e acrescentar a tabela aqui.

### Quando vierem vários preços para o mesmo product e sku

Acontece o tempo todo, e o MCP não diz qual é qual. Regra:

1. Se o meter estiver na allowlist, **use o valor da allowlist** e ignore o resto.
2. Se não estiver, a linha sai sem valor (acima).

**Não deduza a faixa pelo preço.** É tentador supor que o maior valor é
`tierMinimumUnits = 0`, e em armazenamento e Key Vault isso é verdade, porque o
preço cai conforme o volume sobe. Mas não é regra da API: em
`Log Analytics / Analytics Logs Data Ingestion` a faixa 0 custa **0,0** e a faixa de
5 GB custa **4,60** — o menor valor é a primeira faixa. Quem deduzir pelo maior
preço erra aqui.

### Atenção ao nome `discounted_price`

O campo do MCP se chama `discounted_price` e existe um parâmetro
`discount_percentage` na busca. Com o padrão (`show_with_discount: false`) o valor
devolvido **é** o preço retail — conferido contra a API. Mas:

- nunca passe `discount_percentage` nem `show_with_discount`: a Skill cota preço
  público, e desconto negociado é assunto do parceiro;
- se um valor vier abaixo do que a allowlist registra, suspeite de desconto
  aplicado antes de suspeitar de mudança de preço.

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

**Onde esta chave é aplicável.** Ela descreve como o preço foi resolvido para montar
a allowlist abaixo, lendo a Retail Prices API diretamente com `tools/sonda_catalogo.py`.
Ela **não** é executável em tempo de conversa pelo MCP, que não devolve dois dos cinco
campos — ver a seção anterior. Em tempo de conversa, a allowlist é a fonte.

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

**Operações de ADLS Gen2.** Armazenamento é só metade da conta: ingestão em batch
gera dezenas de milhões de operações/mês. Meters de `Hot LRS` e `Hot GRS`:

| skuName | meterName | preço | **unidade** |
| --- | --- | ---: | --- |
| `Hot LRS` | `Hot Write Operations` | 0,091 | **10K** |
| `Hot LRS` | `Hot Iterative Write Operations` | 0,091 | **100** |
| `Hot LRS` | `Hot Iterative Read Operations` | 0,091 | **10K** |
| `Hot GRS` | `Hot GRS Write Operations` | 0,182 | **10K** |
| `Hot GRS` | `Hot GRS Iterative Write Operations` | 0,182 | **100** |
| `Hot GRS` | `Hot GRS Iterative Read Operations` | 0,182 | **10K** |
| `Hot LRS` e `Hot GRS` | `Hot Read Operations` | 0,0073 | 10K |
| `Hot LRS` e `Hot GRS` | `Hot Other Operations` | 0,00728 | 10K |
| `Hot LRS` e `Hot GRS` | `Delete Operations` | 0,0 | 10K |

Três coisas nesta tabela são armadilha, e nenhuma é visível olhando só o preço:

1. **`Iterative Write` cobra por 100, não por 10K** — mesmo preço da linha normal,
   unidade 100× menor. Ver o gate 8.
2. `Hot Read Operations` (0,0073) e `Hot Other Operations` (0,00728) são meters
   diferentes com números quase iguais.
3. `Delete Operations` custa 0,0 e **não** tem meter irmão de faixa maior — pelo
   gate 3, é zero não justificado. Não some, e diga na premissa que não somou.

Se o arquiteto não souber o volume de transações, diga que a linha existe e fica
fora por falta de dado — não a omita em silêncio.

**Máquinas virtuais** — `serviceName = "Virtual Machines"`, 6.775 meters, e a
maioria não serve. Distribuição verificada:

| Recorte | meters | % |
| --- | ---: | ---: |
| `skuName` contém `Spot` | 2.621 | 39% |
| `skuName` contém `Low Priority` | 1.370 | 20% |
| `productName` contém `Windows` | 3.243 | 48% |
| **sobra: Linux pago normal** | **1.472** | **22%** |

Filtro obrigatório para VM paga em Linux:

```
skuName    NÃO contém "Spot" nem "Low Priority"
productName NÃO contém "Windows"
skuName    = "Standard_D4s_v5"   ← formato ARM com underscore, não "D4s v5"
```

Exemplo do fator de erro em `Standard_D2s_v5`: 0,153 (Linux pago) contra 0,245
(Windows), 0,0306 (Low Priority) e 0,028274 (Spot) — fator 5,4 entre o certo e o
mais barato. Spot e Low Priority estão proibidos pela regra de modelo de compra.

**Discos gerenciados** — `serviceName = "Storage"`,
`productName = "Premium SSD Managed Disks"` (ou `Standard SSD ...`). VM com disco
tem duas linhas, e existe um par que engana:

| skuName | meterName | preço |
| --- | --- | ---: |
| `P10 LRS` | `P10 LRS Disk` | 34,05 / mês |
| `P10 LRS` | `P10 LRS Disk Mount` | 1,82 / mês |
| `P10 ZRS` | `P10 ZRS Disk` | 51,075 / mês |
| `E10 LRS` | `E10 LRS Disk` | 17,92 / mês |

`Disk` é o disco; `Disk Mount` é só a montagem em disco compartilhado. Fator 19
entre os dois, e `Disk Mount` existe com **o mesmo 1,82** em toda família — um
total montado só com `Disk Mount` fica barato e uniforme, o que parece plausível.

Disco gerenciado cobra **por mês, não por hora de VM ligada**: em HML e Dev com
VM em 200h, o disco continua custando o mês inteiro.

**Key Vault** — `serviceName = "Key Vault"`, 16 meters. Lista completa:

| productName | meterName | `tierMinimumUnits` | preço |
| --- | --- | ---: | ---: |
| `Key Vault` | `Operations` | 0 | 0,03 / 10K |
| `Key Vault` | `Advanced Key Operations` | 0 | 0,15 / 10K |
| `Key Vault` | `Automated Key Rotation` | 0 | 1,00 / rotação |
| `Key Vault` | `Secret Renewal` | 0 | 1,00 / unidade |
| `Key Vault` | `Certificate Renewal Request` | 0 | 3,00 / unidade |
| `Key Vault` | `Premium HSM-protected RSA 2048-bit key` | 0 | 1,00 / chave |
| `Key Vault` | `Premium HSM-protected Advanced Key` | 0 / 250 / 1.500 / 4.000 | 5,00 / 2,50 / 0,90 / 0,40 |
| `Key Vault HSM Pool` | `Standard B1 Instance` | 0 | 3,20 / hora = 2.336,00/mês |

Uso comum é só `Operations`: 200 mil operações/mês dão 0,60. Não ofereça
`Key Vault HSM Pool` sem o arquiteto ter pedido HSM dedicado — são 2.336,00/mês.

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

**Azure Monitor e Log Analytics** — aparecem em todas as cinco arquiteturas Azure.
São `serviceName` **diferentes**, com meters diferentes:

| serviceName | productName | meterName | `tier` | preço |
| --- | --- | --- | ---: | ---: |
| `Log Analytics` | `Log Analytics` | `Analytics Logs Data Ingestion` | 0 | **0,0** (5 GB grátis) |
| `Log Analytics` | `Log Analytics` | `Analytics Logs Data Ingestion` | 5 | 4,60 / GB |
| `Log Analytics` | `Log Analytics` | `Analytics Logs Data Analyzed` | 0 | 2,30 / GB |
| `Log Analytics` | `Log Analytics` | `Analytics Logs Data Retention` | 0 | 0,20 / GB-mês |
| `Azure Monitor` | `Azure Monitor` | `Basic Logs Data Ingestion` | 0 | 1,00 / GB |
| `Azure Monitor` | `Azure Monitor` | `Auxiliary Logs Data Ingestion` | 0 | 0,10 / GB |
| `Azure Monitor` | `Azure Monitor` | `Alerts Resource Monitored at 1 Minute Frequency` | 0 | 0,30 / mês |
| `Azure Monitor` | `Azure Monitor` | `Alerts Metric Monitored` | 10 | 0,10 / mês |

Os primeiros 5 GB/mês de ingestão em `Analytics Logs` são gratuitos — este é um zero
legítimo, com meter irmão em `tierMinimumUnits = 5`. Para estimar, peça o volume de
log em GB/mês; sem isso a linha sai declarada sem valor.

**Azure Data Factory** — `serviceName = "Azure Data Factory v2"` (não
`Azure Data Factory`, que é a v1). O `skuName` separa onde o pipeline roda:

| skuName | meterName | preço |
| --- | --- | ---: |
| `Cloud` | `Cloud Orchestration Activity Run` | 1,00 / 1K execuções |
| `Cloud` | `Cloud Data Movement` | 0,25 / hora-DIU |
| `Cloud` | `Cloud Pipeline Activity` | 0,005 / hora |
| `Self Hosted` | `Self Hosted Orchestration Activity Run` | 1,50 / 1K execuções |
| `Self Hosted` | `Self Hosted Data Movement` | 0,10 / hora |
| `Cloud` e `Self Hosted` | `Inactive Pipeline` | 0,80 / mês |

`Self Hosted` custa 50% mais por execução que `Cloud`. Pergunte se a ingestão é de
origem on-premise antes de escolher.

**Microsoft Purview** — duas armadilhas de uma vez. Existem **dois** serviços:

| serviceName | O que é |
| --- | --- |
| `Azure Purview` | geração anterior (Purview Data Map) |
| `Microsoft Purview` | o produto atual |

E `Microsoft Purview` se divide em `Microsoft Purview Data Governance` e
`Microsoft Purview Data Compliance`. Referência:

| productName | meterName | preço |
| --- | --- | ---: |
| `Microsoft Purview Data Governance` | `Data Management Basic Data Governance Processing Unit` | 15,00 |
| `Microsoft Purview Data Governance` | `Data Management Advanced Data Governance Processing Unit` | 240,00 |
| `Microsoft Purview Data Governance` | `Data Management Standard Data Governance Processing Unit` | 60,00 |
| `Microsoft Purview Data Governance` | `Data Catalog Standard Asset` | 0,0165 / ativo-dia |
| `Azure Purview Data Map` | `Standard Capacity Unit` | 0,411 / hora |

A cobrança de Data Governance é **por ativo catalogado**, número que o arquiteto
raramente tem na conversa. Na dúvida, declare sem valor em vez de arbitrar.

**ExpressRoute** — só o gateway tem meter aqui; o circuito é contratado à parte,
normalmente já existente no cliente.

| productName | skuName | preço / hora |
| --- | --- | ---: |
| `ExpressRoute Standard Gateway` | `Standard` | 0,19 |
| `ExpressRoute High Performance Gateway` | `High Performance` | 0,49 |
| `ExpressRoute Gateway` | `ErGw1AZ` | 0,361 |
| `ExpressRoute Gateway` | `ErGw2AZ` | 0,632 |
| `ExpressRoute Gateway` | `ErGw3AZ` | 2,151 |

Pergunte sempre se o circuito já existe. Se existir, ele sai do escopo da proposta e
isso vira premissa.

**Microsoft Copilot Studio** — tem meter de consumo no Azure, além do licenciamento
M365: `Pay As You Go Message` e `Pay As You Go Copilot Credit`, ambos a **0,01** por
unidade. Se o cliente for pelo modelo de licença por usuário, aí sim é M365 e sai sem
valor — pergunte qual dos dois antes de decidir.

**IoT Hub** — cobrado por unidade/mês, não por hora. Não aplique redução de horas em
HML e Dev; reduza tier ou quantidade de unidades.

| skuName | preço / mês |
| --- | ---: |
| `B1` | 20,00 |
| `B2` | 100,00 |
| `B3` | 1.000,00 |
| `S1` | 50,00 |
| `S2` | 500,00 |
| `S3` | 5.000,00 |

A cota diária de mensagens por unidade é limite de produto e **não** está na API —
o dimensionamento de quantas unidades vem do arquiteto, e é premissa declarada.

**Stream Analytics** — o `skuName` distingue gerações com preço muito diferente:

| skuName | meterName | `tier` | preço / hora |
| --- | --- | ---: | ---: |
| `Standard` | `Standard Streaming Unit` | 0 | 0,125 |
| `Dedicated` | `Dedicated Streaming Unit` | 0 | 0,125 |
| `Standard V2` | `Standard V2 Streaming Unit/Job` | 0 | 0,6733 |
| `Dedicated V2` | `Dedicated V2 Streaming Unit/Job` | 730 | 0,288307 |
| `Dedicated V2` | `Dedicated V2 Streaming Unit/Job` | 5.840 | 0,239964 |

V2 custa **5,4× mais** que V1 na primeira faixa, e é escalonado por horas acumuladas.
Confirme a geração com o arquiteto; não assuma.

**Azure Functions** — `serviceName = "Functions"`, com dois planos que são
`productName` distintos:

| productName | meterName | `tier` | preço |
| --- | --- | ---: | ---: |
| `Functions` | `Standard Execution Time` | 400.000 | 0,000016 / GB-s |
| `Flex Consumption` | `On Demand Execution Time` | 100.000 | 0,000037 / GB-s |
| `Flex Consumption` | `On Demand Total Executions` | 25.000 | 0,000004 / 10 exec |
| `Flex Consumption` | `Always Ready Baseline` | 0 | 0,000005 / GB-s |

Repare no `tierMinimumUnits` alto: as faixas gratuitas do Consumption clássico são
grandes (400.000 GB-s), então cargas pequenas custam praticamente zero — e esse zero
**é** legítimo. Diga que é faixa gratuita, não omita a linha.

**Azure OpenAI** — `serviceName = "Foundry Models"`, **não** "Azure OpenAI Service",
que não existe como serviço. O nome "Azure OpenAI" aparece no `productName`:

| productName | meterName | preço |
| --- | --- | ---: |
| `Azure OpenAI GPT5` | `GPT 5 Chat Inpt Glbl 1M Tokens` | 1,25 / 1M tokens |
| `Azure OpenAI GPT5` | `GPT 5 Chat outpt Glbl 1M Tokens` | 10,00 / 1M tokens |
| `Azure OpenAI GPT5` | `GPT 5 Chat cchd Inpt Glbl 1M Tokens` | 0,125 / 1M tokens |
| `Azure OpenAI GPT5` | `GPT 5 Batch Inpt Glbl 1M Tokens` | 0,625 / 1M tokens |

São 715 meters sob `Foundry Models`, um por modelo e modalidade. Entrada e saída têm
preços diferentes (fator 8 no GPT-5), e cache e batch são mais baratos. Sem volume de
tokens estimado pelo arquiteto, esta linha sai declarada sem valor — e quase sempre
sai, porque ninguém tem esse número no início do projeto.

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

**8. Mesmo preço, unidade diferente — erro de 100×.** A pior das colisões, porque
os dois números batem e só a unidade separa:

| meterName | `retailPrice` | `unitOfMeasure` |
| --- | ---: | --- |
| `Hot GRS Write Operations` | 0,182 | **10K** |
| `Hot GRS Iterative Write Operations` | 0,182 | **100** |
| `Hot Write Operations` (LRS) | 0,091 | **10K** |
| `Hot Iterative Write Operations` (LRS) | 0,091 | **100** |

50 milhões de escritas dão 910,00 pelo meter certo e **91.000,00** pelo irmão
iterativo. Conferir o preço unitário não pega: é 0,182 nos dois.

Regra: **sempre leia `unitOfMeasure` junto com `retailPrice`** e mostre a unidade
na conta aberta (`50.000.000 ÷ 10K × 0,182`), nunca só o produto final. A conta
aberta com a unidade explícita é o que torna o erro visível na revisão.

Isto vale para todo meter de operação, não só ADLS. A exceção conhecida é a linha
de reserva, onde `unitOfMeasure` mente — ver o gate 4.

### Serviços que não estão na Retail Prices API

A API cobre consumo Azure. Ela **não** cobre licença de usuário, produto M365, nem
software de terceiro. Casos que aparecem nestas propostas:

| Item | Onde vive | Na estimativa |
| --- | --- | --- |
| Power BI Pro / PPU (licença por usuário) | licenciamento M365 | linha separada, sem valor |
| Microsoft Fabric F SKU | calculado por CU | ver a seção Fabric |
| Private Link / Private Endpoint | não existe meter | premissa sem valor |
| Snowflake, Databricks fora do Azure | fornecedor | fora do escopo |

**Nunca ponha preço de memória nestas linhas.** Nem em tabela de comparação, nem em
"próximos passos", nem entre parênteses. Se o valor não veio da API nesta conversa,
ele não tem número — tem nome e um encaminhamento:

```
⚠️ Power BI Pro — licenciamento M365, fora da Retail Prices API.
   [N] usuários. Preço a confirmar com o parceiro M365.
   Não incluído em nenhum total desta estimativa.
```

Isso vale especialmente quando a licença **decide a arquitetura**. A regra de que
capacidade F64 ou maior dispensa licença Pro individual para quem só consome é
real, e muda a escolha do F SKU — mas a comparação entre "F32 mais N licenças" e
"F64 sem licença" só pode ser feita com o preço de licença que o parceiro
confirmar. Apresente a estrutura da decisão ao arquiteto e deixe o número em
aberto; não feche a recomendação com um preço de licença que você não verificou.

Se o arquiteto insistir num número para seguir a conversa, use o que ele der e
registre a origem na premissa: "licença a $X/usuário, valor informado pelo
arquiteto, não verificado na API".

### Nenhuma linha some em silêncio

Duas regras que andam juntas:

1. **Todo serviço em "Serviços incluídos" tem que ter valor em algum total.** Se
   você decidiu não cotar uma linha por ser pequena, ela sai das duas listas ou
   entra nas duas. "Key Vault incluído" com 0,00 no total é contradição.
2. **Se uma linha fica fora por falta de dado, diga.** Falta de informação vira
   premissa declarada, não omissão.

### Todo número declarado vale o mesmo

A disciplina de verificação vale para **qualquer** número que sai na resposta, não
só para a tabela principal. Número em "próximos passos", em comparação lateral, em
"isso pode derrubar ~$X", em texto solto — todos valem uma afirmação para o
cliente, e todos precisam ser calculados, não estimados de cabeça.

Se for citar uma economia possível, calcule: trocar 8.192 GB de OneLake Hot
(0,0407) para Cool (0,0221) economiza `8192 × 0,0186 = 152,37`, não "uns 180".
Arredondar para cima uma economia que você não calculou é o mesmo defeito que a
Skill inteira tenta evitar, só que num lugar onde ninguém confere.

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
allowlist e os oito gates de validação). O MCP não valida intenção: busca mal
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

**Linha que não é hora nem volume escala junto com o que a gera.** Operações de
ADLS, operações de Key Vault e egress não têm "horas" nem "GB armazenados". Use a
mesma proporção do volume do ambiente (~30% em HML, ~10% em Dev) e declare que foi
proporção assumida, não medição. Duas consequências que aparecem sozinhas:

- Egress de HML e Dev quase sempre cai abaixo dos 100 GB gratuitos, indo a 0,00.
  Esse zero é legítimo — diga que é faixa gratuita, para não parecer linha
  esquecida.
- Disco gerenciado **não** escala: é cobrado por mês inteiro nos três ambientes,
  mesmo com a VM em 200h.

**Quando não há tier abaixo.** `Standard_D2s_v5` já é o menor da série Dsv5. Nesse
caso mantenha o hardware, reduza só as horas, e diga isso na premissa — não troque
de série para conseguir um número menor.

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

[Se houver Fabric, ou qualquer serviço com dois modelos de compra, use dois
 cenários em vez de um total só — nunca escolha um modelo em silêncio:]

   CENÁRIO A — produção SOB DEMANDA
   Produção:        $X.XXX/mês
   Homologação:     $X.XXX/mês
   Desenvolvimento: $X.XXX/mês
   ──────────────────────────────
   Total Azure:     $X.XXX/mês

   CENÁRIO B — produção com RESERVA de 1 ano (HML e Dev seguem sob demanda)
   Produção:        $X.XXX/mês
   Homologação:     $X.XXX/mês
   Desenvolvimento: $X.XXX/mês
   ──────────────────────────────
   Total Azure:     $X.XXX/mês

   Diferença: $X.XXX/mês  |  Compromisso anual da reserva: $XX.XXX

[Itens fora da Retail Prices API vão abaixo dos totais, SEM valor e SEM entrar
 em nenhuma soma:]
   ⚠️ Fora dos totais: [licenças Power BI Pro, Private Endpoint, ...]
      — a confirmar com o parceiro

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
- **Não usar meter fora da allowlist** — se o serviço que você precisa cotar não
  está lá, diga que falta, não improvise
- **Não ler `retailPrice` sem `unitOfMeasure`** — `Iterative Write Operations`
  cobra por 100 e a irmã por 10K, pelo mesmo preço: erro de 100×
- **Não cotar VM sem filtrar Spot, Low Priority e Windows** — são 78% dos meters
  de Virtual Machines
- **Não pôr preço de licença de memória** — Power BI Pro e M365 não estão na
  Retail Prices API; entram sem valor, a confirmar com o parceiro
- **Não listar serviço que não foi cotado** — se está em "Serviços incluídos",
  tem valor em algum total
- **Não estimar de cabeça número secundário** — economia citada em "próximos
  passos" vale o mesmo que a tabela principal e precisa ser calculada
- **Não assumir região sem confirmar** — especialmente para clientes de setores regulados
- **Não gerar sem confirmar (Fase 5)** — o resumo evita retrabalho
