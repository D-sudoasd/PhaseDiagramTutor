"""Dump figure JSON and Chinese readout for verification (fresh process)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from phase_tutor.diagrams.registry import get_diagram
from phase_tutor.figure import build_figure, figure_to_json
from phase_tutor.interpreter import interpret
from phase_tutor.readout import format_readout_text


def dump_one(diagram_id: str, x: float, T: float, json_path: Path, txt_path: Path) -> None:
    diagram = get_diagram(diagram_id)
    interp = interpret(diagram, x, T)
    fig = build_figure(diagram, x, T, isopleth_x=x, interp=interp)
    json_path.write_text(json.dumps(figure_to_json(fig), ensure_ascii=False, indent=2), encoding="utf-8")
    txt_path.write_text(format_readout_text(interp), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dump_one("fe_c", 0.40, 800.0, out / "figure_fec.json", out / "readout_fec.txt")
    dump_one("ti_v", 8.0, 600.0, out / "figure_ti.json", out / "readout_ti.txt")
    print("wrote", out)


if __name__ == "__main__":
    main()
