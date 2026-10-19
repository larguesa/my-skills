A prioridade é corrigir a preservação de conteúdo literal e factual. Depois, alinhar o briefing, os modos de trabalho e a validação da entrega.

Revisão estática dos sete arquivos fornecidos, referentes ao commit `4433074e32085320c9cebc8ebace67833e321f92`. Não executei testes nem alterei arquivos. Os comportamentos de código abaixo são deduções da implementação; os testes são propostas de regressão.

**P1** indica risco direto de alterar conteúdo protegido ou ensinar transformações infiéis. **P2** indica falha de validação, contradição operacional ou lacuna editorial relevante.

**1. P1: a proteção permite editar código Markdown válido. Também há divergência entre os formatos de citação reconhecidos.**

Referências: [humanizar.py:74](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L74), especialmente linhas 79–80; [humanizar.py:442](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L442).

Reprodução mínima:

```python
plan_replacements("``vale destacar``", "vale destacar", "destaco")
```

O padrão de código reconhece os dois pares de crases como dois trechos vazios. O conteúdo entre eles fica desprotegido. A função produz uma edição; depois de aprovada, `apply_edits` aceita a alteração. O inventário continua contendo os mesmos dois delimitadores, portanto a conferência posterior também passa.

Outro caso: um bloco delimitado por quatro crases, contendo três crases no interior. O padrão encerra a proteção no delimitador interno, expondo parte do código à edição.

Há ainda uma divergência objetiva:

```python
check("‘prazo — curto’", [])
check('"prazo\n— curto"', [])
```

`protected_spans` reconhece essas citações, mas `CLOSED_LITERAL` não reconhece aspas simples curvas nem citações entre aspas que atravessem linhas. `check` bloqueia o travessão, mesmo quando o trecho é uma citação original que deve permanecer intacta.

**Correção:** compartilhar um analisador de trechos literais entre auditoria, edição, comparação e entrega. Reconhecer comprimento dos delimitadores Markdown, fechamento compatível, código indentado e convenções de citação suportadas. Manter uma diferença explícita: marcação aberta pode receber proteção conservadora na edição, mas precisa de tratamento próprio na validação da entrega.

**Regressão:** testar crases simples e múltiplas, cercas de três e quatro caracteres, delimitadores internos, aspas simples, duplas e curvas, citações multilinha e marcação aberta. Edições dentro de código ou citação original devem ser recusadas; a comparação deve preservar o conteúdo literal.

---

**2. P1: colocar prosa nova entre aspas permite passar travessão proibido.**

