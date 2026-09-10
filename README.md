# Cloud Pricing Calculator

Skill para Claude Code que gera estimativas de custo em nuvem a partir de uma conversa guiada com o arquiteto.

- **AWS** → link oficial `calculator.aws` pronto para enviar ao parceiro
- **Azure** → estimativa detalhada com preços públicos via Retail Prices API

---

## Como rodar

Veja [plugin/INSTALL.md](plugin/INSTALL.md).

---

## Escopo

### Problema

Arquitetos de soluções montam estimativas de custo manualmente nas calculadoras oficiais de cada provider (AWS, Azure, Databricks). O processo é lento, sujeito a erro e gera retrabalho: a conta interna não basta — para solicitar incentivo ao parceiro, é obrigatório enviar a calculadora oficial preenchida.

### Solução

Skill `/cotar_cloud` para Claude Code, integrada a dois MCPs:

- **AWS** — `aws-samples/sample-aws-pricing-calculator-mcp`: cria o estimate e exporta um link oficial `calculator.aws`
- **Azure** — `msftnadavbh/AzurePricingMCP`: consulta a Azure Retail Prices API e estima custo por serviço, incluindo Databricks on Azure via DBU

O arquiteto descreve o problema do cliente ou lista os serviços desejados. A skill detecta o provider, sugere arquitetura (com base nos padrões Dataside), coleta o dimensionamento progressivamente e gera a estimativa.

### O que está dentro do escopo

- Serviços AWS cobertos pela calculadora oficial
- Databricks on AWS: EC2 no estimate + DBU estimado separadamente
- Serviços Azure cobertos pela Retail Prices API (VMs, Storage, SQL, AKS, etc.)
- Databricks on Azure: compute + DBU via MCP (`databricks_dbu_pricing`, `databricks_cost_estimate`)
- Microsoft Fabric: estimativa por F-SKU (Capacity reservation) ou por workload (CU/hora) via `azure_price_search` — cobertura completa da Retail Prices API
- 3 ambientes: Produção, Homologação e Desenvolvimento com sizing proporcional automático
- Modo conversacional: Claude sugere arquitetura, coleta dimensionamento e confirma antes de gerar
- Arquiteturas padrão Dataside cadastradas na skill (AWS: 4 arquiteturas | Azure: a preencher)
- Preços sempre on-demand / retail público (sem descontos)

### O que está fora do escopo

- Link compartilhável da Azure Pricing Calculator — não há API pública para geração programática; o arquiteto recebe a estimativa e preenche a calculadora manualmente se necessário
- Snowflake — custo fora das calculadoras AWS e Azure; valores disponíveis via PDF da calculadora oficial (sem API)
- Google Cloud
- Preços negociados ou com desconto (EA, CSP)

### Arquitetura da solução

```
Arquiteto → /cotar_cloud + provider + descrição
                  ↓
            Claude Code (SKILL_unified.md)
            [detecta provider → sugere arquitetura → dimensiona → confirma]
                  ↓
        ┌─────────────────────────────────────────┐
        │ AWS                    │ Azure           │
        │ MCP: aws-pricing-      │ MCP: azure-     │
        │ calculator             │ pricing-mcp     │
        │ create_estimate →      │ azure_discover_ │
        │ add_service →          │ skus →          │
        │ export_estimate        │ azure_cost_     │
        │ ↓                      │ estimate        │
        │ Link calculator.aws    │ Estimativa USD  │
        └─────────────────────────────────────────┘
```

---

## Como garantimos os valores oficiais

**AWS:** o MCP `aws-samples/sample-aws-pricing-calculator-mcp` usa a mesma API interna do `calculator.aws`. O link retornado por `export_estimate` é um link real do `calculator.aws` — o próprio artefato exigido pelo parceiro.

**Azure:** a Azure Retail Prices API (`prices.azure.com`) é a fonte pública oficial de preços da Microsoft, sem autenticação. Os valores retornados são idênticos aos exibidos em `calculator.microsoft.com`. Não há link gerado — a estimativa é entregue como breakdown de custo por serviço.

**Databricks on AWS:** calculado com a fórmula oficial (`DBU/hora × nós × horas/mês × preço/DBU`) usando a tabela de preços pay-as-you-go de `sa-east-1`. Conta apresentada aberta para conferência.

