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
- Serviços Azure cobertos pela Retail Prices API: Virtual Machines, ADLS Gen2,
  Key Vault, VNet, egress, discos gerenciados
- Databricks on Azure: dois modelos de cobrança separados — clássico
  (`Azure Databricks`, DBU + VM) e serverless (`Azure Databricks Regional`, só DBU)
- Microsoft Fabric: capacidade **calculada a partir do CU** (0,28/CU-hora sob demanda,
  1.458,00/CU-ano na reserva) mais armazenamento OneLake. Não existe meter de F SKU
  na Retail Prices API — ver a seção de armadilhas na Skill
- 3 ambientes: Produção, Homologação e Desenvolvimento, com regras próprias para
  Fabric, Databricks e armazenamento
- Modo conversacional: Claude sugere arquitetura, coleta dimensionamento e confirma antes de gerar
- Arquiteturas padrão Dataside cadastradas na skill (AWS: 4 | Azure: 5)
- Preços retail públicos, sem desconto negociado. Em Fabric, os dois modelos de
  compra são apresentados (sob demanda e reserva), nunca escolhidos em silêncio
- Verificação: `tools/valida_precos.py` reconfere cada preço afirmado na Skill
  contra a API

### O que está fora do escopo

- Link compartilhável da Azure Pricing Calculator — não há API pública para geração programática; o arquiteto recebe a estimativa e preenche a calculadora manualmente se necessário
- Snowflake — custo fora das calculadoras AWS e Azure; valores disponíveis via PDF da calculadora oficial (sem API)
- Google Cloud
- Preços negociados ou com desconto (EA, CSP)
- AKS, Synapse e padrão de microsserviços — fora por indicação do arquiteto de
  soluções (a Dataside não vende AKS nem microsserviços; Synapse praticamente não
  se usa mais)
- Private Link e Private Endpoint — **não existem** na Retail Prices API, nem em
  `brazilsouth` nem em `eastus`. Entram na arquitetura como premissa declarada sem
  valor, a confirmar com o parceiro Microsoft
- Licenças Power BI Pro/PPU e demais itens M365 — licenciamento, não consumo Azure;
  fora da Retail Prices API
- Lado AWS: mantido e congelado, fora do escopo desta entrega

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

**Link da Azure Pricing Calculator:** fora do critério de aceite desde 10/09.
A geração programática exigiria autenticação de sessão de navegador (cookie + CSRF),
e a automação via Playwright foi descontinuada em 09/09 — segundo o arquiteto de
soluções, o link serve principalmente para pedido de incentivo à Microsoft e cerca
de 80% dos clientes não o abre. Se voltar ao escopo, seria via browser agent.

**Snapshot da Retail Prices API como fonte na demo:** `tools/sonda_catalogo.py sweep`
gera um snapshot da região inteira. Resolver preço em cima dele é instantâneo e
reprodutível, em vez de depender da API ao vivo durante apresentação. Proposta ao
time, ainda não decidida — ver `tools/README.md`.

**Google Cloud:** sem MCP disponível no momento; requer desenvolvimento de MCP próprio ou integração com a Cloud Billing API.

**Interface web standalone:** para SAs que não usam Claude Code ou para autoatendimento de clientes.

---

## Verificação de preço

Toda tabela de preço dentro da Skill é uma afirmação sobre a Retail Prices API.
Duas ferramentas em [`tools/`](tools/) permitem reconferir em um comando, sem
dependência externa:

```bash
python tools/valida_precos.py              # confere a Skill contra a API (~50s)
python tools/sonda_catalogo.py probe --service "Microsoft Fabric" --price-type Reservation
```

Rodar antes de apresentar ao cliente, antes de aprovar PR que mexa em número, e
antes de pôr valor em slide. Detalhes em [tools/README.md](tools/README.md).

Para apresentar, o [roteiro de demo](ROTEIRO-DEMO.md) traz um cenário ensaiado com
os números já conferidos, as respostas a dar, o tempo esperado de cada etapa e o
que fazer se algo sair diferente.

