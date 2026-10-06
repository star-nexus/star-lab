"""Verify and archive complete E7 P2; never launch performance or enable E7."""
import argparse
import gzip
import hashlib
import json
import math
from datetime import date
import subprocess
import zipfile
from pathlib import Path

SOURCE = '5b9658bc668b7d13f801351162f255f30622b32a'
EXTENSION = '838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
STREAM = 'e01f2147b0fba41b27d15634c552bfb96ee84480a7628926890e57027a65b76b'
FINAL = 'd069c7173464d787c28f86120f1f173105f9f2c3f5cf959a758ab84290780dbf'
JOBS = [('p2-correctness-t1-static', 1, 'baseline', 'static'),
        ('p2-correctness-t4-exercise', 4, 'baseline', 'exercise'),
        ('p2-correctness-typed-t1-exercise', 1, 'reuse_typed', 'exercise'),
        ('p2-correctness-typed-t4-static', 4, 'reuse_typed', 'static')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_job(runs, job, limit_mib=2500):
    name, threads, consumer, script = job
    path = runs / (name + '.json')
    m = json.loads(path.read_text())
    assert m['source_sha'] == SOURCE and not m['source_dirty']
    assert m['task'] == 'correctness' and m['formal'] and m['all_passed'] and m['full_authority']
    assert not m['diagnostic'] and not m['probe_control']
    assert (m['threads'], m['consumer'], m['display_script']) == (threads, consumer, script)
    assert m['modes'] == ['baseline', 'empty_territory']
    assert m['display_clock'] == 'fixed' and m['overscan_clock'] == 'items'
    assert m['driver'] == 'dummy' and m['surface'] == [2480, 1239]
    assert m['extension_sha256'] == EXTENSION
    assert m['stream_sha256'] == STREAM and m['final_state_sha256'] == FINAL
    assert m['counts'] == dict(request=40994, step=9880, presentation=9880)
    assert m['checks'] == dict(full_authority=19760, command_stream=19760,
                               pixels=19760, projection=19760, full_cold_world=99)
    for key in ('raw', 'authority_raw', 'pixel_raw'):
        item = m[key]
        data = (runs / item['file']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256']
        assert len(data) == item['bytes']
        rows = json.loads(gzip.decompress(data))
        if key == 'raw':
            assert len(rows) == 2 and all(len(side) == 9880 for side in rows)
        else:
            assert len(rows) == 9880
        if key == 'authority_raw':
            assert [r['tick'] for r in rows] == list(range(1, 9881))
    guard = json.loads((runs / (name + '.guard.json')).read_text())
    assert guard['status'] == 'passed' and guard['child_exit'] == 0 and guard['stop_reason'] is None
    assert guard['limit_mib'] == limit_mib
    return m, guard


def archive_job(exp, runs, name):
    path = exp / 'artifacts' / f'display-preparation-{name}-raw.zip'
    suffixes = ('.json', '.samples.json.gz', '.authority.json.gz', '.pixels.json.gz',
                '.guard.json', '.guard.child.log', '.supervisor.log')
    files = [runs / (name + s) for s in suffixes]
    if not path.exists():
        temporary = path.with_suffix('.zip.tmp')
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for file in files:
                z.write(file, 'raw/' + file.name)
            z.writestr('SHA256SUMS', ''.join(sha(f) + '  raw/' + f.name + '\n' for f in files))
        temporary.rename(path)
    with zipfile.ZipFile(path) as z:
        for row in z.read('SHA256SUMS').decode().splitlines():
            expected, member = row.split('  ', 1)
            assert hashlib.sha256(z.read(member)).hexdigest() == expected
        for file in files:
            assert hashlib.sha256(z.read('raw/' + file.name)).hexdigest() == sha(file)
    return dict(file=path.name, sha256=sha(path), bytes=path.stat().st_size)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--remaining-limit-mib', type=float, default=2500)
    p.add_argument('--run-date', default='2026-10-05')
    a = p.parse_args()
    assert math.isfinite(a.remaining_limit_mib) and a.remaining_limit_mib > 0
    date.fromisoformat(a.run_date)
    lab = Path(__file__).resolve().parents[2]
    exp = lab / 'experiments/2026-10-rust-display-preparation'
    rows = []
    reference = None
    for index, job in enumerate(JOBS):
        expected_limit = 2500 if index < 2 else a.remaining_limit_mib
        m, guard = verify_job(a.runs, job, expected_limit)
        identity = {key: m[key] for key in ('source_sha', 'tool_sha256', 'extension_sha256',
                    'trace_sha256', 'initial_sha256', 'display_script_sha256',
                    'fixture_sha256', 'dependency_lock_sha256')}
        if reference is None:
            reference = identity
        assert identity == reference
        name = job[0]
        if name == 'p2-correctness-t1-static':
            evidence = json.loads((exp / 'results/p2-t1-static-completed.json').read_text())
        elif name == 'p2-correctness-t4-exercise':
            evidence = json.loads((exp / 'results/p2-t4-exercise-completed.json').read_text())
        else:
            evidence = archive_job(exp, a.runs, name)
        assert sha(exp / 'artifacts' / evidence['file']) == evidence['sha256']
        rows.append(dict(run=name, threads=m['threads'], consumer=m['consumer'],
                         script=m['display_script'], counts=m['counts'], checks=m['checks'],
                         metadata_sha256=sha(a.runs / (name + '.json')), raw=m['raw'],
                         authority=m['authority_raw'], pixels=m['pixel_raw'], artifact=evidence,
                         memory_guard=f'passed with {expected_limit:g}MiB and unchanged system-pressure policy',
                         elapsed_seconds=m['elapsed_seconds']))
    summary = dict(stage='P2 complete', passed=True, completed_jobs=4, total_jobs=4,
                   identity=reference, results=rows, capacity_claim=False, performance_claim=False,
                   production_enabled=False, next_stage='P3 not started by this tool',
                   scope='Full canonical 40994 requests/9880 ticks per group; complete authority, display, events, command and pixel contracts. Resource guards cover these successful executions; do not prove all-use absence of leaks.',
                   interrupted_attempts='Oct4 and Oct5 incomplete resource attempts retained separately; excluded from pass counts',
                   run_date=a.run_date,
                   resource_budget_note='First two groups retain 2500MiB guards; remaining groups use explicitly recorded authorized limits. Correctness thresholds unchanged; budgets are not a uniform memory-safety or performance comparison.',
                   runs_directory=str(a.runs), finalizer_sha256=sha(Path(__file__)))
    (exp / 'results/p2-complete.json').write_text(json.dumps(summary, indent=2) + '\n')
    filenames = ['manifest.yaml', 'results/open-gap-status-resume.json', 'results/p2-reboot-resume.json']
    if (exp / 'results/p2-budget-resume.json').exists():
        filenames.append('results/p2-budget-resume.json')
    for filename in filenames:
        path = exp / filename
        value = json.loads(path.read_text())
        value.update(status='P2 complete; P3 pending', full_correctness_completed=True,
                     completed_full_correctness_jobs=4, p2_completion='results/p2-complete.json')
        if filename.endswith('open-gap-status-resume.json'):
            value.update(stage='P2 complete; P3 pending', current=None, full_correctness_completed_jobs=4)
        path.write_text(json.dumps(value, indent=2) + '\n')
    report = (f'\n## E7 P2完整通过（恢复运行，{a.run_date}）\n\n'
              '四组完整40994请求/9880tick校验全部通过：ordinary native1/static、ordinary native4/exercise、'
              'reuse_typed native1/exercise与native4/static。每组完整权威、展示/事件、绘制命令、像素、'
              '查询顺序及最终权威指纹通过，原始样本/指纹和内存守护全部保留。'
              '结论只覆盖P2正确性及本次完整执行的资源保护；不代表性能收益、容量提升或一般无泄漏证明。\n'
              '证据入口E7 results/p2-complete.json。前两组归档复用，后两组重启后新完整运行；'
              '历史不完整资源中断继续保留，未计作通过。测量源码5b9658b、原probe/扩展/系统压力策略保持；'
              f'前两组限额2500MiB、剩余两组限额{a.remaining_limit_mib:g}MiB，不能据此宣称统一内存预算验收。\n'
              '进度：`P2完整正确性 4/4 █ | 证据与校验 █ | P3/窗口/默认接入 ░`。'
              '未启动P3、未启用默认路径、未push/merge；既有GAP、容量和Frontier保持。\n')
    for filename in ('records/rust-parallel-handoff.md', 'records/rust-system-parallel-status.md'):
        path = lab / filename
        old = path.read_text()
        index = old.find('\n')
        path.write_text(old[:index+1] + report + old[index+1:])
    for filename in ('README.md', 'analysis.md', 'decision.md'):
        path = exp / filename
        path.write_text(report + '\n' + path.read_text())
    paths = sorted(path for directory in ('results', 'artifacts')
                   for path in (exp / directory).rglob('*')
                   if path.is_file() and path.name != 'SHA256SUMS')
    sums = exp / 'artifacts/SHA256SUMS'
    sums.write_text(''.join(sha(path) + '  ' + path.relative_to(exp).as_posix() + '\n' for path in paths))
    subprocess.run(['shasum', '-a', '256', '-c', 'artifacts/SHA256SUMS'], cwd=exp, check=True)
    (a.runs / 'p2-finalization.json').write_text(json.dumps(dict(status='P2 complete and integrity verified',
                                                    evidence=str(exp / 'results/p2-complete.json')), indent=2) + '\n')
    print(json.dumps(dict(P2_complete=True, integrity_verified=True, performance_claim=False)), flush=True)


if __name__ == '__main__':
    main()
