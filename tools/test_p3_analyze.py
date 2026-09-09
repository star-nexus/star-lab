"""Archive acceptance must detect altered raw data and altered reported metrics."""
import hashlib
import json
import zipfile
import pytest
from p3_local_agents import stats
from p3_analyze import analyze
from p3_archive import archive


def evidence(tmp_path):
    point = tmp_path/'point.json'
    raw = {'frames':[{'t':1,'work_ms':20,'agent_ms':3,'dt':1/30}],
           'events':[{'t':1,'event':'observe','agent':0,'response_ms':4,'build_ms':2,'encode_ms':1,'bytes':100}],
           'censuses':[{'t':1,'alive':3,'moving':1,'position_changes':1,'maxrss':1000}]}
    blob = json.dumps(raw).encode()
    point.with_suffix('.raw.json').write_bytes(blob)
    data = {'raw':{'sha256':hashlib.sha256(blob).hexdigest()},'source':{'sha':'fixture'},
            'workload':{'warmup':0,'agents':1,'units':3,'source':str(tmp_path),'layout':'canonical'},
            'frame_work_ms':stats([20]),'observation_response_ms':stats([4]),
            'action_queue_ms':stats([]),'pass':False}
    point.write_text(json.dumps(data))
    return point, data


def test_forensic_reanalysis_and_package_round_trip(tmp_path):
    point, _ = evidence(tmp_path)
    assert analyze(point)['observation_bytes']['avg']==100
    packages = archive(point,tmp_path/'case')
    rawzip = tmp_path/'case/artifacts'/packages['raw']['path']
    assert hashlib.sha256(rawzip.read_bytes()).hexdigest()==packages['raw']['sha256']
    with zipfile.ZipFile(rawzip) as z:
        z.extractall(tmp_path/'restored')
    assert analyze(tmp_path/'restored/point.json')==analyze(point)


def test_altered_raw_and_metric_are_rejected(tmp_path):
    point, data = evidence(tmp_path)
    raw = point.with_suffix('.raw.json')
    original = raw.read_bytes()
    raw.write_bytes(original+b' ')
    with pytest.raises(ValueError, match='SHA256'): analyze(point)
    raw.write_bytes(original)
    data['frame_work_ms']['p99']=1
    point.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='recomputation'): analyze(point)
