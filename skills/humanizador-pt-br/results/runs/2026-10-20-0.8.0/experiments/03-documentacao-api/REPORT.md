# Desenvolvimento: documentação de API

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Prompt literal

```text
Escreva a documentação de uso desta API de tarefas, incluindo um exemplo curl e a resposta de sucesso.

POST https://api.example.com/v1/jobs
Autenticação: Authorization: Bearer <TOKEN>
Content-Type: application/json
Corpo: {"name":"backup"}
name: string obrigatória, não vazia, com até 80 caracteres.
Sucesso: HTTP 201, {"id":"job_123","status":"queued"}. queued indica que a tarefa entrou na fila.
Idempotency-Key é opcional. Por 24 horas, a mesma chave e o mesmo corpo retornam a tarefa existente; a mesma chave com corpo diferente retorna 409.
Erros: 400 para name inválido; 401 para token ausente ou inválido; 429 ao superar 60 requisições por minuto por token, com Retry-After em segundos.
```

## Comparação completa

| Modelo / modo | Baseline | Skill 0.8.0 | Jev | Astra | Opus |
|---|---|---|---|---|---|
| anthropic/claude-opus-5.5 / on | <pre>&#35; API de Tarefas&#58; Criar tarefa&#10;&#10;Cria uma nova tarefa e a coloca na fila de processamento&#46;&#10;&#10;&#96;&#96;&#96;&#10;POST https&#58;&#47;&#47;api&#46;example&#46;com&#47;v1&#47;jobs&#10;&#96;&#96;&#96;&#10;&#10;&#35;&#35; Autenticação&#10;&#10;Envie um token do tipo Bearer no cabeçalho &#96;Authorization&#96;&#58;&#10;&#10;&#96;&#96;&#96;&#10;Authorization&#58; Bearer &#60;TOKEN&#62;&#10;&#96;&#96;&#96;&#10;&#10;Se o token estiver ausente ou for inválido&#44; a requisição retorna &#96;401 Unauthorized&#96;&#46;&#10;&#10;&#35;&#35; Cabeçalhos&#10;&#10;&#124; Cabeçalho &#124; Obrigatório &#124; Descrição &#124;&#10;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#10;&#124; &#96;Authorization&#96; &#124; Sim &#124; &#96;Bearer &#60;TOKEN&#62;&#96; &#124;&#10;&#124; &#96;Content&#45;Type&#96; &#124; Sim &#124; &#96;application&#47;json&#96; &#124;&#10;&#124; &#96;Idempotency&#45;Key&#96; &#124; Não &#124; Chave para repetir a requisição com segurança&#46; Veja &#91;Idempotência&#93;&#40;&#35;idempotência&#41;&#46; &#124;&#10;&#10;&#35;&#35; Corpo da requisição&#10;&#10;&#96;&#96;&#96;json&#10;&#123;&#10;  &#34;name&#34;&#58; &#34;backup&#34;&#10;&#125;&#10;&#96;&#96;&#96;&#10;&#10;&#124; Campo &#124; Tipo &#124; Obrigatório &#124; Regras &#124;&#10;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#10;&#124; &#96;name&#96; &#124; string &#124; Sim &#124; Não pode ser vazio&#46; Máximo de 80 caracteres&#46; &#124;&#10;&#10;Se &#96;name&#96; não atender a essas regras&#44; a requisição retorna &#96;400 Bad Request&#96;&#46;&#10;&#10;&#35;&#35; Exemplo de requisição&#10;&#10;&#96;&#96;&#96;bash&#10;curl &#45;X POST https&#58;&#47;&#47;api&#46;example&#46;com&#47;v1&#47;jobs &#92;&#10;  &#45;H &#34;Authorization&#58; Bearer &#60;TOKEN&#62;&#34; &#92;&#10;  &#45;H &#34;Content&#45;Type&#58; application&#47;json&#34; &#92;&#10;  &#45;H &#34;Idempotency&#45;Key&#58; 6f1c2a9e&#45;backup&#45;001&#34; &#92;&#10;  &#45;d &#39;&#123;&#34;name&#34;&#58;&#34;backup&#34;&#125;&#39;&#10;&#96;&#96;&#96;&#10;&#10;O cabeçalho &#96;Idempotency&#45;Key&#96; é opcional&#46; Remova a linha correspondente se não precisar dele&#46;&#10;&#10;&#35;&#35; Resposta de sucesso&#10;&#10;&#42;&#42;&#96;201 Created&#96;&#42;&#42;&#10;&#10;&#96;&#96;&#96;json&#10;&#123;&#10;  &#34;id&#34;&#58; &#34;job&#95;123&#34;&#44;&#10;  &#34;status&#34;&#58; &#34;queued&#34;&#10;&#125;&#10;&#96;&#96;&#96;&#10;&#10;&#124; Campo &#124; Descrição &#124;&#10;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#10;&#124; &#96;id&#96; &#124; Identificador da tarefa criada&#46; &#124;&#10;&#124; &#96;status&#96; &#124; Estado da tarefa&#46; &#96;queued&#96; indica que a tarefa entrou na fila&#46; &#124;&#10;&#10;&#35;&#35; Idempotência&#10;&#10;Use o cabeçalho &#96;Idempotency&#45;Key&#96; para reenviar uma requisição com segurança&#44; por exemplo após uma falha de rede&#44; sem criar tarefas duplicadas&#46; A chave vale por &#42;&#42;24 horas&#42;&#42;&#58;&#10;&#10;&#45; &#42;&#42;Mesma chave e mesmo corpo&#58;&#42;&#42; a API retorna a tarefa já existente&#44; sem criar uma nova&#46;&#10;&#45; &#42;&#42;Mesma chave e corpo diferente&#58;&#42;&#42; a API retorna &#96;409 Conflict&#96;&#46;&#10;&#10;Gere uma chave única&#44; como um UUID&#44; para cada tarefa que deseja criar&#46;&#10;&#10;&#35;&#35; Limite de requisições&#10;&#10;Cada token pode fazer até &#42;&#42;60 requisições por minuto&#42;&#42;&#46; Acima desse limite&#44; a API retorna &#96;429 Too Many Requests&#96; com o cabeçalho &#96;Retry&#45;After&#96;&#44; que indica quantos &#42;&#42;segundos&#42;&#42; esperar antes de tentar de novo&#46;&#10;&#10;&#96;&#96;&#96;&#10;HTTP&#47;1&#46;1 429 Too Many Requests&#10;Retry&#45;After&#58; 30&#10;&#96;&#96;&#96;&#10;&#10;&#35;&#35; Códigos de resposta&#10;&#10;&#124; Código &#124; Significado &#124;&#10;&#124;&#45;&#45;&#45;&#124;&#45;&#45;&#45;&#124;&#10;&#124; &#96;201 Created&#96; &#124; Tarefa criada e colocada na fila&#46; &#124;&#10;&#124; &#96;400 Bad Request&#96; &#124; &#96;name&#96; inválido&#58; ausente&#44; vazio&#44; com mais de 80 caracteres ou de tipo diferente de string&#46; &#124;&#10;&#124; &#96;401 Unauthorized&#96; &#124; Token ausente ou inválido&#46; &#124;&#10;&#124; &#96;409 Conflict&#96; &#124; &#96;Idempotency&#45;Key&#96; já usada nas últimas 24 horas com um corpo diferente&#46; &#124;&#10;&#124; &#96;429 Too Many Requests&#96; &#124; Limite de 60 requisições por minuto por token excedido&#46; Consulte &#96;Retry&#45;After&#96;&#46; &#124;</pre><br>[UTF-8 literal](outputs/r00-baseline.txt); completed; USD 0.030156; 12.884s; tokens entrada/saída 314/1445 | ambiguous_intent_without_raw | PENDENTE | PENDENTE | PENDENTE |
| openai/gpt-6-astra / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| x-ai/grok-4.7 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| google/gemini-3.8-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| meta/muse-spark-1.3 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-pro / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-pro / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| z-ai/glm-5.3-prime / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| qwen/qwen3.8-max-prime / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| openai/gpt-6-luna / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| openai/gpt-6-luna / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-flash / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| z-ai/glm-5.3-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| anthropic/claude-sonnet-5.5 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| qwen/qwen3.8-flash / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| qwen/qwen3.8-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| deepseek/deepseek-v4.1-flash / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| deepseek/deepseek-v4.1-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |

## Protocolo e limitações

Chamadas novas e independentes. Baseline recebe só o prompt literal; tratamento recebe SKILL.md 0.8.0 e o briefing local compacto congelado por caso. Nenhum texto de outro braço, preferência pessoal ou feedback de juiz entra nos candidatos.
Mapeamento anônimo e grupos de até quatro pares são congelados; grupo com candidato inválido fica sem julgamento, sem reagrupamento oportunista.
Modelos, modos e providers efetivos são os congelados, incluindo amendments explícitos. Aliases na resposta não comprovam a versão efetiva nem o uso do reasoning solicitado.
Juízes chat: máximo 16384 tokens histórico. Jev Decisions: payload nativo histórico sem max_tokens artificial. Agregado de qualidade: média das quatro dimensões; erro crítico limita correção a 25 e total a 49, preservando notas brutas.

[Resumo agregado](../../SUMMARY.md)
