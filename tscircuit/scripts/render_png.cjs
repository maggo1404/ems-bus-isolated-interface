// Render dist/index/{pcb,schematic}.svg to PNG (docs/img). Usage: node scripts/render_png.cjs [outdir]
const { chromium } = require('playwright')
const fs = require('fs'), path = require('path')
;(async () => {
  const out = process.argv[2] || 'docs/img'
  fs.mkdirSync(out, { recursive: true })
  const b = await chromium.launch()
  for (const [name, f] of [['pcb', 'dist/index/pcb.svg'], ['schematic', 'dist/index/schematic.svg']]) {
    let svg = fs.readFileSync(f, 'utf8')
    const m = svg.match(/viewBox="([^"]+)"/) ; const w = +(svg.match(/<svg[^>]*\swidth="(\d+)/)||[])[1] || 1200, h = +(svg.match(/<svg[^>]*\sheight="(\d+)/)||[])[1] || 800
    const K = 2 // CSS scale-up of the SVG (no viewBox in tscircuit output)
    svg = svg.replace(/<svg([^>]*?)\swidth="(\d+)"\s+height="(\d+)"/, (_, a, W, H) => `<svg${a} viewBox="0 0 ${W} ${H}" width="${W*K}" height="${H*K}"`)
    const p = await b.newPage({ viewport: { width: w*K, height: h*K }, deviceScaleFactor: 2 })
    await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`)
    await p.screenshot({ path: path.join(out, name + '.png'), clip: { x: 0, y: 0, width: w*K, height: h*K } })
    console.log(name, w, h)
  }
  await b.close()
})()
