# Teste funcional de redação, versão 0.8.0

Modelo: `xiaomi/mimo-v2.6-pro` via OpenRouter, raciocínio desativado. Seis pedidos já aprovados (1, 3, 13, 17, 23 e 24), uma geração por pedido, sem baseline, sem juízes e sem reescrita posterior. A skill e o briefing calculado foram fornecidos no sistema; o pedido foi mantido literalmente. O [plano congelado](writing-smoke/plan.json) contém os payloads e hashes de entrada.

## Resultado

- 5 textos completos, todos sem bloqueio mecânico de entrega. Nenhum retornou apenas comandos.
- 1 chamada recusada pelo provedor por limite temporário (pedido 3, documentação de API). Esse pedido ficou sem texto; a recusa foi preservada, sem repetição.
- A leitura editorial identificou imprecisão no título da notícia, analogia com mecanismo diferente no texto sobre cache, afirmações não fornecidas no e-mail e problemas de redação e continuidade na ficção. Passar no verificador não eliminou esses problemas.
- Este teste verifica a execução da versão; não mede preferência ou ganho de humanização. A matriz comparativa anterior não foi retomada.

## Execução de software

117 testes aprovados: 87 da skill, 15 do runner e 15 da análise histórica. Mais 11 reproduções independentes corrigidas. 1546 arquivos congelados conferidos por hash, sem alteração. Logs: [suítes](final-tests.json), [reproduções](reproductions-final.json) e [resumo](verification-summary.json). Os 22 testes do controlador usados na entrega anterior não foram repetidos; não integram o total atual.

## Chamadas de redação

| Pedido | Resultado | Tokens totais | Tempo (s) | Custo nativo (US$) |
|---|---|---:|---:|---:|
| 01 | Texto completo | 6169 | 5.28 | 0.00279879 |
| 03 | Recusada, sem texto | n/d | 0.72 | n/d |
| 13 | Texto completo | 6496 | 21.71 | 0.001995426 |
| 17 | Texto completo | 5996 | 8.21 | 0.001596966 |
| 23 | Texto completo | 6324 | 20.18 | 0.001849701 |
| 24 | Texto completo | 6767 | 41.33 | 0.002271216 |

Tokens das cinco respostas completas: 31752. Custo nativo conhecido dessas respostas: US$ 0.010512099. Tempo medido por chamada HTTP, sem preparação local; o tempo da recusa não entra na média das respostas completas. A recusa não trouxe custo nativo.

## Textos completos e leitura editorial

### 01. Jornalístico: notícia sobre bibliotecas

**Pedido original:**

````text
Redija uma notícia curta para um portal local. A Prefeitura de Vila Clara anunciou em 1º de outubro de 2026 a abertura de 1.200 vagas gratuitas em oficinas de leitura nas seis bibliotecas municipais. As inscrições vão de 5 a 16 de outubro, presencialmente nas bibliotecas, para pessoas a partir de 12 anos. As oficinas começam em 3 de novembro. Os horários e a distribuição das vagas por unidade ainda não foram divulgados.
````

**Resposta preservada:**

````text
Prefeitura de Vila Clara abre inscrições para 1.200 vagas em oficinas de leitura nas bibliotecas

A Prefeitura de Vila Clara anunciou em 1º de outubro de 2026 a abertura de 1.200 vagas gratuitas em oficinas de leitura nas seis bibliotecas municipais. As inscrições vão de 5 a 16 de outubro, presencialmente nas bibliotecas, e são abertas a pessoas a partir de 12 anos.

As oficinas começam em 3 de novembro. Os horários das atividades e a distribuição das vagas por unidade ainda não foram divulgados.

Serviço

O quê: oficinas de leitura gratuitas nas seis bibliotecas municipais de Vila Clara.

Inscrições: de 5 a 16 de outubro de 2026, presencialmente nas bibliotecas.

Quem pode participar: pessoas a partir de 12 anos.

Início das oficinas: 3 de novembro de 2026.

Horários e vagas por unidade: ainda não divulgados.
````

**Leitura editorial:** Mantém os dados no corpo, mas o título diz que as inscrições estão abertas, sem distinguir o anúncio de 1º de outubro do início em 5 de outubro. Repete quase todo o corpo no quadro de serviço.

### 03. Desenvolvimento: documentação de API

**Pedido original:**

````text
Escreva a documentação de uso desta API de tarefas, incluindo um exemplo curl e a resposta de sucesso.

