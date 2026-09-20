# Instalação do plugin `dais-cloud-calculator` (/cotar_cloud)

## Instalação (Claude Code CLI, terminal)

**1. Adicione o marketplace deste repositório:**

```
/plugin marketplace add AndreSilvaDataside/dais-cloud-calculator
```

(ou, fora de uma sessão do Claude Code: `claude plugin marketplace add AndreSilvaDataside/dais-cloud-calculator`)

**2. Instale o plugin:**

```
/plugin install dais-cloud-calculator@dais-cloud-calculator
```

Ou use a UI interativa com `/plugin` (abas Discover / Install / Marketplaces).

**3. Teste:**

```
/cotar_cloud

Quero cotar um lakehouse com Databricks para um cliente de varejo. Usa AWS.
```

Verifique se os MCP servers subiram com `/mcp` — deve aparecer `aws-pricing-calculator` e
`azure-pricing-mcp` como *Connected*.

## Instalação (extensão Claude Code no VS Code)

A extensão do VS Code usa os mesmos comandos por baixo dos panos, mas o painel de plugins tem
outro nome de comando (`/plugins`, no plural) e é uma UI nativa em vez de texto:

**1. No chat da extensão, abra o gerenciador de plugins:**

```
/plugins
```

**2. Na aba "Marketplaces", adicione a fonte:**

- Repositório já publicado no GitHub: `AndreSilvaDataside/dais-cloud-calculator`
- Ou, para testar localmente antes de dar push: o caminho da pasta do projeto no seu Mac
  (ex.: `/Users/ana/Vinicius/Dataside/dais-calculator-project`)

**3. Na aba "Plugins", instale `dais-cloud-calculator` e habilite-o.**

**4. Teste com `/cotar_cloud` no chat e confira `/mcp`** — mesmo comando de status usado no
terminal, mostra os dois servers como *Connected*.

> Plugins e marketplaces configurados na extensão também ficam disponíveis no CLI, e vice-versa
> (compartilham o mesmo `~/.claude/settings.json`). `/doctor` e `/reload-plugins` são específicos
> do CLI de terminal — se você editar `plugin.json` com a extensão aberta, é mais seguro reiniciar
> o painel de chat do que esperar um reload automático.

## Instalação (Claude Code no app Desktop do Claude — aba "Code")

O app Desktop do Claude tem três abas: **Chat**, **Cowork** e **Code**. A aba **Code** roda o
mesmo motor do Claude Code (CLI/VS Code) e lê a mesma configuração
(`~/.claude.json`, `~/.claude/settings.json`) — então, se você já instalou o plugin pelo terminal,
ele **provavelmente já aparece instalado na aba Code**, sem precisar repetir a instalação.

> Atenção: isso vale só para a aba **Code** do Desktop. A aba **Chat** (conversa comum do
> claude.ai) não roda o sistema de plugins do Claude Code — marketplaces, skills e os MCP
> servers deste plugin não existem lá.

**1. Abra o app Desktop e clique na aba "Code".**

**2. Verifique se o plugin já está instalado:**

- Clique no **+** ao lado da caixa de prompt → **Plugins** → confira se `dais-cloud-calculator`
  aparece na lista.
- Clique no **+** → **Slash commands** → confira se `cotar_cloud` aparece.

**3. Se não aparecer, instale por ali mesmo:**

- **+** → **Plugins** → aba **Marketplaces** → adicione a fonte: o repositório do GitHub
  (`AndreSilvaDataside/dais-cloud-calculator`, se já publicado) ou o caminho local do projeto no
  Mac (ex.: `/Users/ana/Vinicius/Dataside/dais-calculator-project`) para testar antes do push.
- **+** → **Plugins** → aba **Plugins** → instale e habilite `dais-cloud-calculator`.

**4. Teste:**

```
/cotar_cloud

Quero cotar um lakehouse com Databricks para um cliente de varejo. Usa AWS.
```

Não existe comando `/mcp` nessa interface gráfica — para conferir se os MCP servers subiram,
olhe o painel de detalhes do plugin (lista o que "será instalado"/já instalado) ou apenas rode o
`/cotar_cloud` de teste acima e veja se ele consegue consultar preços.

## O que acontece na instalação

- Ao instalar a partir do GitHub, o Claude Code clona/baixa este repositório uma única vez para a
  pasta local de plugins (cache). Ao instalar a partir de um caminho local, o plugin roda direto
  da pasta do projeto (sem cópia), então mudanças no `SKILL.md` aparecem na próxima chamada, e
  mudanças no `plugin.json` só depois de `/reload-plugins` (CLI) ou reiniciar o chat (VS Code).
- O skill (`skills/cotar_cloud/SKILL.md`) e os dois MCP servers declarados em
  `.claude-plugin/plugin.json` (`aws-pricing-calculator` via `npx`, `azure-pricing-mcp` via `uvx`)
  são registrados automaticamente — não é preciso configurar nada manualmente.
- **Não há busca remota a cada comando**: o plugin roda a partir da cópia local instalada.
  Para pegar atualizações do repositório (instalação via GitHub), rode
  `/plugin marketplace update dais-cloud-calculator` (ou reinstale o plugin) depois de um novo
  release.

## Pré-requisitos

- Claude Code (CLI, extensão VS Code, ou aba "Code" do app Desktop do Claude)
- Node.js 18+ (para o MCP da AWS via `npx`)
- Python 3.10+ com [`uv`](https://docs.astral.sh/uv/getting-started/installation/) instalado
  (para o MCP da Azure via `uvx`): `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Referências

- Repositório: https://github.com/AndreSilvaDataside/dais-cloud-calculator
- MCP AWS Pricing Calculator: https://github.com/aws-samples/sample-aws-pricing-calculator-mcp
- MCP Azure Pricing: https://github.com/msftnadavbh/AzurePricingMCP
- Calculadora oficial AWS: https://calculator.aws
- Calculadora oficial Azure: https://calculator.microsoft.com
- Azure Retail Prices API: https://prices.azure.com/api/retail/prices
- Calculadora Databricks: https://www.databricks.com/product/pricing
