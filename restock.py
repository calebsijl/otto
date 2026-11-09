#!/usr/bin/env python3
"""Put back anything endless that got eaten. Safe to run any time."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

STOCK = [
 {"id":"apples","name":"a crate of small apples","place":"shop_general",
  "tags":["food","shop","infinite"],"price":1,"note":""},
 {"id":"bread","name":"brown bread","place":"shop_general",
  "tags":["food","shop","infinite"],"price":1,"note":""},
 {"id":"cheese","name":"a wedge of hard cheese","place":"shop_general",
  "tags":["food","shop","infinite"],"price":2,"note":"keeps for weeks. he has never bought it."},
 {"id":"string_ball","name":"a ball of string","place":"shop_oddments",
  "tags":["shop","infinite"],"price":1,"note":""},
 {"id":"paper_stack","name":"a stack of paper","place":"shop_oddments",
  "tags":["shop","infinite"],"price":1,"note":""},
 {"id":"pencil","name":"a pencil","place":"shop_oddments","tags":["shop","infinite"],
  "price":1,"note":""},
 {"id":"glue_pot","name":"a pot of glue","place":"shop_oddments","tags":["shop","infinite"],
  "price":1,"note":"smells strongly. the brush is stuck to the lid."},
 {"id":"wire_coil","name":"a coil of thin wire","place":"shop_oddments","tags":["shop","infinite"],
  "price":2,"note":"bends and stays bent."},
 {"id":"wool_coat","name":"a small wool coat","place":"shop_oddments",
  "tags":["shop","clothing","warm"],"price":4,
  "note":"made for something about your size, which is a strange thought. carry it and the cold takes longer to get in."},
 {"id":"card_sheets","name":"sheets of card","place":"shop_oddments","tags":["shop","infinite"],
  "price":2,"note":"stiffer than paper. cuts straight."},
]
w = jload(WORLD); have = {o["id"] for o in w["objects"]}
back = new = 0
for s in STOCK:
    if s["id"] in have:
        for o in w["objects"]:
            if o["id"] == s["id"]:
                o["place"] = s["place"]; o["tags"] = s["tags"]; back += 1
    else:
        w["objects"].append(dict(s)); new += 1
jsave(WORLD, w)
print(f"restocked {back}, added {new} new lines.")
print("the shops cannot be eaten empty any more.")
