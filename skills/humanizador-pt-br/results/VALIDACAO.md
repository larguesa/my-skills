# Validação local do Humanizador PT-BR 0.4.0

Validação funcional offline, não benchmark de naturalidade ou autoria.

## Execução

Na raiz do repositório:

```text
python3 -W error skills/humanizador-pt-br/results/test_humanizar.py
```

Resultado observado: 37 testes, OK, sem falhas ou avisos. O baseline recuperado do histórico passou nos 15 testes anteriores. Os ciclos de desenvolvimento observaram falhas antes das implementações de busca, estrutura, controles, aleatoriedade, substituição e ritmo.

Verificação adicional: 12 comandos publicados na skill/README executados com retorno JSON válido; 63 combinações de perfil, gênero e abrangência verificadas quanto a seed, ordem e preservação dos obrigatórios. Links relativos válidos, IDs de fontes resolvidos e original de entrada intacto. Uma segunda execução integral, em cópia temporária da pasta e fora do repositório, também passou nos 37 testes.

## Cobertura

- Busca por ID, instrução, palavra, exemplo e exceção; consulta sem acento/maiúsculas, limite validado e gênero exato. O teste PTBR-17 cobre palavras completas e exclamações, sem confundir `IA` com o início de `iate`.
- Desempenho local: um plano com 100 substituições em 4.200 caracteres levou 0,285 s após remover cálculos de diferenças desnecessários (30,648 s antes dessa otimização). A saída aprovada permaneceu exata e o teste tem limite de 10 s. São observações desta execução, não garantia geral de latência.
- Catálogo com 26 regras, 9 perfis e 10 estruturas. Todos os perfis/gêneros e referências de estrutura são exercitados.
- Planos reproduzíveis por seed, gerador local, ordem lógica e instruções obrigatórias preservadas; abrangência altera somente blocos opcionais.
- Substituição literal, limites Unicode, plano não aprovado, hash, offsets, sobreposição e aprovação explícita.
- Proteção conservadora de código, citações, URLs, números, nomes e condições; termos/unidades adicionais por `--protect`.
- Destino novo, original intacto, round-trip UTF-8/CRLF e erros de CLI sem traceback.
- Ritmo descritivo, texto vazio, separadores numéricos e ausência de score/detector.
- Apenas biblioteca padrão; nenhuma chamada de benchmark ou API de geração.

## Documentação e fontes

- Os 24 pedidos aprovados permanecem literais em relação ao commit 71273ed; H1/H2 foram retirados.
- Skill principal: 7603 para 6187 caracteres (18.6% menor), com regras explícitas e chamadas de script.
- Fontes compiladas: 8619 para 7838 caracteres (9.1% menor), preservando origens e limites específicos.
- 13 fontes documentadas, 14 URLs citadas verificadas no registro HTTP; integridade conferida em 50 registros de pesquisa por SHA256. Repositórios/card e artigos têm revisões ou versões fixadas quando disponíveis.

## Limites

Os testes não medem qualidade literária, compreensão, preferência de leitores ou melhoria sobre outra condição. `rhythm` é segmentação aproximada e inclui citações/código; `verify` não reconhece toda entidade nem prova equivalência semântica. Proteções podem recusar uma edição legítima; não devem ser contornadas. Substituições exigem leitura contextual, inclusive ao remover um travessão.

A nova avaliação com modelos continua pendente de aprovação da skill e do protocolo. Não há resultado novo, custo medido ou ganho declarado dessa avaliação.