Falha não é necessariamente bug: se a Azure mudou um preço, a conferência falha e
está certa em falhar — o aviso é de que uma tabela da Skill envelheceu.

---

## Licenças

Este repositório é Apache 2.0 (ver [LICENSE](LICENSE)). O
[AzurePricingMCP](https://github.com/msftnadavbh/AzurePricingMCP) é MIT e é
consumido via `uvx` a partir do repositório de origem, sem cópia de código — as
duas licenças são compatíveis e não há código de terceiro vendorizado aqui.

---

## Equipe

- **Samuel** — documentação, núcleo de preço (descontinuado com o MCP próprio)
- **André** — esqueleto do repositório, integração dos MCPs, arquiteturas Azure
- **Natália** — Skill, regras de resolução e validação, ferramentas de verificação,
  teste ponta a ponta
- **Arthur** — verificação do MCP de comunidade (AzurePricingMCP), demo
- **Cauã Souza Almeida** — referências de arquitetura, validação dos padrões

Fora do time, mas decisivos: **Cauã Pablo Carvalho** (arquiteto de soluções,
avaliador externo), **Oscar** (Head de Dados e IA, dono do critério de aceite) e
**Marcio** (responsável pelo programa).

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

| Data          | Esperado                                                             | Cumprido                                                                                                             |
| ------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 22/06         | Reunião de alinhamento e formulação de perguntas para as entrevistas | Reunião feita                                                                                                        |
| 23/06         | Entrevista com Nelson (SA — Eficiência Operacional)                  | Feito — entendimento do fluxo atual de estimativa e calculadoras                                                     |
| 24/06         | Entrevista com Oscar (Head de Dados e IA)                            | Feito — entendimento do sistema de propostas, critérios de aceitação do parceiro e requisito do link oficial         |
| 25/06         | Decisão de escopo e abordagem técnica                                | Feito — AWS + Databricks via skill Claude Code + MCP; descartadas abordagens Next.js e browser agent para o MVP      |
| 26/06 – 29/06 | Desenvolvimento do primeiro protótipo (skill + MCP)                  | Feito — skill `/cotar_cloud` funcional: estimate AWS com 3 ambientes, estimativa DBU Databricks, link oficial gerado |
| 29/06         | Reunião com Cauã (SA) para apresentação do primeiro protótipo        | Feito — feedback: modo conversacional necessário, ideia de browser agent para Azure                                  |
| 01/07 – 03/07 | Aprimoramento do protótipo com base no feedback                      | Feito — modo conversacional, sugestão de arquitetura pelo Claude, arquiteturas padrão Dataside AWS cadastradas       |
| 03/07         | **DATA FINAL DE ENTREGA — Aceleras**                                 | ✅                                                                                                                   |

### Cronograma 1 (29/07 – 28/08) — histórico, abordagem substituída

> **Registro histórico. Não é plano de trabalho.**
>
> Este cronograma descreve o MCP próprio em Python
> (`samekmd/azure-pricing-estimator`): núcleo de preço, resolvers e automação da
> calculadora oficial via Playwright para gerar link compartilhável. O trabalho
> aconteceu de fato — chegou a 265 testes e foi apresentado na Fase 4.
>
> **Substituído em 09/09.** Depois da apresentação ao arquiteto de soluções em
> 01/09, o time decidiu reconstruir sobre o repositório de Skill, consumindo o
> [AzurePricingMCP](https://github.com/msftnadavbh/AzurePricingMCP) via `uvx` em
> vez do MCP próprio. Com isso caíram: os *resolvers*, o `retail_client.py`, o
> `server.py` FastMCP e todo o `export_estimate` via Playwright.
>
> Mantido aqui porque explica de onde vieram as decisões, e porque o MCP antigo
> fica arquivado como referência, não deletado. As colunas "Cumprido" ficaram em
> branco e assim permanecem — não há o que preencher em trabalho descontinuado.

Três blocos rodavam em paralelo: Samuel fechava o núcleo de preço, André adiantava o esqueleto do MCP e Natália construía a biblioteca de padrões e a Skill.

#### Fase 1 — Núcleo de preço · 29/07 – 01/08

| Membro      | Tarefa                                                                                                            | Cumprido |
| ----------- | ----------------------------------------------------------------------------------------------------------------- | :------: |
| **Samuel**  | `retail_client.py` + `meters.py` (VM, Storage, SQL) + `resolve_price`, com testes pytest                          |          |
| **André**   | Esqueleto do servidor MCP: `server.py` (FastMCP) registrando as 6 tools como _stubs_; validar no MCP Inspector    |          |
| **Natália** | Biblioteca de padrões: 3 arquiteturas de referência em YAML (three-tier, AKS, lakehouse) + rascunho do `SKILL.md` |          |

#### Fase 2 — MCP mínimo (fatia vertical) · 04/08 – 08/08

| Membro      | Tarefa                                                                                                                           | Cumprido |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- | :------: |
| **Samuel**  | Ligar `resolve_price` às tools de preço (`search_azure_services`, `get_service_config_schema`, `resolve_price`, `add_line_item`) |          |
| **André**   | Implementar `export_estimate` dirigindo a UI da calculadora via Playwright: mapear seletores, capturar o link                    |          |
| **Natália** | Testar a fatia vertical no Claude Code (pedido cru → link + custo) e registrar bugs e lacunas de configuração                    |          |

#### Fase 3 — Skill + interpretação · 10/08 – 21/08

| Membro      | Tarefa                                                                                            | Cumprido |
| ----------- | ------------------------------------------------------------------------------------------------- | :------: |
| **Natália** | Finalizar `SKILL.md` (workflow completo) + `interpretation-guide.md` + `validation-rules.md`      |          |
| **Samuel**  | Afinar os resolvers para garantir que todos os serviços dos 3 padrões resolvem preço corretamente |          |
| **André**   | Robustez do export: retry, fallback e detecção de sessão expirada                                 |          |

#### Fase 4 — Integração e entrega · 24/08 – 28/08

| Membro              | Tarefa                                                                                                 | Cumprido |
| ------------------- | ------------------------------------------------------------------------------------------------------ | :------: |
| **Todos**           | Teste ponta a ponta: arquiteto descreve uma arquitetura padrão → recebe link + custo; correção de bugs |          |
| **Samuel**          | Finalizar `README.md`, `PROGRESS.md` e o `.mcp.json` de instalação                                     |          |
| **André + Natália** | Preparar a demo da entrega: roteiro + caso de exemplo completo                                         |          |

---

### Cronograma 2 — Segunda entrega (04/09 – 18/09)

Duas frentes em paralelo: Natália e Cauã redesenham a biblioteca de padrões;
Samuel, Arthur e André trocam o MCP próprio pelo
[AzurePricingMCP](https://github.com/msftnadavbh/AzurePricingMCP).

> **Corrigido em 14/09.** A versão anterior deste cronograma descrevia tarefas que
> foram canceladas com a decisão de 09/09 — adequar o código do AzurePricingMCP à
> estrutura do projeto, integrá-lo ao MCP Playwright, e afinar *resolvers*. Nada
> disso existe na entrega atual: o AzurePricingMCP é consumido via `uvx` sem cópia
> de código, não há Playwright, e não há resolver. As linhas abaixo descrevem o que
> foi efetivamente feito.

#### Bloco 1 — Descoberta e planejamento · 07/09 – 11/09

| Membro      | Tarefa                                                                                              | Cumprido |
| ----------- | --------------------------------------------------------------------------------------------------- | :------: |
| **Natália** | Revisar os padrões atuais e levantar o que muda no redesenho                                        |    ✅    |
| **Cauã**    | Levantar referências de arquitetura para orientar as novas versões dos padrões                      |          |
| **Samuel**  | Rodar o AzurePricingMCP localmente e mapear suas tools/capacidades                                   |          |
| **Arthur**  | Comparar tools do AzurePricingMCP com as do MCP próprio e listar sobreposições/lacunas               |          |
| **André**   | Integrar o AzurePricingMCP via `uvx` no `.mcp.json`                                                  |    ✅    |

#### Bloco 2 — Execução · 14/09 – 16/09

| Membro      | Tarefa                                                                                                          | Cumprido |
| ----------- | ----------------------------------------------------------------------------------------------------------------- | :------: |
| **Natália** | Reescrever a camada Azure da Skill: Fabric calculado por CU, chave de resolução de cinco campos, allowlist por serviço, oito gates de validação, separação clássico/serverless em Databricks |    ✅    |
| **Natália** | `tools/sonda_catalogo.py` e `tools/valida_precos.py`: verificação dos preços da Skill contra a Retail Prices API |    ✅    |
| **Natália** | Teste ponta a ponta em três cenários (Fabric, Databricks, ADLS + Private Endpoint) e correção das lacunas achadas |    ✅    |
| **Natália** | Documentar o que o MCP realmente devolve — ele não expõe `meterName` nem `tierMinimumUnits`, então a allowlist é a fonte de preço; mais 9 serviços na allowlist |    ✅    |
| **Natália** | Carimbar a região na allowlist: os preços são de `brazilsouth` e não há fator de correção regional |    ✅    |
| **André**   | Cadastrar as 5 arquiteturas padrão Dataside para Azure na Skill                                                  |    ✅    |
| **Cauã**    | Validar os padrões cadastrados contra as referências de arquitetura                                              |          |
| **Samuel**  | Corrigir README e cronograma; registrar por escrito a decisão sobre o link e o escopo                            |          |
| **Arthur**  | Verificar a cobertura do AzurePricingMCP para os serviços em escopo                                              |          |

#### Bloco 3 — Fechamento e entrega · 17/09 – 18/09

> **Proposta de antecipação da demo para 16/09.** O desenvolvimento acabou e está
> mergeado no `develop`, e a preparação da demo já tem roteiro ensaiado com números
> conferidos ([ROTEIRO-DEMO.md](ROTEIRO-DEMO.md))
| Membro                      | Tarefa                                                                                             | Cumprido |
| --------------------------- | ---------------------------------------------------------------------------------------------------- | :------: |
| **Natália**                 | Retestar a Skill com as arquiteturas Azure cadastradas — 6 cenários, 6 acertos, incluindo o par difícil (Arq 1 × Arq 5) e um que corretamente não casou com padrão nenhum |    ✅    |
| **Natália**                 | Preparar o roteiro de demo: cenário ensaiado, 22 linhas conferidas, tempo medido por etapa          |    ✅    |
| **Cauã**                    | Validar as arquiteturas cadastradas contra as referências de arquitetura                            |          |
| **André**                   | Resolver o modelo de instalação da Skill: `.gitignore` ignora `.claude/`, então a cópia executada não é versionada e precisa ser refeita a cada edição |          |
| **Todos**                   | Confirmar com o arquiteto se Azure Data Factory e Power BI entram nas propostas                     |          |
| **Samuel + Arthur + André** | Apresentar a demo (roteiro pronto)                                                                  |          |
| **Todos**                   | Revisão final e lançamento de horas no Dataflow                                                     |          |

**O que ainda pode mexer na entrega:** a confirmação do arquiteto sobre Azure Data
Factory e Power BI. Se Power BI entrar nas propostas, muda o formato de saída da
Skill. É a única pendência que altera código — as outras são validação, instalação
e processo. Vindo essa resposta, **18/09 pode fechar em 17/09**.

**O que não depende do time:** a resposta do arquiteto de soluções (avaliador
externo) e o booking no Dataflow. Encurtar prazo não acelera nenhuma das duas.
