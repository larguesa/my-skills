# Humanizador 0.9.1 versus 0.8.1: nova amostra aleatória

## Pergunta e autorização

Ricardo solicitou, em 23/10/2026, implementar as alterações após fornecer ao Claude Code Opus 5.5, esforço máximo, o plano e a crítica em Markdown, e executar outro teste com 20% aleatórios da bateria completa. Esta execução compara diretamente a nova candidata 0.9.1 com a versão distribuída 0.8.1, como recomendado na crítica aprovada. Não mede a diferença causal entre 0.9.0 e 0.9.1 por comparação de médias históricas.

O objetivo principal é maior humanização percebida, com fidelidade e atendimento ao pedido preservados. Tokens, tempo e custo são telemetria, não critérios de sucesso.

## Alterações antes do congelamento

O Claude recebe os dois documentos completos: `results/reviews/2026-10-23-juizes/README.md` e `PLANO-OPUS.md` do commit `72c1d8522b5764f5b36f0aafa6df2c09bee6efa5`. O incremento solicitado começa pelas prioridades P1 e P2, interpretadas conforme a crítica: exemplos não determinam extensão, papéis ou estrutura; a redação confere cobertura do pedido antes de cortar. Não são adotadas proibições de repetição funcional, perguntas finais, formalidade ou seções. Bastidores, atribuição de lacunas e fechos ficam para testes separados. A implementação e os testes de software são conferidos antes das chamadas.

## Sorteio

A população contém os mesmos 24 pedidos literais aprovados em `results/PROMPTS.md`. Não existe corpus final de reescrita aprovado; o teste é de redação.

Um único sorteio, antes de gerar respostas ou observar notas: `sorted(random.Random(12158665897466131185).sample(range(1,25),5))`. A seed veio de `secrets.randbits(64)` e foi preservada em `selection.json`. São 5 pedidos, arredondamento para cima de 4,8, equivalentes a 20,83% da bateria.

Selecionados: 01 (notícia de bibliotecas), 06 (física, período), 12 (discussão acadêmica), 14 (probabilidade condicional) e 16 (comparação de infraestrutura). O pedido 06 participou do diagnóstico anterior; os demais não participaram daquela amostra, mas já existiam no histórico. Não são apresentados como casos inéditos.

## Comparação e denominadores

- Referência: pacote 0.8.1 do commit `607fe0230d19633f07529bcd6dacdab0b3252504`.
- Candidata: pacote 0.9.1 efetivamente implementado e congelado antes da execução.
- Dois braços com skill, em contextos independentes e novas chamadas. Cada um recebe apenas sua SKILL.md, seu briefing de gênero e o pedido literal.
- Não há memória, SOUL, exemplos de respostas do outro braço nem críticas dos juízes nas gerações.
- Mesmos modelos, rotas, modos de raciocínio e limites de saída, 4.096 tokens, em cada par.
- Mantidas as 19 configurações de 14 modelos e as rotas efetivas da amostra anterior.
- 5 pedidos × 19 configurações: 95 pares, 190 gerações e até 285 chamadas individuais de julgamento (três por par válido).
- A ordem percorre uma configuração pelos cinco pedidos; cada par é julgado antes do seguinte.
- Juízes: Jev 1.13, Decisions nativo; GPT-6 Astra; Claude Opus 5.5. Um par anônimo por chamada, sem identidade do braço ou gerador.
- Astra e Opus usam a justificativa prospectiva versão 2, já publicada. Exigem lista de características percebidas como não-humanizadas, trechos literais e efeito contextual; qualidade e fidelidade ficam separadas na mesma string. Schema, escalas e preferência permanecem iguais. Jev permanece sem justificativa textual e sem alteração no contrato.

## Análise

H = 100 menos impressão de IA. ΔH = H da 0.9.1 menos H da 0.8.1, em pontos. A média principal usa pares com os três juízes válidos, com peso igual por par e juiz. ΔH positivo indica melhora percebida nesta amostra; zero, ausência de mudança; negativo, piora.

O relatório apresenta H e ΔH por juiz e pedido, naturalidade, clareza, adequação, correção, preferência e falhas críticas. As dimensões de qualidade e os votos não são substituídos pela humanização. Cada campo informa seu denominador. H é um índice de percepção, não probabilidade calibrada de autoria.

