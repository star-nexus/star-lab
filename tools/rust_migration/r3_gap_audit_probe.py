"""Adversarial compatibility audit; a reproduced difference is not a passed migration gate."""
import argparse
import datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import sys
from unittest.mock import patch
from r3_observations_probe import git


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--expect-numeric-equivalence',action='store_true')
    parser.add_argument('--expect-text-order',action='store_true')
    parser.add_argument('--extended-text-audit',action='store_true')
    args=parser.parse_args();source=args.source.resolve();output=args.output.resolve()
    os.chdir(source);sys.path.insert(0,str(source));os.environ['SDL_VIDEODRIVER']='dummy'
    from star_native import API_VERSION,_native
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.tests.test_native_vision import make_vision_world
    from rotk_env.systems.llm_system import LLMSystem
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,9,12,12)
    cases=[]
    specs=[('mapping_evidence',[('strategy_ping',dict(faction='wei',score=.5,evidence={'z':1,'a':2}))]),
           ('unicode_score',[('strategy_ping',dict(faction='wei',score='０.５'))]),
           ('unicode_counter',[('report_llm_stats',dict(faction='wei',api_stats=dict(total_calls='１２',successful_calls=1))),('report_llm_stats',dict(faction='wei',api_stats=dict(total_calls=2,successful_calls=1)))])]
    if args.extended_text_audit:
        specs += [
            ('nested_mapping_evidence',[('strategy_ping',dict(faction='wei',score=.5,evidence={'z':[{'y':None,'b':True}],'a':False}))]),
            ('stored_mapping_labels',[('report_llm_stats',dict(faction='wei',api_stats={},provider={'z':1,'a':2},model_id=[{'y':1,'b':2}])),('report_llm_stats',dict(faction='wei',api_stats={},provider='next',model_id='next'))]),
            ('float_text',[('strategy_ping',dict(faction='wei',score=.5,evidence=[1e-7]))]),
            ('nonprintable_text',[('strategy_ping',dict(faction='wei',score=.5,evidence=['\u00a0']))]),
        ]
    with patch('time.time',return_value=1720000000.),patch('datetime.datetime',Frozen):
        for name,actions in specs:
            world,_,_=make_vision_world('none');llm=LLMSystem();world.add_system(llm)
            try:
                initial=export_initial_state(world)
                with RustRuntime(initial) as runtime:
                    steps=[]
                    for action,params in [('register_agent_info',dict(faction='wei',provider='synthetic',model_id='fake',base_url='http://local'))]+actions:
                        expected=llm._process_action_request(agent_id='a',action_id=0,action=action,params=dict(params),send_response=False)
                        actual=runtime.execute_action(action,params,agent_id='a')
                        py_state=export_initial_state(world);rs_state=runtime.export_state()
                        steps.append(dict(action=action,parameters=params,python=expected,rust=actual,python_state=py_state,rust_state=rs_state,response_equal=actual==json.loads(json.dumps(expected)),state_equal=rs_state==py_state))
                    expected_equal = (True if name == 'float_text' else args.expect_numeric_equivalence if name.startswith('unicode_')
                                      else args.expect_text_order if name in ('mapping_evidence','nested_mapping_evidence','stored_mapping_labels')
                                      else False)
                    assert steps[-1]['state_equal'] == expected_equal, (name, steps[-1]['state_equal'], expected_equal)
                    cases.append(dict(name=name,initial=initial,steps=steps))
            finally:world.reset()
    output.mkdir(parents=True,exist_ok=True);raw=json.dumps(cases,ensure_ascii=False,separators=(',',':')).encode();path=output/'raw.json.xz';path.write_bytes(lzma.compress(raw))
    result=dict(source_sha=git(source,'rev-parse','HEAD'),source_dirty=git(source,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),api=API_VERSION,extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),migration_gate_passed=False,diagnostic_reproduced=True,numeric_fix_expected=args.expect_numeric_equivalence,text_order_fix_expected=args.expect_text_order,extended_text_audit=args.extended_text_audit,cases=[dict(name=c['name'],response_equal=c['steps'][-1]['response_equal'],state_equal=c['steps'][-1]['state_equal'],python_stats=c['steps'][-1]['python_state']['singletons']['GameStats'],rust_stats=c['steps'][-1]['rust_state']['singletons']['GameStats']) for c in cases],raw=dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,decoded_sha256=hashlib.sha256(raw).hexdigest(),decoded_bytes=len(raw)))
    assert not result['source_dirty']
    (output/'compact.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(diagnostic_reproduced=True,cases=len(cases))))


if __name__=='__main__':main()
