"""Record the R0 skill-list ordering omission and R0b correction across hash seeds."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

CODE = '''
import json
from rotk_env.components import UnitSkills
from rotk_env.prefabs.config import Faction
from rotk_env.systems.llm_action_handler import LLMActionHandler
from rotk_env.tests.test_faction_state_affordances import _world, _spawn
world = _world()
uid = _spawn(world, faction=Faction.WEI, col=0, row=0)
world.add_component(uid, UnitSkills(available_skills={'hide','charge','rockslide','arrow_evasion'}))
print(json.dumps(LLMActionHandler(world)._get_detailed_unit_info(uid)['available_skills']))
'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',type=Path,required=True)
    p.add_argument('--after',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();cases=[]
    for label,path in [('before',a.before),('after',a.after)]:
        path=path.resolve()
        records=[]
        for seed in ('1','99'):
            result=subprocess.check_output([sys.executable,'-c',CODE],cwd=path,
                                           env={**os.environ,'PYTHONHASHSEED':seed},text=True)
            records.append(dict(hash_seed=seed,skills=json.loads(result.splitlines()[-1])))
        cases.append(dict(label=label,source_sha=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip(),
                          clean=not subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True).strip(),records=records))
    raw=dict(schema='star-oracle-skill-order-v1',python=sys.version,
             tool_sha=subprocess.check_output(['git','-C',str(Path(__file__).parents[2]),'rev-parse','HEAD'],text=True).strip(),cases=cases)
    before,after=cases
    raw['guards']=dict(before_not_stable=before['records'][0]['skills']!=before['records'][1]['skills'],
                       after_sorted=all(r['skills']==['arrow_evasion','charge','hide','rockslide'] for r in after['records']),
                       clean_checkouts=all(c['clean'] for c in cases))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(raw,indent=2)+'\n');print(json.dumps(raw,indent=2))
    if not all(raw['guards'].values()):raise SystemExit(1)

if __name__=='__main__':main()
