# Operação no Hermes

Leia antes de instalar ou adaptar uma skill ao Hermes. A documentação oficial vigente é a fonte de verdade; confirme o schema das ferramentas e a versão instalada antes de executar comandos.

## Autoria pessoal

1. Confirme o perfil ativo. Não altere skills de outro perfil sem autorização explícita.
2. Use `skill_manage` para criar ou atualizar skills pessoais. Na API disponível nesta entrega, as mudanças são uma lista `operations` e arquivos de apoio ficam em `references/`, `templates/`, `scripts/` ou `assets/`.
3. Para uma skill em repositório, use as ferramentas de arquivo no checkout e siga os padrões daquele projeto. Não confunda esse destino com a pasta pessoal de skills.
4. Leia arquivos existentes antes de reescrevê-los; para ajustes localizados, prefira patch. Preserve o nome ao atualizar e guarde a revisão usada como baseline fora do pacote final.
5. Resolva o diretório da skill pelo resultado da ferramenta ou pelo perfil ativo. Não coloque caminhos pessoais fixos em um pacote reutilizável.

## Metadados e ferramentas

- Exija `name` e `description`; use nome de diretório coerente.
- Neste catálogo, use descrição de até 60 caracteres, começando pela situação de uso. É uma convenção local mais restrita que o limite geral de Agent Skills.
- Declare `platforms` somente depois de auditar os comandos. Prosa portável não torna um script com chamadas POSIX compatível com Windows.
- Configure filtros em `metadata.hermes` apenas quando necessários. Exigir uma ferramenta errada pode ocultar a skill inteira.
- Declare variáveis necessárias por nome e finalidade; use a fonte de segredos configurada e não grave valores no pacote.
- Cite as ferramentas realmente disponíveis, como `terminal`, `read_file`, `search_files`, `patch` e `skill_manage`. Não invente comandos ou flags.
- O indicador de disponibilidade não substitui um teste real do executável ou da API.

## Instalação e comprovação

1. Valide os arquivos antes de instalar. Use o perfil `hermes` do auxiliar para checagens locais.
2. Após alteração autorizada, confirme os arquivos do destino e o reconhecimento pelo carregador disponível. Recarregar ou abrir nova sessão pode ser necessário conforme a versão; não reinicie serviços sem necessidade.
3. Teste descoberta espontânea separadamente de carregar a skill pelo nome. Carregamento explícito prova acesso, não seleção automática.
4. Para compartilhamento com outro agente, remova ou adapte extensões Hermes segundo a documentação do destino; não passe o perfil Hermes como certificado de portabilidade.

## Fonte

Nous Research, Creating Skills, consulta em 11/11/2026:
https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills

Revisão fixada na comparação original, `57cc40f4699fec61361780a6e6836068eff271a2`:
https://github.com/NousResearch/hermes-agent/blob/57cc40f4699fec61361780a6e6836068eff271a2/website/docs/developer-guide/creating-skills.md

Este arquivo é uma síntese operacional, com convenções locais identificadas como locais.
