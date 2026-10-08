"""Finite E8 continuation: wait existing candidate, verify P2, one service screen.

Never repeats P2 or starts a matrix. No default, capacity or full-host acceptance.
No memory control, timeout, automatic retry or next performance round.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile
import run_observation_admission_p2 as common

def active(pid):
    text=subprocess.run(['ps','-p',str(pid),'-o','stat='],capture_output=True,text=True).stdout.strip()
    return bool(text) and not text.startswith('Z')

def record(message,runs,p2,screen=False,done=False):
    path=common.LAB/'records/rust-observation-admission-status.json';state=json.loads(path.read_text())
    state.update(stage=message,followup_runs=str(runs),source_sha='11d9927f7a1bffa32dd85c9009944424826508e5')
    if p2:state['phases']['P2_correctness']='complete native1 within revised recorded/canonical/edge scope; native4 full admission deferred'
    state['phases']['P3_performance']=('one bounded moving-world service screen '+('complete' if done else 'running')+'; formal full-host validation not started') if screen else 'queued after P2; no matrix'
    common.write(path,state)
    names=['rust-observation-admission-plan.md','rust-observation-admission-plan.json','rust-observation-admission-status.json']
    (common.LAB/'records/rust-observation-admission-SHA256SUMS').write_text(''.join(common.sha(common.LAB/'records'/name)+'  records/'+name+'\n' for name in names))
    marker='## E8 有界后续执行（2026-10-08，当前）'
    body=(f'{marker}\n\n{message}。优先读 `{runs}/progress.json`、`parent.log`、`screen.json` 和 `screen.monitor.json`，'
        '不要重启任何已开始的测试。等待原规范候选父任务退出后核验原始哈希，复用真实接纳与16个边界/故障检查；'
        '仅做一轮native1完整90秒录制输入的服务ABBA筛选，不自动加轮或进入正式窗口。'
        '筛选包括cache开关、wire/bytes、decode与固定消费，排除实时heap扫描及显示apply/render/submit，'
        '不是完整宿主收益门槛；计时受压力干扰则inconclusive，不自动补跑。默认/GAP/容量/Frontier不变。\n\n'
        f'进度：`完整参考 █ | 规范候选 {"█" if p2 else "▓"} | 接纳/边界 █ | 一轮收益筛选 {"█" if done else "▓" if screen else "░"} | 正式宿主/默认 ░`。\n\n')
    handoff=common.LAB/'records/rust-parallel-handoff.md';text=handoff.read_text()
    if text.startswith(marker):text=text[text.index('\n## ',len(marker))+1:]
    handoff.write_text(body+text)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preregister',type=Path,required=True);a=p.parse_args()
    reg=json.loads(a.preregister.read_text());runs=Path(reg['persistent_runs']);runs.mkdir(parents=True,exist_ok=True)
    lock=(runs/'followup.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    progress=runs/'progress.json';assert not progress.exists()
    tools=Path(__file__).parent
    for name,d in reg['tools'].items():assert common.sha(tools/name)==d
    def identity():
        assert subprocess.check_output(['git','-C',str(common.SOURCE),'rev-parse','HEAD'],text=True).strip()==reg['source_sha']
        assert not subprocess.check_output(['git','-C',str(common.SOURCE),'status','--porcelain'],text=True)
        assert common.sha(Path(reg['extension_dir'])/'star_native/_native.cpython-313-darwin.so')==reg['extension_sha256']
    identity();common.EXTENSION_SHA=reg['extension_sha256']
    common.write(progress,dict(status='waiting_existing_canonical',parent_pid=os.getpid(),wait_parent=reg['canonical_parent_pid'],no_duplicate_launch=True))
    try:
        while active(reg['canonical_parent_pid']):time.sleep(5)
        candidate_root=Path(reg['canonical_runs']);result=json.loads((candidate_root/'candidate-result.json').read_text())
        assert result['status']=='canonical_encoded_passed'
        package=common.EXP/result['raw']['file'];assert common.sha(package)==result['raw']['sha256']
        with zipfile.ZipFile(package) as z:
            assert z.testzip() is None
            for line in z.read('SHA256SUMS').decode().splitlines():
                expected,name=line.split('  ',1)
                import hashlib
                assert hashlib.sha256(z.read(name)).hexdigest()==expected
        canonical=common.verify(candidate_root/'encoded-t1.json',common.CANONICAL,'segment_encoded',1)
        assert canonical['counts']['queries']==canonical['counts']['query_accounting_snapshots']==11007
        admitted=common.verify(Path(reg['admitted_report']),Path(reg['trace']),'segment_encoded',1)
        assert admitted['counts']['queries']==3010 and admitted['counts']['segments']==750 and admitted['counts']['scoped_query_accounting_snapshots']==1772
        for path in (reg['edges_report'],reg['faults_report']):
            assert common.sha(path)==reg['prerequisite_sha256'][path] and json.loads(Path(path).read_text())['passed']
        prerequisite=dict(passed=True,source_sha=reg['source_sha'],canonical=canonical,actual_admission=admitted,
            edges=json.loads(Path(reg['edges_report']).read_text()),faults=json.loads(Path(reg['faults_report']).read_text()),
            scope='Revised native1 P2 scope; native1/4 small release contracts. Full native4 admission deferred; encoder fault is diagnostic copy, not release wheel injected fault',
            default_adoption=False,performance_claim=False)
        common.write(common.EXP/'results/p2-native1-complete.json',prerequisite)
        record('P2 native1范围完成，开始唯一一轮移动世界服务收益筛选',runs,True,True)
        identity();assert common.sha(reg['trace'])==reg['trace_sha256'] and common.sha(reg['admission'])==reg['admission_sha256']
        output=runs/'screen.json';monitor=runs/'screen.monitor.json';assert not output.exists() and not monitor.exists()
        common.write(progress,dict(status='screen_running',parent_pid=os.getpid(),P2_complete_native1=True))
        cmd=[sys.executable,str(tools/'screen_admitted_observation_pair.py'),'--source',str(common.SOURCE),'--extension-dir',reg['extension_dir'],
             '--trace',reg['trace'],'--admission',reg['admission'],'--output',str(output)]
        subprocess.run([sys.executable,str(tools/'monitor_observation_admission.py'),'--report',str(monitor),'--',*cmd],check=True,cwd=common.LAB)
        from analyze_admitted_observation_screen import analyze
        analysis=analyze(output,monitor);common.write(runs/'analysis.json',analysis)
        package=common.archive('e8-p3-single-service-screen-20261008',[('raw/'+p.name,p) for p in sorted(runs.glob('screen.*')) if p.is_file()]+[('analysis.json',runs/'analysis.json')])
        decision=dict(status='single_screen_complete',analysis=analysis,raw=package,automatic_retry=False,
            automatic_next_round=False,formal_full_host_acceptance=False,default_adoption=False)
        common.write(common.EXP/'results/p3-single-service-screen.json',decision);common.write(progress,decision)
        record('单轮服务收益筛选完成：'+analysis['decision'],runs,True,True,True)
        for name in ('README.md','analysis.md','decision.md'):
            path=common.EXP/name
            path.write_text('> 2026-10-08 单轮服务筛选结束：'+analysis['decision']+'。'
                '完整结果见 results/p3-single-service-screen.json。这是90秒录制输入的请求/cache服务筛选，'
                '排除真实heap扫描与显示链；不构成正式宿主收益或默认采用。没有自动加轮、重试或窗口。\n\n'+path.read_text())
        manifest_path=common.EXP/'manifest.yaml';manifest=json.loads(manifest_path.read_text())
        manifest['experiment']['status']='P2 revised native1 scope complete; one service screen complete, full-host gate pending'
        manifest['artifacts']['formal'] += ['results/p2-native1-complete.json','results/p3-single-service-screen.json',package['file']]
        common.write(manifest_path,manifest)
    except BaseException as error:
        result=dict(status='failed',error=repr(error),raw_preserved=True,automatic_retry=False)
        common.write(progress,result);common.write(common.EXP/'results/p3-single-service-screen-interruption.json',result)
        record('有界后续校验失败，保存证据，不自动重复',runs,False,False);raise
    finally:common.checksums()

if __name__=='__main__':main()
