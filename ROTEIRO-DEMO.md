# Roteiro de demo — `/cotar_cloud`

Cenário ensaiado, com os números conferidos contra a Retail Prices API. Serve para
apresentar sem surpresa: você sabe o que vai sair antes de rodar.

Ensaiado em 15/09/2026. **Reconfira antes de apresentar** com
`python tools/valida_precos.py` — se algum preço mudou, os números abaixo mudam
junto.

---

## Antes de começar

```bash
# 1. a Skill instalada tem que ser a do repositório
cp plugin/skills/cotar_cloud/SKILL_unified.md .claude/commands/cotar_cloud.md

# 2. os preços do roteiro ainda valem?
python tools/valida_precos.py
```

Se o validador acusar falha, **não apresente com estes números**. Leia a falha,
confirme na API e atualize o roteiro.

Abra uma sessão limpa (`claude`, sem `--continue`). Se a sessão tiver contexto
anterior, o agente pode parecer mais esperto do que é.

---

## O cenário

Fabric puro, de propósito. Três razões:

1. É o que a Dataside vende hoje.
2. Mostra o diferencial mais visível — os dois modelos de compra, com 40,6% de
   diferença.
3. **Não envolve Virtual Machines.** Uma consulta de VM leva ~12s contra ~1s do
   Fabric, e é o único serviço que trava a demo de forma perceptível.

### Abertura — copie e cole

```
/cotar_cloud Cliente de varejo quer uma plataforma de dados no Fabric. Uns 12 TB no lake, três squads de dados, time de BI de 40 pessoas. Rede fechada, tudo com Private Endpoint.
```

### As respostas

O agente pergunta uma ou duas por vez, e a ordem pode variar. Responda assim:

| Ele pergunta | Você responde |
| --- | --- |
| região | `Brazil South, varejo brasileiro, LGPD` |
| F SKU | `F64, não quero apertar` |
| volume e camada do OneLake | `12 TB nas três camadas, tudo Hot no primeiro ano` |
| HML e Dev pausados? | `Sim, 7h às 20h em dia útil, tem automação` |
| ExpressRoute | `Circuito já existe. Cota só o gateway, um ErGw1AZ no hub` |
| VM de runtime | `Roda na infra VMware deles, não entra` |
| volume de log | `60 GB/mês, retenção padrão` |
| Key Vault | `Normal, sem HSM. 500 mil operações/mês` |
| egress | `800 GB/mês` |
| ativos do Purview | `Não temos, o discovery é na primeira sprint` |
| camada de IA | `Fase 2, não dimensiona` |
| autores de Power BI | `12 autores, os outros 40 só consomem` |
| confirma? | `Gera` |

Se ele perguntar algo fora desta lista, responda o que quiser — o roteiro não
quebra. Só o F SKU, o volume e as 200h importam para os números baterem.

---

## O que tem que sair

Se algum destes números vier diferente, **pare e investigue** antes de continuar
na frente do cliente.

### Produção

| Linha | Conta | Valor |
| --- | --- | ---: |
| Fabric F64 sob demanda | 64 × 0,28 × 730h | 13.081,60 |
| Fabric F64 com reserva | 64 × 1.458,00 ÷ 12 | 7.776,00 |
| OneLake Hot | 12.288 GB × 0,0407 | 500,12 |
| ExpressRoute ErGw1AZ | 0,361 × 730h | 263,53 |
| Key Vault Operations | 500.000 ÷ 10K × 0,03 | 1,50 |
| Log Analytics ingestão | (60 − 5) GB × 4,60 | 253,00 |
| Egress Internet | (800 − 100) GB × 0,12 | 84,00 |

### Totais

| | Sob demanda | Com reserva |
| --- | ---: | ---: |
| Produção | 14.183,75 | 8.878,15 |
| Homologação | 1.123,09 | 1.123,09 |
| Desenvolvimento | 278,76 | 278,76 |
| **Total** | **15.585,60** | **10.280,00** |

Diferença: **5.305,60/mês**. Compromisso anual da reserva: **93.312,00**.

### Fora dos totais, sem valor

