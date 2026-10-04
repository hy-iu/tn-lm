#!/usr/bin/env bash
# Assemble translated chunks into chapter files, then build flattened
# English/Chinese documents for the whole-file structural checks.
set -e
cd "$(dirname "$0")/.."
TOOLS=/Users/bjergsen/mnt/u26/research/tn/zh/tools
CH="chapter0_notations chapter1_intro chapter2_basics chapter3_operations chapter4_decompositions chapter5_gradients chapter6_probability_random_vectors chapter7_conclusion"

for f in $CH; do
  cat parts/${f}_*.tex > "$f.tex"
  n=$(ls parts/${f}_*.tex | wc -l | tr -d ' ')
  printf '%-38s %3s chunks -> %s lines\n' "$f" "$n" "$(wc -l < "$f.tex" | tr -d ' ')"
done

# flattened documents (macros + chapters in \input order)
{ echo '\\documentclass{article}'; cat macros.tex; for f in $CH; do cat "$f.tex"; echo; done; echo '\\end{document}'; } > tools_x/flat_zh.tex
( cd _baseline && { echo '\\documentclass{article}'; cat macros.tex; for f in $CH; do cat "$f.tex"; echo; done; echo '\\end{document}'; } ) > tools_x/flat_en.tex

echo
echo "===== parity.py (structural: envs / label / cite / ref / math) ====="
python3 "$TOOLS/parity.py" tools_x/flat_en.tex tools_x/flat_zh.tex || true
echo
echo "===== check_untranslated.py (residual English prose) ====="
python3 "$TOOLS/check_untranslated.py" tools_x/flat_zh.tex || true
