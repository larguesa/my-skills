# Humanizador PT-BR

Skill de redação e revisão em português brasileiro. Ajuda a escrever com clareza, ritmo e voz coerente a partir de um briefing, ou a revisar um texto existente sem perder precisão.

## Uso

Copie a pasta completa para o diretório de skills do agente e carregue [SKILL.md](SKILL.md). Não é necessário fornecer um rascunho para redigir.

Exemplos:

> Escreva uma explicação de cache para quem está começando a programar. Use humanizador-pt-br.

> Redija um e-mail para negociar o prazo com a cliente usando estes dados: [...]. Use humanizador-pt-br.

> Revise este artigo com humanizador-pt-br: [...].

> Avalie a clareza deste texto, sem reescrevê-lo: [...].

As regras de fidelidade factual estão na própria skill: usar o contexto disponível, não inventar fontes ou experiências, preservar citações e distinguir fatos, hipóteses e opiniões. Ficção permite invenção compatível com o pedido, sem transformar a cena em um fato real.

## Recursos

- [SKILL.md](SKILL.md): procedimento para redigir, revisar ou diagnosticar.
- [Catálogo editorial](references/catalogo.json): fórmulas a evitar ou inspecionar, com exceções contextuais.
- [Estilos](references/estilos.json): orientação de registro e ritmo, sem personas sorteadas.
- [Fontes e limites](references/fontes.md): origem e limites das heurísticas, não referências factuais para qualquer texto.
- [Script local](scripts/humanizar.py): inspeção e aplicação conservadora de edições aprovadas, sem chamadas externas.
- [results/](results/README.md): preparação dos novos testes e, após autorização, seus resultados.

## Script opcional

A skill não exige Python para escrever. O script usa somente a biblioteca padrão e pode inspecionar tanto um novo rascunho quanto um texto recebido. Ele não é um gerador de textos, verificador de fontes ou detector de IA.

Na pasta da skill:

```text
python3 scripts/humanizar.py audit rascunho.txt
python3 scripts/humanizar.py suggest rascunho.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py verify rascunho.txt revisado.txt
python3 scripts/humanizar.py apply rascunho.txt --plan plano.json --output revisado.txt
```

`audit` não altera o texto. `suggest` retorna recomendações, uma ênfase do perfil e eventuais edições com `approved: false`; com o catálogo editorial atual, é normal retornar `edits: []`. Uma orientação editorial não vira substituição literal automaticamente.

`apply` exige o SHA256 da entrada, índices de caracteres Unicode (fim exclusivo), trecho exato e aprovação por edição. O destino deve ser novo. Formato de plano para a entrada literal `vale destacar: ação.`, sujeito à revisão contextual:

```json
{"input_sha256":"HASH_DA_ENTRADA_OBTIDO_NA_AUDITORIA","edits":[{"start":0,"end":13,"original":"vale destacar","replacement":"destaco","approved":true}]}
```

`--protect "termo"` acrescenta proteção. Números, possíveis nomes, código, citações e condições têm bloqueios heurísticos conservadores, não reconhecimento completo de entidades. `verify` compara versões, mas não comprova equivalência semântica nem veracidade. Toda alteração relevante precisa de leitura contextual.

## Novos testes

A pasta `tests/` foi retirada desta versão. Os materiais anteriores permanecem no histórico do Git, no [commit anterior à revisão](https://github.com/larguesa/my-skills/tree/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests).

Os [prompts propostos](results/PROMPTS.md) aguardam aprovação. Não houve nova geração de textos nem nova avaliação por modelos nesta revisão.

A comparação proposta usa o mesmo pedido em duas chamadas independentes do mesmo modelo, uma sem a skill e outra com a skill. Nenhuma resposta serve de entrada à outra. O protocolo completo e a execução serão definidos após aprovação.

Não há resultado novo, ganho demonstrado ou promessa de proteção contra detectores. O objetivo é avaliar a qualidade da escrita, não provar autoria.
