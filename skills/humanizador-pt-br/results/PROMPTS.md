# Prompts aprovados

Status: 24 prompts aprovados por Ricardo em 06/10/2026. H1 e H2 descartados. Início da nova avaliação autorizado em 10/10/2026; o andamento está em [README.md](README.md).

Os briefings com nomes, eventos e dados específicos são cenários de avaliação, não apuração jornalística, estudos reais ou registros de clientes. Essa informação pertence à documentação do experimento, não será acrescentada aos prompts dos candidatos nem aos textos finais.

## Como comparar após aprovação

- Usar cada prompt literalmente em duas chamadas novas e independentes do mesmo modelo e configuração.
- Na condição sem skill, enviar o pedido sem orientação editorial adicional.
- Na condição com skill, acrescentar apenas a skill aprovada e as mesmas referências editoriais definidas no protocolo. Manter idêntico o pedido do usuário.
- Não fornecer rascunho, resposta, crítica ou nota de uma condição à outra. A revisão interna do próprio rascunho não é reescrita da saída de outra chamada.
- Não herdar memória, preferências pessoais, instruções desta sessão ou regras de pontuação do assistente nos candidatos. Qualquer mensagem técnica obrigatória deve ser igual e registrada nas duas condições.
- Os prompts não contêm instruções de humanização, proibição de pontuação, avisos de ficção ou regras genéricas contra invenção de fontes. Dados, condições técnicas e informações indisponíveis fazem parte do briefing, não de uma rubrica escondida.
- Configurações, referências injetadas, repetições, juízes e regras de avaliação serão congelados antes da execução autorizada. A aprovação isolada destes prompts não autoriza chamadas pagas ou retomada automática.

## 24 casos da ampliação

### 01. Jornalístico: notícia sobre bibliotecas

```text
Redija uma notícia curta para um portal local. A Prefeitura de Vila Clara anunciou em 1º de outubro de 2026 a abertura de 1.200 vagas gratuitas em oficinas de leitura nas seis bibliotecas municipais. As inscrições vão de 5 a 16 de outubro, presencialmente nas bibliotecas, para pessoas a partir de 12 anos. As oficinas começam em 3 de novembro. Os horários e a distribuição das vagas por unidade ainda não foram divulgados.
```

### 02. Jornalístico: reportagem sobre drenagem

```text
Escreva uma reportagem explicativa sobre o monitoramento de drenagem em Porto Sereno, com base neste briefing: 48 sensores de nível de água foram instalados em oito pontos; o piloto durou dois meses, acompanhou duas chuvas fortes e custou R$ 180 mil. O boletim técnico municipal 07/2026 não apresenta grupo de comparação nem estimativa de redução de alagamentos. Lia Prado, engenheira responsável, declarou: "O sensor avisa que o nível subiu; ele não aumenta a capacidade do canal." A associação de moradores da Baixada afirmou em nota: "Queremos saber quem recebe o alerta e em quanto tempo age."
```

### 03. Desenvolvimento: documentação de API

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

### 04. Desenvolvimento: análise de bug

```text
Explique o bug desta função Python e apresente uma correção com exemplos de teste. Quando o chamador passar uma lista, a função deve continuar acrescentando o item àquela mesma lista e retornando-a.

def collect(item, bucket=[]):
    bucket.append(item)
    return bucket

Em um processo novo, collect("A") retorna ["A"], mas a chamada seguinte collect("B") retorna ["A", "B"].
```

### 05. Física: movimento e energia

```text
Explique para um aluno do ensino médio como a energia muda durante a queda de um objeto de 2,0 kg, solto do repouso a 5,0 m do chão. Considere g = 10 m/s², despreze a resistência do ar e adote energia potencial zero no chão. Calcule a energia potencial inicial e a rapidez do objeto imediatamente antes de atingir o chão, mostrando as contas.
```

### 06. Física: medidas de período

```text
Redija um pequeno relatório sobre estas cinco medidas do período de um oscilador: 1,20 s; 1,22 s; 1,19 s; 1,21 s; 1,18 s. Calcule a média e explique o que os resultados permitem concluir. O instrumento tem incerteza absoluta de ±0,02 s por leitura. Não há curva de calibração nem valor teórico de referência disponíveis.
```

### 07. Química: equilíbrio

