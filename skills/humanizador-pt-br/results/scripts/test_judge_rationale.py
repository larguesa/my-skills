"""Offline contracts for prospective rationale guidance, not perception evidence."""
import importlib.util
import json
from pathlib import Path
import unittest

import eval_judges as judges

HERE = Path(__file__).resolve().parent


class RationaleContractTests(unittest.TestCase):
    def test_prospective_prompt_requests_evidence_per_text(self):
        self.assertEqual(getattr(judges, 'RATIONALE_VERSION', None), '2')
        for fragment in (
            'Características não-humanizadas:',
            'lista numerada',
            'trecho literal',
            'gênero e pedido',
            'Nenhuma característica identificada',
            'Qualidade e fidelidade:',
            'Não invente defeitos',
            'não bastam isoladamente',
        ):
            self.assertIn(fragment, judges.JUDGE)
        self.assertIn('justificativa:string', judges.JUDGE)
        self.assertIn('Não gere versões novas', judges.JUDGE)

    def test_runner_injects_guidance_only_into_chat_judges(self):
        import generation_eval as runner
        frozen = HERE / 'fixtures/evidence-2026-10-13/frozen'
        config = json.loads((frozen / 'config.json').read_text())
        config['judge_rationale_version'] = '2'
        case = config['cases'][0]
        blind = runner.blind_case(config, case)
        tids = [tid for pid in blind['groups'][0] for tid in blind['pairs'][pid].values()]
        records = {blind['mapping'][tid]: (None, {'status':'completed', 'text':'Texto neutro ' + tid}) for tid in tids}
        calls, missing = runner.judge_calls(config, case, blind, 0, records)
        self.assertEqual(missing, [])
        self.assertEqual({c['judge'] for c in calls}, {'jev','astra','opus'})
        for call in calls:
            if call['judge'] == 'jev':
                self.assertEqual(call['payload'], judges.decisions_payload(call['judge_state']))
            else:
                self.assertEqual(call['payload']['messages'][0], {'role':'system','content':judges.JUDGE})
                self.assertIn('Características não-humanizadas:', call['payload']['messages'][0]['content'])

    def test_historical_json_contract_and_native_jev_remain_compatible(self):
        fixture = HERE / 'fixtures/evidence-2026-10-13'
        spec = importlib.util.spec_from_file_location('historical_judges', fixture / 'frozen/runner/eval_judges.py')
        historical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(historical)
        state = {'prompt':'Pedido neutro.', 'textos':{'t001':'Primeiro texto.', 't002':'Segundo texto.'}, 'pares':{'p001':{'A':'t001','B':'t002'}}}
        self.assertEqual(judges.JUDGE_V1, historical.JUDGE)
        self.assertEqual(judges.decisions_payload(state), historical.decisions_payload(state))
        payload = {'deteccao':{'t001':30,'t002':40}, 'preferencia':{'p001':'A'}, 'qualidade':{tid:dict(naturalidade=75,clareza=75,adequacao=75,correcao=75,critico=False,justificativa='Justificativa histórica.') for tid in state['textos']}}
        self.assertEqual(judges.validate_judge(payload,state), historical.validate_judge(payload,state))
        self.assertEqual(judges.DIMENSIONS, historical.DIMENSIONS)
        self.assertEqual(judges.ANCHORS, historical.ANCHORS)
        self.assertEqual(judges.CRITICAL, historical.CRITICAL)


if __name__ == '__main__':
    unittest.main()
