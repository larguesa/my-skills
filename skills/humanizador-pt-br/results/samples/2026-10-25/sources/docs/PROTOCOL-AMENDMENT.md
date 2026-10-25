## Emenda autorizada em 25/10/2026, antes do congelamento

Ricardo autorizou incorporar à candidata 0.9.1 os três diagnósticos condicionais do parecer `STOP-SLOP.md` de 24/10 e corrigir a candidata antes de retomar os testes. Esta emenda substitui exclusivamente o adiamento desses diagnósticos na seção “Alterações antes do congelamento”:

1. Tranquilização automática: retirar comentários do assistente sem função no artefato; preservar acolhimento solicitado, voz autoral e atendimento legítimo.
2. Fechos de parágrafo repetidamente enfáticos: rever quando a frase de efeito substitui desenvolvimento; preservar frases curtas, nominais e fechos funcionais.
3. Responsabilidade escondida em abstrações: nomear o agente somente quando identificado no material e relevante; não inventar responsabilidade nem proibir sujeitos não humanos legítimos.

Não se importa integralmente stop-slop, nem se acrescentam proibições universais, detector ou bloqueio automático. As correções precisam preservar fidelidade e passar TODOS os testes originais, sem falhas ou skips, com fixtures completas e documentação, em cópia byte-matched. Não se alteram os testes originais nem seus limites para obter aprovação.

O restante do protocolo permanece intacto: referência 0.8.1 no commit `607fe0230d19633f07529bcd6dacdab0b3252504`; seed `12158665897466131185` e seleção já realizada `1,6,12,14,16`, sem novo sorteio; pedidos literais, 19 configurações de 14 modelos, 95 pares, 190 gerações e até 285 julgamentos; três juízes, rationale v2; rotas e limites originais, prazo de 600 segundos, piloto de cinco chamadas e continuação sem repetição automática.

A retomada é um estudo emendado prospectivamente, não uma reprodução inalterada. Não recebe resultados pagos anteriores. Catálogo, endpoints e pré-flight read-only de 25/10 são fornecidos pela controladora em `control-preflight/`; as sondagens inferenciais reaproveitadas permanecem históricas e não são descritas como sondagens atuais. A candidata fica em `candidate-repo/skills/humanizador-pt-br` da nova pasta; a referência e as pastas de 23/10 e 24/10 permanecem preservadas. A fase desta entrega é exclusivamente OFFLINE: nenhuma inferência, leitura de chave, publicação ou e-mail; qualquer execução paga exige gate verde, freeze revisado e pré-flight vivo pela controladora.