POST https://api.example.com/v1/jobs
Autenticação: Authorization: Bearer <TOKEN>
Content-Type: application/json
Corpo: {"name":"backup"}
name: string obrigatória, não vazia, com até 80 caracteres.
Sucesso: HTTP 201, {"id":"job_123","status":"queued"}. queued indica que a tarefa entrou na fila.
Idempotency-Key é opcional. Por 24 horas, a mesma chave e o mesmo corpo retornam a tarefa existente; a mesma chave com corpo diferente retorna 409.
Erros: 400 para name inválido; 401 para token ausente ou inválido; 429 ao superar 60 requisições por minuto por token, com Retry-After em segundos.
````

**Resposta preservada:**

````text
Sem resposta de redação.
````

**Leitura editorial:** Sem texto: o provedor recusou a chamada por limite temporário. Não houve repetição nem troca de rota.

### 13. Didático: cache

**Pedido original:**

````text
Explique cache para quem está começando a programar. Use como exemplo uma página que guarda por até 30 segundos o preço recebido de uma API. Dentro desse período, ela pode reutilizar o valor guardado; depois do prazo, a próxima consulta busca o preço na API. Esse cache não recebe notificações quando o preço muda. Mostre a vantagem e o risco desse funcionamento com uma comparação cotidiana.
````

**Resposta preservada:**

````text
Imagine uma página que mostra o preço de um produto vindo de uma API. Toda vez que alguém abre a página, o código consulta a API e recebe o valor atual. Sem cache, cada visita gera uma consulta nova, mesmo que duas pessoas acessem a página com um segundo de diferença.

Cache é guardar uma resposta para reutilizá-la por um tempo, em vez de refazer o trabalho que a gerou. Nesse exemplo, a página guarda o preço por até 30 segundos. Enquanto o prazo não vence, qualquer consulta lê o valor guardado e não chama a API. Passados os 30 segundos, a próxima consulta descarta o valor guardado, busca o preço na API e guarda a resposta nova, que volta a valer por mais 30 segundos.

Uma comparação cotidiana ajuda a entender o mecanismo. Pense em uma placa de preço na porta de uma loja. Um funcionário sai à rua a cada 30 minutos, confere o preço no mercado e atualiza a placa. Enquanto ele não volta, quem olha a placa vê sempre o mesmo valor. Isso é rápido e resolve bem o caso de quem quer só saber o preço para decidir a compra.

A vantagem está aí: a página responde rápido, porque ler o valor guardado é mais barato do que fazer uma chamada de rede, e a API recebe menos consultas, o que alivia o servidor e evita custo desnecessário. Se 100 pessoas abrem a página em 30 segundos, a API é consultada uma vez.

O risco também está na placa. Se o preço na rua muda cinco minutos depois da última atualização, a placa continua mostrando o valor antigo até o funcionário voltar. Do mesmo modo, o cache não recebe notificação quando o preço muda na API. Ele só percebe a mudança quando o prazo de 30 segundos vence e a consulta seguinte vai até a API. Nesse intervalo, o usuário pode comprar com base em um preço que já não vale. Quanto maior o prazo do cache, maior a economia e maior a chance de mostrar dado desatualizado.

Note onde a comparação deixa de valer: a placa física pode ser atualizada no momento exato da mudança, se alguém avisar o funcionário. O cache que você descreveu não tem esse aviso; a única forma de atualizar o valor é esperar o prazo e consultar de novo.

Por isso, a escolha do tempo do cache depende do preço do erro. Para um catálogo de livros, 30 segundos é pouco. Para uma cotação que alguém usa para fechar negócio, pode ser muito: nesse caso, convém reduzir o prazo, ou avisar o usuário de que aquele preço pode não ser o mais recente.
````

**Leitura editorial:** Explica cache e desatualização, mas a comparação descreve atualização periódica a cada 30 minutos, diferente da consulta sob demanda após 30 segundos. O texto aponta outro limite da analogia, mas não essa diferença. O número 100 está numa hipótese explícita, não é fato inventado.

### 17. Comunicação profissional: negociação de prazo

**Pedido original:**

````text
Escreva um e-mail de Paula, da equipe de integração, para a cliente Marina, propondo um ajuste no prazo. A entrega estava prevista para 9 de outubro de 2026. Um arquivo necessário, esperado para 5 de outubro, chegou em 7 de outubro, e a equipe precisa de dois dias úteis para validá-lo antes da homologação. Paula quer propor a entrega em 13 de outubro e manter uma demonstração parcial em 9 de outubro. A mudança depende da aprovação de Marina.
````

