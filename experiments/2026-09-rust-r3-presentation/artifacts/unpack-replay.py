"""Restore the full forensic JSON trace as gzip for the original replay tool."""
import argparse,gzip,hashlib,json,lzma
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
experiment=Path(__file__).resolve().parents[1]
packing=json.loads((experiment/'results/packing.json').read_text())
archive=(experiment/'results'/packing['archive_file']).read_bytes()
assert hashlib.sha256(archive).hexdigest()==packing['archive_sha256']
raw=lzma.decompress(archive)
assert hashlib.sha256(raw).hexdigest()==packing['raw_content_sha256']
data=gzip.compress(raw,mtime=0)
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(data)
print(json.dumps(dict(raw_content_verified=True,output=str(args.output),gzip_sha256=hashlib.sha256(data).hexdigest(),original_gzip_byte_identical=hashlib.sha256(data).hexdigest()==packing['original_sha256'])))
