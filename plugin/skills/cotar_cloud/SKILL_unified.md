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

Use as tools na sequência para cada serviço da arquitetura:

```
azure_discover_skus    → encontrar o SKU correto para o serviço
azure_cost_estimate    → calcular custo mensal (Produção)
azure_cost_estimate    → calcular custo mensal (Homologação: ~30% de uso)
azure_cost_estimate    → calcular custo mensal (Desenvolvimento: ~50% de uso, 1 tier abaixo)
```

**Regras de sizing por ambiente (idênticas ao AWS):**

| Ambiente        | Horas de uso    | Hardware         |
|-----------------|-----------------|------------------|
| Produção        | 100% (730h/mês) | Tamanho definido |
| Homologação     | ~30% (200h/mês) | Mesmo hardware   |
| Desenvolvimento | ~50% horas prod | 1 tier abaixo    |

**Sempre usar preços on-demand (retail public).** Nunca Reserved Instances ou Spot.

Use `azure_region_recommend` se o arquiteto não tiver preferência de região e quiser
a opção mais barata para o serviço principal.

#### Microsoft Fabric on Azure

Fabric é cobrado por **Capacity Unit (CU) por hora**, não por serviço individual.
O modelo de cobrança é baseado em F-SKU (F2, F4, F8, F16, F32, F64, F128, F256, F512, F1024, F2048).

**Fluxo de dimensionamento:**

1. Pergunte qual F-SKU o cliente pretende usar, ou ajude a estimar:
   - Carga leve (notebooks exploratórios, DW pequeno): F8–F16
   - Carga média (pipelines diários, DW corporativo): F32–F64
   - Carga pesada (processamento contínuo, múltiplas equipes): F128+

2. Use `azure_price_search` para buscar o preço do F-SKU alvo:
   ```
   serviceName: "Microsoft Fabric"
   skuName: "F[N] Capacity"  ← ex: "F64 Capacity"
   region: brazilsouth
   ```

3. Se o cliente quiser estimar por workload específico (ex: só Eventhouse ou só Data Warehouse),
   use `azure_price_search` com o nome do workload (ex: `skuName: "Eventhouse Capacity Usage"`).

**Regras de ambiente para Fabric:**

| Ambiente        | Abordagem                                      |
|-----------------|------------------------------------------------|
| Produção        | F-SKU completo × 730h/mês                     |
| Homologação     | F-SKU 1 tier abaixo × 200h/mês (ou compartilhado) |
| Desenvolvimento | F-SKU mínimo (F2/F4) × uso estimado           |

Apresente o custo como: `preço CU/hora × horas/mês = $X/mês por ambiente`.

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

Use as tools do MCP diretamente:

```
databricks_dbu_pricing  → buscar preços de DBU para o tipo de cluster e região
databricks_cost_estimate → calcular custo mensal completo (compute + DBU)
```

Calcule para os 3 ambientes com as mesmas regras de sizing.

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
   Região: [região] | Preço: on-demand retail público | Moeda: USD

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
- **Não usar preços com desconto** — sempre on-demand / retail público
- **Não somar EC2 do Databricks (AWS) duas vezes** — já está no estimate AWS
- **Não assumir região sem confirmar** — especialmente para clientes de setores regulados
- **Não gerar sem confirmar (Fase 5)** — o resumo evita retrabalho