**Resposta preservada:**

````text
Assunto: Novo prazo de entrega e demonstração parcial em 9 de outubro

Olá, Marina,

O arquivo que esperávamos para 5 de outubro chegou em 7 de outubro. Como a equipe de integração precisa de dois dias úteis para validá-lo antes da homologação, não conseguimos concluir tudo até 9 de outubro.

Gostaria de propor duas coisas: manter uma demonstração parcial em 9 de outubro e transferir a entrega final para 13 de outubro. A demonstração mostra o que já está pronto e permite discutir os pontos abertos antes da homologação.

A mudança depende da sua aprovação. Se você concordar, confirmo o novo cronograma com a equipe e seguimos para a demonstração de 9 de outubro.

Aguardo seu retorno para seguir.

Abraço,
Paula
Equipe de integração
````

**Leitura editorial:** Preserva a proposta e a aprovação da cliente, mas acrescenta que a equipe não consegue concluir até 9 de outubro e uma finalidade da demonstração que não estão declaradas no pedido. A omissão do ano foi sinalizada pelo verificador.

### 23. Literário: conto na oficina

**Pedido original:**

````text
Escreva um conto curto em primeira pessoa, narrado por uma aprendiz de relojoaria. No último atendimento antes de fechar a oficina, ela encontra dentro de um relógio parado um bilhete sem assinatura: "não acerte a hora". A cliente volta para buscar o relógio antes do fechamento. Deixe o final aberto.
````

**Resposta preservada:**

````text
Sete horas e dez. O mostrador lá fora já escurecia e a porta da oficina estava entreaberta desde as cinco, quando a senhora deixou o relógio sobre o balcão e foi embora sem dizer o nome.

Era um de bolso, de caixa prateada, com a tampa gasta no lugar onde o polegar repousa. Parado às três e quarenta e dois. Eu tinha acabado de limpar o escapamento quando vi que a ponteira do segundeiro estava torta, e empurrei a tampa com a unha para olhar melhor o miolo.

Sobre a platina, entre a roda de pilha e a mola, havia um papel dobrado em quatro. Papel de receituário, amarelado, com a dobra já mole de tanto abrir. "não acerte a hora", estava escrito, em letra pequena, sem ponto e sem assinatura. Escreveram antes de fecharem a caixa, pensei. Alguém que sabia que eu abriria.

Dobrei o papel e coloquei de volta, no mesmo ângulo em que estava. Peguei o carrinho de rosca e levantei a coroa só para sentir o trem rodar, sem dar corda.

O relógio da parede do senhor Aparecido marcou sete e meia. Eu já estava com a chave da gaveta na mão quando a campainha tocou.

Era a senhora. O mesmo casaco de lã, a bolsa presa no braço, a sombrinha que não abria desde a manhã.

"Está pronto?", ela disse.

Fiz que sim e coloquei o relógio sobre o balcão, entre nós duas. A caixa prateada brilhou um pouco na luz fraca da oficina.

Ela estendeu a mão, depois parou.

"E a hora?", disse ela.

Olhei para a ponteira torta. Olhei para ela.

O relógio do senhor Aparecido começou a bater as oito.
````

**Leitura editorial:** Preserva primeira pessoa, bilhete literal, cliente de volta e final aberto. A sequência passa de sete e meia a oito durante uma conversa curta, sem transição; a ambientação técnica pede revisão especializada.

### 24. Literário: crônica na lavanderia

**Pedido original:**

````text
Escreva uma crônica em primeira pessoa sobre uma manhã em uma lavanderia de bairro. A atendente anota no recibo uma meia sem par que não pertence ao narrador. Explore esse pequeno desencontro com humor discreto.
````

**Resposta preservada:**

````text
Havia uma meia de lã azul-marinho, com bolinhas brancas, sendo anotada no meu recibo. A meia não era minha. As minhas meias eram todas pretas, essas de pacote de três no supermercado, sem ambição cromática nenhuma.

A dona Cida, que lavanderia de bairro não é lugar, é gente, nem levantou os olhos do caderninho. Escreveu "1 meia sem par", arrancou o canhoto e me estendeu a folha maior com aquele gesto que é meio paciência e meio cansaço.

"Está aqui, meu bem."

Olhei a meia. Ela estava enrolada em cima do balcão, entre um pacote de pregadores e um potinho de alvejante sem rótulo. Azul-marinho de lã, bolinhas brancas, o calcanhar já gastinho. Um casal de meia bonito, naquele jeito de coisa que já teve dono e carinho.

