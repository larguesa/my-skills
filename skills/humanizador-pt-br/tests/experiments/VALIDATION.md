# Validação da preparação

## Resultado executado

| Verificação | Resultado |
|---|---|
| Suíte offline do pacote | ✅ 48 testes aprovados |
| Relatórios por pedido | ✅ 26 arquivos: dois com resultados reais e 24 preparados |
| Cobertura nova | ✅ 12 gêneros, dois pedidos por gênero |
| Preservação da rodada histórica | ✅ 76 gerações únicas e 38 pares completos, com três juízes separados |
| Tabelas completas dos dois contos | ✅ 19 linhas por relatório, com textos, três juízes, custos e tempos |
| Posições da matriz nova | ⏸️ 456 linhas pendentes, sem respostas ou notas inventadas |
| Links locais do índice e dos relatórios | ✅ nenhum destino ausente |
| Segurança estática do diff Python | ✅ nenhum segredo fixo, shell inseguro, eval/exec ou pickle encontrado |
| Chamada paga durante a preparação | ✅ nenhuma chamada de geração ou julgamento ao OpenRouter |
| Avaliação de qualidade dos novos textos | ⏸️ não realizada, não existem textos novos ainda |

A cobertura foi conferida por contagem programática, comparação das células com os registros originais e reconstrução determinística dos relatórios. O teste de publicação offline bloqueia acesso de rede enquanto renderiza os 26 relatórios em uma pasta temporária.

A suíte original tinha 43 testes aprovados antes da alteração. Os cinco testes adicionados tiveram falha observada antes da implementação e passaram depois: preservação dos pares por experimento, rejeição de IDs duplicados/fora do formato, publicação offline dos relatórios, preservação literal de HTML e código nos pedidos e coerência do critério de CTA com o pedido do caso LinkedIn.

`SKILL.md`, respostas brutas, mapas anônimos, julgamentos, congelamento e relatório histórico não foram modificados. O histórico não foi reexecutado para preencher a estrutura nova. O manifesto desta pasta registra a preparação, não um congelamento final de execução paga.

## Repetir as verificações

Na raiz do repositório:

```text
python3 -m unittest discover -s skills/humanizador-pt-br/tests -p 'test_*.py' -v
python3 skills/humanizador-pt-br/tests/scripts/relatorio.py --experiments
git diff --check
```

Essas verificações avaliam software, organização e fidelidade das evidências preservadas. Não comprovam naturalidade, eficácia geral, autoria humana ou correção dos futuros textos técnicos.

[Voltar ao índice](../README.md)
