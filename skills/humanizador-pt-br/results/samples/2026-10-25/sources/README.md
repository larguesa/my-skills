# Fontes congeladas da comparação

Código, pedidos, payloads, configurações, mapa cego, ordem de execução e
briefings locais são cópias byte a byte dos inputs usados na comparação.
A dependência `runner/fixtures/history.json` está incluída.

Este pacote contém os inputs, não as respostas ou notas. Os resultados estão
no [relatório](../report/README.md).

## Proveniência e privacidade

O manifesto original está preservado em `provenance/PRIVATE-MANIFEST.json`,
com SHA-256 `bbb79d9988b10343e0e3ec0a50fc6c1a08d2f517a9efce6fcdd3faf92083db19`.
O `manifest.json` desta pasta é uma projeção derivada, com hashes recalculados.
Os dois manifestos têm hashes diferentes.

Os registros de pré-flight, que não participam da geração dos payloads,
foram substituídos por registros explícitos de omissão contendo o hash original.
Não são respostas de API. HTTP bruto e dados de conta ficaram fora do pacote.
Consulte a [comparação de hashes](provenance/SOURCE-PUBLIC-HASHES.json),
as [omissões](provenance/OMISSIONS.json), o [inventário](PACKAGE-INVENTORY.json),
o [protocolo](docs/PROTOCOL.md) e a [emenda](docs/PROTOCOL-AMENDMENT.md).

Os campos `paid_calls: 0` e `frozen_at` descrevem o congelamento anterior às
chamadas, não o encerramento do estudo. Esta projeção não substitui o registro
privado para retomada de chamadas.

## Verificação local, sem inferência

Após conferir o código de `runner/` e seus hashes, execute nesta pasta:

```sh
sha256sum -c SHA256SUMS
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runner python3 -B -c 'import sample_eval; c=sample_eval.load_frozen("."); print("load_frozen OK; casos:", len(c["cases"]))'
```

O carregador confere a integridade dos inputs e a correspondência dos planos
com os payloads. A cobertura e os resultados editoriais constam do relatório.
