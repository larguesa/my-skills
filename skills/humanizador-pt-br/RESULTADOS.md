# Humanizador PT-BR: implementação e piloto parcial

Código e evidências: esta pasta, na branch `main` do repositório my-skills.

Implementação validada com 31 testes locais. Catálogo de 20 heurísticas e quatro perfis; somente dois scripts de produção e biblioteca padrão. O PR anterior já constava incorporado à main antes desta reorganização. As correções de organização são publicadas diretamente na main, sem novo PR. Outras skills não foram alteradas nesta etapa.

## Execução real
- 72 revisões concluídas, 1 chamada com falha; 155 combinações elegíveis não tentadas.
- 228 combinações elegíveis e 108 excluídas por indisponibilidade de modo/rota entre 336 posições teóricas.
- 14 modelos com resultados; 57 revisões do comunicado e 15 da nota técnica. Ensaio e mensagem não executados.
- Custo das revisões: US$ 0.9988842356; sondagens: US$ 0.0148813972. Uso final da chave: US$ 1.013765632, abaixo do teto US$ 10. Diferença entre soma e chave: -8E-10 USD (precisão do retorno).
- A execução parou após falha externa. Não houve repetição automática. A causa específica não foi preservada pelo runner, portanto não se atribui a saldo, modelo ou provedor. Chave desativada, estado confirmado.

## Evidências no repositório
- [comparacao.html](results/comparacao.html): abrir no navegador. Pedido, original e revisão; metadados, mensagens completas, tokens, custo, tempo e diferenças em seções expansíveis. Resultados ausentes estão identificados.
- [comparacao-blind.html](results/comparacao-blind.html): formulário de avaliação sem identidades; exporta JSON local. Entregar apenas esse arquivo ao avaliador que não tenha visto a comparação identificada. A chave de identificação foi preservada separadamente, não publicada nesta pasta.
- [editorial-audit.md](results/editorial-audit.md) e [JSON](results/editorial-audit.json): inspeção por assistente, não humana nem cega, de 12 saídas do corte inicial. Uma omitiu a equipe Aurora e deve ser rejeitada; não se infere vencedor.
- [resumo.json](results/resumo.json): cobertura, custos por modelo e triagem literal final. Ausência/presença lexical não prova equivalência semântica.

## Cobertura e consumo por modelo
Cobertura desigual: custos totais não comparam eficiência ou qualidade diretamente. Latência inclui a duração observada de cada chamada, não apenas geração de tokens.

| Modelo | Revisões | Custo USD | Mediana s | Tokens entrada | Tokens saída |
|---|---:|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 | 6 | 0.236176 | 9.56 | 41304 | 3548 |
| openai/gpt-6-astra | 6 | 0.3636375 | 6.86 | 23740 | 1361 |
| x-ai/grok-4.7 | 6 | 0.108524 | 18.81 | 32800 | 8882 |
| google/gemini-3.8-flash | 6 | 0.05071500 | 8.21 | 24795 | 8565 |
| meta/muse-spark-1.3 | 6 | 0.08223925 | 21.57 | 23509 | 12436 |
| xiaomi/mimo-v2.6-pro | 6 | 0.0078775236 | 8.95 | 26900 | 2315 |
| z-ai/glm-5.3-prime | 3 | 0.02619408 | 1.94 | 12956 | 353 |
| qwen/qwen3.8-max-prime | 3 | 0.059768 | 9.85 | 12172 | 2454 |
| openai/gpt-6-luna | 6 | 0.003690800 | 2.90 | 23814 | 1451 |
| xiaomi/mimo-v2.6-flash | 6 | 0.003520020 | 32.56 | 26900 | 1340 |
| z-ai/glm-5.3-flash | 3 | 0.00209254 | 3.77 | 12956 | 329 |
| anthropic/claude-sonnet-5.5 | 3 | 0.046940 | 2.41 | 20720 | 550 |
| qwen/qwen3.8-flash | 6 | 0.003106562 | 3.78 | 24428 | 1879 |
| deepseek/deepseek-v4.1-flash | 6 | 0.00440296 | 21.85 | 28017 | 7644 |

## Triagem literal final
1 saídas sinalizadas em 72 revisões. Sinal não substitui inspeção de sentido.
- 9a0ae329f1e1cb7113c4346976fc0baf0e10aacac89175f45d163d6ee2bcc6a7: openai/gpt-6-luna / comunicado / on / simple; ausentes: Aurora.

## Limites e próximos passos
- Piloto parcial, sem ranking. Avaliação humana cega ainda não realizada; a inspeção por assistente não a substitui.
- Os casos são artificiais autorais, não corpus humano. Nenhuma calibragem de voz de Ricardo foi feita.
- A exploração Madras contém apenas 20 registros real/c4_pt, sem grupo sintético comparável. Não houve calibração estatística com PT-Detect nem teste independente por fonte.
- Fontes, prompts e matriz foram congelados antes da geração. O código entregue depois recebeu correções de números/sinais/negações, rejeição de IDs duplicados e apresentação HTML. As entradas originais e respostas do piloto não foram regeneradas.
- O braço com scripts acrescenta auditoria prévia, não executa reescrita automática nem ciclo de reparo.
- Campos on/off representam pedido explícito e evidência disponível da rota, não prova de computação interna. Não confundir raciocínio oculto com desligado.
- Moonlight/Kimi continuam fora da matriz até definição. Rodada completa e orçamento precisam ser decididos após esta etapa.
- A proteção mecânica é conservadora e incompleta; termos técnicos e unidades adicionais devem ser protegidos explicitamente. O benchmark requer POSIX; editor sem dependência externa.

## Reproduzir a validação de software

Na raiz do repositório:

```sh
python3 -m unittest discover -s skills/humanizador-pt-br/tests -v
```

Dentro da pasta da skill:

```sh
python3 -m unittest discover -s tests -v
```

A suíte é offline e usa respostas sintéticas apenas nos testes de software. Não confundir essas fixtures com o piloto real. Esta mudança limita-se à localização da suíte e à documentação/evidência; o código de produção não foi alterado.

[Plano histórico](results/pilot-plan.json), [estado com respostas reais](results/pilot-state.json) e [reconciliação](results/reconciliation-final.json) preservados sem regeneração. Os prompts completos estão no plano/estado. Somente caminhos locais na auditoria editorial foram convertidos em referências relativas para publicação. A existência desses arquivos não autoriza retomar chamadas pagas.