**Databricks on Azure:** estimado via tools do MCP (`databricks_dbu_pricing`, `databricks_cost_estimate`) que consultam a Retail Prices API diretamente.

---

## O que faríamos diferente / Features futuras

**Link da Azure Pricing Calculator:** a geração programática exige autenticação de sessão de navegador (cookie + CSRF). Abordagem V2 via browser agent (Playwright ou Claude in Chrome).

**Arquiteturas Dataside Azure:** os padrões Azure (Databricks Lakehouse, Fabric, AI Agent) serão cadastrados na skill à medida que forem documentados.

**Google Cloud:** sem MCP disponível no momento; requer desenvolvimento de MCP próprio ou integração com a Cloud Billing API.

**Interface web standalone:** para SAs que não usam Claude Code ou para autoatendimento de clientes.

---

## Impacto estimado

> Estimativas de mercado — valores reais devem ser validados com o time.

### Redução de custo operacional

| | Manual | Com skill |
|---|---|---|
| Tempo por estimativa | 3h | 20 min |
| Estimativas/mês (por SA) | 6 | 6 |
| Horas gastas/mês | 18h | 2h |
| Custo interno (R$ 200/h) | R$ 3.600 | R$ 400 |

**Redução: ~R$ 3.200/mês por SA** em horas recuperadas.

### Receita potencial

| Horas recuperadas/mês | Taxa faturável | Receita potencial/mês | Receita potencial/ano |
|---|---|---|---|
| 16h por SA | R$ 350/h | R$ 5.600 por SA | R$ 67.200 por SA |
| Com 3 SAs | — | R$ 16.800 | **~R$ 200.000** |

---

## Equipe

- **Samuel** — núcleo de preço, integração das tools, documentação
- **André** — servidor MCP, automação do navegador (export)
- **Natália** — Skill, biblioteca de padrões, testes de ponta a ponta
- **Arthur** — integração do MCP de comunidade (AzurePricingMCP) com o MCP próprio
- **Cauã** — redesenho da biblioteca de padrões de arquitetura

---

## Referências

