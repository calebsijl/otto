/* ---------- the station ----------
   A victorian country station: cast iron columns with the fan of tracery
   under the canopy, a dagged valance, a barrel roof glazed along its spine,
   diamond tiles, a clock tower, and one wooden carriage standing at the
   platform with no engine anywhere, because nothing has run here in years.

   Built in its own coordinates and then scaled by p.scale, so the whole
   thing is one number to resize. Everything is merged by colour: the station
   is about twenty meshes, not two thousand.

   The clock hands are the exception. They are their own meshes on a pivot,
   and the frame loop turns them to his own clock, so he can tell the time by
   looking at the tower. */
const STATION_CLOCKS = [];
const CLOCK_HAND_MAT = new THREE.MeshStandardMaterial({color:0x241a14, roughness:.9});

BUILDERS.station = function(id, p){
  const [x,,z] = p.pos;
  const gy = landHeight(x, z);
  const tag = {name:p.name, note:p.description, id};
  const S = p.scale || 0.5;

  const grp = new THREE.Group();
  grp.position.set(x, gy, z);
  grp.scale.setScalar(S);
  worldGroup.add(grp);

  const C = {wood:0x8a3d1c, woodDark:0x5e2812, woodTrim:0xa8542a, gold:0xcf9b3a,
             roofLead:0x8b9496, under:0x241f1c, iron:0x2d3a37, ironLit:0x3c4c48,
             glass:0x9fc2d2, stone:0xa89a86, brick:0x8c4a33, roof:0x4e4038,
             tileA:0xcfc3ad, tileB:0x4a4440, ballast:0x4f4639, rail:0x6b4a33,
             face:0xe8ddc4, weed:0x5e7034};

  const B = new Map();
  const put = (geo, col, px, py, pz, rot, scl) => {
    const q = geo.clone();
    if (scl) q.scale(scl[0], scl[1], scl[2]);
    if (rot) q.applyMatrix4(new THREE.Matrix4().makeRotationFromEuler(
      new THREE.Euler(rot[0]||0, rot[1]||0, rot[2]||0)));
    q.translate(px, py, pz);
    if (!B.has(col)) B.set(col, []);
    B.get(col).push(q);
    geo.dispose();
  };
  const bx = (c,w,h,d,px,py,pz,rot) => put(new THREE.BoxGeometry(w,h,d), c,px,py,pz,rot);
  const cy = (c,r0,r1,h,px,py,pz,seg,rot) =>
    put(new THREE.CylinderGeometry(r0,r1,h,seg||10), c,px,py,pz,rot);
  const sp = (c,r,px,py,pz,scl) => put(new THREE.SphereGeometry(r,9,7), c,px,py,pz,null,scl);
  const to = (c,R,t,px,py,pz,arc,rot,seg) =>
    put(new THREE.TorusGeometry(R,t,5,seg||16, arc===undefined?Math.PI*2:arc),
        c,px,py,pz,rot);

  const TRACK = -6.5, GAUGE = 1.35, PY = 1.0, EDGE = -3.4;

  /* the line, running left to right and away both ways */
  bx(C.ballast, 120, .3, 6.4, 0, .15, TRACK);
  for (let i = -42; i <= 42; i++) bx(0x4e4034, .34, .14, 3.2, i*1.4, .32, TRACK);
  for (const s of [-1,1]) bx(C.rail, 120, .18, .16, 0, .46, TRACK + s*GAUGE);
  for (let i = 0; i < 80; i++)
    cy(C.weed, 0, .08, .3 + Math.random()*.4, (Math.random()-.5)*110, .45,
       TRACK + (Math.random()-.5)*2.6, 4);

  /* platform and its diamond tiling */
  bx(0x8c7f6d, 46, PY, 15, 0, PY/2, 4.2);
  bx(0x6f665a, 46, PY + .06, .5, 0, PY/2, EDGE - .25);
  bx(0xd8cdb4, 46, .05, .36, 0, PY + .03, EDGE + .5);
  for (let i = -19; i <= 19; i++)
    for (let j = 0; j < 10; j++)
      bx((i+j) % 2 ? C.tileA : C.tileB, .83, .06, .83, i*1.15, PY+.03,
         EDGE + 1.4 + j*1.15, [0, Math.PI/4, 0]);

  /* the iron columns, and the fan of tracery that is the whole character */
  for (let n = -4; n <= 4; n++){
    const cx2 = n*5.2, cz = EDGE + 1.1, h = 3.6;
    bx(C.iron, 1.0, .22, 1.0, cx2, PY+.11, cz);
    cy(C.iron, .34, .42, .4, cx2, PY+.38, cz, 12);
    cy(C.iron, .2, .24, h, cx2, PY+.58+h/2, cz, 12);
    for (let i = 0; i < 8; i++)
      cy(C.ironLit, .028, .028, h*.9, cx2 + Math.cos(i/8*6.28)*.21,
         PY+.58+h/2, cz + Math.sin(i/8*6.28)*.21, 4);
    cy(C.iron, .38, .26, .34, cx2, PY+.6+h, cz, 12);
    bx(C.iron, .9, .18, .9, cx2, PY+.82+h, cz);
    for (const s of [-1, 1]){
      const R = 1.5, base = PY + .72 + h;
      to(C.ironLit, R, .055, cx2, base - R + .1, cz, Math.PI/2,
         [0, 0, s > 0 ? 0 : Math.PI/2], 12);
      for (let i = 1; i < 6; i++){
        const a = i/6 * Math.PI/2;
        cy(C.ironLit, .035, .035, R, cx2 + s*Math.sin(a)*R/2,
           base - R + .1 + Math.cos(a)*R/2, cz, 4, [0, 0, s*a]);
      }
      sp(C.ironLit, .12, cx2 + s*.5, base - .1, cz);
    }
  }

  /* the barrel canopy, glazed along the spine, dagged along the edge */
  const H = 5.6, Z0 = EDGE - .4, Z1 = 11.4, SEG = 7, span = Z1 - Z0;
  for (let i = 0; i < SEG; i++){
    const t0 = i/SEG, t1 = (i+1)/SEG;
    const z0 = Z0 + span*t0, z1 = Z0 + span*t1;
    const y0 = H + Math.sin(Math.PI*t0)*1.5, y1 = H + Math.sin(Math.PI*t1)*1.5;
    const mz = (z0+z1)/2, my = (y0+y1)/2;
    const len = Math.hypot(z1-z0, y1-y0), ang = Math.atan2(y1-y0, z1-z0);
    bx(C.roof, 46, .16, len, 0, PY+my, mz, [-ang, 0, 0]);
    if (i === 3) bx(C.glass, 46, .05, len*.8, 0, PY+my+.12, mz, [-ang, 0, 0]);
    for (let c = -19; c <= 19; c += 2)
      bx(C.iron, .14, .22, len, c*1.15, PY+my-.14, mz, [-ang, 0, 0]);
  }
  for (let i = -22; i <= 22; i++){
    bx(C.iron, .46, .5, .1, i*1.0, PY+H-.3, Z0);
    bx(C.iron, .14, .78, .1, i*1.0+.5, PY+H-.44, Z0);
  }
  bx(C.iron, 46, .2, .18, 0, PY+H+.02, Z0);

  /* a clock whose hands actually turn */
  const clockHands = (px, py, pz, R, faceY) => {
    const pivot = new THREE.Group();
    pivot.position.set(px, py, pz); pivot.rotation.y = faceY;
    const hand = (len, wide, lift) => {
      const geo = new THREE.BoxGeometry(wide, len, .04);
      geo.translate(0, len/2, lift);
      const m = new THREE.Mesh(geo, CLOCK_HAND_MAT);
      m.castShadow = true; pivot.add(m); return m;
    };
    const c = {hour: hand(R*.52, R*.13, R*.13), minute: hand(R*.84, R*.09, R*.15)};
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(R*.08, R*.08, .06, 8),
                               CLOCK_HAND_MAT);
    cap.rotation.x = Math.PI/2; cap.position.z = R*.16; pivot.add(cap);
    grp.add(pivot); STATION_CLOCKS.push(c);
  };

  /* the building, and its tower */
  const BZ = 14.5, BH = 9;
  bx(C.brick, 40, BH, 7, 0, PY + BH/2, BZ);
  bx(C.stone, 41, .7, 7.6, 0, PY + BH + .2, BZ);
  bx(C.roof, 41.5, .5, 8.4, 0, PY + BH + .8, BZ);
  for (const px of [-16, -8, 0, 8, 16]) bx(C.stone, 1.2, BH, .4, px, PY + BH/2, BZ - 3.7);
  for (let i = -6; i <= 6; i++){
    const px = i*2.9, isDoor = (i === -3 || i === 0 || i === 3);
    const h2 = isDoor ? 4.2 : 3.2, py = PY + h2/2 + (isDoor ? 0 : 1.6);
    bx(isDoor ? 0x3a2a20 : C.glass, 1.7, h2, .22, px, py, BZ - 3.6);
    bx(C.stone, 2.1, .28, .3, px, py + h2/2 + .1, BZ - 3.62);
    to(C.stone, .95, .17, px, py + h2/2 + .1, BZ - 3.62, Math.PI, null, 12);
    bx(C.stone, .22, h2, .3, px - 1.0, py, BZ - 3.62);
    bx(C.stone, .22, h2, .3, px + 1.0, py, BZ - 3.62);
  }
  const TX = -19.5, TH = 17, CY2 = PY + TH - 2.6;
  bx(C.brick, 6.2, TH, 6.2, TX, PY + TH/2, BZ - 1);
  bx(C.stone, 7, .6, 7, TX, PY + TH + .2, BZ - 1);
  for (const [dx, dz, ry] of [[0,-3.3,Math.PI],[0,3.3,0],
                              [-3.3,0,-Math.PI/2],[3.3,0,Math.PI/2]]){
    const flat = (ry === 0 || ry === Math.PI);
    cy(C.face, 1.5, 1.5, .22, TX+dx, CY2, BZ-1+dz, 18,
       [Math.PI/2, 0, flat ? 0 : Math.PI/2]);
    to(C.stone, 1.72, .22, TX+dx, CY2, BZ-1+dz, undefined, [0, ry, 0], 18);
    for (let i = 0; i < 12; i++){
      const a = i/12 * Math.PI*2, ox = Math.sin(a)*1.22, oy = Math.cos(a)*1.22;
      bx(0x3a2a20, flat ? .1 : .06, i % 3 ? .16 : .26, flat ? .06 : .1,
         TX+dx + (flat ? ox : (dx > 0 ? .13 : -.13)), CY2 + oy,
         BZ-1+dz + (flat ? (dz > 0 ? .13 : -.13) : ox));
    }
    clockHands(TX + dx + (flat ? 0 : (dx > 0 ? .14 : -.14)), CY2,
               BZ - 1 + dz + (flat ? (dz > 0 ? .14 : -.14) : 0), 1.5, ry);
  }
  bx(C.roof, 7.4, .4, 7.4, TX, PY + TH + .6, BZ - 1);
  cy(C.roof, 0, 5.4, 4.6, TX, PY + TH + 3.1, BZ - 1, 4, [0, Math.PI/4, 0]);
  cy(C.gold, .09, .09, 1.4, TX, PY + TH + 6.0, BZ - 1, 6);
  sp(C.gold, .3, TX, PY + TH + 6.8, BZ - 1);

  /* the hanging clock, out over the platform edge */
  bx(C.iron, .1, 1.0, .1, 6, PY + 4.9, EDGE + 1.1);
  for (const s of [-1, 1]){
    cy(C.face, .78, .78, .16, 6, PY + 4.1, EDGE + 1.1 + s*.1, 16, [Math.PI/2, 0, 0]);
    to(C.iron, .9, .1, 6, PY + 4.1, EDGE + 1.1 + s*.1, undefined, null, 16);
  }
  clockHands(6, PY + 4.1, EDGE + 1.28, .78, 0);
  clockHands(6, PY + 4.1, EDGE + 0.92, .78, Math.PI);

  /* benches, looking at the rails */
  for (const px of [-13, -2.5, 8.5]){
    const bz = 6.0;
    for (const dx of [-1.0, 1.0]){
      bx(C.iron, .11, .44, .62, px + dx, PY + .22, bz);
      bx(C.iron, .16, .07, .74, px + dx, PY + .035, bz);
      bx(C.iron, .1, .62, .09, px + dx, PY + .74, bz + .42, [-.22, 0, 0]);
    }
    for (let i = 0; i < 4; i++)
      bx(0x6b5134, 2.1, .06, .14, px, PY + .46, bz - .27 + i*.18);
    for (let i = 0; i < 3; i++)
      bx(0x6b5134, 2.1, .13, .07, px, PY + .62 + i*.25, bz + .34 + i*.07, [-.22, 0, 0]);
  }

  /* bracket lamps, which come up at dusk like the ones on the river walk */
  for (let n = -3; n <= 3; n += 2){
    const px = n*5.2, pz = EDGE + 1.1, ly = PY + 4.2;
    bx(C.iron, .1, .1, 1.1, px, ly, pz + .55);
    to(C.ironLit, .45, .05, px, ly - .2, pz + .3, Math.PI/2, [0,0,0], 10);
    cy(C.iron, .18, .12, .22, px, ly + .34, pz + 1.05, 8);
    const glassMat = new THREE.MeshStandardMaterial({color:0x2a2420,
      emissive:new THREE.Color(0xff7a24), emissiveIntensity:2.2, roughness:.4});
    const g2 = new THREE.Mesh(new THREE.BoxGeometry(.42,.56,.42), glassMat);
    g2.position.set(px, ly - .12, pz + 1.05); grp.add(g2);
    const l = new THREE.PointLight(0xff7a24, 9, 11/S, 2);
    l.position.copy(g2.position); grp.add(l);
    lamps.push({win:{material:{color:{setHex(){}}}}, glow:l});
    EMBERS.push(glassMat);
  }

  /* ---- the carriage. wooden, varnished, and on its own ---- */
  const cx = -1, L = 15, W = 2.9, FLOOR = PY + .28, BODY = 2.9, bodyL = L - 3.4;
  bx(C.under, L, .5, W - .2, cx, FLOOR - .3, TRACK);
  for (const s of [-1, 1]) bx(C.under, L - 2, .1, .1, cx, FLOOR - .85, TRACK + s*.7);
  bx(C.wood, bodyL, BODY, W, cx, FLOOR + BODY/2, TRACK);
  for (const s of [-1, 1]){
    const zz = TRACK + s*(W/2 + .03);
    bx(C.woodDark, bodyL, .22, .07, cx, FLOOR + .35, zz);
    bx(C.woodDark, bodyL, .22, .07, cx, FLOOR + 1.15, zz);
    bx(C.woodDark, bodyL, .18, .07, cx, FLOOR + BODY - .2, zz);
    bx(C.gold, bodyL - 1.2, .1, .05, cx, FLOOR + .74, zz);
    for (let i = 0; i <= 10; i++)
      bx(C.woodDark, .16, .78, .06, cx - bodyL/2 + .6 + i*(bodyL-1.2)/10, FLOOR + .75, zz);
    for (let i = 0; i < 10; i++){
      const wx = cx - bodyL/2 + .95 + i*(bodyL-1.9)/9;
      bx(C.glass, .72, 1.25, .06, wx, FLOOR + 1.92, zz);
      bx(C.woodTrim, .86, .1, .05, wx, FLOOR + 2.6, zz);
      bx(C.glass, .72, .38, .06, wx, FLOOR + 2.82, zz);
      bx(C.woodTrim, .1, 1.72, .05, wx - .43, FLOOR + 2.2, zz);
      bx(C.woodTrim, .1, 1.72, .05, wx + .43, FLOOR + 2.2, zz);
    }
  }
  for (const s of [-1, 1]) bx(C.woodDark, .12, BODY, W, cx + s*bodyL/2, FLOOR + BODY/2, TRACK);
  for (let i = 0; i < 5; i++){
    const t0 = i/5, t1 = (i+1)/5;
    const z0 = TRACK - W/2 + W*t0, z1 = TRACK - W/2 + W*t1;
    const y0 = Math.sin(Math.PI*t0)*.34, y1 = Math.sin(Math.PI*t1)*.34;
    const mz = (z0+z1)/2, my = (y0+y1)/2;
    const len = Math.hypot(z1-z0, y1-y0), ang = Math.atan2(y1-y0, z1-z0);
    bx(C.roofLead, L, .14, len, cx, FLOOR + BODY + my + .05, mz, [-ang, 0, 0]);
  }
  bx(C.wood, bodyL - .6, .5, W - 1.5, cx, FLOOR + BODY + .6, TRACK);
  for (const s of [-1, 1])
    for (let i = 0; i < 12; i++)
      bx(C.glass, .34, .22, .05, cx - bodyL/2 + .9 + i*(bodyL-2.2)/11,
         FLOOR + BODY + .62, TRACK + s*(W/2 - .74));
  for (let i = 0; i < 5; i++){
    const t0 = i/5, t1 = (i+1)/5, w2 = W - 1.3;
    const z0 = TRACK - w2/2 + w2*t0, z1 = TRACK - w2/2 + w2*t1;
    const y0 = Math.sin(Math.PI*t0)*.22, y1 = Math.sin(Math.PI*t1)*.22;
    const mz = (z0+z1)/2, my = (y0+y1)/2;
    const len = Math.hypot(z1-z0, y1-y0), ang = Math.atan2(y1-y0, z1-z0);
    bx(C.roofLead, bodyL - .4, .12, len, cx, FLOOR + BODY + .88 + my, mz, [-ang, 0, 0]);
  }
  for (const s of [-1, 1]){
    const ex = cx + s*(bodyL/2 + .85);
    bx(C.under, 1.7, .22, W - .3, ex, FLOOR - .08, TRACK);
    bx(C.roofLead, 1.9, .16, W + .3, ex + s*.1, FLOOR + BODY + .42, TRACK);
    for (const zz of [TRACK - W/2 + .2, TRACK + W/2 - .2])
      cy(C.iron, .07, .07, BODY + .4, ex + s*.72, FLOOR + BODY/2 + .2, zz, 6);
    to(C.iron, .62, .055, ex + s*.72, FLOOR + 1.1, TRACK, Math.PI,
       [Math.PI/2, 0, s > 0 ? 0 : Math.PI], 12);
    bx(C.iron, 1.5, .06, .06, ex, FLOOR + 1.1, TRACK - W/2 + .2);
    bx(C.iron, 1.5, .06, .06, ex, FLOOR + 1.1, TRACK + W/2 - .2);
    for (let i = 0; i < 3; i++)
      bx(C.under, 1.1, .1, .5, ex, FLOOR - .32 - i*.34, TRACK - W/2 - .35 - i*.12);
    if (s > 0){
      cy(C.iron, .06, .06, 1.5, ex + .45, FLOOR + .7, TRACK + .8, 6);
      to(C.iron, .34, .05, ex + .45, FLOOR + 1.5, TRACK + .8, undefined,
         [Math.PI/2, 0, 0], 12);
      for (let i = 0; i < 4; i++)
        bx(C.iron, .06, .62, .06, ex + .45, FLOOR + 1.5, TRACK + .8,
           [Math.PI/2, 0, i/4*Math.PI]);
    }
    bx(0x5e2a20, .22, .6, W - .4, ex + s*.95, FLOOR - .18, TRACK);
  }
  for (const bxp of [cx - L/2 + 3.2, cx + L/2 - 3.2]){
    bx(C.under, 3.2, .34, 1.9, bxp, FLOOR - .72, TRACK);
    for (const wx of [bxp - .95, bxp + .95])
      for (const s of [-1, 1]){
        const zz = TRACK + s*GAUGE;
        to(0x1b1816, .44, .07, wx, .55, zz, undefined, [0, Math.PI/2, 0], 12);
        to(0x1b1816, .3, .06, wx, .55, zz, undefined, [0, Math.PI/2, 0], 10);
        cy(0x1b1816, .1, .1, .2, wx, .55, zz, 8, [0, 0, Math.PI/2]);
        for (let i = 0; i < 8; i++){
          const a = i/8*6.283;
          bx(0x1b1816, .05, .3, .05, wx, .55 + Math.cos(a)*.17, zz + Math.sin(a)*.17,
             [a, 0, 0]);
        }
      }
  }

  /* out it goes, merged by colour */
  for (const [col, parts] of B){
    const m = new THREE.Mesh(mergeGeometries(parts, false),
      new THREE.MeshStandardMaterial({color:col, roughness:.92}));
    m.castShadow = m.receiveShadow = true;
    m.userData = tag; grp.add(m); pickable.push(m);
    for (const q of parts) q.dispose();
  }

  /* you cannot walk through the building, the tower or the carriage */
  const block = (x0, x1, z0, z1) => BLOCKS.push({
    x: x + (x0 + x1)/2 * S, z: z + (z0 + z1)/2 * S,
    hx: Math.abs(x1 - x0)/2 * S, hz: Math.abs(z1 - z0)/2 * S});
  block(-20, 20, BZ - 3.5, BZ + 3.5);
  block(TX - 3.1, TX + 3.1, BZ - 4.1, BZ + 2.1);
  block(cx - L/2, cx + L/2, TRACK - W/2, TRACK + W/2);
};
