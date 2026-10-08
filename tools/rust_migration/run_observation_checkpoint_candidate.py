"""One E8 encoded candidate against validated fingerprints; no repeated baseline.

No automatic retry or P3. Memory pressure is telemetry only. Targeted and
actual admission checks remain separate, so this never marks all P2 complete.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import run_observation_admission_p2 as common

def stage(message, runs):
    path = common.LAB / 'records/rust-observation-admission-status.json'
    state = json.loads(path.read_text())
    state.update(stage=message, persistent_runs=str(runs),
                 resource_policy='telemetry only; no automatic pause/kill/timeout')
    state['phases']['P2_correctness'] = message
    common.write(path, state)
    names = ['rust-observation-admission-plan.md', 'rust-observation-admission-plan.json', 'rust-observation-admission-status.json']
    (common.LAB / 'records/rust-observation-admission-SHA256SUMS').write_text(''.join(
        common.sha(common.LAB / 'records' / name)+'  records/'+name+'\n' for name in names))
    handoff = common.LAB / 'records/rust-parallel-handoff.md'
    marker = '## E8 精简候选校验（2026-10-08，当前）'
    body = (f'{marker}\n\n{message}。恢复先读 `{runs}/candidate-progress.json`、'
            f'`encoded-t1.progress.json`、`encoded-t1.monitor.json` 与 `parent.log`。'
            '普通完整轨迹两次结果已归档，不重跑；no_reuse 冗长组按用户精简要求取消，'
            '未完成前缀保留而不算通过。候选复用独立旧二进制的已核验完整状态指纹，'
            '仍检查每个写入/step、单条或段末全状态、全部响应/展示及逐查询计数。'
            '本阶段仅规范轨迹候选，targeted 与实际接纳校验仍待完成；'
            'P2不宣称完成，P3/默认未启动。不因压力自动暂停/终止；'
            '不关闭GAP，不改容量/Frontier/5000Agents暂缓。\n\n'
            '进度：`普通完整参考 █ | encoded候选 ▓ | targeted/实际接纳 ░ | P3 ░ | 默认 ░`。\n\n')
    text = handoff.read_text()
    if text.startswith(marker): text = text[text.index('\n## ', len(marker))+1:]
    handoff.write_text(body+text)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preregister', type=Path, required=True)
    a = p.parse_args(); reg = json.loads(a.preregister.read_text())
    runs = Path(reg['persistent_runs']); runs.mkdir(parents=True, exist_ok=True)
    lock = (runs / 'candidate.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    progress = runs / 'candidate-progress.json'; assert not progress.exists()
    tools = Path(__file__).parent
    for name, digest in reg['tools'].items(): assert common.sha(tools/name) == digest
    assert subprocess.check_output(['git','-C',str(common.SOURCE),'rev-parse','HEAD'], text=True).strip() == reg['source_sha']
    assert not subprocess.check_output(['git','-C',str(common.SOURCE),'status','--porcelain'], text=True)
    extension = Path(reg['extension_dir']) / 'star_native/_native.cpython-313-darwin.so'
    assert common.sha(extension) == reg['extension_sha256']
    common.EXTENSION_SHA = reg['extension_sha256']
    reference = Path(reg['reference_report'])
    assert common.sha(reference) == reg['reference_report_sha256']
    common.verify(reference, common.CANONICAL, 'single', 1)
    mini = Path(reg['mini_validation'])
    validated = json.loads(mini.read_text())
    assert validated['passed'] and validated['tool_sha256'] == reg['tools']['verify_observation_checkpoints.py']
    for pid in reg['terminated_old_pids']:
        assert not subprocess.run(['ps','-p',str(pid),'-o','stat='], capture_output=True,text=True).stdout.strip()
    output = runs/'encoded-t1.json'; monitor = runs/'encoded-t1.monitor.json'
    assert not output.exists() and not monitor.exists()
    common.write(progress, dict(status='running', parent_pid=os.getpid(), preregister_sha256=common.sha(a.preregister)))
    try:
        cmd = [sys.executable, str(tools/'verify_observation_checkpoints.py'), '--source', str(common.SOURCE),
               '--extension-dir',reg['extension_dir'],'--trace',str(common.CANONICAL),
               '--reference-report',str(reference),'--output',str(output),'--threads','1']
        subprocess.run([sys.executable,str(tools/'monitor_observation_admission.py'),'--report',str(monitor),'--',*cmd],
                       check=True, cwd=common.LAB)
        report = common.verify(output, common.CANONICAL, 'segment_encoded', 1)
        assert report['counts']['queries'] == report['counts']['query_accounting_snapshots'] == 11007
        guard = json.loads(monitor.read_text())
        assert guard['status'] == 'passed' and guard['child_exit'] == 0
        assert not guard['automatic_pause'] and not guard['automatic_termination']
        package = common.archive('e8-p2-streamlined-20261008-encoded-t1',
            [('raw/'+p.name,p) for p in sorted(runs.glob('encoded-t1.*')) if p.is_file()])
        result = dict(status='canonical_encoded_passed', report=report, raw=package,
            reference_reused=True, P2_complete=False, targeted_complete=False, actual_admission_complete=False,
            P3_started=False, performance_claim=False, default_adoption=False,
            resource_policy='telemetry only', resource_events=len(guard['events']))
        common.write(runs/'candidate-result.json',result)
        common.write(common.EXP/'results/p2-streamlined-candidate.json',result)
        stage('规范 encoded 候选完整通过；targeted/实际接纳待完成',runs)
        common.write(progress,result)
    except BaseException as error:
        result = dict(status='failed',error=repr(error),raw_preserved=True,automatic_retry=False,P3_started=False)
        common.write(progress,result)
        common.write(common.EXP/'results/p2-streamlined-candidate.json',result)
        stage('规范 encoded 候选校验失败，保留原始尝试，不自动重跑',runs)
        raise
    finally:
        common.checksums()

if __name__ == '__main__': main()
