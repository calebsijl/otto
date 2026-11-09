/* look.js - the printed look.
   One full-screen pass over the rendered frame: quantise to a small palette,
   ordered dither, a little line work, and one accent colour kept back for fire.

   world.html wires it in four lines. Delete those four and this file and the
   world goes back to exactly how it was.

   Press P in the lane for the tuning panel. */

export const PALETTES = {
  /* these colour the BASE world only: ground, walls, roofs, sky.
     saturated things keep their own hue on top (see the vivid pass). */
  marmalade: {name:'marmalade',  ramp:['#3a1410','#9c3317','#e2701f','#f7b64a','#fff4dc'], accent:'#2b6fb5'},
  periwinkle:{name:'periwinkle', ramp:['#2b2f6b','#4a56a8','#7c89d4','#b3bce8','#eef1fb'], accent:'#ff7fc4'},
};

const DEFAULTS = {
  on: true,
  palette: 'marmalade',
  levels: 5,        // how many steps in the ramp get used
  dot: 2.0,         // dither dot size, in css pixels
  lift: 0.02,       // black point
  gain: 1.7,        // contrast before quantising
  edge: 0.35,       // line work strength
  edgeThresh: 0.06, // how big a change counts as a line
  accent: 0.0,      // a forced accent hue. off by default now that real colour survives
  accentBias: 0.34, // how warm a pixel must be to count as fire
  accentGain: 3.0,
  accentLit: 0.70,  // how bright a warm pixel must be before it counts as lit
  vivid: 1.0,       // how much saturated things keep their own colour
  satCut: 0.30,     // how saturated a thing must be to escape the ramp
  satSoft: 0.18,    // how soft that cutoff is
  vividSat: 1.25,   // chroma boost on the things that escape
  hueSteps: 8,      // snap surviving hues to this many. 0 leaves them alone
  colour: 0.0,      // driven by `strength` below; not edited directly any more
  // How much of the look is applied, kept per palette so marmalade can sit at
  // three quarters while periwinkle stays full. 1 is the full effect, 0 is the
  // world exactly as it was rendered.
  strength: {marmalade: 1.0, periwinkle: 1.0},
  encode: 1.0,      // the render target is linear; 1 encodes it back to perceptual
  scale: 1.0,       // render scale. below 1 gives chunkier pixels and more speed
};

const VERT = `
varying vec2 vUv;
void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }
`;

