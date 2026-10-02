# Recuperação após rejeição de infraestrutura

A primeira execução parou na chamada com ID `3c38de91189e45fb547df22e8d10224e17eb124b83b9dc7f2be063f13dada758`, do braço com skill de MiMo Flash sem raciocínio no primeiro caso.

A API devolveu HTTP 429, com `engine_overloaded` e `upstream_provider_shared_pool`. Não devolveu texto nem uso de tokens. Isso não é uma resposta de candidato nem evidência de qualidade ruim do modelo. O registro bruto da rejeição é preservado.

Após a interrupção, a leitura da chave exclusiva apresentou US$ 0.613382394, exatamente a soma das 26 respostas precificadas e das 20 sondagens. A consulta ao identificador de geração fornecido no cabeçalho devolveu 404. O 404 sozinho não prova ausência de cobrança; a conciliação da chave é a evidência contábil utilizada. A leitura será repetida antes da recuperação.

## Emenda operacional

Não haverá nova tentativa dessa posição, mudança de rota, aumento de limite ou edição de resposta. Após confirmação da conciliação, a posição rejeitada será reclassificada como `invalid_response`, com custo atribuído pela conciliação, não como custo informado pela API. A cópia original, seu hash e a evidência contábil ficam separados. Isso desbloqueia somente posições ainda não iniciadas no plano original. Todas as respostas válidas permanecem byte a byte iguais.

Qualquer nova rejeição ou falha de transporte volta a interromper a execução. Sua classificação depende de inspeção e conciliação próprias; não há repetição automática nem classificação automática como gratuita. O estudo final deve informar esta intervenção e manter explícitas as posições sem texto e os julgamentos ausentes. A skill, os prompts, os parâmetros e o código congelado do runner não são alterados.
