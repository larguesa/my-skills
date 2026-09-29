# Protocolo editorial e avaliação

## Estado e separação de evidências

Implementados nesta camada: procedimento textual, catálogo rastreável de heurísticas e contrato de variação editorial. Testes de utilitários verificam comportamento de software, não naturalidade, autoria ou validade de uma hipótese linguística. Exploração de dados em `exploracao-amostral.json` é descritiva. Calibração empírica das regras permanece pendente.

Distinguir sempre: (1) regra proposta; (2) regex executada; (3) ocorrência contextual confirmada; (4) edição aprovada; (5) ganho editorial observado em avaliação. Nenhuma etapa implica automaticamente a seguinte.

## Uso em um documento

1. Guardar original e hash, autorização, gênero, público e restrições.
2. Inventariar afirmações e seus limites: sujeito, ação, objeto, condição, tempo, negação, modalidade, causalidade e fonte.
3. Produzir achados com ID, trecho, posição e contexto. Incluir exceções aplicáveis e risco, não apenas contagem.
4. Propor alterações localizadas. Manter a alternativa de não editar. Fonte vaga exige consulta, não uma referência fabricada.
5. Aplicar apenas alterações explicitamente autorizadas. Regra não concede permissão de edição. Não sobrescrever silenciosamente.
6. Comparar original e final com revisão semântica, além de retenção de números, datas, URLs, nomes e unidades.
7. Entregar texto, diff ou resumo suficiente de alterações, preservações e dúvidas. Publicação é autorização separada.

## Três braços comparáveis

- **Simples:** instrução curta para melhorar clareza preservando fatos e voz, sem carregar catálogo ou relatório.
- **Textual:** mesmo texto, orçamento e objetivo, com SKILL e referências editoriais, sem resultados de script.
- **Assistido por scripts:** mesma base textual, acrescida da auditoria local compacta produzida antes da chamada. Os perfis editoriais integram igualmente os dois braços com skill; o benchmark não executa `suggest`, aplicação de edições ou um ciclo de correção pós-resposta. O editor oferece essas operações separadamente. Scripts não redigem nem autorizam substituições por conta própria.

Registrar prompt integral, versão da skill e catálogo, modelo e provedor exatos, parâmetros disponíveis, seed quando suportada, entradas e saídas, falhas, tentativas, tokens, latência e custo observado. Não declarar custo zero por ausência de cobrança visível. Se o provedor não expuser custo final, marcar desconhecido.

Parear os braços pelo mesmo texto-fonte. Fixar critérios e conjunto de avaliação antes de observar resultados; não escolher vencedor pela menor contagem de gatilhos. Falhas de preservação factual eliminam a versão, mesmo que seja preferida estilisticamente.

## Amostragem e proveniência

Antes de ampliar um corpus, conferir direitos e disponibilidade. Registrar dataset, revisão, arquivo/configuração/split, índice ou ID, classe declarada, fonte, data, gênero, tamanho e método de seleção. Registrar modelo, prompt, versão original e ID de grupo quando existentes; usar nulo ou desconhecido quando ausentes.

Separar conjuntos por fonte original, não por linha aleatória. Artigo humano, reescritas, traduções e gerações a partir do mesmo conteúdo pertencem ao mesmo grupo. Se identidade de fonte estiver ausente, não afirmar independência. Usar hashes para duplicatas exatas e agrupamento por n-gramas ou similaridade para quase duplicatas, com limiar documentado e inspeção manual. Manter os grupos inteiros numa única partição.

Controlar gênero, tema, veículo/domínio, período, tamanho e qualidade de extração. Modelo e pipeline são estratos, não sinônimos de autoria. Reservar fontes e modelos não vistos para teste de generalização quando viável. Não ajustar padrões ou limiares olhando o teste final.

Amostra de conveniência de preview não representa o corpus. Sem grupo sintético comparável, não calcular excesso relativo ou razão entre classes. Sem URLs de origem, não reconstruir autoria por suposição.

## Medidas descritivas

Relatar contagem bruta e denominador junto de qualquer frequência. Uma possibilidade explícita é `1000 * ocorrencias / palavras`, com tokenizador documentado; reportar também documentos com pelo menos uma ocorrência e total de documentos. No denominador zero, frequência é indefinida, não zero. Contagens sobrepostas e múltiplas regras para o mesmo trecho precisam de convenção registrada.

Usar a mesma normalização Unicode e tokenização nos grupos. Preservar offsets e texto original para inspeção. A contagem de `word_count` fornecida pelo dataset pode divergir da recomputada: informar qual foi usada. Um valor por mil palavras não é probabilidade de autoria nem uma escala calibrada de naturalidade.

Para eventual análise comparativa, estimar incerteza com reamostragem por documento-fonte/grupo, não por ocorrência; examinar distribuição e fontes influentes. Definir previamente comparações e tratar multiplicidade. Não transformar frequência alta em proibição nem baixa em autorização estilística.

## Julgamento editorial

Revisão cega com ordem contrabalançada e identificação de braço oculta. Julgadores recebem original, finalidade e referência de voz autorizada. Avaliam separadamente:

- Preservação integral de fatos, condições, negações e grau de certeza.
- Clareza e utilidade para aquele leitor.
- Adequação à voz, gênero e função do trecho.
- Fluência sem ornamentação ou informalidade imposta.
- Alterações desnecessárias e perdas de informação.

Permitir empate e rejeição de ambas as versões. Registrar discordâncias e razões concretas. Juiz LLM é auxiliar, com prompt e versão registrados, não árbitro de autoria nem substituto de leitor competente. Exemplos humanos de qualidade ajudam a aferir se a rubrica recompensa o trabalho desejado; não presumir que toda referência humana seja superior por origem.

A pesquisa Meta RAM motiva conferir seleção e função da seção, em vez de premiar cobertura máxima. Não se executa RL-XAR neste pacote. Não alegar reprodução dos ganhos publicados.

## Critérios de promoção

Uma heurística só muda de status após amostra definida, revisão contextual, taxa de falsos positivos documentada, análise por gênero e teste separado. Exigir avaliação de termos técnicos legítimos, citações, texto curto e usos autorais. Relatar também casos em que não editar foi a melhor decisão.

Testes determinísticos de regex, preservação e CLI devem continuar separados dessa calibração. Não publicar ranking de modelos ou braços sem resultados reais e limitações. Piloto pequeno informa a próxima rodada, não estabelece superioridade geral.