A comparação principal é dentro desta execução. A amostra anterior usou outros pedidos e a versão anterior do prompt de julgamento, portanto suas médias não demonstram que as duas mudanças isoladamente melhoraram a 0.9.0. Redação e reescrita não se misturam. Não há aprovação de release por este estudo amostral; a versão distribuída permanece 0.8.1.

## Integridade e execução

Pacotes, scripts, pedidos, seleção, payloads, mapa anônimo, rubrica, protocolo e supervisor são congelados por SHA-256. O plano fica fixo antes da primeira chamada. Não se altera a candidata em função das notas.

As saídas são preservadas literalmente. Nenhuma resposta é corrigida, substituída ou repetida. Saída vazia, truncada ou acima do limite fica registrada como inválida, sem nota inventada; não bloqueia o julgamento de outros pares independentes. Falha sem resposta, erro de infraestrutura ou submissão/cobrança ambígua interrompe chamadas novas, sem repetição automática.

O supervisor aplica prazo total de 600 segundos por passo, além do timeout de socket. Se interromper uma chamada, conserva a tentativa e não atribui automaticamente causa ao provedor nem custo zero. O piloto inicial usa os primeiros cinco slots reais, duas gerações e três juízes; se válidos, a continuação reutiliza esses resultados, sem repeti-los.

Chave OpenRouter dedicada a esta nova amostra, sem teto monetário, conforme autorização do estudo. Saldo e capacidade da chave são conferidos. Catálogo e endpoints são consultados novamente. Sondagens históricas documentam compatibilidade passada e não são descritas como sondagens atuais. Toda chamada paga fica na contabilidade, incluindo saídas inválidas e erros com custo registrado.

A leitura humana dos exemplos segue pendente. Não será simulada. Os testes offline de software usam transporte sintético, sem representar evidência de humanização.

## Publicação

Publicar textos completos e julgamentos por pedido, sumário agregado, seleção, protocolo, hashes e implementação. Respostas HTTP privadas, credenciais e metadados de conta ficam fora da publicação. Se houver interrupção, informar a cobertura real e o que permanece pendente. Preservar os relatórios e freezes anteriores sem alteração.

## Emenda autorizada em 25/10/2026, antes do congelamento

Ricardo autorizou incorporar à candidata 0.9.1 os três diagnósticos condicionais do parecer `STOP-SLOP.md` de 24/10 e corrigir a candidata antes de retomar os testes. Esta emenda substitui exclusivamente o adiamento desses diagnósticos na seção “Alterações antes do congelamento”:

1. Tranquilização automática: retirar comentários do assistente sem função no artefato; preservar acolhimento solicitado, voz autoral e atendimento legítimo.
2. Fechos de parágrafo repetidamente enfáticos: rever quando a frase de efeito substitui desenvolvimento; preservar frases curtas, nominais e fechos funcionais.
3. Responsabilidade escondida em abstrações: nomear o agente somente quando identificado no material e relevante; não inventar responsabilidade nem proibir sujeitos não humanos legítimos.

Não se importa integralmente stop-slop, nem se acrescentam proibições universais, detector ou bloqueio automático. As correções precisam preservar fidelidade e passar TODOS os testes originais, sem falhas ou skips, com fixtures completas e documentação, em cópia byte-matched. Não se alteram os testes originais nem seus limites para obter aprovação.

O restante do protocolo permanece intacto: referência 0.8.1 no commit `607fe0230d19633f07529bcd6dacdab0b3252504`; seed `12158665897466131185` e seleção já realizada `1,6,12,14,16`, sem novo sorteio; pedidos literais, 19 configurações de 14 modelos, 95 pares, 190 gerações e até 285 julgamentos; três juízes, rationale v2; rotas e limites originais, prazo de 600 segundos, piloto de cinco chamadas e continuação sem repetição automática.

A retomada é um estudo emendado prospectivamente, não uma reprodução inalterada. Não recebe resultados pagos anteriores. Catálogo, endpoints e pré-flight read-only de 25/10 são fornecidos pela controladora em `control-preflight/`; as sondagens inferenciais reaproveitadas permanecem históricas e não são descritas como sondagens atuais. A candidata fica em `candidate-repo/skills/humanizador-pt-br` da nova pasta; a referência e as pastas de 23/10 e 24/10 permanecem preservadas. A fase desta entrega é exclusivamente OFFLINE: nenhuma inferência, leitura de chave, publicação ou e-mail; qualquer execução paga exige gate verde, freeze revisado e pré-flight vivo pela controladora.