Referências: [SKILL.md:35](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/SKILL.md#L35); [humanizar.py:466](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L466).

Reprodução:

```python
check(
    '“Agora — espere.”',
    [],
    briefing='Escreva um diálogo novo.'
)
```

Resultado dedutível: `deliverable=True`, com `travessao_protegido` apenas como alerta.

O verificador confunde duas propriedades:

- O trecho está delimitado por aspas.
- O trecho reproduz conteúdo original protegido.

A primeira não demonstra a segunda. Isso viola diretamente a proibição de travessão em diálogos novos.

O problema inverso também existe: um nome literal fornecido, como `A—B`, pode precisar ser preservado fora de aspas. `check` não recebe termos protegidos nem distingue esse dado original de pontuação produzida pelo redator.

**Correção:** separar reconhecimento sintático e comprovação de origem. Para citações, conceder a exceção ao travessão quando o trecho corresponder ao original fornecido ou a um registro explícito de conteúdo protegido. Código deve continuar recebendo tratamento próprio. A origem pode vir de um arquivo original e de intervalos protegidos vinculados ao seu hash.

**Regressão:** usar o mesmo trecho em três situações:

1. Diálogo novo: bloquear travessão.
2. Citação literal presente na fonte: preservar e registrar a exceção.
3. Nome ou dado literal protegido fora de aspas: preservar.

O teste atual de [test_humanizar.py:911](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/results/test_humanizar.py#L911) verifica apenas delimitação, sem origem. Precisa dessa distinção.

---

**3. P1: muitos pares “Evite/Prefira” acrescentam fatos, restringem o alcance ou aumentam a certeza.**

Referências: [catalogo.json](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/catalogo.json#L1); renderização dos pares em [humanizar.py:418](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L418).

A diferença semântica entre os exemplos é verificável. Seu efeito sobre futuras gerações é uma hipótese editorial, ainda não demonstrada por esta revisão.

O aviso “Exemplos editoriais não são fatos reutilizáveis” reduz o risco de copiar dados para outro texto. Não resolve o ensinamento implícito de que uma frase vaga pode ser transformada em uma afirmação específica sem informação adicional.

| Regra e linha de `catalogo.json` | Mudança não sustentada pelo exemplo “Evite” |
|---|---|
| PTBR-02, linha 3 | Acrescenta duas modalidades de cadastro: site e balcão. |
| PTBR-03, linha 4 | Acrescenta o horário das 18h. |
| PTBR-05, linha 6 | Acrescenta que **todas** as configurações estão em uma única tela. |
| PTBR-06, linha 7 | Troca especialistas pela equipe de suporte; acrescenta redução pela metade e o mês de março. Também troca uma alegação causal por uma observação temporal. |
| PTBR-07, linha 8 | Acrescenta que o botão abre o formulário na mesma tela. |
| PTBR-08, linha 9 | Acrescenta atualização, falha de login e travamento do aplicativo. |
| PTBR-09, linha 10 | Acrescenta uma garantia operacional: continuar respondendo com um servidor indisponível. |
| PTBR-10, linha 11 | Acrescenta duração inicial e final do cadastro. |
| PTBR-11, linha 12 | Acrescenta duas equipes, uma planilha e sua finalidade. |
| PTBR-12, linha 13 | Estar no topo não garante aparecer sem rolagem. |
| PTBR-13, linha 14 | “Poderia” vira “pode”, alterando modalidade e possivelmente o enquadramento hipotético. |
| PTBR-15, linha 16 | Aparência ou apresentação vira identidade; acrescenta “de instalação”. |
| PTBR-16, linha 17 | Acrescenta versão em inglês e lançamento em março. |
| PTBR-17, linha 18 | Acrescenta a existência de um guia de instalação e uma orientação para consultá-lo. |
| PTBR-19, linha 20 | “Ajuda” vira uma aba com vídeos curtos. |
| PTBR-22, linha 23 | Acrescenta salvamento automático a cada campo. |
| PTBR-23, linha 24 | Acrescenta uma redução de três telas para uma. |
| PTBR-24, linha 25 | Acrescenta a obrigação de refazer o cadastro após perder o prazo. |
| PTBR-25, linha 26 | Uma pergunta vira uma explicação causal sobre CPF com pontos. |
| PTBR-27, linha 28 | Um preâmbulo vira uma afirmação sobre anexos PDF. |
| PTBR-29, linha 30 | Acrescenta pagamento por boleto e uma etapa de interface. |
| PTBR-32, linha 33 | “Endereçar” vira “corrigir”, elevando tratar de um problema a prometer sua resolução. |

Algumas correções mínimas já são possíveis:

| Regra | Forma preferida que evita o acréscimo identificado |
|---|---|
| PTBR-03 | “O prazo termina amanhã.” |
| PTBR-12 | “O botão mudou para o topo da página.” |
| PTBR-13 | “A falha poderia voltar.” |
| PTBR-19 | “O menu tem ajuda.” |
| PTBR-29 | “Para pagar, acesse o aplicativo.” |
| PTBR-32 | “A equipe vai tratar do problema na próxima versão.” |

Nos casos em que retirar a fórmula deixa pouco conteúdo, a solução é enriquecer **o material comum do exemplo**, não inventar informação apenas no “Prefira”. Por exemplo, PTBR-17 pode conter uma informação útil seguida de “Espero que isso ajude”; a versão preferida conserva essa informação e elimina somente o resíduo.

Os pares PTBR-01, 04, 14, 18, 20 e 28 preservam melhor o núcleo informativo. Ainda exigem contexto: retirar uma lista útil ou um enquadramento temporal relevante pode piorar o texto. PTBR-30 depende de estar estabelecido que a finalidade foi acrescentada sem apoio. PTBR-21 e 26 são descrições, não transformações textuais. PTBR-31 introduz uma chaleira, admissível como criação ficcional, mas inadequada como revisão de um relato real.

**Correção:** classificar exemplos como revisão fiel ou ilustração de criação. Para revisão, fornecer uma base factual comum quando necessária. Preservar atribuição, modalidade, alcance, condições e compromissos. Rever também `meaning_risk`: PTBR-29 e 32 estão classificados como risco baixo, embora seus exemplos atuais alterem informação relevante.

**Regressão:** criar casos revisados para as 32 regras, com invariantes semânticos explícitos. Conferir, por exemplo, que “poderia” não vira certeza maior e que tratar um problema não vira garantir correção.

O teste de PTBR-30 em [test_humanizar.py:1092](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/results/test_humanizar.py#L1092) é insuficiente: inclusão de conjuntos de palavras não prova fidelidade. “Ana venceu Bia” e “Bia venceu Ana” têm o mesmo conjunto; retirar “não” também satisfaz a inclusão.

---

**4. P1: o briefing em texto descarta as orientações e exceções que tornam o catálogo contextual.**

Referências: [humanizar.py:377](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L377), [humanizar.py:415](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L415); promessa documental em [README.md:23](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/README.md#L23).

`brief()` inclui `como` e `excecoes` em cada regra. `brief_text()` não imprime nenhum desses campos:

- Regras de foco: imprime exemplos e termos.
- Demais regras: imprime termos ou o exemplo evitado.

Portanto, texto e JSON não entregam o mesmo conteúdo editorial, contrariando o README.

Exemplo decisivo: PTBR-04 determina “nunca remover por ocorrência isolada”. Essa instrução desaparece. O leitor recebe um par que troca “Ademais” por “também” e uma lista de conectores a evitar.

Também desaparecem orientações como:

- Não apagar silenciosamente uma alegação cuja fonte precisa ser conferida.
- Preservar distinção entre aparência e realidade.
- Conservar incerteza.
- Manter listas por consulta e acessibilidade.
- Aceitar uma linha de apresentação que pertença ao próprio e-mail.

A ressalva genérica “salvo termo técnico, citação literal ou uso pedido” não substitui essas condições.

**Correção:** transmitir orientação e exceções relevantes nas duas representações, para todas as regras. Manter o catálogo inteiro. A hierarquia por gênero pode continuar, mas “foco” deve indicar prioridade de leitura, não exclusividade de aplicação.

**Regressão:** conferir que `como` e `excecoes` sobrevivem à renderização, inclusive em uma regra fora do foco. Acrescentar casos de uso legítimo: conector isolado, contraste técnico, síntese necessária e lista consultável.

Os limites atuais de caracteres precisam acomodar esse conteúdo. Não convém preservar um teto que obrigue a retirar justamente as condições de uso.

---

**5. P2: o detector de saída somente com comandos aceita comandos evidentes e bloqueia documentação curta válida.**

Referências: [humanizar.py:434](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L434), [humanizar.py:477](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L477).

Casos aceitos pelo código atual no contrato padrão de prosa:

```python
check("ls", [])
check("curl https://exemplo.test", [])
check('{"titulo": "Cadastro"}', [])
```

O primeiro não contém o espaço exigido pelo padrão. O segundo usa um executável ausente da lista. JSON comum não é identificado como incompatível com o artefato esperado.

Caso bloqueado:

```python
check("Execute:\n```sh\nls -la\n```", [])
```

É uma instrução técnica curta, mas sobra menos de oito palavras após remover o código. A extensão da explicação decide se a entrega parece válida. Acrescentar palavras dispensáveis pode fazê-la passar.

O mesmo problema afeta uma explicação curta de marcação de ferramentas. O teste em [test_humanizar.py:938](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/results/test_humanizar.py#L938) fixa como inválido um formato que pode ser exatamente o solicitado.

**Correção:** substituir o limiar de oito palavras por validação do formato esperado. Diferenciar prosa, código, JSON, plano e documento misto quando o pedido exigir. Detectar casos inequívocos de incompatibilidade, sem exigir enchimento para legitimar exemplos técnicos.

Manter `--artifact codigo` como escolha explícita vinculada ao pedido. Não usá-lo como escape para qualquer reprovação.

**Regressão:** comandos sem argumentos, executáveis diferentes, JSON isolado, plano entregue no lugar de texto, documentação curta com código e exemplos literais de ferramentas. Uma explicação válida não deve precisar crescer para passar.

---

**6. P2: o bloqueio de preâmbulos ignora uma exceção do próprio catálogo e deixa passar preâmbulos após uma saudação.**

Referências: [catalogo.json:28](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/catalogo.json#L28); [humanizar.py:484](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L484).

Falso positivo:

```text
Seguem os documentos:
- contrato
- recibo
```

A primeira linha pode pertencer legitimamente a um e-mail. O catálogo prevê essa exceção. `check` bloqueia sem considerar a função da linha.

Falso negativo:

```text
Claro!
Aqui está a notícia:
O cadastro foi aberto.
```

PTBR-27 encontra a segunda linha, mas o bloqueio exige que ela alcance o início da primeira linha não vazia. O preâmbulo vira apenas alerta.

**Correção:** analisar o segmento inicial de apresentação, não somente uma linha isolada. Distinguir anúncio do artefato ao solicitante de introdução de uma lista ou anexo dentro do artefato. Casos ambíguos precisam de contexto ou alerta, não de bloqueio automático baseado apenas em “segue”.

**Regressão:** preâmbulo precedido por cortesia, preâmbulo com formatação Markdown, e-mail com anexo e mensagem que apresenta uma lista real.

---

**7. P2: instruções de redação nova são aplicadas também à revisão e ao diagnóstico.**

Referências: [SKILL.md:19](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/SKILL.md#L19), [SKILL.md:74](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/SKILL.md#L74), [humanizar.py:357](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L357).

A definição de revisão manda alterar apenas o que melhora o texto. Entretanto, o fluxo exige reescrever frases copiadas do pedido, e o contrato de entrega pergunta se as frases são “suas”.

Em revisão, o texto do autor faz parte do pedido. Conservar uma frase boa é o comportamento correto.

Exemplo:

```text
Revise apenas a pontuação:
O cadastro termina em 20 de maio.
```

Não há motivo para mudar a frase ou completar um gênero. A instrução de originalidade sintática cria pressão para uma alteração desnecessária.

No diagnóstico, falta uma ramificação explícita que impeça o fluxo geral de conduzir à redação do gênero analisado.

**Correção:** separar o fluxo por modo:

- Redação: construir o artefato com formulação própria.
- Revisão: preservar passagens adequadas; respeitar o escopo da intervenção.
- Diagnóstico: apresentar trechos, motivos e prioridades, sem versão substituta.

O briefing pode receber `mode`, com padrão compatível com o uso atual. O contrato de entrega deve refletir esse modo.

Também é preciso resolver “sinalize a exceção”, em SKILL.md:44, diante de “sem bastidores”. A sinalização pode ficar no relatório interno de verificação; só deve entrar no artefato quando fizer parte do pedido.

**Regressão:** revisão sem alteração necessária, correção restrita à acentuação, revisão parcial e diagnóstico sem reescrita. Nenhum desses casos deve exigir frases diferentes apenas para se distanciarem do original.

---

**8. P2: a política factual diverge entre arquivos e não resolve pedidos explicativos com pouco material.**

Referências: [SKILL.md:50](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/SKILL.md#L50), [estilos.json:28](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L28), [README.md:9](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/README.md#L9).

A skill permite fatos fornecidos **ou verificados**. O briefing limita fatos e fontes ao pedido. Isso pode fazer o redator descartar informação legitimamente verificada durante a tarefa.

Há também uma lacuna no exemplo de uso:

```text
Redija uma explicação de cache para iniciantes.
```

O pedido não contém os fatos conceituais necessários. A documentação não distingue claramente:

- Fatos específicos sobre pessoas, organizações, acontecimentos e resultados.
- Conhecimento conceitual necessário para explicar um tema.
- Exemplos hipotéticos didáticos.
- Dados acrescentados por pesquisa autorizada.

A analogia é incentivada, mas a política factual não explicita como empregar exemplos hipotéticos em um texto informativo.

Outra distinção necessária: informação ausente do briefing não significa informação não divulgada pela fonte. A instrução “Diga a lacuna uma vez” pode estimular essa conversão.

**Correção:** unificar a política em SKILL.md e briefing. Definir as fontes admissíveis e o estatuto de exemplos hipotéticos. Não apresentar conhecimento presumido como pesquisa realizada.

Para lacunas: omitir detalhes dispensáveis; pedir esclarecimento quando a falta impede a tarefa; declarar “não divulgado” somente quando essa condição estiver sustentada. Isso preserva a redação independente, sem exigir que todo usuário forneça um tratado sobre o assunto.

**Regressão editorial:**

- Explicação conceitual sem texto-base: útil, sem estudo ou experiência inventados.
- Redação com fonte verificada adicional: preservação da atribuição.
- Notícia sem horário no briefing: não afirmar automaticamente que o horário não foi divulgado.
- Exemplo numérico hipotético: identificação como hipótese, sem atribuição a um caso real.

---

**9. P2: a comparação factual perde sinais e percentuais; a comparação de datas aceita coincidências dentro de palavras.**

Referências: [humanizar.py:440](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L440), [humanizar.py:493](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L493).

Casos sem alerta numérico:

```python
check("Saldo: 20 reais.", [], briefing="Saldo: -20 reais.")
check("Taxa: 20.", [], briefing="Taxa: 20%.")
```

`NUMBER` extrai apenas `20` nos dois lados. A comparação usa conjuntos, portanto também perde multiplicidade.

Caso de data:

```python
check(
    "A entrega será domingo.",
    [],
    briefing="Domingos revisou o aviso."
)
```

A busca normalizada encontra `domingo` dentro de `domingos`, suprimindo `data_inferida`.

O aviso de que `check` não prova fidelidade é correto. Ainda assim, sinais, percentuais e limites de palavra são verificações mecânicas que podem ser feitas com precisão maior.

**Correção:** compartilhar a identificação de literais numéricos com as proteções, preservando sinais e percentuais. Usar contagens quando pertinentes, mantendo os resultados como alertas contextuais. Comparar expressões temporais identificadas no briefing, não substrings arbitrárias.

**Regressão:** inversão de sinal, perda de percentual, repetição e omissão de valores, `Domingos` versus `domingo`, datas e horas. Continuar documentando que a presença dos mesmos números não demonstra sua associação correta a pessoas, produtos ou períodos.

---

**10. P2: normalização Unicode e abreviações permitem alterar conteúdo que deveria estar sob proteção de negação ou condição.**

Referências: [humanizar.py:81](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L81), [humanizar.py:89](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L89).

Reproduções:

```python
plan_replacements("na\u0303o aceito.", "aceito", "recuso")
plan_replacements("se o sr. pedir, aceite.", "aceite", "recuse")
```

No primeiro caso, “não” usa acentuação decomposta. O padrão literal não reconhece a negação.

No segundo, o ponto de `sr.` encerra a proteção antes da oração principal. A alteração posterior é aceita.

Não se trata de exigir equivalência semântica geral do editor. São lacunas na proteção expressamente implementada para essas construções.

**Correção:** reconhecer formas Unicode equivalentes sem normalizar silenciosamente o arquivo original. Uma representação normalizada para busca precisa manter correspondência com os offsets originais. Na delimitação de condições, tratar abreviações e trechos literais antes de considerar pontos como fim de frase.

**Regressão:** versões NFC e NFD das mesmas negações, nomes e termos; condições com abreviações; preservação dos offsets e dos bytes originais. Os testes de marcas combinantes hoje existentes cobrem limites da substituição, não essas proteções.

---

**11. P2: o catálogo deixa de detectar uma expressão que ele próprio lista e algumas flexões prometidas.**

Referências: [catalogo.json:33](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/catalogo.json#L33), [catalogo.json:12](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/catalogo.json#L12); contrato em [SKILL.md:38](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/SKILL.md#L38).

Exemplos:

```text
Precisamos endereçar um problema.
Otimizamos o fluxo.
Potencializamos os resultados.
```

PTBR-32 lista “endereçar um problema” em `avoid`, mas sua expressão regular não admite `um` ou `uma` nessa construção.

PTBR-11 não contempla `amos` para os verbos correspondentes. Os testes de flexão cobrem algumas formas, mas deixam essa lacuna.

**Correção:** ajustar os padrões aos termos declarados e manter uma matriz de flexões usuais. Não ampliar por radicais indiscriminados, pois isso aumentaria alertas sobre usos literais e técnicos.

**Regressão:** testar cada expressão literal de `avoid` que deva ser detectável, distinguindo-a de descrições e esquemas como “não é apenas X, mas Y”. Acrescentar pessoas e tempos verbais comuns, acompanhados de controles negativos.

---

Além desses defeitos, as **estruturas precisam de maior adaptação ao pedido**. A evidência é a presença de instruções categóricas nos planos. O efeito provável, ainda uma hipótese editorial, é produzir gêneros uniformes ou preencher lacunas desnecessariamente.

| Estrutura e referência | Limitação | Melhoria concreta e caso de regressão |
|---|---|---|
| Reportagem, [estilos.json:892](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L892) | O bloco obrigatório exige falas literais entre aspas. Uma reportagem documental pode não ter nenhuma fala disponível. | Exigir atribuição das informações; usar discurso direto somente quando houver citação literal. Testar reportagem baseada apenas em documentos. |
| Mensagem, [estilos.json:536](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L536) | Saudação pelo nome, proposta, ação esperada e assinatura são tratadas como convenções gerais. Nem toda mensagem precisa desses elementos. | Condicionar ao canal, à finalidade e aos dados disponíveis. Testar aviso informativo curto sem ação do destinatário e sem nomes fornecidos. |
| Post, [estilos.json:587](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L587) | O ofício descreve principalmente um relato profissional com números, resultados e aprendizado aplicável a outra equipe. | Diferenciar anúncio, opinião, relato e publicação literária. Testar post opinativo sem números nem experiência pessoal. |
| Roteiro, [estilos.json:638](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L638) | O ofício exige componentes visuais mesmo abrangendo “fala”; o bloco visual já é condicional, criando divergência interna. | Condicionar imagens, colunas e tempos ao formato. Testar discurso oral sem tela e roteiro ficcional sem chamada prática final. |
| Acadêmico, [estilos.json:1029](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L1029) | O plano pressupõe pesquisa empírica com método, participantes, intervenção e resultados numéricos. | Selecionar funções por subtipo: resumo, introdução, discussão, revisão teórica ou ensaio. Testar introdução de artigo teórico, sem inventar método ou participantes. |
| Conto, [estilos.json:1086](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L1086) | Restringe o conhecimento do narrador e proíbe nomear sentimentos como regra geral. | Tratar essas opções como recursos, subordinados ao narrador e à voz pedidos. Testar narrador onisciente e prosa introspectiva. |
| Crônica, [estilos.json:1138](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L1138) | Primeira pessoa, humor, ironia e leveza ficam próximos de requisitos. | Admitir terceira pessoa, sobriedade e relato real. Testar crônica factual triste, sem humor, fala inventada ou mudança de pessoa narrativa. |
| Proposta, [estilos.json:935](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L935) | “Defina” exclusões e responsável pelo aceite pode induzir criação de condições contratuais ausentes. | Apresentar condições autorizadas; esclarecer lacunas indispensáveis. Testar orçamento sem responsável pelo aceite ou serviço opcional informado. |

A regra geral de precedência do pedido ajuda, mas não elimina o conflito entre ordens locais. A condicionalidade deve aparecer perto da instrução específica.

Há também uma mistura entre **voz e estrutura**:

- `argumentativo-sobrio/post` seleciona `argumento`, cujo nome é “Artigo de opinião”, porque essa é a primeira estrutura compatível. O plano específico de post fica preterido nesse par.
- `tecnico-preciso/email` é recusado, embora precisão técnica e formato de e-mail sejam compatíveis editorialmente.

Referências: [estilos.json:116](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/references/estilos.json#L116), [humanizar.py:233](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L233), [humanizar.py:263](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/scripts/humanizar.py#L263).

Proposta: preservar os 12 perfis e separar melhor sua orientação de voz da escolha de estrutura. Permitir uma seleção explícita compatível com o pedido, sem depender exclusivamente da ordem de `structure_ids`. Regressões: post argumentativo curto e e-mail técnico, mantendo gênero e registro.

A formulação “Vícios mais comuns neste gênero” também excede o que os dados fornecidos sustentam. Os focos são seleções editoriais, sem frequência demonstrada por gênero. “Pontos de atenção do gênero” descreve melhor sua função.

Quanto aos **testes sugeridos**, os casos de cada achado devem ser acompanhados destes ajustes na estratégia da suíte:

1. **Separar detecção lexical de defeito editorial.**  
   O teste de [test_humanizar.py:1036](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/results/test_humanizar.py#L1036) exige ausência total de ocorrências do catálogo nos exemplos preferidos. Isso impede representar adequadamente uma exceção legítima que continue correspondendo ao padrão. Usar expectativas explícitas de ocorrência e de tratamento contextual.

2. **Substituir critérios de tamanho por critérios de conteúdo necessário.**  
   Os tetos de [test_humanizar.py:827](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/results/test_humanizar.py#L827) e a comparação com 0.6.0 em [test_humanizar.py:1267](https://github.com/larguesa/my-skills/blob/4433074e32085320c9cebc8ebace67833e321f92/skills/humanizador-pt-br/results/test_humanizar.py#L1267) podem impedir a restituição das exceções. Registrar tamanho como diagnóstico; a aceitação deve exigir catálogo efetivo, condições de uso, fidelidade e contrato de entrega.

3. **Testar contratos entre componentes.**  
   Uma citação original aceita como protegida na edição deve receber tratamento compatível na entrega. Uma exceção disponível no JSON deve sobreviver no briefing em texto. Os modos de revisão e diagnóstico devem produzir contratos diferentes do modo de redação.

4. **Adicionar casos editoriais sintéticos, fora dos 24 prompts aprovados.**  
   Avaliar fidelidade por atribuição, modalidade, alcance, condições, unidades, compromissos e ausência de fatos inventados. Avaliar utilidade pelo leitor e pelo gênero. Não usar notas históricas como objetivo de ajuste.

5. **Manter os controles já úteis.**  
   Hash da entrada, aprovação explícita, offsets Unicode, recusa de sobreposição, destino novo, preservação de CRLF e aleatoriedade local são boas bases. O catálogo instalado não possuir substituições automáticas também é coerente com seu risco semântico; não é necessário introduzi-las para torná-lo efetivo.

6. **Preservar os requisitos como testes permanentes.**  
   Doze perfis, norma culta e acentuação, prosa nova sem travessão, catálogo integral e contextual, redação independente ou revisão, diagnóstico sem reescrita e iteração final até não haver melhoria concreta. Manter os 24 prompts e os resultados históricos intactos.

Ordem recomendada de implementação: proteção literal e origem das citações; pares factuais; restituição das orientações no briefing; validação da entrega; distinção dos modos; adaptação dos gêneros. Cada correção deve entrar com sua reprodução mínima e sua regressão, sem reescrever evidências históricas para acomodar o comportamento novo.