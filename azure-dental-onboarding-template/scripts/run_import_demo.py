import json
from pathlib import Path
from import_core import run_folder
data=Path(__file__).resolve().parents[1]/'data'
rep=run_folder(data)
Path(__file__).resolve().parents[1].joinpath('scripts','out_report.json').write_text(json.dumps(rep,indent=2))
print(json.dumps(rep['summary'],indent=2))