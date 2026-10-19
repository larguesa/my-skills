# Comunicação profissional: indisponibilidade

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Prompt literal

```text
Redija um comunicado aos clientes do Painel Aurora sobre a indisponibilidade de acesso em 1º de outubro de 2026, das 14h10 às 14h42, no fuso UTC-3. O serviço foi restabelecido às 14h42. A causa está em investigação. Até o momento, nenhuma perda de dados foi confirmada, mas a análise dos registros ainda não terminou. A próxima atualização está prevista para 2 de outubro, às 12h, no mesmo fuso.
```

## Comparação completa

| Modelo / modo | Baseline | Skill 0.7.0 | Jev | Astra | Opus |
|---|---|---|---|---|---|
| anthropic/claude-opus-5.5 / on | <pre>&#42;&#42;Assunto&#58;&#42;&#42; Indisponibilidade de acesso ao Painel Aurora em 1º de outubro de 2026&#10;&#10;Prezado&#40;a&#41; cliente&#44;&#10;&#10;Em 1º de outubro de 2026&#44; entre &#42;&#42;14h10 e 14h42 &#40;UTC&#45;3&#41;&#42;&#42;&#44; o acesso ao Painel Aurora ficou indisponível por cerca de 32 minutos&#46; O serviço foi restabelecido às 14h42&#46;&#10;&#10;&#42;&#42;O que sabemos até o momento&#42;&#42;&#10;&#10;&#45; &#42;&#42;Causa&#58;&#42;&#42; está em investigação&#46; Nossa equipe técnica trabalha para identificá&#45;la&#46;&#10;&#45; &#42;&#42;Dados&#58;&#42;&#42; até agora&#44; nenhuma perda de dados foi confirmada&#46; A análise dos registros&#44; porém&#44; ainda não terminou&#46; Só poderemos apresentar uma conclusão definitiva quando ela for concluída&#46;&#10;&#10;&#42;&#42;Próxima atualização&#42;&#42;&#10;&#10;Publicaremos uma nova atualização em &#42;&#42;2 de outubro de 2026&#44; às 12h &#40;UTC&#45;3&#41;&#42;&#42;&#46; Se houver novidades relevantes antes disso&#44; informaremos imediatamente&#46;&#10;&#10;&#42;&#42;Se notar algo incomum&#42;&#42;&#10;&#10;Caso perceba alguma inconsistência nas suas informações ou no funcionamento do Painel Aurora&#44; entre em contato com nosso suporte pelo &#91;canal de atendimento&#93;&#46; Indique&#44; se possível&#44; o horário e uma breve descrição do que observou&#46; Esses detalhes ajudarão nossa investigação&#46;&#10;&#10;Pedimos desculpas pelo transtorno e agradecemos a sua compreensão&#46;&#10;&#10;Atenciosamente&#44;&#10;Equipe Painel Aurora&#10;&#91;Contato de suporte&#93;</pre><br>[UTF-8 literal](outputs/r00-baseline.txt); completed; USD 0.021296; 9.829s; tokens entrada/saída 179/1029 | <pre>&#42;&#42;Assunto&#58; Indisponibilidade de acesso ao Painel Aurora em 1º de outubro de 2026&#42;&#42;&#10;&#10;Prezados clientes&#44;&#10;&#10;O acesso ao Painel Aurora foi restabelecido às 14h42 de 1º de outubro de 2026&#44; no fuso UTC&#45;3&#46; O serviço estava indisponível desde as 14h10 do mesmo dia&#46;&#10;&#10;A causa da falha ainda está em investigação&#46;&#10;&#10;Até o momento&#44; não confirmamos perda de dados&#46; A análise dos registros&#44; porém&#44; ainda não terminou&#46; Por isso&#44; a falta de confirmação não permite afirmar que nenhum dado foi perdido&#46;&#10;&#10;A próxima atualização está prevista para 2 de outubro de 2026&#44; às 12h &#40;UTC&#45;3&#41;&#46;&#10;&#10;Equipe do Painel Aurora</pre><br>[UTF-8 literal](outputs/r00-skill.txt); completed; USD 0.053048; 14.050s; tokens entrada/saída 7202/1212 | Impressão B/S 73.00/64.00; qualidade B/S 93.31/78.88; preferência: baseline; crítico B/S False/False; Justificativa indisponível em Decisions / Justificativa indisponível em Decisions | Impressão B/S 85.00/55.00; qualidade B/S 84.50/97.25; preferência: skill; crítico B/S False/False; Preserva os fatos centrais e organiza bem as informações, mas amplia desnecessariamente o comunicado e deixa campos de suporte sem preencher. Transforma a atualização prevista em compromisso firme e acrescenta promessa de comunicação imediata não fornecida no pedido. / Comunicado direto, profissional e completo, com datas, horários, fuso e ressalvas preservados. A explicação adicional sobre a ausência de confirmação de perda é fiel, embora ligeiramente redundante. | Impressão B/S 62.00/50.00; qualidade B/S 84.75/79.25; preferência: baseline; crítico B/S False/False; É completo e bem organizado, com duração de 32 minutos calculada corretamente e ressalva sobre dados preservada. Inclui pedido de desculpas e orientação ao cliente. Assume, porém, o compromisso não fornecido de atualizar antes do prazo se houver novidades. Os placeholders de contato ficaram pendentes, e as seções em negrito deixam o texto algo padronizado. / Preserva com fidelidade todos os fatos: horários, fuso, causa em investigação, ressalva sobre dados e próxima atualização. A frase sobre a falta de confirmação soa redundante e pouco natural. Como comunicado a clientes, fica seco: não pede desculpas e não indica canal de contato. |
| openai/gpt-6-astra / on | <pre>&#42;&#42;Comunicado &#8212; Indisponibilidade do Painel Aurora&#42;&#42;&#10;&#10;Informamos que o acesso ao Painel Aurora ficou indisponível em &#42;&#42;1º de outubro de 2026&#44; das 14h10 às 14h42 &#40;UTC&#45;3&#41;&#42;&#42;&#46; O serviço foi restabelecido às 14h42&#46;&#10;&#10;A causa da indisponibilidade está em investigação&#46; Até o momento&#44; &#42;&#42;nenhuma perda de dados foi confirmada&#42;&#42;&#44; mas a análise dos registros ainda não foi concluída&#46;&#10;&#10;A próxima atualização está prevista para &#42;&#42;2 de outubro de 2026&#44; às 12h &#40;UTC&#45;3&#41;&#42;&#42;&#46;&#10;&#10;Pedimos desculpas pelos transtornos e agradecemos a compreensão&#46;</pre><br>[UTF-8 literal](outputs/r01-baseline.txt); completed; USD 0.00827; 4.072s; tokens entrada/saída 112/143 | <pre>&#35;&#35; Painel Aurora&#58; acesso restabelecido&#10;&#10;O acesso ao Painel Aurora foi restabelecido às 14h42 de 1º de outubro de 2026&#44; após indisponibilidade das 14h10 às 14h42 &#40;UTC&#45;3&#41;&#46;&#10;&#10;A causa está em investigação&#46; Até o momento&#44; nenhuma perda de dados foi confirmada&#44; mas a análise dos registros ainda não terminou&#46;&#10;&#10;A próxima atualização está prevista para 2 de outubro de 2026&#44; às 12h &#40;UTC&#45;3&#41;&#46;</pre><br>[UTF-8 literal](outputs/r01-skill.txt); completed; USD 0.0589925; 5.128s; tokens entrada/saída 4280/110 | PENDENTE | PENDENTE | PENDENTE |
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

Chamadas novas e independentes. Baseline recebe só o prompt literal; tratamento recebe SKILL.md 0.7.0 e o briefing local compacto congelado por caso. Nenhum texto de outro braço, preferência pessoal ou feedback de juiz entra nos candidatos.
Mapeamento anônimo e grupos de até quatro pares são congelados; grupo com candidato inválido fica sem julgamento, sem reagrupamento oportunista.
Modelos, modos e providers efetivos são os congelados, incluindo amendments explícitos. Aliases na resposta não comprovam a versão efetiva nem o uso do reasoning solicitado.
Juízes chat: máximo 16384 tokens histórico. Jev Decisions: payload nativo histórico sem max_tokens artificial. Agregado de qualidade: média das quatro dimensões; erro crítico limita correção a 25 e total a 49, preservando notas brutas.

[Resumo agregado](../../SUMMARY.md)
