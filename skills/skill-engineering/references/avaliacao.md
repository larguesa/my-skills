# Protocolo de avaliação

Leia antes de executar ensaios ou alegar ganho. O auxiliar deste pacote valida e agrega resultados; a coleta vem da execução real no agente escolhido.

## Níveis separados

1. Estrutura: YAML, caminhos, campos e consistência do pacote.
2. Função: exemplos executados e produto correto segundo critérios prévios.
3. Utilidade comparativa: mesma tarefa com skill nova e baseline, em contextos limpos.
4. Descoberta: seleção observada no catálogo real, sem fornecer a skill ao executor.

Carregar a skill explicitamente permite testar execução, mas não descoberta. Testes de scripts com fixtures não medem melhoria de modelos.

## Planejamento

- Preencha o modelo de plano com finalidade, entradas, autorização e orçamento. Inferência paga, publicação e alterações em produção precisam estar no escopo autorizado.
- Fixe critérios antes de ver as saídas. Inclua conteúdo, uso, ausências e falhas críticas, não apenas presença de arquivos.
- Separe desenvolvimento, validação para escolher versões e teste final novo. Não reutilize o teste final para selecionar a próxima versão.
- Para nova skill, use `without_skill`; para melhoria, use `old_skill`. Preserve a revisão de cada condição.
- Use o mesmo modelo, provedor, ferramentas, revisões de entrada e limite de execução nos pares. Contextos devem ser limpos e não compartilhar respostas.
- Balanceie a ordem das condições ou execute em paralelo com capacidade suficiente. Para afirmar tendência, repita e apresente dispersão e diferenças por caso.

## Descoberta

Monte pedidos positivos, negativos semanticamente próximos e compostos. Observe a consulta real da skill e das referências necessárias, não apenas a frase “eu usaria esta skill”. Preserve o catálogo e o log usados. Registre `triggered` separadamente de `status`; erro de rede, timeout ou falha do executor é `technical_error`, nunca um acerto negativo.

O auxiliar de agregação abaixo mede execução, não pontuação de descoberta. Não use uma lista de intenções produzida pelo modelo como se fosse teste de acionamento.

## Registro canônico de execução

Use um único arquivo JSON, em vez de depender de descoberta implícita de diretórios. Estrutura mínima:

```json
{
  "schema_version": 1,
  "baseline": "without_skill",
  "runs": [
    {
      "case_id": "caso-real",
      "replicate": 1,
      "condition": "with_skill",
      "status": "completed",
      "task_success": true,
      "critical_failures": 0,
      "duration_ms": null,
      "input_tokens": null,
      "output_tokens": null,
      "cost_usd": null
    }
  ]
}
```

O bloco demonstra o schema, não uma medição. Um par utilizável requer também o registro da baseline para o mesmo `case_id` e `replicate`.

Campos `case_id`, `replicate`, `condition`, `status`, `task_success` e `critical_failures` são obrigatórios. Em cada registro, `condition` aceita exatamente `with_skill` ou `baseline`; o campo `baseline` do envelope identifica se essa condição significa `without_skill` ou `old_skill`. Os demais campos de métricas aceitam `null` ou ausência quando não observados. Use repetição inteira positiva e uma única execução para cada chave caso/repetição/condição.

- `completed`: execução terminada e avaliada; `task_success` é booleano e `critical_failures` é inteiro não negativo. Falha no produto é `completed` com `task_success=false`, não erro técnico.
- `technical_error` ou `not_run`: `task_success` e `critical_failures` ficam `null`. Guarde motivo e evidência fora do indicador de qualidade.
- `duration_ms`: duração de parede observada no escopo declarado, em milissegundos. Informe se inclui ferramentas ou apenas inferência.
- `input_tokens` e `output_tokens`: inteiros reportados pelo runtime no mesmo escopo nas duas condições. Não substitua tokens por caracteres, palavras ou tamanho do arquivo. Tokens totais, quando só eles existirem, ficam em campo separado de evidência; não os distribua artificialmente.
- `cost_usd`: custo observado, em dólares; desconhecido é `null`. Preço de tabela não é cobrança medida.
- Mantenha artefatos, logs e critérios ao lado do registro. A agregação confia no registro fornecido, não reavalia os artefatos.

## Agregação e interpretação

O comando `aggregate` rejeita chaves duplicadas, estados e valores inválidos. Reporta contagens por condição, erros técnicos, não executados e pares incompletos. Erros técnicos e não executados não entram no acerto de qualidade; aparecem nas contagens e reduzem a cobertura de pares.

Compare sucesso somente nos pares cujas duas execuções foram concluídas. Uma execução concluída com falha crítica conta como insucesso, mesmo se `task_success` tiver sido marcado como verdadeiro; preserve essa inconsistência no diagnóstico. Reporte diferença em pontos percentuais, não percentual relativo disfarçado.

Para duração, tokens e custo, agregue somente pares com a medida observada nas duas condições, indicando o número de pares de cada métrica e a dispersão. Não preencha valores ausentes com zero. Sem pares válidos, a diferença é `null`, não zero.

Examine os artefatos e os casos individuais antes de recomendar uma versão. Um pequeno ensaio pode mostrar um defeito ou uma capacidade; somente a evidência coletada autoriza a conclusão correspondente.

## Revisão humana e encerramento

Quando usar um visualizador externo, confira antes seu contrato de entrada; não force estes resultados no schema de outro agregador. Para revisão simples, entregue prompt, artefatos de cada condição, critérios e observações em HTML estático, com identidade das condições ocultada se a comparação for cega.

Aplique uma mudança por padrão de falha, preserve regressões e refaça os casos afetados. Ao finalizar, informe a versão, o que foi testado, o resultado concreto e as medições disponíveis. Não acrescente advertências genéricas ao produto do usuário.
