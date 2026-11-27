// Close-up PNG of a region of dist/index/pcb.svg / pcb_bottom.svg. Usage: node scripts/render_closeup.cjs <svg> <out.png> <x0> <y0> <x1> <y1> [mirror]
// Board mm (Y up, board centre = origin) -> tscircuit SVG px: px = 400 + 7.1451 x, py = 300 - 7.1451 y (800 x 600 svg, no viewBox); [mirror] = bottom view (x flipped).
const { chromium } = require('playwright')
const fs = require('fs')
;(async () => {
  const [src, out, x0, y0, x1, y1, mirror] = process.argv.slice(2)
  const s = 7.1451, X = (x) => 400 + (mirror ? -x : x) * s, Y = (y) => 300 - y * s
  const xs = [X(+x0), X(+x1)].sort((a, b) => a - b), ys = [Y(+y1), Y(+y0)]
  const vb = `${xs[0]} ${ys[0]} ${xs[1] - xs[0]} ${ys[1] - ys[0]}`
  const W = 1600, H = Math.round(W * (ys[1] - ys[0]) / (xs[1] - xs[0]))
  let svg = fs.readFileSync(src, 'utf8')
  svg = svg.replace(/<svg([^>]*?)\swidth="(\d+)"\s+height="(\d+)"/, (_, a) => `<svg${a} viewBox="${vb}" width="${W}" height="${H}"`)
  const b = await chromium.launch()
  const p = await b.newPage({ viewport: { width: W, height: H } })
  await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`)
  await p.screenshot({ path: out })
  await b.close()
})()
