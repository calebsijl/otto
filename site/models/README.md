Drop .glb files in here, named exactly as the MODELS table in world.html expects:

  range.glb       the kitchen range in the front room
  chair.glb       the rush-seated chair
  worktable.glb   the work table
  bed.glb         his bed
  nightstand.glb  the nightstand
  slab.glb        the cooking slab in the kitchen
  sink.glb        the stone sink
  bath.glb        the tin bath
  jug.glb         the white jug
  bookcase.glb    library shelving
  counter.glb     a shop counter

Each one is measured on load, scaled to the size the world wants, stood on the
floor and turned to face into the room, so a model straight off the internet
lands correctly without hand fitting. A missing or broken file is ignored and
the hand-built version is used instead.

Keep them under about 500 KB each. Anything bigger should be run through
gltf-transform first.