const FRAG = `
precision highp float;
varying vec2 vUv;
uniform sampler2D tFrame;
uniform sampler2D tPal;
uniform vec2  uRes;      // css pixels, for the dither grid
uniform vec2  uTexel;    // 1 / render target size, for the line work
uniform float uLevels;
uniform float uDot;
uniform float uLift;
uniform float uGain;
uniform float uEdge;
uniform float uEdgeThresh;
uniform float uAccent;
uniform float uAccentBias;
uniform float uAccentGain;
uniform vec3  uAccentCol;
uniform float uColour;
uniform float uEncode;
uniform float uAccentLit;
uniform float uVivid;
uniform float uSatCut;
uniform float uSatSoft;
uniform float uVividSat;
uniform float uHueSteps;

float lum(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

/* the scene lands in the target in linear light; the dither has to work in
   perceptual space or everything crushes to the dark end of the ramp */
vec3 rgb2hsv(vec3 c){
  vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
  vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
  vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
  float d = q.x - min(q.w, q.y);
  return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
}
vec3 hsv2rgb(vec3 c){
  vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
  vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
  return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 toSRGB(vec3 c){
  c = max(c, vec3(0.0));
  return mix(c * 12.92, 1.055 * pow(c, vec3(0.41666)) - 0.055, step(vec3(0.0031308), c));
}
vec3 frame(vec2 uv){
  vec3 c = texture2D(tFrame, uv).rgb;
  return uEncode > 0.5 ? toSRGB(c) : c;
}

/* ordered dither, the recursive bayer trick. gives a proper 8x8 without an array */
float bayer2(vec2 a){ a = floor(a); return fract(a.x * 0.5 + a.y * a.y * 0.75); }
float bayer4(vec2 a){ return bayer2(0.5 * a) * 0.25 + bayer2(a); }
float bayer8(vec2 a){ return bayer4(0.5 * a) * 0.25 + bayer2(a); }

void main(){
  vec3 src = frame(vUv);
  float v = lum(src);

  /* line work: how fast brightness changes around this pixel */
  float e = 0.0;
  if (uEdge > 0.001){
    float l  = lum(frame(vUv + vec2(-uTexel.x, 0.0)));
    float r  = lum(frame(vUv + vec2( uTexel.x, 0.0)));
    float u  = lum(frame(vUv + vec2(0.0,  uTexel.y)));
    float d  = lum(frame(vUv + vec2(0.0, -uTexel.y)));
    float g  = abs(r - l) + abs(u - d);
    e = smoothstep(uEdgeThresh, uEdgeThresh * 3.0, g) * uEdge;
  }

  /* levels, then quantise with the dither riding in index space */
  float g2 = clamp((v - uLift) * uGain, 0.0, 1.0);
  g2 = clamp(g2 - e, 0.0, 1.0);                 // lines push toward the dark end
  float n  = max(1.0, uLevels - 1.0);
  float th = bayer8(vUv * uRes / max(0.5, uDot)) - 0.5;
  float idx = clamp(floor(g2 * n + th + 0.5), 0.0, n);

  vec3 col = texture2D(tPal, vec2((idx + 0.5) / uLevels, 0.5)).rgb;

  /* the ramp is for the base world: ground, walls, roofs, sky. anything
     genuinely saturated keeps its own hue instead of being flattened into it,
     which is what stops a one-colour world. hue snapping keeps the survivors
     down to a handful of colours so it still reads as designed. */
  if (uVivid > 0.001){
    vec3 hsv = rgb2hsv(src);
    float h = hsv.x;
    if (uHueSteps > 0.5) h = floor(h * uHueSteps + 0.5) / uHueSteps;
    float vq = mix(0.28, 1.0, idx / n);
    vec3 vivid = hsv2rgb(vec3(h, clamp(hsv.y * uVividSat, 0.0, 1.0), vq));
    float keep = smoothstep(uSatCut, uSatCut + max(0.01, uSatSoft), hsv.y) * uVivid;
    col = mix(col, vivid, keep);
  }

  /* fire and lamplight keep the accent colour. warm is not enough on its own,
     or every brick in the lane turns red: it has to be warm AND bright */
  if (uAccent > 0.001){
    float warm = clamp((src.r - src.b) * uAccentGain - uAccentBias, 0.0, 1.0);
    warm *= smoothstep(uAccentLit, uAccentLit + 0.22, v);
    float a = step(0.5, warm + th * 0.9) * uAccent;
    col = mix(col, uAccentCol * (0.55 + 0.45 * g2), a);
  }

  col = mix(col, src, clamp(uColour, 0.0, 1.0));
  gl_FragColor = vec4(col, 1.0);
}
`;

