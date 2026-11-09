  if (kind === 'deadtrain'){
    /* An american eight-wheeler with its tender, a carriage, and one more
       carriage that has gone into the ground. It has not moved in years and
       nothing about it is going to move again.

       Every piece is collected by colour and merged, so the whole train is
       about ten meshes rather than the three hundred it is built from. */
    const g = new THREE.Group();
    const R = () => Math.random();
    const BK = new Map();
    const put = (geo, col, px, py, pz, rot, scl) => {
      const q = geo.clone();
      if (scl) q.scale(scl[0], scl[1], scl[2]);
      if (rot) q.applyMatrix4(new THREE.Matrix4().makeRotationFromEuler(
        new THREE.Euler(rot[0] || 0, rot[1] || 0, rot[2] || 0)));
      q.translate(px, py, pz);
      if (!BK.has(col)) BK.set(col, []);
      BK.get(col).push(q);
      geo.dispose();
    };
    const bx = (c, bw, bh, bd, px, py, pz, rot) =>
      put(new THREE.BoxGeometry(bw, bh, bd), c, px, py, pz, rot);
    const cy = (c, rt, rb, hh, px, py, pz, seg, rot) =>
      put(new THREE.CylinderGeometry(rt, rb, hh, seg || 10), c, px, py, pz, rot);
    const sp = (c, r, px, py, pz, scl) =>
      put(new THREE.SphereGeometry(r, 8, 6), c, px, py, pz, null, scl);

    const BLACK = 0x221d1a, LINED = 0x2a2522, IRON = 0x1b1816;
    const RUST = 0x7a4028, RUSTD = 0x5a2f1d, MOSS = 0x4f5a34;
    const DULL = 0x6e5a33, BAND = 0x8a7342, EARTH = 0x6d5a3c;
    const BODY = 0x6d3a2a, CANVAS = 0x8e8470, DARK = 0x0d0f12;

    const wheelAt = (r, px, py, pz, n) => {
      put(new THREE.TorusGeometry(r - .03, .05, 5, 16), IRON, px, py, pz, [0, Math.PI / 2, 0]);
      put(new THREE.TorusGeometry(r - .13, .06, 5, 14), IRON, px, py, pz, [0, Math.PI / 2, 0]);
      cy(IRON, .12, .12, .2, px, py, pz, 8, [0, 0, Math.PI / 2]);
      const len = r - .18;
      for (let i = 0; i < n; i++){
        const a = i / n * Math.PI * 2;
        bx(IRON, .05, len, .05, px, py + Math.cos(a) * len / 2,
           pz + Math.sin(a) * len / 2, [a, 0, 0]);
      }
    };

    /* ---- the engine ---- */
    bx(LINED, 9.6, .26, 1.9, 1.0, 1.62, 0);
    for (const dz of [1.62, -1.62]) bx(LINED, 8.2, .12, .42, 1.2, 1.80, dz);
    cy(BLACK, .72, .72, 5.1, 1.65, 2.60, 0, 16, [0, 0, Math.PI / 2]);
    cy(BLACK, .80, .80, .9, 4.55, 2.60, 0, 16, [0, 0, Math.PI / 2]);
    cy(LINED, .78, .78, .14, 5.02, 2.60, 0, 16, [0, 0, Math.PI / 2]);
    cy(DULL, .24, .24, .07, 5.11, 2.60, 0, 12, [0, 0, Math.PI / 2]);
    for (const ax of [.3, 1.65, 3.0])
      cy(BAND, .75, .75, .09, ax, 2.60, 0, 16, [0, 0, Math.PI / 2]);

    cy(BLACK, .26, .30, .6, 3.9, 3.50, 0, 12);            // stack, split open
    cy(RUSTD, .54, .28, .74, 3.9, 4.08, 0, 14, [.1, 0, -.17]);
    cy(RUSTD, .60, .58, .09, 4.02, 4.44, .07, 14, [.22, 0, -.3]);
    sp(0x6b5a3a, .27, 3.9, 4.2, 0, [1, .45, 1]);           // something nesting

    bx(LINED, .75, .14, .14, 5.3, 3.40, 0);                // headlamp, hanging
    bx(LINED, .6, .7, .6, 5.62, 3.70, 0, [0, 0, .26]);
    cy(LINED, .02, .44, .24, 5.68, 4.16, 0, 4, [0, Math.PI / 4, .26]);
    bx(DARK, .05, .44, .44, 5.93, 3.62, 0, [0, 0, .26]);

    for (const dz of [.2, -.2]) bx(DULL, .09, .42, .09, 2.9, 3.30, dz);
    bx(DULL, .09, .09, .5, 2.9, 3.50, 0);                  // the yoke, bell gone

    for (const [ax, r] of [[2.2, .32], [1.1, .28], [0.0, .30]]){
      cy(BLACK, r, r, .42, ax, 3.45, 0, 10);
      if (ax !== 1.1) sp(DULL, r + .04, ax, 3.66, 0, [1, .6, 1]);
    }
    cy(RUSTD, .32, .32, .07, 1.5, 1.90, 1.5, 10, [.1, 0, .3]);  // the lid, off

    bx(BLACK, 2.2, 1.9, 2.4, -2.05, 2.95, 0);              // cab
    bx(RUSTD, 2.8, .12, 1.1, -2.05, 4.00, -.9);
    bx(RUSTD, 2.7, .12, .9, -2.05, 3.92, .95, [.12, 0, .05]);
    for (const dz of [1.21, -1.21])
      for (const ax of [-1.4, -2.65]){
        bx(DARK, .52, .64, .08, ax, 3.02, dz);
        cy(DARK, .26, .26, .08, ax, 3.34, dz, 10, [Math.PI / 2, 0, 0]);
      }

    for (const dz of [1.3, -1.3]){
      cy(LINED, .32, .32, 1.1, 3.5, 1.45, dz, 10, [0, 0, Math.PI / 2]);
      bx(LINED, .3, .28, .28, 2.85, 1.45, dz);
    }
    bx(IRON, 3.3, .1, .07, 1.5, .88, 1.46);
    bx(RUSTD, 3.1, .1, .07, 1.3, .34, -1.5, [0, 0, -.16]);
    for (const dz of [1.52, -1.52]) bx(IRON, 2.3, .11, .06, -1.5, .88, dz);

    bx(LINED, 2.0, .2, 2.4, 3.3, .95, 0);                  // the leading truck
    for (const ax of [2.8, 3.8]) for (const dz of [1.3, -1.3])
      wheelAt(.40, ax, .50, dz, 8);
    for (const ax of [-0.4, -2.6]) for (const dz of [1.3, -1.3]){
      if (ax === -0.4 && dz < 0) continue;                 // this one is off
      wheelAt(.78, ax, .88, dz, 12);
    }
    put(new THREE.TorusGeometry(.75, .05, 5, 16), IRON, .9, .16, -2.6, [Math.PI / 2, 0, .14]);
    cy(IRON, .12, .12, .2, .9, .16, -2.6, 8);

    bx(0x5e2a20, .3, .9, 2.7, 5.35, 1.50, 0);              // the pilot, askew
    for (let i = 0; i < 9; i++){
      if (i === 2 || i === 5 || i === 7) continue;         // slats gone
      const dz = -1.0 + i * .25;
      bx(LINED, 1.6, .1, .12, 6.15, .88, dz, [0, -dz * .22, -.52]);
    }
    for (const dz of [1.14, -1.14])
      bx(LINED, 1.6, .13, .13, 6.15, .84, dz, [0, -dz * .22, -.52]);
    cy(LINED, .05, .05, .9, 5.4, .9, .3, 6, [.25, 0, .3]);

    /* ---- the tender ---- */
    bx(LINED, 4.6, .26, 2.2, -6.0, 1.45, 0);
    bx(BLACK, 4.4, 1.7, 2.3, -6.0, 2.40, 0);
    for (const dz of [1.18, -1.18]){
      bx(DULL, 3.7, .08, .06, -6.0, 3.05, dz);
      bx(DULL, 3.7, .08, .06, -6.0, 1.80, dz);
      for (const ax of [-1.85, 1.85]) bx(DULL, .08, 1.25, .06, -6.0 + ax, 2.42, dz);
    }
    for (let i = 0; i < 14; i++)                           // weeds where the coal was
      cy(MOSS, 0, .07, .45 + R() * .5, -7.9 + R() * 3.8, 3.4, (R() - .5) * 1.8, 4);
    for (const bxp of [-4.5, -7.5]){
      bx(LINED, 1.6, .18, 2.4, bxp, 1.05, 0);
      for (const dx of [-.5, .5]) for (const dz of [1.3, -1.3])
        wheelAt(.40, bxp + dx, .50, dz, 8);
    }

    /* ---- rust, and weeds through all of it ---- */
    for (const [ax, ay, dz, bw, bh] of [[.9,2.9,1,1.1,.5],[2.6,2.3,1,.9,.6],
                                        [-2.3,3.2,-1,.8,.5],[4.5,2.2,-1,.7,.5]])
      bx(RUST, bw, bh, .06, ax, ay, dz > 0 ? .68 : -.68);
    for (const [ax, dz] of [[-5.2,1.19],[-6.6,1.19],[-5.8,-1.19],[-7.0,-1.19]])
      bx(RUST, .55, .6, .05, ax, 2.5, dz);
    for (const [ax, dz] of [[-5.4,1.2],[-6.4,1.2],[-6.0,-1.2]])
      bx(RUSTD, .1, .9, .04, ax, 1.95, dz);
    bx(RUST, .08, 2.0, 1.4, -3.35, 1.3, 1.15, [0, 0, .22]);
    for (let i = 0; i < 30; i++)
      cy(MOSS, 0, .06, .4 + R() * .55, -8.0 + R() * 14.0, .24, (R() - .5) * 3.0, 4);

    /* ---- a carriage, and one that has gone into the ground ---- */
    const carriage = (cx, sunk) => {
      const rz = sunk ? .10 : 0, dy = sunk ? -1.35 : 0;
      const ca = Math.cos(rz), sa = Math.sin(rz);
      // the sunk one is pitched about its own centre, so every piece is turned
      // and moved by the same amount rather than sheared into place
      const AX = (px, py) => cx + (px * ca - py * sa);
      const AY = (px, py) => dy + (px * sa + py * ca);
      const rot = extra => [0, extra || 0, rz];

      bx(LINED, 7.0, .32, 2.6, AX(0, .95), AY(0, .95), 0, rot());
      bx(BODY, 6.8, 2.1, 2.5, AX(0, 2.2), AY(0, 2.2), 0, rot());
      for (const [rx, len] of [[-2.4, 1.9], [0.5, 1.5], [2.8, 1.2]])
        cy(CANVAS, 1.3, 1.3, len, AX(rx, 3.1), AY(rx, 3.1), 0, 12,
           [0, 0, Math.PI / 2 + rz]);
      bx(RUSTD, 1.1, .07, 2.3, AX(1.85, 2.98), AY(1.85, 2.98), 0, rot());
      for (const dz of [1.27, -1.27])
        for (let i = 0; i < 5; i++){
          const gx = -2.6 + i * 1.3;
          bx(DARK, .82, .8, .08, AX(gx, 2.5), AY(gx, 2.5), dz, rot());
          bx(0xd3c6ad, .92, .9, .06, AX(gx, 2.5), AY(gx, 2.5),
             dz + (dz > 0 ? .06 : -.06), rot());
        }
      if (!sunk)
        for (const b of [-2.3, 2.3])
          for (const dx of [-.6, .6]) for (const dz of [1.25, -1.25])
            wheelAt(.5, cx + b + dx, .6, dz, 8);
      bx(BODY, .1, 1.7, 1.0, AX(3.25, 1.95), AY(3.25, 1.95), 1.65, rot(.95));
      for (let i = 0; i < 16; i++)                          // ivy up the far end
        sp(MOSS, .17, cx - 3.45 + R() * .55, dy + 1.1 + R() * 2.1,
           -1.35 + R() * 2.7);
      if (sunk){
        bx(0x2b2a22, 2.3, .45, 2.32, AX(-2.4, 2.95), AY(-2.4, 2.95), 0, rot());
        // the earth heaped along it, which sits on the ground, not on the car
        bx(EARTH, 9.2, .55, 3.2, cx + .2, .12, 0);
        for (const dz of [2.05, -2.05])
          bx(EARTH, 9.6, 1.15, 1.6, cx + .2, .3, dz, [0, 0, .05]);
        bx(EARTH, 3.8, 1.5, 5.4, cx - 4.5, .35, 0, [0, 0, .13]);
        for (let i = 0; i < 40; i++)
          cy(MOSS, 0, .07, .4 + R() * .6, cx - 4.8 + R() * 10.4, .6,
             (R() - .5) * 4.8, 4);
      }
    };
    carriage(-12.2, false);
    carriage(-19.8, true);

    for (const [col, parts] of BK){
      const m = new THREE.Mesh(mergeGeometries(parts, false),
        new THREE.MeshStandardMaterial({color:col, roughness:.92}));
      m.castShadow = m.receiveShadow = true; g.add(m);
      for (const q of parts) q.dispose();
    }
    return g;
  }

  if (kind === 'stationclock'){
    const g = new THREE.Group();
    const iron = new THREE.MeshStandardMaterial({color:0x2b2724, roughness:.85});
    const put = (geo, m, px, py, pz, rz) => {
      const e = new THREE.Mesh(geo, m); e.position.set(px, py, pz);
      if (rz) e.rotation.z = rz; e.castShadow = true; g.add(e); return e;
    };
    put(new THREE.BoxGeometry(.13, 2.4, .13), iron, 0, 1.2, 0);
    put(new THREE.BoxGeometry(.5, .12, .12), iron, .25, 2.35, 0);
    const face = put(new THREE.CylinderGeometry(.42, .42, .1, 18),
      new THREE.MeshStandardMaterial({color:0xe8ddc4, roughness:.9}), .5, 2.3, 0);
    face.rotation.x = Math.PI / 2;
    const rim = new THREE.Mesh(new THREE.TorusGeometry(.45, .05, 5, 18), iron);
    rim.position.set(.5, 2.3, 0); g.add(rim);
    // twenty past four, and nobody has wound it either way
    const hand = (len, wide, ang) => {
      const m = put(new THREE.BoxGeometry(wide, len, .03),
        new THREE.MeshStandardMaterial({color:0x241a14}),
        .5 + Math.sin(ang) * len / 2, 2.3 + Math.cos(ang) * len / 2, .07);
      m.rotation.z = -ang; return m;
    };
    hand(.22, .05, 2.269);
    hand(.34, .04, 2.094);
    return g;
  }

