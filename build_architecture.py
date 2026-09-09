"""Generate the workshop architecture as .drawio (editable) and .svg (self-contained)."""
from __future__ import annotations

import base64
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

W, H = 1700, 1180
BG, LANE, HDR, STROKE = "#f7f4ef", "#ffffff", "#f5f5f5", "#919191"
NODE_BG, NODE_ST = "#fcfbf8", "#dedede"
ROSE, BLUE, GREY, TEXT, SUB = "#b11f4b", "#0078d4", "#5c5c5c", "#242424", "#5c5c5c"


def data_uri(name: str) -> str:
    raw = (ICONS / name).read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")


# (key, x, y, w, h, icon, title, subtitle, azure2 stencil for draw.io)
DELIVERY = [
    ("repo", 76, 190, 170, 130, "github.svg", "GitHub repo", "branch + commit", None),
    ("pr", 273, 190, 170, 130, "github-copilot.svg", "Pull request", "Copilot + reviewers", None),
    ("ci", 470, 190, 170, 130, "github-actions.svg", "CI checks", "backend · frontend · bicep", None),
    ("codeql", 667, 190, 170, 130, "github.svg", "CodeQL", "python · js-ts", None),
    ("main", 864, 190, 170, 130, "github.svg", "Protected main", "5 required checks", None),
    ("deploy", 1061, 190, 170, 130, "github-actions.svg", "Deploy workflow", "OIDC · no secrets", None),
    ("acr", 1258, 190, 170, 130, "container-registry.svg", "Container Registry",
     "SHA-tagged images", "containers/Container_Registries"),
    ("aca", 1455, 190, 170, 130, "container-app.svg", "Container Apps", "new revision",
     "other/Worker_Container_App"),
]

RUNTIME = [
    ("browser", 100, 536, 165, 120, "browser.svg", "Browser", "session cookie", "general/Browser"),
    ("frontend", 293, 536, 165, 120, "container-app.svg", "Frontend", "React + proxy",
     "other/Worker_Container_App"),
    ("api", 486, 536, 165, 120, "container-app.svg", "FastAPI", "metadata · SAS · chat",
     "other/Worker_Container_App"),
    ("storage", 679, 536, 165, 120, "storage.svg", "Azure Storage", "Blob · Queue · Table",
     "storage/Storage_Accounts"),
    ("worker", 872, 536, 165, 120, "container-app.svg", "Worker", "analyze → index",
     "other/Worker_Container_App"),
    ("search", 1065, 536, 165, 120, "search.svg", "AI Search", "hybrid · 3072d",
     "app_services/Search_Services"),
    ("cleanup", 679, 736, 165, 120, "workflow.svg", "Cleanup job", "Blob + Search sweep",
     "general/Workflow"),
    ("insights", 872, 736, 165, 120, "app-insights.svg", "App Insights", "traces · release SHA",
     "devops/Application_Insights"),
    ("foundry", 1316, 536, 280, 300, "foundry.svg", "Microsoft Foundry", "",
     "ai_machine_learning/AI_Foundry"),
]

# Services listed inside the single Foundry node.
FOUNDRY_ROWS = [
    ("Content Understanding", "analyzers · 2025-11-01"),
    ("text-embedding-3-large", "3,072 dimensions"),
    ("GPT-5", "grounded generation"),
]

# (number, svg path, badge x, badge y, legend text)
FLOWS = [
    (1, "M265 566 H293", 279, 566, "Browser → Frontend · user opens the console over HTTPS"),
    (2, "M458 566 H486", 472, 566, "Frontend → API · session cookie and upload init"),
    (3, "M651 566 H679", 665, 566, "API → Storage · metadata, quota and user-delegation SAS"),
    (4, "M182 536 V508 H761 V536", 471, 508, "Browser → Storage · direct Blob PUT of the file bytes"),
    (5, "M844 566 H872", 858, 566, "Storage → Worker · ingestion queue message under Blob lease"),
    (6, "M954 536 V508 H1456 V536", 1205, 508,
     "Worker → Foundry · analyze selected pages, then embed the chunks"),
    (7, "M1037 566 H1065", 1051, 566, "Worker → AI Search · upsert 3,072-d vectors for the session"),
    (8, "M520 656 V900 H1456 V836", 988, 900, "API → Foundry · question embedding and GPT-5 generation"),
    (9, "M1147 656 V886 H568 V656", 857, 886, "AI Search → API · hybrid retrieval, top 8 evidence chunks"),
    (10, "M761 736 V660", 761, 700, "Cleanup → Storage · tombstone sweep of Blob and Search artifacts"),
]