Private Endpoint, Purview, Azure OpenAI, Power BI Pro, circuito ExpressRoute,
Self-Hosted IR.

---

## Onde parar e mostrar

A demo tem quatro momentos que valem pausa. O resto é conversa.

**1. Ele reconhece o padrão da casa.** Na Fase 3 ele diz *"sugiro a arquitetura
padrão Dataside Microsoft Fabric End-to-End Platform"*. Não é conhecimento geral
de Azure — é o catálogo da Dataside. Testado: seis cenários, seis acertos,
incluindo um que corretamente **não** casou com padrão nenhum.

**2. Ele mostra os dois modelos de compra.** 13.081,60 contra 7.776,00 na mesma
tela, com a diferença calculada. Não escolhe por você. Esse é o número que o
cliente leva para a reunião de decisão.

**3. Ele recusa o que não sabe.** Private Endpoint, Purview e Power BI Pro saem
**sem valor**, com o motivo escrito. Esse é o momento mais importante da demo e o
menos óbvio: a ferramenta está dizendo o que ela *não* sabe, em vez de preencher
com número plausível.

Se der abertura, é aqui que entra a frase: *uma linha sem valor e declarada é
honesta; uma linha com número errado vira proposta.*

**4. As premissas.** Camada e redundância, horas de pausa, proporção de HML e Dev,
data da consulta, o que ficou de fora e por quê. É o que transforma a estimativa
em algo defensável três meses depois.

---

## Tempo

Medido no ensaio: **cerca de 5 minutos** do comando à estimativa final, com um
arquiteto respondendo sem hesitar. Com cliente na sala, conte mais.

| Etapa | Tempo |
| --- | --- |
| cada consulta ao MCP | 5 a 9s |
| consulta de Purview | ~20s (a mais lenta) |
| consulta de Virtual Machines | ~12s — **evitada neste cenário** |
| total de consultas do roteiro | 10 |

A API em si é rápida: Fabric responde em 1,2s medido direto. O que soma é o
agente entre as chamadas.

**Os três minutos de silêncio de 01/09 não eram a API** — eram o MCP antigo
dirigindo o navegador com Playwright, que não existe mais. Não use aquele episódio
como argumento sobre a solução atual.

---

## Se algo der errado

**A API não responde.** O agente vai dizer. Não deixe ele preencher de memória — a
Skill proíbe, mas confirme em voz alta que não há número inventado. Tenha esta
página aberta: os valores esperados estão acima, e você pode seguir a conversa
mostrando o raciocínio sem o número ao vivo.

**Um número saiu diferente do roteiro.** Duas causas possíveis, e vale dizer qual:
a Azure mudou o preço (roda `tools/valida_precos.py` e mostra), ou o agente
resolveu errado. A segunda é bug e vale anotar na hora.

**Perguntaram por um serviço fora do catálogo.** Ele vai sair sem valor. Isso é o
comportamento correto, e é a resposta: *a ferramenta cobre o que a Dataside vende,
e diz claramente onde não cobre.* A allowlist cobre 17 `serviceName` verificados.

**Perguntaram por outra região.** A tabela de preços da Skill é toda de
`brazilsouth`. Em `eastus` o Fabric custa 56% menos, e não há fator de correção —
alguns meters variam, outros não. O agente é instruído a reconfirmar meter por
meter fora de `brazilsouth`. Vale demonstrar isso se a pergunta vier, mas não
puxe o assunto: é uma limitação, não um recurso.

**Perguntaram do link da calculadora Azure.** Saiu do critério de aceite em 10/09.
Não há API pública para gerar o link programaticamente. O arquiteto de soluções
avaliou que ele serve principalmente para pedido de incentivo à Microsoft, e que
cerca de 80% dos clientes não abre.

---

## O que não prometer

- **Não prometa cobertura completa da Retail Prices API.** A allowlist cobre 17
  `serviceName` verificados. Fora deles a estimativa sai sem valor, de propósito.
- **Não prometa preço com desconto negociado.** Tudo é retail público.
- **Não prometa o link da calculadora.**
- **Não prometa o lado AWS.** Está congelado, e os números de DBU do Databricks on
  AWS estão marcados como não verificados no próprio arquivo.
