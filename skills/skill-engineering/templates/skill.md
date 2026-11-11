---
name: nome-da-skill
description: Capacidade e situação de uso, conforme o agente-alvo.
---

# Nome da capacidade

## Contrato

Objetivo: resultado específico, sem ampliar o pedido.
Entradas: arquivos, campos, contexto e fontes necessários.
Saída: artefato e formato que o usuário utilizará.
Restrições: o que preservar e quais operações estão autorizadas.
Ausência: como agir se faltar informação ou falhar a leitura.

## Pré-requisitos

Declare ferramentas e dependências efetivamente usadas. Não inclua valores de segredos.

## Procedimento

1. Inspecione as entradas e confirme versões. Avance quando o conjunto necessário estiver identificado.
2. Execute a transformação ou análise solicitada. Se faltar uma entrada crítica, peça-a em vez de presumir.
3. Verifique o produto por teste, fonte, validador ou revisão visual pertinente. Corrija falhas observadas.
4. Entregue o artefato e a informação útil ao seu uso. Separe pendências concretas.

## Exemplos

Caso comum, entrada: pedido e insumo concretos.
Caso comum, saída: exemplo completo no formato requerido.

Exceção, entrada: exemplo com informação ausente.
Exceção, saída: ausência representada conforme o contrato, sem conteúdo inventado.

## Referências condicionais

Inclua somente caminhos existentes e diga exatamente em qual situação abrir cada arquivo.

## Armadilhas

Substitua esta orientação pelos erros específicos do domínio e pela ação corretiva.

## Conclusão

Termine quando todas as entradas e requisitos pedidos estiverem contemplados e o artefato passar nas verificações definidas. Informe separadamente o que não pôde ser verificado.