```text
Explique equilíbrio químico para alunos do ensino médio usando a reação em solução A ⇌ B. A temperatura é fixa e K_c = [B]/[A] = 4. No equilíbrio inicial, [A] = 0,20 mol/L e [B] = 0,80 mol/L. Depois de adicionar A, as concentrações imediatamente após a mistura são [A] = 0,40 mol/L e [B] = 0,80 mol/L. Calcule Q_c nesse instante e explique em que sentido o sistema tende a evoluir.
```

### 08. Química: titulação

```text
Escreva a discussão dos resultados de uma titulação de HCl com NaOH 0,1000 mol/L. Foram usadas alíquotas de 25,00 mL de HCl e os volumes de NaOH foram 12,40 mL, 12,50 mL e 12,60 mL. Considere a reação HCl + NaOH → NaCl + H2O, com proporção 1:1 e ponto final coincidente com a equivalência. Calcule o volume médio e a concentração média do HCl e comente a dispersão das medidas. Não estão disponíveis valor de referência, branco ou orçamento de incerteza.
```

### 09. Biologia e meio ambiente: decomposição

```text
Escreva uma explicação para leigos sobre o que acontece com os restos de plantas em uma horta e qual é o papel dos fungos e das bactérias na decomposição. Relacione o processo ao retorno de nutrientes ao solo e ao destino do carbono. Use um exemplo cotidiano para ajudar na compreensão.
```

### 10. Biologia e meio ambiente: estudo ambiental

```text
Prepare uma nota de análise sobre estas medidas de oxigênio dissolvido em um rio, coletadas no mesmo dia: a montante, 7,1; 7,0; 7,2 mg/L; a jusante, 5,9; 6,0; 6,1 mg/L. Calcule as médias e a diferença entre jusante e montante. Temperatura, vazão, horários individuais e outras substâncias não foram registrados, e não houve coleta em outros dias. Explique como interpretar os resultados.
```

### 11. Acadêmico: resumo

```text
Escreva um resumo acadêmico deste estudo: 120 voluntários adultos de um único curso online foram distribuídos aleatoriamente em dois grupos de 60. Durante oito semanas, o grupo A fez exercícios com feedback semanal e o grupo B fez os mesmos exercícios sem esse feedback. A média inicial na prova, de 0 a 100, foi 50 nos dois grupos. Ao final, foi 68 no grupo A e 61 no grupo B. Não estão disponíveis dados individuais, medidas de dispersão, informações sobre cegamento ou abandono, nem acompanhamento após as oito semanas.
```

### 12. Acadêmico: discussão

```text
Redija uma discussão acadêmica dos resultados e das limitações deste estudo: 120 voluntários adultos de um único curso online foram distribuídos aleatoriamente em dois grupos de 60. Durante oito semanas, o grupo A fez exercícios com feedback semanal e o grupo B fez os mesmos exercícios sem esse feedback. A média inicial na prova, de 0 a 100, foi 50 nos dois grupos. Ao final, foi 68 no grupo A e 61 no grupo B. Não estão disponíveis dados individuais, medidas de dispersão, informações sobre cegamento ou abandono, nem acompanhamento após as oito semanas.
```

### 13. Didático: cache

```text
Explique cache para quem está começando a programar. Use como exemplo uma página que guarda por até 30 segundos o preço recebido de uma API. Dentro desse período, ela pode reutilizar o valor guardado; depois do prazo, a próxima consulta busca o preço na API. Esse cache não recebe notificações quando o preço muda. Mostre a vantagem e o risco desse funcionamento com uma comparação cotidiana.
```

### 14. Didático: probabilidade condicional

```text
Resolva e explique este problema para uma turma de probabilidade: uma fábrica tem 10.000 peças, das quais 2% têm defeito. Um sensor sinaliza 90% das peças defeituosas e 5% das peças sem defeito. Entre as peças sinalizadas, qual é a porcentagem de peças realmente defeituosas? Organize os números em uma tabela e explique o raciocínio.
```

### 15. Negócios: proposta comercial

```text
Redija uma proposta comercial para o Estúdio Boreal integrar seu sistema de estoque a uma API de pedidos existente. O escopo é uma integração, com homologação pelo cliente, sem aplicativo móvel ou migração de dados históricos. O prazo estimado é de seis semanas após a entrega das credenciais e a aprovação do mapeamento. A implantação custa R$ 30.000, em duas parcelas iguais, na assinatura e no aceite da homologação. A manutenção é opcional, custa R$ 600 por mês e inclui até duas horas mensais de suporte. O próximo passo é aprovar o escopo e indicar o responsável pela homologação.
```

