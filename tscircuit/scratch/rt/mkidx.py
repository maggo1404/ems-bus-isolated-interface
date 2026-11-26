import sys,re
name,battrs=sys.argv[1],sys.argv[2]
s=open("index.circuit.tsx").read()
s=s.replace('./src/','../../src/').replace('layers={2} borderRadius="2mm">','layers={2} borderRadius="2mm" '+battrs+'>')
open(f"scratch/rt/{name}.circuit.tsx","w").write(s)
