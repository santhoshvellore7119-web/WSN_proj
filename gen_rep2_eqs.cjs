
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');
const fs = require('fs');

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const tex = new TeX({ packages: AllPackages });
const svg = new SVG({ fontCache: 'none' });
const html = mathjax.document('', { InputJax: tex, OutputJax: svg });

const eqs = [
  String.raw`B(P) = \min\left( E_{\mathrm{proj}}(v_0, t_0),\; \min_{1 \le i < k} \left[ E_{\mathrm{proj}}(v_i, t_i) - E_{\mathrm{rx}} \right] \right)`,
  String.raw`P^{*} = \arg\max_{P,\ |P| \le H} B(P) \quad \text{subject to} \quad E_{\mathrm{proj}}(v_i, t_i) \ge E_{\mathrm{tx}}\big(k, d(v_i, v_{i+1})\big)`,
  String.raw`dp[v][h][t] = \max_{u \in \mathrm{nbr}(v)} \min\left( dp[u][h-1][t-\delta],\; E_{\mathrm{proj}}(v, t) - E_{\mathrm{rx}} \right)`,
  String.raw`T(n) = \frac{p}{1 - p\,(r \bmod 1/p)} \cdot \frac{E_n + \beta H_n}{E_{\mathrm{avg}} + \beta H_{\mathrm{avg}}}`,
  String.raw`E_{\mathrm{tx}}(k,d) = \begin{cases} k E_{\mathrm{elec}} + k\,\varepsilon_{\mathrm{fs}}\, d^{2} & d < d_0 \\ k E_{\mathrm{elec}} + k\,\varepsilon_{\mathrm{mp}}\, d^{4} & d \ge d_0 \end{cases} \qquad E_{\mathrm{rx}}(k) = k E_{\mathrm{elec}}`,
  String.raw`\max_{\pi,\, w} \sum_{(u, v) \in \pi} \log P\left( E_{\mathrm{bel}}(u, t) \ge E_{\mathrm{tx}}\big(k, d(u, v)\big) \right)`,
  String.raw`B(P_{\mathrm{DP}}) \;\ge\; B_{\mathrm{proj}}(P_{\mathrm{DP}}) - \varepsilon \;\ge\; B_{\mathrm{proj}}(P^{*}) - \varepsilon \;\ge\; B(P^{*}) - 2\varepsilon`
];

eqs.forEach((eq, idx) => {
  const node = html.convert(eq, { display: true });
  const svgString = adaptor.innerHTML(node);
  fs.writeFileSync(`rep2_eq_${idx + 1}.svg`, svgString, 'utf8');
});
