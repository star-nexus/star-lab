"""E8 private local-host recording entry; does not change ordinary CLI defaults."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from admitted_observation_agents import AdmittedAgents, AdmittedLoopTrace, LAB
import p3_runtime
import rust_migration.native_loop_trace as recorder_module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--admission-mode',choices=['single','segment_no_reuse','segment_encoded'],required=True)
    p.add_argument('--admission-profile',action='store_true')
    p.add_argument('--admission-output',type=Path,required=True)
    a,runtime_args=p.parse_known_args();assert not a.admission_output.exists()
    assert '--record-native-inputs' in runtime_args and '--native-wire' in runtime_args
    instances=[]
    class Configured(AdmittedAgents):
        research_mode=a.admission_mode
        research_diagnostics=a.admission_profile
        def __init__(self,*args,**kw):
            super().__init__(*args,**kw);instances.append(self)
    p3_runtime.LocalAgents=Configured
    recorder_module.NativeLoopTrace=AdmittedLoopTrace
    sys.argv=[sys.argv[0],*runtime_args]
    meta=p3_runtime.main()
    meta['hardware'].pop('chrome',None)
    meta['hardware']['other_applications']='not controlled; research recording only'
    meta['guards']['not_diagnostic']=False;meta['pass']=False
    meta['admission_mode']=a.admission_mode
    Path(meta['workload']['output']).write_text(json.dumps(meta,indent=2)+'\n')
    assert len(instances)==1
    a.admission_output.write_text(json.dumps(dict(mode=a.admission_mode,
        profile=a.admission_profile,source=meta['source'],extension=meta['extension'],
        segments=instances[0].segment_records,default_adoption=False),separators=(',',':'))+'\n')
    print(json.dumps(dict(stage='private host recording complete',mode=a.admission_mode,
                          segments=len(instances[0].segment_records))),flush=True)


if __name__=='__main__':main()