- [MCP AWS Pricing Calculator](https://github.com/aws-samples/sample-aws-pricing-calculator-mcp)
- [MCP Azure Pricing](https://github.com/msftnadavbh/AzurePricingMCP)
- [Calculadora oficial AWS](https://calculator.aws)
- [Calculadora oficial Azure](https://calculator.microsoft.com)
- [Azure Retail Prices API](https://prices.azure.com/api/retail/prices)
- [Calculadora Databricks](https://www.databricks.com/product/pricing)
- [Instalação](plugin/INSTALL.md)

---

## Log de organização

### Fase original — Desafio Aceleras (Grupo 2: Sarah + André)

| Data          | Esperado                                                             | Cumprido                                                                                                                |
| ------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 22/06         | Reunião de alinhamento e formulação de perguntas para as entrevistas | Reunião feita                                                                                                           |
| 23/06         | Entrevista com Nelson (SA — Eficiência Operacional)                  | Feito — entendimento do fluxo atual de estimativa e calculadoras                                                        |
| 24/06         | Entrevista com Oscar (Head de Dados e IA)                            | Feito — entendimento do sistema de propostas, critérios de aceitação do parceiro e requisito do link oficial            |
| 25/06         | Decisão de escopo e abordagem técnica                                | Feito — AWS + Databricks via skill Claude Code + MCP; descartadas abordagens Next.js e browser agent para o MVP         |
| 26/06 – 29/06 | Desenvolvimento do primeiro protótipo (skill + MCP)                  | Feito — skill `/cotar_cloud` funcional: estimate AWS com 3 ambientes, estimativa DBU Databricks, link oficial gerado    |
| 29/06         | Reunião com Cauã (SA) para apresentação do primeiro protótipo        | Feito — feedback: modo conversacional necessário, ideia de browser agent para Azure                                     |
| 01/07 – 03/07 | Aprimoramento do protótipo com base no feedback                      | Feito — modo conversacional, sugestão de arquitetura pelo Claude, arquiteturas padrão Dataside AWS cadastradas          |
| 03/07         | **DATA FINAL DE ENTREGA — Aceleras**                                 | ✅                                                                                                                      |

### Fase atual — Produto real · Cronograma 1 (29/07 – 28/08)

Três blocos de trabalho rodando em paralelo: enquanto Samuel fecha o núcleo de preço, André adianta o esqueleto do MCP e Natália constrói a biblioteca de padrões e a Skill.

#### Fase 1 — Núcleo de preço · 29/07 – 01/08

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Samuel** | `retail_client.py` + `meters.py` (VM, Storage, SQL) + `resolve_price`, com testes pytest | |
| **André** | Esqueleto do servidor MCP: `server.py` (FastMCP) registrando as 6 tools como *stubs*; validar no MCP Inspector | |
| **Natália** | Biblioteca de padrões: 3 arquiteturas de referência em YAML (three-tier, AKS, lakehouse) + rascunho do `SKILL.md` | |

#### Fase 2 — MCP mínimo (fatia vertical) · 04/08 – 08/08

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Samuel** | Ligar `resolve_price` às tools de preço (`search_azure_services`, `get_service_config_schema`, `resolve_price`, `add_line_item`) | |
| **André** | Implementar `export_estimate` dirigindo a UI da calculadora via Playwright: mapear seletores, capturar o link | |
| **Natália** | Testar a fatia vertical no Claude Code (pedido cru → link + custo) e registrar bugs e lacunas de configuração | |

#### Fase 3 — Skill + interpretação · 10/08 – 21/08

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Natália** | Finalizar `SKILL.md` (workflow completo) + `interpretation-guide.md` + `validation-rules.md` | |
| **Samuel** | Afinar os resolvers para garantir que todos os serviços dos 3 padrões resolvem preço corretamente | |
| **André** | Robustez do export: retry, fallback e detecção de sessão expirada | |

#### Fase 4 — Integração e entrega · 24/08 – 28/08

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Todos** | Teste ponta a ponta: arquiteto descreve uma arquitetura padrão → recebe link + custo; correção de bugs | |
| **Samuel** | Finalizar `README.md`, `PROGRESS.md` e o `.mcp.json` de instalação | |
| **André + Natália** | Preparar a demo da entrega: roteiro + caso de exemplo completo | |

---

### Cronograma 2 — Segunda entrega (04/09 – 18/09)

Duas frentes em paralelo: Natália e Cauã redesenham a biblioteca de padrões; Samuel, Arthur e André integram o [AzurePricingMCP](https://github.com/msftnadavbh/AzurePricingMCP) ao projeto.

#### Bloco 1 — Descoberta e planejamento · 07/09 – 11/09

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Natália** | Revisar os 3 padrões atuais e levantar o que muda no redesenho | |
| **Cauã** | Levantar referências de arquitetura para orientar as novas versões dos 3 padrões | |
| **Samuel** | Rodar o AzurePricingMCP localmente e mapear suas tools/capacidades | |
| **Arthur** | Comparar tools do AzurePricingMCP com as do MCP próprio e listar sobreposições/lacunas | |
| **André** | Levantar os padrões de entrega do projeto que o AzurePricingMCP precisa seguir para ser incorporado | |

#### Bloco 2 — Execução · 14/09 – 16/09

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Natália** | Redesenhar os 3 padrões (novas versões dos YAMLs de arquitetura) | |
| **Cauã** | Validar os padrões redesenhados contra os resolvers existentes | |
| **Samuel** | Adequar o código do AzurePricingMCP à estrutura/testes do projeto | |
| **Arthur + André** | Primeira tentativa de integração entre o AzurePricingMCP e o MCP Playwright; checar consistência de preços | |

#### Bloco 3 — Fechamento e entrega · 17/09 – 18/09

| Membro | Tarefa | Cumprido |
|--------|--------|:--------:|
| **Natália + Cauã** | Testar arquiteturas redesenhadas ponta a ponta e atualizar documentação da Skill/padrões | |
| **Samuel + Arthur + André** | Fechar a integração do AzurePricingMCP, corrigir bugs e preparar a demo | |
| **Todos** | Teste ponta a ponta da entrega, revisão final | |