export function makeLook(THREE, renderer, scene, camera){
  const P = Object.assign({}, DEFAULTS, loadSaved());

  /* No multisampling here. The pass quantises everything to five colour steps
     with a dither over the top and draws its own line work, so smoothed edges
     are thrown away a line later. On a retina screen the 4x buffer was costing
     well over a hundred megabytes of graphics memory for nothing, which is
     what made safari throw the whole context away. */
  const rt = new THREE.WebGLRenderTarget(1, 1);
  rt.depthBuffer = true;

  const palTex = makePalTex(THREE, P);

  const uniforms = {
    tFrame:      {value: rt.texture},
    tPal:        {value: palTex},
    uRes:        {value: new THREE.Vector2(1, 1)},
    uTexel:      {value: new THREE.Vector2(1, 1)},
    uLevels:     {value: P.levels},
    uDot:        {value: P.dot},
    uLift:       {value: P.lift},
    uGain:       {value: P.gain},
    uEdge:       {value: P.edge},
    uEdgeThresh: {value: P.edgeThresh},
    uAccent:     {value: P.accent},
    uAccentBias: {value: P.accentBias},
    uAccentGain: {value: P.accentGain},
    uAccentCol:  {value: new THREE.Color(PALETTES[P.palette].accent)},
    uColour:     {value: P.colour},
    uEncode:     {value: 1.0},
    uAccentLit:  {value: P.accentLit},
    uVivid:      {value: P.vivid},
    uSatCut:     {value: P.satCut},
    uSatSoft:    {value: P.satSoft},
    uVividSat:   {value: P.vividSat},
    uHueSteps:   {value: P.hueSteps},
  };

  const quad = new THREE.Mesh(
    new THREE.PlaneGeometry(2, 2),
    new THREE.ShaderMaterial({vertexShader: VERT, fragmentShader: FRAG, uniforms, depthTest: false, depthWrite: false})
  );
  quad.frustumCulled = false;
  const quadScene = new THREE.Scene(); quadScene.add(quad);
  const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  function makePalTex(T, p){
    const ramp = PALETTES[p.palette].ramp;
    const n = Math.max(2, Math.min(ramp.length, Math.round(p.levels)));
    const data = new Uint8Array(n * 4);
    for (let i = 0; i < n; i++){
      // spread the chosen number of steps across the whole ramp
      const f = n === 1 ? 0 : (i / (n - 1)) * (ramp.length - 1);
      const a = new T.Color(ramp[Math.floor(f)]), b = new T.Color(ramp[Math.ceil(f)]);
      const c = a.lerp(b, f - Math.floor(f));
      data[i*4] = Math.round(c.r*255); data[i*4+1] = Math.round(c.g*255);
      data[i*4+2] = Math.round(c.b*255); data[i*4+3] = 255;
    }
    const t = new T.DataTexture(data, n, 1);
    t.magFilter = t.minFilter = T.NearestFilter;
    t.needsUpdate = true;
    return t;
  }

  // how strong the look is for whichever palette is selected
  const strengthOf = () => {
    const v = P.strength && P.strength[P.palette];
    return v == null ? 1 : v;
  };
  const setStrength = v => {
    P.strength = P.strength || {};
    P.strength[P.palette] = v;
  };

  const UMAP = {levels:'uLevels', dot:'uDot', lift:'uLift', gain:'uGain', edge:'uEdge',
                edgeThresh:'uEdgeThresh', accent:'uAccent', accentBias:'uAccentBias',
                accentGain:'uAccentGain', accentLit:'uAccentLit',
                vivid:'uVivid', satCut:'uSatCut', satSoft:'uSatSoft',
                vividSat:'uVividSat', hueSteps:'uHueSteps', colour:'uColour', encode:'uEncode'};

  function sync(){
    for (const k in UMAP) if (k in P) uniforms[UMAP[k]].value = P[k];
    // the master knob is the last word: at 0 the frame comes through untouched
    uniforms.uColour.value = 1 - strengthOf();
    uniforms.uLevels.value = Math.round(P.levels);
    uniforms.uAccentCol.value.set(PALETTES[P.palette].accent);
  }

  function rebuildPalette(){
    uniforms.tPal.value.dispose();
    uniforms.tPal.value = makePalTex(THREE, P);
    uniforms.uAccentCol.value.set(PALETTES[P.palette].accent);
    uniforms.uLevels.value = Math.round(P.levels);
  }

  function resize(){
    const pr = renderer.getPixelRatio();
    const w = Math.max(1, Math.floor(innerWidth  * pr * P.scale));
    const h = Math.max(1, Math.floor(innerHeight * pr * P.scale));
    rt.setSize(w, h);
    const f = P.scale < 0.999 ? THREE.NearestFilter : THREE.LinearFilter;
    rt.texture.magFilter = rt.texture.minFilter = f;
    rt.texture.needsUpdate = true;
    uniforms.uRes.value.set(innerWidth, innerHeight);
    uniforms.uTexel.value.set(1 / w, 1 / h);
  }
  resize();
  sync();

  function render(){
    if (!P.on){ renderer.setRenderTarget(null); renderer.render(scene, camera); return; }
    renderer.setRenderTarget(rt);
    renderer.render(scene, camera);
    renderer.setRenderTarget(null);
    renderer.render(quadScene, quadCam);
  }

  /* ---------- the tuning panel, P to show it ---------- */
  function loadSaved(){
    try { return JSON.parse(localStorage.getItem('otto.look') || '{}'); } catch(e){ return {}; }
  }
  function save(){
    try { localStorage.setItem('otto.look', JSON.stringify(P)); } catch(e){}
  }

  const panel = document.createElement('div');
  panel.id = 'lookpanel';
  panel.style.cssText =
    'position:fixed;top:12px;right:12px;z-index:50;display:none;width:232px;padding:12px 13px;' +
    'background:rgba(22,20,17,.92);color:#e8e2d4;border:1px solid rgba(232,226,212,.22);border-radius:10px;' +
    'font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;backdrop-filter:blur(6px)';

  const rows = [
    ['levels',     'steps',       2,   5,   1],
    ['dot',        'dot size',    1,   6,   0.5],
    ['lift',       'black point', -0.2, 0.4, 0.01],
    ['gain',       'contrast',    0.6, 2.4, 0.05],
    ['edge',       'line work',   0,   1,   0.05],
    ['edgeThresh', 'line catch',  0.01, 0.3, 0.005],
    ['accent',     'fire accent', 0,   1,   0.05],
    ['accentBias', 'fire catch',  0,   1,   0.02],
    ['accentLit',  'fire floor',  0.2, 1,   0.02],
    ['vivid',      'keep colour', 0,   1,   0.05],
    ['satCut',     'colour cut',  0,   1,   0.02],
    ['vividSat',   'colour punch',0.5, 2,   0.05],
    ['hueSteps',   'hue steps',   0,   12,  1],
    ['scale',      'render scale',0.4, 1,   0.05],
  ];

  panel.innerHTML =
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px">' +
      '<strong style="font-weight:600;letter-spacing:.04em">the look</strong>' +
      '<label style="cursor:pointer;opacity:.85"><input id="lk_on" type="checkbox" ' +
        (P.on ? 'checked' : '') + ' style="vertical-align:-1px"> on</label>' +
    '</div>' +
    '<select id="lk_pal" style="width:100%;margin-bottom:9px;background:#2a2621;color:#e8e2d4;' +
      'border:1px solid rgba(232,226,212,.25);border-radius:5px;padding:4px;font:inherit">' +
      Object.entries(PALETTES).map(([k, v]) =>
        `<option value="${k}"${k === P.palette ? ' selected' : ''}>${v.name}</option>`).join('') +
    '</select>' +
    '<div style="margin-bottom:10px;padding-bottom:9px;' +
      'border-bottom:1px solid rgba(232,226,212,.14)">' +
      '<div style="display:flex;justify-content:space-between">' +
        '<span>effect</span><span id="lk_strength_v">' + strengthOf() + '</span></div>' +
      '<input id="lk_strength" type="range" min="0" max="1" step="0.05" ' +
        'value="' + strengthOf() + '" style="width:100%;accent-color:#c89b5c">' +
      '<div style="opacity:.5;margin-top:3px">how much of it is applied, ' +
        'saved per palette</div>' +
    '</div>' +
    rows.map(([k, label, min, max, step]) =>
      `<div style="margin-bottom:6px">` +
        `<div style="display:flex;justify-content:space-between;opacity:.8">` +
          `<span>${label}</span><span id="lk_${k}_v">${P[k]}</span></div>` +
        `<input id="lk_${k}" type="range" min="${min}" max="${max}" step="${step}" value="${P[k]}" ` +
          `style="width:100%;accent-color:#c89b5c"></div>`).join('') +
    '<button id="lk_copy" style="width:100%;margin-top:6px;padding:5px;background:#3a342c;color:#e8e2d4;' +
      'border:1px solid rgba(232,226,212,.25);border-radius:5px;font:inherit;cursor:pointer">copy settings</button>' +
    '<div style="margin-top:7px;opacity:.55">P closes this</div>';

  document.body.appendChild(panel);

  panel.querySelector('#lk_on').onchange = e => { P.on = e.target.checked; save(); };
  const strengthEl = () => panel.querySelector('#lk_strength');
  const strengthOut = () => panel.querySelector('#lk_strength_v');
  panel.querySelector('#lk_pal').onchange = e => {
    P.palette = e.target.value;
    rebuildPalette();
    // each palette keeps its own level, so the slider follows the choice
    strengthEl().value = strengthOf();
    strengthOut().textContent = strengthOf();
    sync(); save();
  };
  strengthEl().oninput = () => {
    const v = parseFloat(strengthEl().value);
    setStrength(v);
    strengthOut().textContent = v;
    sync(); save();
  };
  for (const [k] of rows){
    const el = panel.querySelector('#lk_' + k), out = panel.querySelector('#lk_' + k + '_v');
    el.oninput = () => {
      P[k] = parseFloat(el.value); out.textContent = P[k];
      if (k === 'levels') rebuildPalette();
      else if (k === 'scale') resize();
      else sync();
      save();
    };
  }
  panel.querySelector('#lk_copy').onclick = () => {
    const txt = JSON.stringify(P, null, 2);
    navigator.clipboard?.writeText(txt);
    panel.querySelector('#lk_copy').textContent = 'copied';
    setTimeout(() => { panel.querySelector('#lk_copy').textContent = 'copy settings'; }, 1200);
  };

  addEventListener('keydown', e => {
    if (e.code === 'KeyP' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '')){
      e.preventDefault();
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
  });

  const api = {render, resize, rebuildPalette, sync, params: P, panel};
  window.__look = api;        // handy for tuning from the console
  return api;
}
