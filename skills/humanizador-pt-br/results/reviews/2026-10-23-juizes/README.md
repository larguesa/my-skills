# Justificativas dos juízes: plano do Opus e crítica de Sofia

## Resultado

O Claude Code analisou a amostra com **Opus 5.5, esforço máximo**. Foram disponibilizadas e lidas as **304 justificativas textuais**, 152 do Astra e 152 do Opus, referentes aos dois textos de cada um dos 76 pares julgados. Jev fornece notas e preferência, mas não justificativas textuais.

**Parecer de Sofia:** a direção é boa, mas o plano precisa das correções abaixo antes de virar mudança da skill. O problema não é apenas retirar marcas de IA: é fazer isso sem apagar explicações, alterar papéis ou transformar o texto em um modelo rígido de concisão.

[Plano completo do Claude Code, preservado como recebido](PLANO-OPUS.md). As observações abaixo corrigem pontos desse documento, sem reescrevê-lo retroativamente.

## O plano proposto pelo Opus

1. **Usar exemplos como orientação, não como molde.** A extensão, a abertura e os papéis das pessoas devem vir do pedido, não ser copiados do exemplo do gênero.
2. **Conferir o atendimento completo ao pedido antes de cortar.** Se o pedido manda explicar e calcular, a resposta precisa fazer ambos.
3. **Retirar bastidores da redação final.** Evitar referências à tarefa, como “o material fornecido”, e rótulos como “Linha fina:”, quando não pertencem ao artefato solicitado.
4. **Revisar contrastes e encerramentos formulaicos.** Evitar simetria mecânica entre parágrafos e frases de efeito que apenas repetem a tese.
5. **Preservar a atribuição das lacunas.** Uma pergunta dos moradores não prova que o documento deixou de tratar do assunto.

O Opus também propôs explicações estruturadas para os próximos julgamentos, com evidência textual e distinção entre humanização, fatos e atendimento ao pedido.

## Minha crítica

### 1. Há evidências concretas para melhorar, mas as justificativas atuais não explicam toda a nota de humanização

Os comentários históricos misturam qualidade geral, fidelidade e adequação; frequentemente não dizem por que o juiz atribuiu determinada impressão de IA. São material útil de diagnóstico, não uma taxonomia completa das causas da nota.

Exemplos conferidos nos textos:

- **Reportagem, rota 1, candidata:** “o material fornecido” aparece dentro da reportagem. Astra e Opus apontaram o bastidor inadequado ao gênero.
- **Química, rotas 9 e 10, candidata:** a resposta calcula corretamente Q_c, mas não explica o caráter dinâmico do equilíbrio, embora o pedido solicite uma explicação para alunos do ensino médio.
- **Reportagem, rota 14, candidata:** “Linha fina:” aparece como rótulo de produção; o encerramento também atribui ao boletim uma omissão não estabelecida no briefing.

Esses exemplos justificam ações específicas. Não justificam proibir títulos, listas, formalidade ou textos curtos em qualquer gênero.

### 2. As causas propostas são hipóteses, não efeitos demonstrados

A hipótese de que o exemplo curto induziu cortes é plausível. Nos seis pares de textos que o Opus comparou diretamente, a candidata é mais curta, conferido pela contagem de palavras. Entretanto, várias instruções mudaram juntas. Não sabemos se o efeito veio do exemplo, da orientação de entrega ou de outro componente.

A adequação agregada caiu apenas **0,24 ponto**, de 83,64 para 83,40, com divergência entre juízes. Isso não sustenta, sozinho, uma conclusão ampla de perda de adequação. A preferência desfavorável é um sinal distinto que merece investigação por caso.

**Correção proposta:** testar mudanças pequenas e identificáveis, começando pelo uso dos exemplos e pela cobertura do pedido, sem aplicar os cinco blocos de uma vez.

### 3. Duas recomendações criariam novas fórmulas artificiais

Não adotaria literalmente:

- **“Cada número entra uma vez.”** Um resultado pode precisar aparecer na tabela e na conclusão. Cortar repetição sem função é diferente de proibir retomadas úteis.
- **Retirar a pergunta do encerramento do ensaio.** A pergunta pode ser legítima. O critério deve ser se acrescenta uma questão concreta ou apenas produz um efeito previsível.

Também restringiria o alerta de bastidores à prosa em que ele destoa. “Material fornecido” pode ser apropriado em um parecer sobre documentação recebida, por exemplo. O alerta deve pedir revisão contextual, não substituição automática.

### 4. Algumas críticas dos juízes também precisam de crítica

No relatório de física, o Opus cobra uma incerteza associada ao resultado final. O pedido exige calcular a média e discutir as conclusões, mas não determina esse formato nem uma regra para a incerteza da média. Essa cobrança não vira automaticamente requisito obrigatório.

