# tools — verificação de preço Azure

Duas ferramentas de apoio à Skill `cotar_cloud`. Nenhuma das duas é executada pela
Skill: a Skill usa o MCP em tempo de conversa. Estas servem para **conferir** o que
a Skill afirma.

Só stdlib, sem dependência externa. Python 3.10+.

| Arquivo | O que faz |
| --- | --- |
| `sonda_catalogo.py` | consulta a Azure Retail Prices API: descobre, varre e sonda |
| `valida_precos.py` | confere cada preço afirmado na Skill contra a API |

---

## Por que existem

Toda tabela de preço dentro de `SKILL_unified.md` é uma afirmação sobre a Retail
Prices API. Sem ferramenta, quem revisa um PR que mexe em número tem que acreditar
em quem escreveu. Com elas, reconfere em um comando.

Foi assim que três números deste projeto foram corrigidos: os meters que colidem em
0,0407 são 6 e não 4, a divergência de `meterName` atinge 8% das linhas e não 13%, e
a quebra dos zeros é 153/325 e não 150/328.

---

## valida_precos.py

Confere os preços de meter, as faixas escalonadas, a aritmética da tabela de F SKU,
as sete armadilhas e a consistência interna da Skill.

```bash
# ao vivo, só os serviços em escopo — ~50s, 87 conferências
python tools/valida_precos.py

# sobre um snapshot — instantâneo, e habilita as contagens da região inteira
python tools/valida_precos.py --snapshot brazilsouth-2026-09-11.json

# mostra também o que passou
python tools/valida_precos.py --snapshot arquivo.json --verbose
```

Sai com código 0 se tudo passou, 1 se houve falha, 2 se não conseguiu carregar dado.

**Rode antes de:** apresentar para cliente ou para o Oscar; aprovar PR que mexa em
tabela de preço; colocar número em slide.

### Falha não é necessariamente bug

Se a Azure mudou um preço, a conferência falha — e está certa em falhar. O aviso é
de que uma tabela da Skill envelheceu.

O caminho é: ler a falha, confirmar na API com `sonda_catalogo.py probe`, corrigir a
**Skill**, e só então ajustar o valor esperado em `valida_precos.py`. Ajustar só o
número esperado faz a ferramenta parar de servir para qualquer coisa.

Por isso ela **não serve como teste de CI que tem que passar sempre**. É conferência
deliberada, não gate automático.

### Modo ao vivo e modo snapshot

O modo ao vivo busca só os serviços em escopo (`SERVICOS` no topo do arquivo). Isso
cobre todos os preços que a Skill afirma, mas não as contagens sobre a região
inteira — quantas combinações a chave de cinco campos desambigua, quantos zeros são
faixa gratuita, quantas VMs uma busca por "F64" devolve. Essas precisam de snapshot.

---

## sonda_catalogo.py

```bash
# varre a região inteira e salva o snapshot
python tools/sonda_catalogo.py sweep --region brazilsouth --max-pages 400 \
    --json brazilsouth-$(date +%F).json

# quais serviceName existem numa serviceFamily
python tools/sonda_catalogo.py discover --family Data --region brazilsouth

# um serviço tem meter? quais? qual unidade?
python tools/sonda_catalogo.py probe --service "Microsoft Fabric" --price-type Reservation
python tools/sonda_catalogo.py probe --service "Private Link" --region any

# procura um termo no snapshot, imune a hífen e caixa
python tools/sonda_catalogo.py grep --file brazilsouth-2026-09-11.json \
    --term "onelake" --term "data stored"
```

Dois detalhes que economizam tempo:

- `--region any` omite o filtro de região. Necessário para confirmar que um serviço
  realmente não tem meter, em vez de não ter naquela região.
- `--price-type all` traz `Consumption` e `Reservation` juntos. A reserva do Fabric
  **não aparece** no padrão (`Consumption`) — foi o que escondeu 1458,00 por um
  tempo.

---

## O snapshot não está versionado

Um sweep de `brazilsouth` dá ~7,5 MB (~0,9 MB comprimido no git). O `.gitignore`
bloqueia o padrão `brazilsouth*.json` de propósito, por dois motivos:

1. Um snapshot sem data no nome envelhece em silêncio — exatamente o defeito que a
   seção de premissas da Skill tenta fechar.
2. Usar snapshot com data declarada como fonte de preço na demo, em vez de bater na
   API ao vivo, ainda é **proposta ao time**, não decisão tomada. Commitar o arquivo
   embutiria essa decisão sem ela ter sido discutida.

Se o time aprovar a proposta, o snapshot entra com a data no nome
(`brazilsouth-AAAA-MM-DD.json`), a regra do `.gitignore` é afrouxada para permitir
esse formato, e a premissa da Skill passa a apontar para o arquivo específico.

Contexto da proposta: na apresentação de 01/09 houve cerca de três minutos de
silêncio com o agente esperando a API.

Para gerar o seu:

```bash
python tools/sonda_catalogo.py sweep --region brazilsouth --max-pages 400 \
    --json brazilsouth-$(date +%F).json
```