"Essa não é minha."

A dona Cida aí levantou os olhos. Não para me contrariar. Para me medir.

"Era de um senhor que trouxe um saco de roupa de cama na semana passada", ela disse. "Encontrei a meia dentro do lençol. Fica no balanço."

"Fica no balanço", eu repeti, como se fosse a coisa mais natural do mundo, uma meia morando num balanço.

O balanço, descobri olhando por cima do ombro dela, era uma gaveta do armário de metal, a de cima, onde ela guardava as pílulas antimofo e um maço de chiclete. Abriu para pegar uma etiqueta e eu vi, dormindo ali dentro, uma meia de criança, uma meia feminina cor de pele, meia de meia, dessas de sutiã, e mais duas que eu não consegui identificar. Um abrigo. Uma pensão para meias órfãs.

É esse tipo de coisa que faz a lavanderia de bairro ser diferente da lavanderia do shopping. Na do shopping, a meia sumida vira uma ocorrência, uma ressalva no sistema, um e-mail educado. Aqui, ela vira memória do bairro. A dona Cida sabe de quem é o lençol de quem, de quem perdeu a meia no tanque, de quem trouxe camisa de formatura e voltou buscar com um nó no laço do colarinho. Ela guarda as coisas das pessoas sem fazer escândalo disso.

"O senhor velho que tinha a outra?", perguntei, meio sem saber por quê.

"A do par?", ela disse. "Foi. Não apareceu mais. Trouxe a roupa e sumiu." Fez uma pausa, do tipo que não pede resposta. "Aí fica."

Paguei. Peguei minha trouxa de camisa, que cheirava a sabão de coco e a ferro quente, e a meia azul ficou lá, em cima do balcão, esperando. Não sei o que uma meia espera. Talvez espere o pé que falta. Talvez espere só ser lembrada de vez em quando, quando alguém abrir a gaveta de cima para pegar o chiclete.

Na rua, o ônibus já passava de novo. Uma mulher segurava um cachorrinho no braço. No portão do prédio do lado, um senhor arrastava uma cadeira de plástico para o sol da manhã. O mundo girando com suas coisas pequenas e suas pendências invisíveis.

Deu vontade de voltar e perguntar à dona Cida se ela tinha a meia que eu perdi mês passado, aquela preta de pacote, que sumiu na máquina da minha casa, não na dela. Mas seria injusto com o balanço. Ele tem suas regras. E ela tem seu caderninho.

Então segui andando, com minha trouxa de camisa e minha manhã de segunda-feira, deixando a meia azul-marinho de volta ao seu sono de lã, no armário de metal, em cima da gaveta, à espera do pé que talvez nunca chegue.
````

**Leitura editorial:** Há humor e primeira pessoa, mas aparecem construções inadequadas como "um casal de meia" e "meia de meia, dessas de sutiã". A meia alterna balcão, gaveta e armário sem transição clara. Os alertas de números e datas são invenção permitida pelo pedido ficcional, não falhas factuais.

## Consumo da rodada completa

OpenRouter, diferença de consumo da chave dedicada: **US$ 2.759021183**. Respostas com custo nativo: US$ 0.723328683. Restam US$ 2.035692500 sem atribuição nativa por chamada: os eventos do Codex não trazem custo/ID de geração e a recusa do teste também não traz custo. Não atribuí todo o residual ao Codex nem considerei a recusa gratuita.

Claude Code usou a assinatura autenticada. A estimativa acumulada final a preço de tabela é US$ 12,991587, separada do gasto OpenRouter e sem somar novamente a primeira etapa retomada. [Telemetria por modelo e etapa](accounting.json).

A tentativa inicial do MiMo com raciocínio terminou no limite de 32.768 tokens, sem relatório final; o relatório usado na consolidação veio da segunda tentativa sem raciocínio. A primeira foi mantida no consumo. No Grok, a requisição declarou `max_tokens: 32768`; a resposta informou 84.251 tokens de conclusão, incluindo 76.779 de raciocínio. São valores nativos preservados, não uma afirmação de que o teto foi respeitado.

As respostas públicas removem apenas o identificador de conta do erro do provedor. Os cinco textos permanecem byte a byte iguais aos originais. O runner deste teste é [writing-smoke-runner.py](writing-smoke-runner.py); seu caminho privado e a leitura da credencial foram parametrizados para reprodução, sem alterar seleção de pedidos, payloads ou verificação.
