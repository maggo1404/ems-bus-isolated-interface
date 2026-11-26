import json,sys,collections
cj=json.load(open('dist/scratch/ems/circuit.json'))
comp={c['source_component_id']:c['name'] for c in cj if c['type']=='source_component'}
ports={}
for p in cj:
    if p['type']=='source_port':
        ports[p['source_port_id']]=(comp.get(p.get('source_component_id'),'?'),p.get('pin_number'),p.get('name'))
nets={n['source_net_id']:n['name'] for n in cj if n['type']=='source_net'}
par={}
def f(x):
    par.setdefault(x,x)
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for t in cj:
    if t['type']=='source_trace':
        ids=list(t.get('connected_source_port_ids',[]))+list(t.get('connected_source_net_ids',[]))
        for i in ids[1:]: par[f(i)]=f(ids[0])
        if ids: f(ids[0])
groups=collections.defaultdict(set)
for k in list(par):
    g=f(k)
    if k in ports: groups[g].add(f"{ports[k][0]}.{ports[k][1]}")
    elif k in nets: groups[g].add('NET:'+nets[k])
got={}
for g,s in groups.items():
    names=[x[4:] for x in s if x.startswith('NET:')]
    pins=frozenset(x for x in s if not x.startswith('NET:'))
    got[frozenset(pins)]=names
ref=json.load(open('docs/netlist_v1.json'))
ok=True
def mapname(n):
    return {'+5V':'V5_EMS','GND':'GND_EMS','VIN':'EMS_VIN','MCUGND':'GND','MCUVCC':'V3V3','MCURX':'MCU_RX','MCUTX':'MCU_TX'}.get(n,n)
def cvt(pin):
    r,pad=pin.split('.')
    pad={'A':'1','C':'2','+':'1','-':'2'}.get(pad,pad)
    return f"{r}.{pad}"
exp={}
for n in ref['nets']:
    pins=frozenset(cvt(p) for p in n['pins'] if not p.startswith('P2.'))
    if len(pins)>=1: exp[pins]=n['name']
for pins,name in exp.items():
    if pins in got: 
        print('OK  ',name,'->',got[pins]); 
    else:
        ok=False; print('DIFF missing',name,sorted(pins))
for pins in got:
    if pins not in exp: ok=False; print('EXTRA',got[pins],sorted(pins))
print('ALL MATCH' if ok else 'MISMATCH')
