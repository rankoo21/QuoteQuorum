# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Multi-source quote quorum with bounded dispersion."""
from genlayer import *
from urllib.parse import urlparse
import hashlib,json

def enc(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def ident(v):
    v=v.strip().upper()
    if not 3<=len(v)<=64 or not all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in v): raise gl.vm.UserError("invalid feed ID")
    return v
def https(v):
    p=urlparse(v.strip())
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.fragment: raise gl.vm.UserError("clean HTTPS URL required")
    return v.strip()
def sources(raw):
    x=json.loads(raw)
    if type(x) is not list or not 3<=len(x)<=5: raise ValueError("three to five sources required")
    out=[]; hosts=set()
    for item in x:
        if type(item) is not dict or set(item)!={"url","path"}: raise ValueError("invalid source")
        u=https(item["url"]); host=urlparse(u).hostname.lower()
        if host in hosts: raise ValueError("source hosts must differ")
        path=item["path"]
        if type(path) is not list or not path or not all(isinstance(k,str) and k for k in path): raise ValueError("invalid JSON path")
        hosts.add(host); out.append({"url":u,"path":path})
    return out
def parse_at(body,path):
    v=json.loads(body)
    for k in path: v=v[int(k)] if isinstance(v,list) else v[k]
    return float(v)
def result(raw):
    x=json.loads(raw)
    if type(x) is not dict or set(x)!={"status","median","spread_bps","quotes"} or x["status"] not in ("CONSISTENT","OUTLIER","UNAVAILABLE"): raise ValueError("bad quote result")
    if not isinstance(x["quotes"],list) or len(x["quotes"])>5: raise ValueError("bad quotes")
    return {"status":x["status"],"median":float(x["median"]),"spread_bps":float(x["spread_bps"]),"quotes":x["quotes"]}
def assess(values,max_spread):
    if len(values)!=3: return {"status":"UNAVAILABLE","median":0.0,"spread_bps":0.0,"quotes":[]}
    # Providers can move by a few cents while validators fetch them. Commit a
    # bounded market snapshot rather than pretending raw floating point bytes
    # are stable across independent fetch times.
    values=[round(v,-2) for v in values]
    ordered=sorted(values); median=ordered[len(ordered)//2]; spread=(ordered[-1]-ordered[0])*10000/median if median else 0.0
    return {"status":"CONSISTENT" if spread<=max_spread else "OUTLIER","median":median,"spread_bps":spread,"quotes":values}

class QuoteQuorum(gl.Contract):
    feeds: TreeMap[str,str]
    def __init__(self): pass
    def key(self,o,i): return str(o).lower()+":"+ident(i)
    @gl.public.write
    def register_feed(self,feed_id:str,sources_json:str,max_spread_bps:int)->None:
        owner=str(gl.message.sender_address).lower(); key=self.key(owner,feed_id)
        if self.feeds.get(key,""): raise gl.vm.UserError("feed ID already exists")
        if not 1<=int(max_spread_bps)<=5000: raise gl.vm.UserError("invalid spread bound")
        try: src=sources(sources_json)
        except Exception: raise gl.vm.UserError("invalid source set")
        self.feeds[key]=enc({"id":ident(feed_id),"owner":owner,"sources":src,"max_spread_bps":int(max_spread_bps),"state":"OPEN","status":"","median":0.0,"spread_bps":0.0,"quotes":[],"digests":[]})
    @gl.public.write
    def sample_feed(self,feed_id:str)->None:
        key=self.key(str(gl.message.sender_address),feed_id); r=json.loads(self.feeds.get(key,"{}"))
        if not r or r["state"]!="OPEN": raise gl.vm.UserError("feed is not open")
        def run():
            bodies=[gl.nondet.web.get(s["url"]).body.decode("utf-8") for s in r["sources"]]
            vals=[parse_at(b,s["path"]) for b,s in zip(bodies,r["sources"])]
            if any(v<=0 for v in vals): raise gl.vm.UserError("quote must be positive")
            out=assess(vals,r["max_spread_bps"])
            return enc({**out,"digests":[hashlib.sha256(enc({"url":s["url"],"quote":q}).encode()).hexdigest() for s,q in zip(r["sources"],out["quotes"])]})
        def valid(x):
            if not isinstance(x,gl.vm.Return): return False
            try:
                bodies=[gl.nondet.web.get(s["url"]).body.decode("utf-8") for s in r["sources"]]; vals=[parse_at(b,s["path"]) for b,s in zip(bodies,r["sources"])]
                out=assess(vals,r["max_spread_bps"]); expected={**out,"digests":[hashlib.sha256(enc({"url":s["url"],"quote":q}).encode()).hexdigest() for s,q in zip(r["sources"],out["quotes"])]}
                return json.loads(x.calldata)==expected
            except Exception: return False
        r.update(json.loads(gl.vm.run_nondet_unsafe(run,valid))); r["state"]="SAMPLED"; self.feeds[key]=enc(r)
    @gl.public.view
    def get_feed(self,owner:str,feed_id:str)->str: return self.feeds.get(self.key(owner,feed_id),"{}")
