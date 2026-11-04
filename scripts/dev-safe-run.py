#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,queue,signal,subprocess,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path

def now(): return datetime.now(timezone.utc).isoformat()
def atomic_json(p,data):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(".tmp")
    t.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(t,p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--timeout",type=int,default=1800); ap.add_argument("--heartbeat",type=int,default=20); ap.add_argument("command",nargs=argparse.REMAINDER)
    a=ap.parse_args(); cmd=a.command[1:] if a.command and a.command[0]=="--" else a.command
    if not cmd: print("缺少命令",file=sys.stderr); return 2
    root=Path(__file__).resolve().parents[1]; state=root/".dev-state"; logs=state/"logs"; logs.mkdir(parents=True,exist_ok=True)
    log=logs/f"{time.strftime('%Y%m%d-%H%M%S')}.log"; meta=state/"last-command.json"
    data={"status":"starting","command":cmd,"started_at":now(),"log":str(log.relative_to(root)),"timeout":a.timeout}; atomic_json(meta,data)
    p=subprocess.Popen(cmd,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,start_new_session=True)
    data.update({"status":"running","pid":p.pid}); atomic_json(meta,data)
    q=queue.Queue()
    def reader():
        assert p.stdout
        for line in p.stdout: q.put(line)
        q.put(None)
    threading.Thread(target=reader,daemon=True).start()
    start=last=time.monotonic(); stream=False
    with log.open("w",encoding="utf-8") as f:
        while True:
            if time.monotonic()-start>a.timeout:
                msg=f"[TIMEOUT] hard timeout after {a.timeout}s\n"; print(msg,end=""); f.write(msg); f.flush()
                try: os.killpg(p.pid,signal.SIGTERM)
                except Exception: p.terminate()
                time.sleep(1)
                if p.poll() is None:
                    try: os.killpg(p.pid,signal.SIGKILL)
                    except Exception: p.kill()
                data.update({"status":"timeout","finished_at":now(),"exit_code":124}); atomic_json(meta,data); return 124
            try:
                item=q.get(timeout=1)
                if item is None: stream=True
                else: print(item,end=""); f.write(item); f.flush(); last=time.monotonic()
            except queue.Empty: pass
            if time.monotonic()-last>=a.heartbeat and p.poll() is None:
                msg=f"[HEARTBEAT] pid={p.pid} elapsed={int(time.monotonic()-start)}s\n"; print(msg,end=""); f.write(msg); f.flush(); last=time.monotonic()
            if p.poll() is not None and stream:
                rc=p.returncode; data.update({"status":"success" if rc==0 else "failed","finished_at":now(),"exit_code":rc}); atomic_json(meta,data); return rc
if __name__=="__main__": raise SystemExit(main())
