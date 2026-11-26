const fps = ["soic8","sot23_5","sot23_6","sot23","sot223","sod123","0805","0603","1206","2010","pinrow4","pinrow4_p2.54mm","soic8_w5.3mm_p1.27mm","sod323","sma","smb","dip8_wide","ssop8"]
export default () => (
  <board width="120mm" height="120mm">
    {fps.map((f, i) => (
      <chip key={f} name={`U${i}`} footprint={f} pcbX={-50 + (i % 6) * 18} pcbY={-40 + Math.floor(i / 6) * 25} />
    ))}
  </board>
)
