BUILDERS.station = function(id, p){
  const [x,,z] = p.pos, [w,h,d] = p.size;
  const gy = landHeight(x, z);
  const tag = {name:p.name, note:p.description, id};
  const M = (c, r = .95) => new THREE.MeshStandardMaterial({color:c, roughness:r});
  const add = (mesh, collide) => {
    mesh.castShadow = mesh.receiveShadow = true;
    mesh.userData = tag; worldGroup.add(mesh); pickable.push(mesh);
    if (collide){
      mesh.updateMatrixWorld(true);
      const bb = new THREE.Box3().setFromObject(mesh);
      BLOCKS.push({x:(bb.min.x+bb.max.x)/2, z:(bb.min.z+bb.max.z)/2,
                   hx:(bb.max.x-bb.min.x)/2, hz:(bb.max.z-bb.min.z)/2});
    }
    return mesh;
  };
  const bx = (bw, bh, bd, c, ax, ay, az, collide, rx) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, bd), c.isMaterial ? c : M(c));
    m.position.set(x + ax, gy + ay, z + az);
    if (rx) m.rotation.x = rx;
    return add(m, collide);
  };
  const cy = (rt, rb, hh, c, ax, ay, az, seg, collide) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, hh, seg || 10),
                             c.isMaterial ? c : M(c));
    m.position.set(x + ax, gy + ay, z + az);
    return add(m, collide);
  };

  const TRACK = -4.0, GAUGE = 1.3;        // rails sit at TRACK +/- GAUGE

  /* the trackbed, and the line running away both ways */
  bx(60, .22, 5.2, 0x4f4639, 0, .11, TRACK);
  for (let i = -21; i <= 21; i++)
    bx(.32, .12, 3.1, 0x4e4034, i * 1.4, .26, TRACK);
  for (const sgn of [-1, 1])
    bx(60, .16, .15, 0x6b4a33, 0, .38, TRACK + sgn * GAUGE);
  for (let i = 0; i < 60; i++){            // grass up through it. nothing runs.
    const gx = (Math.random() - .5) * 52, gz = TRACK + (Math.random() - .5) * 2.4;
    cy(0, .08, .3 + Math.random() * .35, 0x5e7034, gx, .4, gz, 4);
  }

  /* the platform. kept low on purpose: he is a hedgehog and a proper one
     would be a cliff, so this is a step he can get up. */
  bx(21, .3, 4.6, 0x8d8577, 0, .15, .9);
  bx(21, .34, .36, 0x7a7266, 0, .17, TRACK + GAUGE + 1.05);
  bx(21, .06, .4, 0xcfc6b2, 0, .32, TRACK + GAUGE + 1.5);

  /* the canopy, on cast posts, with a scalloped valance along the edge */
  for (const ax of [-8, -4, 0, 4, 8]){
    cy(.13, .16, 2.9, 0x2b2724, ax, 1.75, -.9, 8);
    cy(.28, .28, .14, 0x2b2724, ax, .37, -.9, 8);
  }
  bx(19, .16, 4.2, 0x4e4038, 0, 3.3, .3, false, -.08);
  for (let i = -15; i <= 15; i++){
    bx(.42, .36, .1, 0x45382f, i * .6, 2.95, -1.75);
    bx(.14, .54, .1, 0x45382f, i * .6 + .3, 2.86, -1.75);
  }

  /* the station building itself */
  const B = {x:-4.5, z:4.4};
  bx(10, 3.2, 3.6, 0xa08794, B.x, 1.6, B.z, true);
  bx(6.2, .2, 4.4, 0x4e4038, B.x, 3.55, B.z - 1.0, false, .42);
  bx(6.2, .2, 4.4, 0x4e4038, B.x, 3.55, B.z + 1.0, false, -.42);
  bx(10.3, .26, 3.8, 0x4e4038, B.x, 3.3, B.z);
  bx(.8, 1.4, .8, 0x6b5a4c, B.x + 3.4, 4.3, B.z + .5);
  bx(1.3, 2.2, .14, 0x3a2a20, B.x - 2.2, 1.1, B.z - 1.82);
  for (const ax of [.4, 2.6, -4.2]){
    bx(1.1, 1.3, .1, 0x2e4450, B.x + ax, 1.9, B.z - 1.81);
    bx(1.25, 1.45, .07, 0xd8cdb8, B.x + ax, 1.9, B.z - 1.86);
  }
  bx(3.6, .54, .12, 0x1f3a4a, B.x - .4, 2.72, B.z - 1.86);
};
