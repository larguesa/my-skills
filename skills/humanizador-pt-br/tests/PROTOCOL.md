# Protocolo dos contos, versão 1

## O que foi fixado antes da execução

- Dois prompts originais: uma chave no ônibus e um bolo na portaria. Textos de 80 a 120 palavras, em terceira pessoa.
- Os 14 modelos do piloto anterior, com as mesmas rotas que tinham evidência de aceitação. Cinco também têm modo desligado solicitado. São 19 configurações.
- Duas gerações independentes por configuração e por conto: sem skill e com a skill textual completa, catálogo e estilos. Não é uma reescrita do original.
- A instrução comum solicita somente o conto, sem título ou análise, e sem travessão longo. Modelo, rota, raciocínio e teto de 4.096 tokens são iguais dentro de cada par.
- Uma primeira resposta por condição. Não selecionar a melhor de várias tentativas, editar a prosa ou regenerar texto válido. Saídas truncadas, vazias e recusadas são falhas, não texto comprimido.
- A versão 0.2.0 da skill e os scripts de execução foram congelados por SHA256, antes das chamadas. O protocolo operacional verificável é [frozen/config.json](frozen/config.json); o tratamento integral está em [frozen/skill-bundle.txt](frozen/skill-bundle.txt).

## Juízes

Jev `typesafe/jev-1.13`, Astra `openai/gpt-6-astra` e Opus `anthropic/claude-opus-5.5`.

Cada conto tem seu lote próprio: 38 textos e 19 pares. Os juízes recebem o prompt original, os textos e os pares com IDs opacos, sem nomes dos geradores e sem indicação da skill. A ordem dos pares e a posição A/B são embaralhadas com seed fixa. O mapa é preservado para compor o relatório depois, não enviado ao juiz.

Cada juiz fornece:

1. Impressão de escrita por IA para cada texto, em escala de 0 a 100.
2. Preferência de leitura por par, A, B ou empate, considerando naturalidade, ritmo e atendimento ao prompt.

Jev usa o endpoint nativo `https://openrouter.ai/api/alpha/decisions`, com perguntas `noul` para impressão e `choice` para preferência. Seu retorno `noul` é multiplicado por 100 apenas para apresentação. Astra e Opus recebem a mesma tarefa por chat, com teto de 8.192 tokens e raciocínio ligado em esforço medium.

As respostas tipadas e os números dos juízes não estabelecem verdade nem calibração de autoria. Os contos das duas condições são sabidamente de IA. Juízes podem premiar polimento, reconhecer o próprio estilo ou sofrer viés de posição. A preferência não será usada para modificar a skill.

## Escopo e custo

O novo estudo é uma reformulação do piloto já autorizado, não uma rodada completa. O teto global anterior continua em US$ 10. Do teto, US$ 1,013765632 já foram consumidos no histórico. A chave exclusiva deste estudo foi limitada ao restante, US$ 8,986234368; isso é teto, não estimativa ou compromisso de gasto.

Planos e estados são persistidos antes e depois das chamadas. O runner reutiliza o controle de preço e orçamento do benchmark anterior. Uma requisição incerta bloqueia repetição automática. Um estado já concluído não é reexecutado. A cobrança da chave precisa ser reconciliada antes de qualquer recuperação. Não há recarga forçada de conta ou troca silenciosa de modelo.

As chamadas usam dados ficcionais públicos. Não carregam SOUL.md, memórias, outras skills ou contexto do Hermes. Os parâmetros e provedores efetivamente retornados ficam nas respostas reais. Raciocínio “desligado” descreve o pedido enviado em uma rota com aceitação anterior, não prova sobre computação interna.

### Emenda operacional anterior aos juízes

As tentativas sem resposta são preservadas e reconciliadas em [RECOVERY.md](RECOVERY.md). Após falhas de disponibilidade, oito posições MiMo Pro e Flash do conto do bolo passam de DeepInfra para GMICloud, com a mesma rota nos dois braços de cada par. Prompt, skill, raciocínio e teto permanecem iguais. O plano original continua preservado; [o plano efetivo](results/generation-plan.json) e [a emenda](results/attempts/route-amendment.json) registram os pedidos executados. As quatro sondagens de rota somam US$ 0,00003767 e entram no custo da rodada. Nenhum resultado válido foi repetido.

## Reproduzir

Na raiz do repositório:

```text
python3 -m unittest discover -s skills/humanizador-pt-br/tests -v
python3 skills/humanizador-pt-br/tests/scripts/contos.py
python3 skills/humanizador-pt-br/tests/scripts/relatorio.py
```

O segundo comando valida os hashes e mostra o plano, sem inferência paga. O terceiro usa somente resultados já registrados e reconciliação, sem novas chamadas. Nenhum gera um benchmark fictício para preencher resultados ausentes.

Uma nova execução paga exige autorização, uma nova pasta de estado e configuração própria congelada. Defina `OPENROUTER_API_KEY` somente no ambiente e use `contos.py --execute-paid --out <nova-pasta> --config <nova-configuração>`. O runner requer Linux/macOS por reutilizar o bloqueio POSIX do benchmark; o editor local `humanizar.py` continua portátil. Não reutilize cegamente a configuração histórica para avaliar versões modificadas da skill.

## Publicação e avaliação humana

Publicar `README.me` da skill, `tests/README.md` e `tests/REPORT.md`, com exemplos completos lado a lado, além dos registros reais e scripts sob `tests/`. Não publicar credenciais ou dados de conta. Manter o piloto anterior em `tests/historico-20260929/`, separado da comparação de contos.

A primeira publicação pede a Ricardo uma avaliação humana. Não ajustar a skill, escolher textos favoráveis nem iterar a geração com base no trio de juízes. Nenhum ranking geral ou ganho de qualidade será anunciado antes dessa avaliação.