DELIVERY_ARROWS = [
    "M246 255 H273", "M443 255 H470", "M640 255 H667", "M837 255 H864",
    "M1034 255 H1061", "M1231 255 H1258", "M1428 255 H1455",
]


def build_svg() -> str:
    uris = {n: data_uri(n) for n in {n[5] for n in DELIVERY} | {n[5] for n in RUNTIME}}
    p: list[str] = []
    add = p.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="ttl desc">')
    add('<title id="ttl">Content Understanding RAG architecture</title>'
        '<desc id="desc">GitHub delivery control plane and Azure runtime for the workshop.</desc>')
    add('<defs>'
        f'<marker id="ar" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">'
        f'<path d="M0,0 L0,6 L9,3 z" fill="{ROSE}"/></marker>'
        f'<marker id="ab" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">'
        f'<path d="M0,0 L0,6 L9,3 z" fill="{BLUE}"/></marker>'
        f'<marker id="ag" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">'
        f'<path d="M0,0 L0,6 L9,3 z" fill="{GREY}"/></marker>'
        '<style>'
        f'.h{{font:700 30px "Segoe UI",sans-serif;fill:{TEXT}}}'
        f'.s{{font:15px "Segoe UI",sans-serif;fill:{SUB}}}'
        f'.lane{{font:700 12px Consolas,monospace;fill:{TEXT};letter-spacing:1.2px}}'
        f'.reg{{font:700 12px "Segoe UI",sans-serif;fill:{SUB};letter-spacing:.6px}}'
        f'.t{{font:700 14px "Segoe UI",sans-serif;fill:{TEXT}}}'
        f'.u{{font:11px "Segoe UI",sans-serif;fill:{SUB}}}'
        f'.lg{{font:12px "Segoe UI",sans-serif;fill:{TEXT}}}'
        f'.lgh{{font:700 12px "Segoe UI",sans-serif;fill:{TEXT}}}'
        '.bn{font:700 11px "Segoe UI",sans-serif;fill:#fff}'
        f'.rose{{stroke:{ROSE};stroke-width:2.5;fill:none;marker-end:url(#ar)}}'
        f'.blue{{stroke:{BLUE};stroke-width:2.5;fill:none;marker-end:url(#ab)}}'
        f'.dash{{stroke:{GREY};stroke-width:2;stroke-dasharray:6 5;fill:none;marker-end:url(#ag)}}'
        '</style></defs>')
    add(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    add(f'<text x="48" y="58" class="h">Content Understanding RAG \u2014 GitHub delivery to Azure runtime</text>')
    add('<text x="48" y="88" class="s">Reviewed change \u2192 required checks \u2192 CodeQL '
        '\u2192 OIDC release \u2192 grounded, citable answer</text>')

    for x, y, w, h, label in ((48, 112, 1604, 250, "DELIVERY CONTROL PLANE \u00b7 GITHUB"),
                              (48, 392, 1604, 610, "RUNTIME \u00b7 AZURE")):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{LANE}" '
            f'stroke="{STROKE}" stroke-width="2"/>')
        add(f'<path d="M{x} {y+16}a16 16 0 0 1 16-16h{w-32}a16 16 0 0 1 16 16v22H{x}z" fill="{HDR}"/>')
        add(f'<text x="{x+28}" y="{y+26}" class="lane">{escape(label)}</text>')

    for x, w, label in ((76, 1180, "SOUTHEAST ASIA \u00b7 application + data plane"),
                        (1288, 336, "EAST US 2 \u00b7 Microsoft Foundry")):
        add(f'<rect x="{x}" y="448" width="{w}" height="530" rx="12" fill="none" '
            f'stroke="{NODE_ST}" stroke-width="2" stroke-dasharray="7 5"/>')
        add(f'<text x="{x+20}" y="478" class="reg">{escape(label)}</text>')

    for group in (DELIVERY, RUNTIME):
        for key, x, y, w, h, icon, title, sub, _st in group:
            cx, iw = x + w / 2, 44
            add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{NODE_BG}" '
                f'stroke="{NODE_ST}" stroke-width="1.5"/>')
            add(f'<image href="{uris[icon]}" x="{cx - iw / 2:.0f}" y="{y + 12}" '
                f'width="{iw}" height="{iw}"/>')
            if key == "foundry":
                add(f'<text x="{cx:.0f}" y="{y + 82}" text-anchor="middle" class="t">{escape(title)}</text>')
                for i, (name, detail) in enumerate(FOUNDRY_ROWS):
                    ry = y + 122 + i * 60
                    add(f'<line x1="{x + 24}" y1="{ry - 22}" x2="{x + w - 24}" y2="{ry - 22}" '
                        f'stroke="{NODE_ST}" stroke-width="1"/>')
                    add(f'<text x="{cx:.0f}" y="{ry}" text-anchor="middle" class="t">{escape(name)}</text>')
                    add(f'<text x="{cx:.0f}" y="{ry + 19}" text-anchor="middle" class="u">{escape(detail)}</text>')
                continue
            add(f'<text x="{cx:.0f}" y="{y + h - 38}" text-anchor="middle" class="t">{escape(title)}</text>')
            add(f'<text x="{cx:.0f}" y="{y + h - 18}" text-anchor="middle" class="u">{escape(sub)}</text>')

    for d in DELIVERY_ARROWS:
        add(f'<path d="{d}" class="rose"/>')
    add('<path d="M1540 320 V376 H761 V392" class="rose"/>')
    add('<text x="1160" y="370" text-anchor="middle" class="u">deploy revisions</text>')

    for num, d, bx, by, _txt in FLOWS:
        cls = "dash" if num == 10 else "blue"
        add(f'<path d="{d}" class="{cls}"/>')
        fill = GREY if num == 10 else BLUE
        add(f'<circle cx="{bx}" cy="{by}" r="11" fill="{fill}"/>')
        add(f'<text x="{bx}" y="{by + 4}" text-anchor="middle" class="bn">{num}</text>')

    add('<path d="M954 656 V736" class="dash"/>')
    add('<text x="972" y="702" class="u">telemetry</text>')

    add('<text x="48" y="1032" class="lgh">Runtime flow</text>')
    for i, (num, _d, _bx, _by, txt) in enumerate(FLOWS):
        col, row = divmod(i, 5)
        x, y = 48 + col * 830, 1060 + row * 24
        add(f'<circle cx="{x + 10}" cy="{y - 4}" r="10" fill="{GREY if num == 10 else BLUE}"/>')
        add(f'<text x="{x + 10}" y="{y}" text-anchor="middle" class="bn">{num}</text>')
        add(f'<text x="{x + 30}" y="{y}" class="lg">{escape(txt)}</text>')
    add('</svg>')
    return "\n".join(p)


