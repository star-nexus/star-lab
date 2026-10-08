"""Finite E8 fault harness; product/wheel unchanged, one encoder error seam.

Compiles a copy of the pinned native boundary, injecting only a final-encoding
error wrapper shared by ordinary and scoped responses. Records exact diff.
Real release-wheel panic/poison and lifecycle checks are in the edge tool.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--initial',type=Path,required=True)
    p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--target-dir',type=Path)
    a=p.parse_args();a.runs.mkdir(parents=True,exist_ok=True)
    assert not (a.runs/'Cargo.toml').exists()
    assert subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip()=='11d9927f7a1bffa32dd85c9009944424826508e5'
    src=a.source/'native/python/src/lib.rs';original=src.read_text()
    expression='serde_json::to_string(&r.execute_request(request)?)'
    assert original.count(expression)==2
    patched=original.replace(expression,'e8_encode(&r.execute_request(request)?)')
    assert patched.count('serde_json::to_string(&response)')==1
    patched=patched.replace('serde_json::to_string(&response)','e8_encode(&response)')
    helper='''
thread_local! { static E8_FAIL_ENCODING: std::cell::Cell<bool> = const { std::cell::Cell::new(false) }; }
fn e8_encode<T: serde::Serialize>(response: &T) -> Result<String, serde_json::Error> {
    if E8_FAIL_ENCODING.with(|fault| fault.replace(false)) {
        return Err(serde_json::Error::io(std::io::Error::other("injected final encode fault")));
    }
    serde_json::to_string(response)
}
'''
    companion=Path(__file__).with_name('observation_boundary_faults.rs')
    (a.runs/'src').mkdir();(a.runs/'src/lib.rs').write_text(patched+helper+companion.read_text())
    (a.runs/'encoder-seam.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),patched.splitlines(True),fromfile=str(src),tofile='diagnostic copy only')))
    shutil.copyfile(a.initial,a.runs/'initial.json')
    fixture=json.loads(a.initial.read_text())
    assert fixture['singletons']['TeamCoordination']['unit_owners']['$map']==[[37,'alpha']]
    (a.runs/'Cargo.toml').write_text(f'''[package]
name = "e8-boundary-fault-checks"
version = "0.0.0"
edition = "2024"
[dependencies]
star-core = {{ path = "{a.source}/native/core" }}
star-rotk = {{ path = "{a.source}/native/rotk" }}
pyo3 = {{ version = "=0.29.2", features = ["auto-initialize"] }}
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = {{ version = "1.0", features = ["float_roundtrip", "arbitrary_precision", "preserve_order", "raw_value"] }}
''')
    # Keep the product's resolved transitive versions; an external crate would
    # otherwise choose newer cached patch releases even in offline mode.
    shutil.copyfile(a.source/'Cargo.lock',a.runs/'Cargo.lock')
    cmd=['/Users/liyang/.cargo/bin/cargo','+1.98.1','test','--offline','--manifest-path',str(a.runs/'Cargo.toml'),'--lib','--','--test-threads=1']
    env=dict(os.environ,CARGO_TARGET_DIR=str(a.target_dir or a.runs/'target'),PYO3_PYTHON=str(a.source/'.venv/bin/python'))
    libdir=subprocess.check_output([env['PYO3_PYTHON'],'-c',"import sysconfig;print(sysconfig.get_config_var('LIBDIR'))"],text=True).strip()
    env['DYLD_FALLBACK_LIBRARY_PATH']=libdir
    with (a.runs/'cargo.log').open('wb') as log:
        result=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
    output=(a.runs/'cargo.log').read_text();passed=result.returncode==0 and '4 passed; 0 failed' in output
    record=dict(passed=passed,returncode=result.returncode,command=cmd,python_libdir=libdir,tool_sha256=sha(__file__),companion_sha256=sha(companion),
        product_boundary_sha256=sha(src),diagnostic_boundary_sha256=sha(a.runs/'src/lib.rs'),
        fixture_sha256=sha(a.runs/'initial.json'),cargo_log_sha256=sha(a.runs/'cargo.log'),
        source_unchanged=src.read_text()==original,
        scope='Debug diagnostic copy of exact pinned boundary/dependencies, three serializer call sites wrap one synthetic error seam; not release-wheel fault injection or performance proof',
        bounded_cache_scope='64 tiny 4-query scopes / 7 resets, current cache summary stable and absent at each end; not general RSS leak proof')
    (a.runs/'faults.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
    assert passed,output[-2500:]

if __name__=='__main__':main()
