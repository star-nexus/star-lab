"""Restore canonical E3 replay inputs and binary packages without changing any venv."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--work-dir', type=Path, required=True)
    a = p.parse_args()
    root = a.experiment.resolve()
    m = json.loads((root/'manifest.yaml').read_text())
    work = a.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    def archive(item):
        path = root/item['archive']
        assert sha(path.read_bytes()) == item['archive_sha256']
        return zipfile.ZipFile(path)
    def save(path, data, expected):
        assert sha(data) == expected
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for key in ['trace', 'initial', 'contracts']:
        item = m['canonical_inputs'][key]
        with archive(item) as z:
            save(work/'inputs'/Path(item['member']).name, z.read(item['member']), item['sha256'])
    index = json.loads((root/'results/packages.json').read_text())
    item = dict(archive=index['raw']['file'], archive_sha256=index['raw']['sha256'])
    baseline = m['baseline_binary']
    for name, arch, member, expected in [('candidate',item,m['binary']['wheel_member'],m['binary']['extension_sha256']),
                                        ('baseline',baseline,baseline['wheel_member'],baseline['extension_sha256'])]:
        with archive(arch) as z:
            wheel = z.read(member)
        import io
        with zipfile.ZipFile(io.BytesIO(wheel)) as w:
            for member in w.namelist():
                if member.startswith('star_native/') and not member.endswith('/'):
                    data = w.read(member)
                    if member.endswith('.so'):
                        assert sha(data) == expected
                    path = work/name/member
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_bytes(data)
    print(json.dumps(dict(work_dir=str(work),candidate_package=str(work/'candidate'),baseline_package=str(work/'baseline'),inputs=str(work/'inputs'))))


if __name__ == '__main__':
    main()
