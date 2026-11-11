# Escrita e decisões, guia Claude

Use ao revisar clareza, exemplos, liberdade de execução e quantidade de contexto.

## Práticas incorporadas

1. Inclua somente informação que muda decisões. Corte explicações genéricas sobre ferramentas que o agente já domina.
2. Preserve no núcleo as condições necessárias à tarefa. Economizar contexto não significa remover exceções ou critérios de conclusão.
3. Ajuste o grau de liberdade à fragilidade: sequência fixa em migração delicada; critérios e resultado em análise aberta.
4. Prefira exemplos curtos de entrada e saída que mostrem decisões complementares, incluindo um caso incompleto.
5. Crie avaliações a partir de falhas observadas antes de expandir a documentação. Compare com baseline.
6. Use referências condicionais e rasas. Se uma referência for necessária, diga quando lê-la e confirme sua existência.
7. Para saídas verificáveis, exija execução e inspeção. Para peças visuais, examine também a renderização; testes de texto não detectam cortes e sobreposição.

## Aplicação editorial

Fraco: “Seja um especialista extremamente rigoroso e revise tudo várias vezes.”

Operacional: “Confira cada divergência no trecho original. Corrija as que não puderem ser reproduzidas e identifique separadamente trechos ilegíveis. Termine quando todos os campos solicitados tiverem valor ou ausência documentada.”

## Decisões da síntese

O guia recomenda terceira pessoa na descrição e corpo abaixo de 500 linhas. Use essas orientações quando forem compatíveis com o agente-alvo. Não as transforme em exigências universais nem em prova de eficiência. No Hermes local, priorize a convenção de descrição curta do ambiente.

## Fonte

Anthropic, Skill authoring best practices, consulta em 11/11/2026:
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Este arquivo é uma síntese operacional autoral, não uma tradução integral.
