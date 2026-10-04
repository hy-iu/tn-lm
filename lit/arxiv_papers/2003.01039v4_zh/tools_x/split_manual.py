#!/usr/bin/env python3
"""Cut a tex file at given 1-based line boundaries into en_parts/ + parts/."""
import sys, shutil
from pathlib import Path

def cut(src, outbase, cuts):
    lines = Path(src).read_text().split("\n")
    if lines[-1] == "":
        lines = lines[:-1]
    en = Path(outbase) / "en_parts"
    zh = Path(outbase) / "parts"
    shutil.rmtree(en, ignore_errors=True); shutil.rmtree(zh, ignore_errors=True)
    en.mkdir(); zh.mkdir()
    cuts[-1] = len(lines) + 1
    mans = []
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        chunk = "\n".join(lines[a-1:b-1]) + "\n"
        (en / f"part_{i:03d}.tex").write_text(chunk)
        (zh / f"part_{i:03d}.tex").write_text(chunk)
        mans.append(f"part_{i:03d}.tex\tlines {a}-{b-1}\t({b-a})")
    joined = "".join((en / f"part_{i:03d}.tex").read_text() for i in range(len(cuts)-1))
    orig = Path(src).read_text()
    assert joined == orig or joined + "\n" == orig or joined == orig + "\n", "reassembly mismatch"
    print("\n".join(mans))
    print("REASSEMBLY OK")

if __name__ == "__main__":
    cut(sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3:]])
