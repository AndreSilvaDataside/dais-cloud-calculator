# Instalação do comando /cotar_cloud

## Pré-requisitos

- Node.js 18+
- Python 3.10+ com `uv` instalado ([instalação](https://docs.astral.sh/uv/getting-started/installation/): `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Claude Code (extensão VS Code ou CLI)
- Git

---

## 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/dais-cloud-calculator.git
cd dais-cloud-calculator
```

O `.mcp.json` na raiz registra os dois servidores MCP. Na primeira abertura no
Claude Code, você verá um prompt pedindo aprovação — clique em **Allow**.

---

## 2. Instalar o MCP da AWS Pricing Calculator

Não exige clonar nada — o npx baixa e executa diretamente do npm:

```bash
# Teste rápido (opcional):
npx -y sample-aws-pricing-calculator-mcp
```

O `.mcp.json` já configura o npx automaticamente para o Claude Code.

---

## 3. Instalar o MCP da Azure Pricing

Nenhuma ação necessária — o `.mcp.json` já configura o `uvx` para baixar e executar
o MCP diretamente do GitHub, sem clonar nem criar venv:

```bash
# Teste rápido (opcional):
uvx --from git+https://github.com/msftnadavbh/AzurePricingMCP azure-pricing-mcp
```

> **Nota:** `uvx` usa cache local após o primeiro download. Para forçar atualização:
> `uvx --refresh --from git+https://github.com/msftnadavbh/AzurePricingMCP azure-pricing-mcp`

---

## 4. Instalar o comando /cotar_cloud

```bash
mkdir -p .claude/commands
cp plugin/skills/cotar_cloud/SKILL_unified.md .claude/commands/cotar_cloud.md
```

---

## 5. Testar a instalação

Reinicie o Claude Code e envie:

```
/cotar_cloud

Quero cotar um lakehouse com Databricks para um cliente de varejo. Usa AWS.
```

E para Azure:

```
/cotar_cloud

Preciso estimar um ambiente de analytics com Azure Databricks. Região Brazil South.
```

---

## Estrutura de arquivos

```
projeto/
├── .mcp.json                         ← registra AWS (npx) e Azure (uvx) MCPs
├── README.md
├── .claude/
│   └── commands/
│       └── cotar_cloud.md            ← gerado no passo 4
└── plugin/
    ├── INSTALL.md                    ← este arquivo
    └── skills/
        └── cotar_cloud/
            ├── SKILL_unified.md      ← skill unificada AWS + Azure (recomendada)
            ├── SKILL_v1.md           ← versão original AWS sem arquiteturas
            └── SKILL_v2.md           ← versão original AWS com placeholder
```

---

## Referências

- MCP AWS Pricing Calculator: https://github.com/aws-samples/sample-aws-pricing-calculator-mcp
- MCP Azure Pricing: https://github.com/msftnadavbh/AzurePricingMCP
- Calculadora oficial AWS: https://calculator.aws
- Calculadora oficial Azure: https://calculator.microsoft.com
- Azure Retail Prices API: https://prices.azure.com/api/retail/prices
- Calculadora Databricks: https://www.databricks.com/product/pricing