def build_drawio() -> str:
    icon_uris = {n: data_uri(n) for n in {n[5] for n in DELIVERY} | {n[5] for n in RUNTIME}}
    cells: list[str] = []
    style_img = ("image;aspect=fixed;html=1;labelBackgroundColor=none;align=center;"
                 "verticalLabelPosition=bottom;verticalAlign=top;fontSize=13;fontColor=#242424;image=")

    def cell(cid: str, value: str, style: str, x: float, y: float, w: float, h: float) -> None:
        cells.append(f'<mxCell id="{cid}" value="{escape(value)}" style="{style}" vertex="1" '
                     f'parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
                     f'as="geometry"/></mxCell>')

    def edge(eid: str, value: str, src: str, tgt: str, colour: str, dashed: bool = False) -> None:
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={colour};"
                 f"strokeWidth=2;endArrow=block;endFill=1;fontSize=11;"
                 f"{'dashed=1;' if dashed else ''}")
        cells.append(f'<mxCell id="{eid}" value="{escape(value)}" style="{style}" edge="1" '
                     f'parent="1" source="{src}" target="{tgt}">'
                     f'<mxGeometry relative="1" as="geometry"/></mxCell>')

    cell("title", "Content Understanding RAG \u2014 GitHub delivery to Azure runtime",
         "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=26;fontStyle=1;"
         "fontColor=#242424;", 40, 20, 1100, 40)
    cell("laneA", "DELIVERY CONTROL PLANE \u00b7 GITHUB",
         "swimlane;html=1;rounded=1;startSize=38;fillColor=#F5F5F5;swimlaneFillColor=#FFFFFF;"
         "strokeColor=#919191;fontColor=#242424;fontStyle=1;fontSize=13;", 40, 90, 1620, 250)
    cell("laneB", "RUNTIME \u00b7 AZURE",
         "swimlane;html=1;rounded=1;startSize=38;fillColor=#F5F5F5;swimlaneFillColor=#FFFFFF;"
         "strokeColor=#919191;fontColor=#242424;fontStyle=1;fontSize=13;", 40, 370, 1620, 620)
    cell("sea", "SOUTHEAST ASIA \u00b7 application + data plane",
         "rounded=1;html=1;fillColor=none;strokeColor=#DEDEDE;dashed=1;verticalAlign=top;"
         "align=left;spacingLeft=12;fontSize=12;fontColor=#5C5C5C;fontStyle=1;", 68, 430, 1190, 540)
    cell("eus2", "EAST US 2 \u00b7 Microsoft Foundry",
         "rounded=1;html=1;fillColor=none;strokeColor=#DEDEDE;dashed=1;verticalAlign=top;"
         "align=left;spacingLeft=12;fontSize=12;fontColor=#5C5C5C;fontStyle=1;", 1290, 430, 340, 540)

    for key, x, y, w, h, icon, title, sub, stencil in DELIVERY + RUNTIME:
        img = f"img/lib/azure2/{stencil}.svg" if stencil else icon_uris[icon]
        label = f"{title}\n{sub}" if sub else title
        if key == "foundry":
            label = title + "\n" + "\n".join(f"{n} · {d}" for n, d in FOUNDRY_ROWS)
        cell(key, label, style_img + img, x + 40, y + 20, 90, 76)

    chain = [("repo", "pr"), ("pr", "ci"), ("ci", "codeql"), ("codeql", "main"),
             ("main", "deploy"), ("deploy", "acr"), ("acr", "aca")]
    for i, (s, t) in enumerate(chain):
        edge(f"d{i}", "", s, t, ROSE)
    edge("d7", "deploy revisions", "aca", "sea", ROSE)

    runtime_edges = [
        ("browser", "frontend", "1 open console"),
        ("frontend", "api", "2 session + upload init"),
        ("api", "storage", "3 metadata + SAS authorization"),
        ("browser", "storage", "4 direct Blob PUT"),
        ("storage", "worker", "5 ingestion queue"),
        ("worker", "foundry", "6 analyze pages · embed chunks"),
        ("worker", "search", "7 upsert 3,072-d vectors"),
        ("api", "foundry", "8 question embedding + GPT-5"),
        ("search", "api", "9 hybrid retrieval \u00b7 top 8"),
    ]
    for i, (s, t, label) in enumerate(runtime_edges):
        edge(f"r{i}", label, s, t, BLUE)
    edge("r9", "10 tombstone sweep", "cleanup", "storage", GREY, dashed=True)
    edge("r10", "telemetry", "worker", "insights", GREY, dashed=True)

    body = "\n        ".join(cells)
    return (
        '<mxfile host="app.diagrams.net" agent="GitHub Copilot" type="device">\n'
        '  <diagram id="content-understanding-rag" name="Architecture">\n'
        '    <mxGraphModel dx="1800" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1700" pageHeight="1180" '
        'math="0" shadow="0">\n'
        "      <root>\n"
        '        <mxCell id="0"/>\n'
        '        <mxCell id="1" parent="0"/>\n'
        f"        {body}\n"
        "      </root>\n"
        "    </mxGraphModel>\n"
        "  </diagram>\n"
        "</mxfile>\n"
    )


if __name__ == "__main__":
    svg_path = ASSETS / "content-understanding-rag-architecture.svg"
    drawio_path = ASSETS / "content-understanding-rag-architecture.drawio"
    svg_path.write_text(build_svg(), encoding="utf-8")
    drawio_path.write_text(build_drawio(), encoding="utf-8")
    print(f"svg={svg_path.stat().st_size} drawio={drawio_path.stat().st_size}")
