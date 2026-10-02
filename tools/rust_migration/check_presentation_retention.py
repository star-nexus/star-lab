"""Supplemental E6 retained-allocation check; not a speed/capacity benchmark."""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import tracemalloc


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    sys.path.insert(0,str(a.source))
    from framework import World
    from rotk_env.runtime.world_presentation import WorldPresentation
    from rotk_env.tests.test_presentation_cache_research import delta
    reports=[]
    for mode in ('baseline','reuse_constructed','reuse_typed'):
        projection=WorldPresentation(World());payload=delta();projection._apply_research(payload,mode=mode)
        for i in range(1,5001):
            payload['revision']=i;projection._apply_research(payload,mode=mode)
        gc.collect();tracemalloc.start();gc.disable();samples=[]
        try:
            for i in range(5001,55001):
                payload['revision']=i;projection._apply_research(payload,mode=mode)
                if i%10000==5000:
                    current,peak=tracemalloc.get_traced_memory()
                    samples.append(dict(updates=i-5000,current_bytes=current,peak_bytes=peak,maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
            assert len(projection.world.entities)==1
            # Only bounded metadata/sample integers should survive repeated publication.
            growth=samples[-1]['current_bytes']-samples[0]['current_bytes']
            assert growth<65536,(mode,growth)
            reports.append(dict(mode=mode,updates=50000,entities=1,samples=samples,retained_growth_bytes=growth,passed=True))
        finally:
            tracemalloc.stop();gc.enable();projection.world.reset()
    result=dict(source_sha=subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip(),
                reports=reports,all_passed=True,performance_claim=False,capacity_claim=False,
                tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
