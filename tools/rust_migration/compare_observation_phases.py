"""Compare full raw results and states before/after typed public fact encoding."""
import argparse,json,lzma
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=Path,required=True);a=p.parse_args();root=a.results
    names=('oracle','before','after');reports=[json.loads((root/n/'compact.json').read_text()) for n in names]
    raw=[json.loads(lzma.decompress((root/n/'raw.json.xz').read_bytes())) for n in names]
    assert all(len(r['rows'])==18 and r['all_guards_passed'] for r in reports)
    cases=[];thread_reference={};scheduling={'parallel_panel_batches','panel_tasks','panel_worker_threads'}
    for i in range(18):
        rows=[r['rows'][i] for r in reports];ref=rows[0]
        for j,row in enumerate(rows):
            for k in ('scenario','variant','threads','requests','distinct_panels','initial_sha256','final_sha256','agent_response_sha256','bytes','reachable_cells'):assert row[k]==ref[k],(names[j],k)
            assert raw[j][i]['response']['results']==raw[0][i]['response']['results']
            assert raw[j][i]['parameters']==raw[0][i]['parameters']
            assert {k:v for k,v in row['metrics'].items() if k!='panel_worker_threads'}=={k:v for k,v in ref['metrics'].items() if k!='panel_worker_threads'}
            key=(row['scenario'],row['variant']);facts=(row['agent_response_sha256'],row['initial_sha256'],row['final_sha256'],{k:v for k,v in row['metrics'].items() if k not in scheduling})
            if key not in thread_reference:thread_reference[key]=facts
            assert facts==thread_reference[key]
            for t in raw[j][i]['phase_samples']:
                assert sum(t[k] for k in ('parse_ns','batch_ns','final_encode_ns','drop_ns'))<=t['native_ns']
                assert t['profile']['census_ns']<=t['profile']['faction_ns']<=t['batch_ns']
                assert t['profile']['public_encode_ns']<=t['profile']['faction_ns']
                assert t['profile']['panels_ns']<=t['batch_ns']
        cases.append(dict(scenario=ref['scenario'],variant=ref['variant'],threads=ref['threads'],reachable_cells=ref['reachable_cells'],bytes=ref['bytes'],medians_ms={n:r['median_ms'] for n,r in zip(names,rows)},after_over_before=rows[2]['median_ms']/rows[1]['median_ms'],phases_ms={n:r['phase_medians_ms'] for n,r in zip(names,rows)},exact_results_and_states_equal=True))
    ingress=[]
    left=json.loads((root/'before-public/compact.json').read_text())
    right=json.loads((root/'after-public/compact.json').read_text())
    lraw=json.loads(lzma.decompress((root/'before-public/raw.json.xz').read_bytes()))
    rraw=json.loads(lzma.decompress((root/'after-public/raw.json.xz').read_bytes()))
    assert len(left['rows'])==len(right['rows'])==15
    for i,(x,y) in enumerate(zip(left['rows'],right['rows'])):
        for k in ('scenario','mode','requests','initial_sha256','final_sha256','agent_response_sha256','wire_bytes','metrics','reachable_cells'):assert x[k]==y[k],k
        assert lraw[i]['response']==rraw[i]['response']
        ingress.append(dict(scenario=x['scenario'],mode=x['mode'],requests=x['requests'],before_ms=x['median_ms'],after_ms=y['median_ms'],full_response_equal=True))
    out=dict(all_guards_passed=True,rows=84,profile_rows=54,ingress_rows=30,ingress=ingress,paired_cases=18,thread_equivalence=True,unchanged_wire_bytes=True,capacity_claim=False,cases=cases)
    (root/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS:54phase+30ingress rows, full response/state/byte length/work counters and phase nesting')

if __name__=='__main__':main()
