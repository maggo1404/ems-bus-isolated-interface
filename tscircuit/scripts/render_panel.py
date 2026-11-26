#!/usr/bin/env python3
"""Render the panel Gerbers (docs/img/panel.png): top view via gerbonara SVG + headless Chromium (playwright, as scripts/render_png.cjs).
Usage: python3 scripts/render_panel.py [single.zip] [panel.zip] [out.png]"""
import os, sys, subprocess, tempfile, zipfile, shutil
from gerbonara import LayerStack

single = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0-gerbers.zip"
panel = sys.argv[2] if len(sys.argv) > 2 else "fab/EMSinterface_V2.0-panel-gerbers.zip"
out = sys.argv[3] if len(sys.argv) > 3 else "docs/img/panel.png"
d = tempfile.mkdtemp(prefix="panelrender_")
with zipfile.ZipFile(panel) as z:
    z.extractall(d)
stack = LayerStack.open(d)
svg = str(stack.to_pretty_svg(side="top"))
svgf = os.path.join(d, "panel.svg")
open(svgf, "w").write(svg)
js = os.path.join(d, "shot.cjs")
open(js, "w").write("""const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:2200,height:1500},deviceScaleFactor:1});
const svg=fs.readFileSync(process.argv[2],'utf8').replace(/<svg([^>]*?)\\swidth="[^"]*"\\s+height="[^"]*"/,'<svg$1 width="2200"');
await p.setContent('<html><body style="margin:0;background:#fff">'+svg+'</body></html>');
const el=await p.$('svg');await el.screenshot({path:process.argv[3]});await b.close()})()""")
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
subprocess.run(["node", js, svgf, os.path.abspath(out)], check=True, cwd=os.getcwd(),
               env={**os.environ, "NODE_PATH": os.pathsep.join(p for p in (os.path.join(os.getcwd(), "node_modules"), subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()) if p)})
shutil.rmtree(d, ignore_errors=True)
print("render_panel:", out)
