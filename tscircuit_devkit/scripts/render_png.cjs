// Render dist/index/{pcb,schematic}.svg to PNG (docs/img). Usage: node scripts/render_png.cjs [outdir]
const { chromium } = require('playwright')
const fs = require('fs'), path = require('path')
// the default tscircuit schematic.svg is only 1200 x 600 px: re-render it large (the schematic is ~100 x 43 schematic units)
try { const { convertCircuitJsonToSchematicSvg } = require('circuit-to-svg'); fs.writeFileSync('dist/index/schematic.svg', convertCircuitJsonToSchematicSvg(JSON.parse(fs.readFileSync('dist/index/circuit.json', 'utf8')), { width: 6400, height: 2900 })) } catch (e) { console.log('schematic re-render skipped', e.message) }
;(async () => {
  const out = process.argv[2] || 'docs/img'
  fs.mkdirSync(out, { recursive: true })
  const b = await chromium.launch()
  for (const [name, f] of [['pcb', 'dist/index/pcb.svg'], ['pcb_bottom', 'dist/index/pcb_bottom.svg'], ['schematic', 'dist/index/schematic.svg'], ['assembly', 'dist/index/assembly.svg']]) {
    if (!fs.existsSync(f)) continue
    let svg = fs.readFileSync(f, 'utf8')
    const m = svg.match(/viewBox="([^"]+)"/) ; const w = +(svg.match(/<svg[^>]*\swidth="(\d+)/)||[])[1] || 1200, h = +(svg.match(/<svg[^>]*\sheight="(\d+)/)||[])[1] || 800
    const K = name === 'schematic' ? 1 : 2 // CSS scale-up of the SVG (no viewBox in tscircuit output)
    svg = svg.replace(/<svg([^>]*?)\swidth="(\d+)"\s+height="(\d+)"/, (_, a, W, H) => `<svg${a} viewBox="0 0 ${W} ${H}" width="${W*K}" height="${H*K}"`)
    const p = await b.newPage({ viewport: { width: w*K, height: h*K }, deviceScaleFactor: 2 })
    await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`)
    await p.screenshot({ path: path.join(out, name + '.png'), clip: { x: 0, y: 0, width: w*K, height: h*K } })
    console.log(name, w, h)
  }
  await b.close()
})()
