"""Build isolated mechanism probes against exact STAR types / resolved versions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    lab = Path(__file__).resolve().parents[2]
    scratch = lab / 'runs/ecs-parallel-mechanism-probe'
    (scratch / 'src').mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    assert actual == args.source_sha
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True).strip()
    rust = Path(__file__).with_name('ecs_parallel_probe.rs')
    (scratch / 'src/main.rs').write_bytes(rust.read_bytes())
    original = tomllib.loads((source / 'Cargo.lock').read_text())
    versions = {p['name']: p['version'] for p in original['package']}
    manifest = f'''[package]
name = "ecs-parallel-mechanism-probe"
version = "0.1.0"
edition = "2024"
[dependencies]
star-core = {{ path = {json.dumps(str(source/'native/core'))} }}
star-rotk = {{ path = {json.dumps(str(source/'native/rotk'))} }}
bevy_ecs = {{ version = "={versions['bevy_ecs']}", default-features = false, features = ["std", "multi_threaded"] }}
bevy_tasks = {{ version = "={versions['bevy_tasks']}", features = ["multi_threaded"] }}
serde_json = "={versions['serde_json']}"
[profile.release]
lto = "thin"
codegen-units = 1
'''
    (scratch / 'Cargo.toml').write_text(manifest)
    env = dict(os.environ, PATH='/Users/liyang/.cargo/bin:' + os.environ['PATH'])
    commands = []

    def call(name, argv):
        entry = dict(name=name, argv=list(map(str, argv)), cwd=str(scratch))
        commands.append(entry)
        with (output / f'{name}.log').open('w') as log:
            result = subprocess.run(entry['argv'], cwd=scratch, env=env, stdout=log, stderr=subprocess.STDOUT)
        entry['exit_status'] = result.returncode
        (output / 'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        assert result.returncode == 0, name

    call('lock', ['cargo', 'generate-lockfile', '--offline', '--manifest-path', scratch/'Cargo.toml'])
    resolved = tomllib.loads((scratch/'Cargo.lock').read_text())
    original_packages = {(p['name'], p['version'], p.get('source')) for p in original['package']}
    assert all((p['name'], p['version'], p.get('source')) in original_packages
               for p in resolved['package'] if p['name'] != 'ecs-parallel-mechanism-probe'), 'dependency drift'
    (output/'probe.Cargo.lock').write_bytes((scratch/'Cargo.lock').read_bytes())
    (output/'probe.Cargo.toml').write_bytes((scratch/'Cargo.toml').read_bytes())
    call('build', ['cargo', 'build', '--release', '--locked', '--offline', '--manifest-path', scratch/'Cargo.toml'])
    executable = scratch/'target/release/ecs-parallel-mechanism-probe'
    runs = []
    for mode, threads in [('schedule', 1), ('schedule', 2), ('schedule', 4), ('scoped', 2), ('scoped', 4)]:
        name = f'{mode}-t{threads}'
        call(name, [executable, mode, str(threads)])
        value = json.loads((output/f'{name}.log').read_text())
        assert value['all_passed']
        (output/f'{name}.json').write_text(json.dumps(value, indent=2)+'\n')
        runs.append(dict(mode=mode, threads=threads, all_passed=True))
    metadata = dict(source_sha=actual, source_lock_sha256=sha(source/'Cargo.lock'),
                    runner_sha256=sha(Path(__file__)), rust_probe_sha256=sha(rust),
                    executable_sha256=sha(executable), probe_lock_sha256=sha(output/'probe.Cargo.lock'),
                    dependency_versions_match_source=True, build='release', runs=runs,
                    scope='synthetic access/concurrency/active-query mechanisms; not real Systems or capacity')
    (output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata))


if __name__ == '__main__':
    main()