A abertura de quatro propostas comerciais da candidata permite leitura ambígua sobre o papel do Estúdio Boreal. Isso merece uma conferência de papéis, mas não prova quatro inversões factuais: na rota 5, o restante do texto identifica o Estúdio como responsável pela homologação, e o próprio pedido admite ambiguidade sintática.

Portanto, conferir o texto e o pedido vem antes de incorporar uma recomendação do juiz.

### 5. Há um erro factual no resumo do Opus sobre os gêneros

O plano afirma que apenas química teve preferência majoritária pela 0.8.1 nos três juízes. **O ensaio também teve.** A recontagem dos dados preservados produz:

| Pedido | Votos 0.8.1 | Votos 0.9.0 | Empates |
|---|---:|---:|---:|
| Reportagem | 22 | 24 | 2 |
| Física | 28 | 14 | 3 |
| Química | 34 | 13 | 1 |
| Proposta comercial | 30 | 15 | 3 |
| Ensaio | 28 | 11 | 0 |
| **Total** | **142** | **77** | **9** |

Os três juízes atribuíram aumento de H à candidata. Isso não elimina a preferência global pela referência, porque são perguntas diferentes. Jev responde por 65 votos da referência, mas não informa por quê; não se deve inventar essa explicação nem excluí-lo por discordar.

### 6. Eu simplificaria a mudança de julgamento

O Opus propõe três listas novas no JSON. Para atender ao pedido atual, basta estruturar a justificativa existente. Isso mantém compatibilidade e evita ampliar o contrato antes de demonstrar necessidade. A atualização das justificativas já foi solicitada por Ricardo, não é uma autorização ainda pendente como a lista final do Opus sugere; mudar o schema ou a rota do Jev seria outra decisão.

Também não adotaria a proibição absoluta de um problema factual aparecer na análise de humanização: uma mesma passagem pode afetar duas dimensões, desde que cada efeito seja explicado separadamente. O erro factual, sozinho, não prova artificialidade.

### 7. O teste seguinte precisa separar desenvolvimento de confirmação

Jev não é um grupo de controle apenas por não escrever justificativas. Continua sendo um avaliador de IA dos mesmos textos. Os outros 19 pedidos ficam fora desta amostra, mas já existem no histórico do projeto; não são automaticamente um conjunto inédito.

Recomendo registrar previamente quais casos serão usados para aperfeiçoar a candidata e quais serão reservados para confirmação, manter a leitura humana dos exemplos e avaliar redação e reescrita separadamente. Se a pergunta for evolução entre versões, a comparação deve ser direta com a 0.8.1, como nesta amostra; o protocolo desse ciclo precisa declarar essa referência antes da execução.

## O que foi atualizado agora

A instrução de justificativa passou à **versão 2, prospectiva**, no runner distribuído. Por texto, Astra e Opus devem informar:

1. lista das características percebidas como não-humanizadas;
2. trecho literal que sustenta cada característica;
3. efeito na leitura, considerando gênero e pedido;
4. análise separada de qualidade e fidelidade;
5. ausência explícita de características quando não houver evidência concreta.

O formato JSON e as escalas permanecem iguais. Jev mantém seu contrato nativo, sem justificativa textual. Novas preparações `v2-brief` congelam a versão 2; configurações históricas e a reprodução `v1-full-json` conservam a versão 1. A emenda está documentada no [RUNNER.md](../../scripts/RUNNER.md#justificativas-prospectivas-versão-2).

A atualização foi validada por **18 testes do runner e 88 testes da skill**, incluindo preservação do prompt antigo e envio da instrução nova aos juízes de chat. Esses testes são de software. A skill distribuída continua **0.8.1**, a candidata continua **0.9.0**, e nenhuma nova rodada de geração ou julgamento foi executada.

O runner amostral externo e um novo plano de comparação precisarão incorporar essa seleção antes de uma execução futura. Não se altera o runner congelado da amostra anterior.

## Recomendação de execução

Para uma próxima candidata, eu priorizaria:

1. explicitar que exemplos não definem tamanho nem papéis;
2. conferir cobertura do pedido antes de reduzir o texto;
3. tratar bastidores e falsas atribuições de omissão com alertas contextuais;
4. testar a hipótese sobre fechos e simetrias separadamente.

Implementar essa próxima candidata e executar novos testes ficam para a decisão de Ricardo. A atualização do prompt solicitada nesta mensagem já está preparada e validada.

## Fontes e execução

- [Amostra original, preservada](../../samples/2026-10-23/README.md).
- [Textos, notas e justificativas originais](../../samples/2026-10-23/RESULTS.json).
- [Registro verificável desta análise](VERIFICATION.json).

Claude Code 2.1.303, modelo efetivamente retornado `claude-opus-5-5`, `--effort max`, assinatura Max. O plano foi produzido em leitura, sem ferramentas de escrita. Os nove arquivos dos pacotes comparados foram conferidos pelos hashes da amostra, e o contexto fornecido permaneceu inalterado.
