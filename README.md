# Cloud Pricing Calculator

Atualizado: 03/07/2026

Skill para Claude Code que gera estimativas de custo em nuvem a partir de uma conversa guiada com o arquiteto, retornando um link oficial do AWS Pricing Calculator pronto para enviar ao parceiro AWS.

**Grupo 2:** Sarah + André

---

## Como rodar

Veja [plugin/INSTALL.md](plugin/INSTALL.md).

---

## Escopo

### Problema

Arquitetos de soluções montam estimativas de custo manualmente nas calculadoras oficiais de cada provider (AWS, Azure, Databricks). O processo é lento, sujeito a erro e gera retrabalho: a conta interna não basta — para solicitar incentivo ao parceiro, é obrigatório enviar a calculadora oficial preenchida.

### Solução

Skill `/cotar_cloud` para Claude Code, integrada ao MCP oficial da AWS (`aws-samples/sample-aws-pricing-calculator-mcp`). O arquiteto descreve a arquitetura — ou simplesmente descreve o problema do cliente — e recebe:

- Conversa guiada que sugere a arquitetura (com base nos padrões Dataside cadastrados) e coleta o dimensionamento progressivamente, uma ou duas perguntas por vez
- Link compartilhável oficial do `calculator.aws` com os serviços organizados em grupos de ambiente (Produção, Homologação, Desenvolvimento)
- Estimativa de custo DBU do Databricks calculada separadamente, com instrução para confirmar no site oficial

### Decisões de escopo

**Provider:** AWS + Databricks on AWS — foco do MVP, baseado nas entrevistas com os SAs da Dataside (maior volume de uso e melhor suporte programático via MCP).

**O que está dentro do escopo:**

- Serviços AWS cobertos pela calculadora oficial
- Databricks Job Cluster e All-Purpose Cluster (custo EC2 no estimate AWS + estimativa de DBU separada)
- 3 ambientes: Produção, Homologação e Desenvolvimento com sizing proporcional automático
- Modo conversacional: Claude sugere arquitetura, coleta dimensionamento progressivamente e confirma antes de gerar
- Arquiteturas padrão Dataside cadastradas na skill (4 arquiteturas AWS)
- Preços sempre on-demand (sem descontos)

**O que está fora do escopo no MVP:**

- Azure e Google Cloud — não há API pública que gere links oficiais programaticamente; abordagem V2 via browser agent
- Microsoft Fabric — modelo de cobrança por capacidade (diferente de serviço a serviço), sem suporte na calculadora via MCP
- Snowflake on AWS — custo Snowflake está fora da AWS Pricing Calculator
- Serviços fora da calculadora oficial (ex: Vector Search) — sinalizados ao arquiteto com link para a pricing page

### Arquitetura da solução

```
Arquiteto → /cotar_cloud + descrição do cliente
                  ↓
            Claude Code (SKILL.md)
            [modo conversa: sugere arquitetura → dimensiona → confirma]
                  ↓
         MCP: aws-pricing-calculator
         (aws-samples/sample-aws-pricing-calculator-mcp)
                  ↓
    create_estimate → add_service (prod/homolog/dev) → export_estimate
                  ↓
        Link oficial calculator.aws
        + Estimativa DBU Databricks (calculada na skill)
```

---

## Como garantimos os valores oficiais

**AWS:** o MCP `aws-samples/sample-aws-pricing-calculator-mcp` é o repositório oficial da AWS e usa a mesma API interna do `calculator.aws`. O estimate criado pelo MCP é idêntico ao que seria gerado manualmente — o link retornado por `export_estimate` é um link real do `calculator.aws`, o próprio artefato exigido pelo parceiro. Não há recálculo intermediário: os valores vêm diretamente da API oficial.

**Databricks:** não existe API que gere links programáticos da calculadora Databricks. A solução adotada foi calcular o custo de DBU com a fórmula oficial (`DBU/hora × nós × horas/mês × preço/DBU`), usando a tabela de preços pay-as-you-go de sa-east-1 como referência. A conta é apresentada aberta para o arquiteto rastrear e conferir. Ao final, a skill instrui o arquiteto a validar o valor em `databricks.com/product/pricing` e anexar o print à proposta.

---

## O que faríamos diferente/Features futuras

**Cobrir Azure:** a Azure Retail Prices API (`prices.azure.com`) é pública e sem autenticação — dá para buscar preços de qualquer serviço. O problema é que não há API equivalente para gerar um link compartilhável da Azure Pricing Calculator. A solução viável para V2 é um browser agent (Playwright ou Claude in Chrome) que preenche a calculadora e exporta o link, replicando o que o MCP faz para a AWS.

**Cobrir Databricks on Azure:** diferente do Databricks on AWS (duas calculadoras separadas), o Databricks on Azure tem calculadora própria da Microsoft — o mesmo problema de geração programática de link se aplica.

**Arquiteturas de outros providers:** as 4 arquiteturas padrão Dataside cadastradas na skill são todas AWS. Com mais tempo, adicionaríamos os padrões Azure (Fabric + Databricks), GCP e os padrões híbridos.

**Interface web standalone:** a skill resolve o problema para quem usa Claude Code. Para SAs que não usam (ou clientes que queiram autoatendimento), uma interface web com os mesmos fluxos conversacionais seria o próximo passo natural.

---

## Referências

- [MCP AWS Pricing Calculator](https://github.com/aws-samples/sample-aws-pricing-calculator-mcp)
- [Calculadora oficial AWS](https://calculator.aws)
- [Calculadora Databricks](https://www.databricks.com/product/pricing)
- [Instalação do plugin](plugin/INSTALL.md)

---

## Log de organização

Registro do planejamento e execução ao longo das duas semanas do desafio.

| Data          | Esperado                                                             | Cumprido                                                                                                                |
| ------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 22/06         | Reunião de alinhamento e formulação de perguntas para as entrevistas | Reunião feita                                                                                                           |
| 23/06         | Entrevista com Nelson (SA — Eficiência Operacional)                  | Feito — entendimento do fluxo atual de estimativa e calculadoras                                                        |
| 24/06         | Entrevista com Oscar (Head de Dados e IA)                            | Feito — entendimento do sistema de propostas, critérios de aceitação do parceiro e requisito do link oficial            |
| 25/06         | Decisão de escopo e abordagem técnica                                | Feito — AWS + Databricks via skill Claude Code + MCP; descartadas abordagens Next.js e browser agent para o MVP         |
| 26/06 – 29/06 | Desenvolvimento do primeiro protótipo (skill + MCP)                  | Feito — skill `/cotar_cloud` funcional: estimate AWS com 3 ambientes, estimativa DBU Databricks, link oficial gerado    |
| 29/06         | Reunião com Cauã (SA) para apresentação do primeiro protótipo        | Feito — feedback: modo conversacional necessário (SA não quer preencher formulário), ideia de browser agent para Azure  |
| 01/07 – 03/07 | Aprimoramento do protótipo com base no feedback                      | Feito — modo conversacional implementado, sugestão de arquitetura pelo Claude, arquiteturas padrão Dataside cadastradas |
| 03/07         | **DATA FINAL DE ENTREGA**                                            | ✅                                                                                                                      |
