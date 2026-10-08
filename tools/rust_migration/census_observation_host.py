"""Single-factor census host screen on ordinary single-query ingestion."""
import argparse
import json
from pathlib import Path
import sys
import admitted_observation_host as host

EXTENSION_SHA = 'c6a60a42fdafeee481620e89248a1a8604b7e3b3835b7b2a0f43053999977d88'
BaseWire = host.LiveWire


class CensusWire(BaseWire):
    scan_mode = 'baseline'

    def __init__(self, runtime, output, source, extension, threads):
        if self.scan_mode not in ('baseline', 'borrowed_census'):
            raise ValueError('invalid census host mode')
        assert extension['sha256'] == EXTENSION_SHA
        # Both arms configure once before the warmup; no measured getter/setter.
        runtime._set_observation_scan_research(self.scan_mode)
        assert runtime._native._observation_scan_research() == self.scan_mode
        super().__init__(runtime, output, source, extension, threads)

    def finish(self):
        assert self.runtime._native._observation_scan_research() == self.scan_mode
        return dict(super().finish(), scan_mode=self.scan_mode,
                    scan_mode_persisted=True, scan_configuration_calls=1)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scan-mode', choices=['baseline', 'borrowed_census'], required=True)
    opts,args=p.parse_known_args()
    assert '--host-mode' not in args and '--output' in args
    target=Path(args[args.index('--output')+1]).resolve()
    CensusWire.scan_mode=opts.scan_mode
    host.EXTENSION_SHA=EXTENSION_SHA
    host.LiveWire=CensusWire
    sys.argv=[sys.argv[0], '--host-mode', 'single', *args]
    host.main()
    meta=json.loads(target.read_text())
    assert meta['host_mode']=='single' and meta['admitted_segments']['count']==0
    meta['census_scan_mode']=opts.scan_mode
    meta['independent_variable']='census key ownership only; ordinary single-query ingestion both sides'
    meta['formal_full_host_acceptance']=False
    meta['default_adoption']=False
    target.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')


if __name__=='__main__':main()