### 16. Negócios: comparação de infraestrutura

```text
Prepare uma nota executiva comparando duas opções de infraestrutura para 24 meses. A opção local exige R$ 120.000 de compra inicial e R$ 4.000 por mês de operação. A nuvem não tem compra inicial e custa R$ 6.000 por mês. Compare os custos nominais e apresente uma recomendação. As duas opções precisam atender à mesma carga e disponibilidade, algo que ainda será validado em teste. Migração, impostos adicionais, câmbio, valor residual e custo de capital não estão incluídos nos valores fornecidos.
```

### 17. Comunicação profissional: negociação de prazo

```text
Escreva um e-mail de Paula, da equipe de integração, para a cliente Marina, propondo um ajuste no prazo. A entrega estava prevista para 9 de outubro de 2026. Um arquivo necessário, esperado para 5 de outubro, chegou em 7 de outubro, e a equipe precisa de dois dias úteis para validá-lo antes da homologação. Paula quer propor a entrega em 13 de outubro e manter uma demonstração parcial em 9 de outubro. A mudança depende da aprovação de Marina.
```

### 18. Comunicação profissional: indisponibilidade

```text
Redija um comunicado aos clientes do Painel Aurora sobre a indisponibilidade de acesso em 1º de outubro de 2026, das 14h10 às 14h42, no fuso UTC-3. O serviço foi restabelecido às 14h42. A causa está em investigação. Até o momento, nenhuma perda de dados foi confirmada, mas a análise dos registros ainda não terminou. A próxima atualização está prevista para 2 de outubro, às 12h, no mesmo fuso.
```

### 19. Opinião e ensaio: IA na educação

```text
Escreva um artigo de opinião sobre o uso de IA na educação. Defenda uma posição sobre como aproveitar a ferramenta para apoiar a aprendizagem sem delegar integralmente a avaliação ao modelo. Considere a possibilidade de feedback útil, os erros nas respostas automáticas e a importância de o professor compreender como o estudante chegou à resposta. Inclua um contraponto à posição defendida.
```

### 20. Opinião e ensaio: concentração e disponibilidade

```text
Escreva um ensaio sobre a tensão entre proteger o tempo de concentração e estar disponível para a equipe. Parta desta situação: uma pessoa reservou duas horas para concluir uma análise, mas uma colega precisa de ajuda para destravar uma entrega. Explore diferentes maneiras de lidar com esse conflito.
```

### 21. Redes sociais: aprendizado com deploys

```text
Escreva um post para o LinkedIn, em primeira pessoa, a partir deste relato de uma coordenadora: nossa equipe criou um checklist de revisão de deploy. Nas quatro semanas anteriores, tivemos 28 deploys e 12 rollbacks; nas quatro semanas seguintes, foram 35 deploys e três rollbacks. A mediana do tempo de deploy passou de 30 para 18 minutos. Não houve grupo de controle nem registro de outras mudanças na equipe. Quero compartilhar o que aprendemos com essa experiência.
```

### 22. Redes sociais: roteiro sobre senhas

```text
Crie um roteiro para um vídeo educativo de cerca de um minuto explicando por que um serviço não deve guardar senhas em texto aberto. Aborde a diferença entre hash e criptografia reversível, a função do salt individual e a importância de usar uma função própria para senhas, com processamento deliberadamente caro. Inclua sugestões visuais para acompanhar a fala.
```

### 23. Literário: conto na oficina

```text
Escreva um conto curto em primeira pessoa, narrado por uma aprendiz de relojoaria. No último atendimento antes de fechar a oficina, ela encontra dentro de um relógio parado um bilhete sem assinatura: "não acerte a hora". A cliente volta para buscar o relógio antes do fechamento. Deixe o final aberto.
```

### 24. Literário: crônica na lavanderia

```text
Escreva uma crônica em primeira pessoa sobre uma manhã em uma lavanderia de bairro. A atendente anota no recibo uma meia sem par que não pertence ao narrador. Explore esse pequeno desencontro com humor discreto.
```
