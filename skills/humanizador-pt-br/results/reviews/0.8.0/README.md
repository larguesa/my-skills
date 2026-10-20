# Revisões independentes da versão 0.7.0

Base comum: commit `4433074e32085320c9cebc8ebace67833e321f92`. Os três revisores receberam os mesmos sete arquivos completos: skill, README, script, catálogo, estilos, testes e revisão 0.7.0. As revisões foram independentes, sem acesso às respostas dos outros revisores.

| Revisor | Configuração | Relatório |
|---|---|---|
| Codex CLI 0.163.0 | `openai/gpt-6-astra`, `xhigh`, endpoint Responses do OpenRouter | [Resposta completa](codex.md) |
| Grok 4.7 | `x-ai/grok-4.7`, `xhigh`, máximo listado no catálogo da rota | [Resposta completa](grok.md) |
| MiMo 2.6 Pro | `xiaomi/mimo-v2.6-pro`, OpenRouter, raciocínio desativado na resposta completa | [Resposta completa](mimo.md) |

A primeira tentativa do MiMo, com raciocínio ativado, consumiu 32.768 tokens de raciocínio e terminou por limite, sem texto final. Foi preservada e contabilizada. A segunda tentativa produziu o relatório completo; o pedido não fixou esforço para esse revisor.

As três respostas completas foram concatenadas, sem resumo ou seleção prévia, no pedido de consolidação enviado ao Claude Code, `claude-opus-5-5`, esforço `max`. A comprovação dos hashes e da inclusão está em [provenance.json](provenance.json). Os [hashes dos arquivos revisados](source-hashes.json) identificam a base comum.

[Teste funcional, textos completos e consumo](SMOKE.md): 117 testes de software aprovados, 11 reproduções corrigidas e cinco textos completos, com problemas editoriais descritos no relatório. Um pedido de redação foi recusado pelo provedor.

Os relatórios registram os pareceres dos revisores, inclusive sugestões posteriormente rejeitadas. As decisões e a implementação ficam na [revisão consolidada 0.8.0](REVISAO.md). Apenas os links locais do parecer do Codex foram convertidos para links públicos fixados no commit original.
