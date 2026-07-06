# Instalação do comando /cotar_cloud

## Pré-requisitos

- Node.js 18+
- Claude Code (extensão VS Code ou CLI)
- Git

---

## 1. Clonar o repositório

```bash
git clone https://github.com/AndreViniNe/dais-cloud-calculator.git
cd dais-cloud-calculator
```

O repositório inclui um `.mcp.json` na raiz que configura o MCP automaticamente. Na primeira abertura no Claude Code, você verá um prompt pedindo aprovação para ativar o MCP — clique em **Allow**.

---

## 2. Instalar o comando /cotar_cloud

```bash
mkdir -p .claude/commands
cp plugin/skills/cotar_cloud/SKILL_v2.md .claude/commands/cotar_cloud.md
```

O frontmatter do arquivo declara quais tools do MCP são necessárias — o Claude Code as ativa automaticamente quando o comando é invocado.

---

## 3. Testar a instalação

Reinicie o Claude Code no VS Code (feche e reabra o painel) e envie:

```
/cotar_cloud

Teste simples: EC2 t3.medium em sa-east-1,
S3 com 100GB, RDS MySQL db.t3.small. Só produção.
```

Se retornar um link `https://calculator.aws/...`, a instalação está correta.

---

## Instalação manual do MCP (opcional)

Se preferir não usar npx ou precisar inspecionar o código do MCP:

```bash
git clone https://github.com/aws-samples/sample-aws-pricing-calculator-mcp.git
cd sample-aws-pricing-calculator-mcp
npm install
npm run build
cd ..

claude mcp add aws-pricing-calculator node "$HOME/sample-aws-pricing-calculator-mcp/dist/mcp-server.js"
```

Nesse caso, remova ou ignore o `.mcp.json` da raiz do projeto.

---

## Estrutura de arquivos

```
projeto/
├── .mcp.json                       ← configura o MCP automaticamente
├── README.md
├── .claude/
│   └── commands/
│       └── cotar_cloud.md          ← comando gerado no passo 2
└── plugin/
    ├── INSTALL.md                  ← este arquivo
    └── skills/
        └── cotar_cloud/
            ├── SKILL_merged_v1.md  ← versão sem arquiteturas Dataside
            └── SKILL_merged_v2.md  ← versão com arquiteturas Dataside (recomendada)
```

---

## Referências

- MCP Server AWS: https://github.com/aws-samples/sample-aws-pricing-calculator-mcp
- Calculadora oficial AWS: https://calculator.aws
- Calculadora Databricks: https://www.databricks.com/product/pricing
