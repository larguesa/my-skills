# Jornalístico: notícia sobre bibliotecas

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Prompt literal

```text
Redija uma notícia curta para um portal local. A Prefeitura de Vila Clara anunciou em 1º de outubro de 2026 a abertura de 1.200 vagas gratuitas em oficinas de leitura nas seis bibliotecas municipais. As inscrições vão de 5 a 16 de outubro, presencialmente nas bibliotecas, para pessoas a partir de 12 anos. As oficinas começam em 3 de novembro. Os horários e a distribuição das vagas por unidade ainda não foram divulgados.
```

## Comparação completa

| Modelo / modo | Baseline | Skill 0.8.0 | Jev | Astra | Opus |
|---|---|---|---|---|---|
| anthropic/claude-opus-5.5 / on | <pre>&#42;&#42;Vila Clara abre 1&#46;200 vagas gratuitas em oficinas de leitura nas bibliotecas municipais&#42;&#42;&#10;&#10;&#42;Inscrições vão de 5 a 16 de outubro e devem ser feitas presencialmente&#46; Podem participar pessoas a partir de 12 anos&#46;&#42;&#10;&#10;A Prefeitura de Vila Clara anunciou nesta quarta&#45;feira &#40;1º&#41; a abertura de 1&#46;200 vagas gratuitas em oficinas de leitura&#46; As atividades serão realizadas nas seis bibliotecas municipais da cidade&#46;&#10;&#10;As inscrições começam na próxima segunda&#45;feira &#40;5&#41; e seguem até 16 de outubro&#46; Elas devem ser feitas presencialmente&#44; em qualquer uma das bibliotecas participantes&#46; As oficinas são abertas a pessoas a partir de 12 anos&#46;&#10;&#10;As aulas começam em 3 de novembro&#46;&#10;&#10;Os horários das oficinas e a distribuição das vagas entre as unidades ainda não foram divulgados pela Prefeitura&#46; O portal acompanhará o tema e publicará as informações assim que forem anunciadas&#46;&#10;&#10;&#45;&#45;&#45;&#10;&#10;&#42;&#42;Serviço&#42;&#42;&#10;&#42;&#42;O quê&#58;&#42;&#42; oficinas gratuitas de leitura&#10;&#42;&#42;Vagas&#58;&#42;&#42; 1&#46;200&#44; distribuídas nas seis bibliotecas municipais&#10;&#42;&#42;Inscrições&#58;&#42;&#42; de 5 a 16 de outubro&#44; presencialmente nas bibliotecas&#10;&#42;&#42;Público&#58;&#42;&#42; pessoas a partir de 12 anos&#10;&#42;&#42;Início das oficinas&#58;&#42;&#42; 3 de novembro&#10;&#42;&#42;Horários e vagas por unidade&#58;&#42;&#42; a divulgar</pre><br>[UTF-8 literal](outputs/r00-baseline.txt); completed; USD 0.01248; 6.802s; tokens entrada/saída 190/586 | <pre>&#35; Vila Clara abre 1&#46;200 vagas gratuitas em oficinas de leitura nas bibliotecas municipais&#10;&#10;&#42;&#42;Inscrições vão de 5 a 16 de outubro&#44; presencialmente&#44; para quem tem a partir de 12 anos&#42;&#42;&#10;&#10;A Prefeitura de Vila Clara anunciou em 1º de outubro a abertura de 1&#46;200 vagas gratuitas em oficinas de leitura nas seis bibliotecas municipais&#46; As aulas começam em 3 de novembro&#46;&#10;&#10;Podem se inscrever pessoas a partir de 12 anos&#46; A inscrição é feita presencialmente&#44; nas próprias bibliotecas&#44; entre 5 e 16 de outubro&#46;&#10;&#10;A prefeitura ainda não divulgou os horários das oficinas nem quantas vagas cada unidade vai oferecer&#46;&#10;&#10;&#42;&#42;Serviço&#42;&#42;&#10;Oficinas de leitura nas bibliotecas municipais de Vila Clara&#10;Vagas&#58; 1&#46;200&#44; gratuitas&#10;Público&#58; a partir de 12 anos&#10;Inscrições&#58; de 5 a 16 de outubro&#44; presencialmente nas bibliotecas&#10;Início das oficinas&#58; 3 de novembro</pre><br>[UTF-8 literal](outputs/r00-skill.txt); completed; USD 0.0565; 11.225s; tokens entrada/saída 8490/1127 | Impressão B/S 61.00/62.00; qualidade B/S 90.31/89.69; preferência: baseline; crítico B/S False/False; Justificativa indisponível em Decisions / Justificativa indisponível em Decisions | Impressão B/S 80.00/65.00; qualidade B/S 85.00/94.75; preferência: skill; crítico B/S False/False; Preserva os dados principais e as ressalvas, mas identifica incorretamente 1º de outubro de 2026 como quarta-feira: era quinta-feira. Também omite o ano e acrescenta compromisso editorial do portal sem respaldo na base. Repetições e esse acréscimo prejudicam a concisão. / Notícia clara, com título informativo e preservação dos dados e das informações ainda não divulgadas. Omite o ano de 2026 e repete informações no quadro de serviço, mas atende bem ao gênero e à brevidade solicitada. | Impressão B/S 50.00/45.00; qualidade B/S 83.00/89.00; preferência: skill; crítico B/S False/False; O texto tem bom estilo jornalístico e mantém a ressalva, que também aparece no serviço como &#x27;a divulgar&#x27;. Porém afirma que 1º de outubro de 2026 é quarta-feira, quando o dia cai numa quinta-feira; a segunda-feira (5) está correta. Também acrescenta o compromisso de acompanhamento do portal e a expressão &#x27;qualquer uma das bibliotecas&#x27;, que não constam da base. São erros periféricos, não centrais. / A notícia é fiel a todos os dados: vagas, gratuidade, seis bibliotecas, período e forma de inscrição, idade mínima, data de início e a ressalva sobre horários e distribuição por unidade. O texto é enxuto e claro, com um bloco de serviço útil. A redação é algo seca e omite o ano 2026, o que tem impacto mínimo. |
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
