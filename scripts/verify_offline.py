"""Run the local solvers with network access blocked."""
from pathlib import Path
import sys, subprocess, os, json, hashlib, platform
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)>1 and sys.argv[1]=='--child':
    import socket, runpy
    def denied(*args,**kwargs): raise RuntimeError('Network disabled during the offline run')
    socket.socket.connect=denied
    socket.socket.connect_ex=denied
    socket.create_connection=denied
    target=sys.argv[2]
    sys.argv=[target]
    runpy.run_path(target,run_name='__main__')
    raise SystemExit
results=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
env.pop('PYTHONPATH',None)
scripts=sorted((ROOT/'src/solvers').glob('*/solve_cycles.py'))+sorted((ROOT/'src/solvers').glob('*/solve.py'))+sorted((ROOT/'src/solvers').glob('*/decrypt.py'))+sorted((ROOT/'src/solvers').glob('*/mechanism_demo.py'))
for script in scripts:
    slug=script.parent.name
    cwd=ROOT/'outputs'/slug;cwd.mkdir(parents=True,exist_ok=True)
    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(script)],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
    results.append(dict(slug=slug,script=script.relative_to(ROOT).as_posix(),kind='demo' if script.name=='mechanism_demo.py' else 'solver',exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest()))
    print(slug,p.returncode)
report=dict(timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%d'),python=f'{sys.version_info.major}.{sys.version_info.minor}',platform=platform.system(),scope='Isolated local run with socket connections blocked. Original challenge executables are parsed, not executed.',results=results)
report_path=ROOT/'docs/test-results.json'
temporary=report_path.with_suffix('.json.tmp')
temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
os.replace(temporary,report_path)
raise SystemExit(any(x['exit_code'] for x in results))
