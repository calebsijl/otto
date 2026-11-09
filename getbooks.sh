#!/bin/bash
# Stock otto's library from Project Gutenberg. Run once, from the otto folder.
cd "$(dirname "$0")/library" || exit 1

get () {   # get <id> <filename> <what it is>
  if [ -f "$2.txt" ]; then echo "  already have  $2"; return; fi
  for u in "https://www.gutenberg.org/cache/epub/$1/pg$1.txt" \
           "https://www.gutenberg.org/files/$1/$1-0.txt" \
           "https://www.gutenberg.org/ebooks/$1.txt.utf-8"; do
    if curl -fsL --max-time 60 -o "$2.txt" "$u" 2>/dev/null && [ -s "$2.txt" ]; then
      printf "  got %-22s %6s KB   %s\n" "$2" "$(( $(wc -c <"$2.txt") / 1024 ))" "$3"
      return
    fi
  done
  rm -f "$2.txt"; echo "  FAILED  $2  (id $1)"
}

echo "stocking otto's shelf..."
get 1408  selborne        "one man watching one small place for 40 years"
get 12655 boy-mechanic    "700 practical builds, real technique"
get 205   walden          "strong opinions, living deliberately"
get 11    alice           "nonsense, steers him nowhere"
get 2130  aristotle-poetics "how things are put together, argued"

echo
echo "on the shelf now:"
ls -lh *.txt 2>/dev/null | awk '{printf "  %-26s %s\n", $9, $5}'
echo
echo "delete bridges-sample.txt if you want him starting clean:  rm library/bridges-sample.txt"
