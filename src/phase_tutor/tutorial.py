"""Beginner path: six steps, each driving the same interpreter and diagram."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TutorialStep:
    id: str
    title_zh: str
    diagram_id: str
    x: float
    T: float
    isopleth_x: float
    body_md: str
    takeaway_zh: str


STEPS: tuple[TutorialStep, ...] = (
    TutorialStep(
        id="what",
        title_zh="1. 相图是一张地图",
        diagram_id="cu_ni",
        x=50.0,
        T=1400.0,
        isopleth_x=50.0,
        body_md="""
**相**是合金里一种成分、结构都均匀的部分。钢液是一个相，奥氏体是一个相，铁素体又是另一个相。

**组元**是你用来配料的独立化学物种。Cu–Ni 有两个组元，所以这是二元相图。钢铁把碳当作第二组元，先按 Fe–C 二元来读。

**相图**不是组织照片。它是一张 **T–x 地图**：横轴是成分，纵轴是温度。你在地图上的一个点，表示「这块合金、此刻这个温度」。地图用颜色告诉你：这里有几个相、它们叫什么。

右边这张 Cu–Ni 图是最简单的一种——**完全互溶**。固态只有一个相 α，液态只有一个相 L。两块单相区中间夹着一条透镜形的 **L+α** 双相区，上下两条边界分别叫 **液相线** 和 **固相线**。

把点放在 50 wt% Ni、1400 °C：这里在液相线以上，所以 100% 是液体。下一步把温度拖下来，看它怎样穿过透镜。
""",
        takeaway_zh="先记住：点 = 成分 + 温度；颜色 = 有哪些相。",
    ),
    TutorialStep(
        id="read_point",
        title_zh="2. 一个点怎么读",
        diagram_id="cu_ni",
        x=50.0,
        T=1100.0,
        isopleth_x=50.0,
        body_md="""
同一根合金，温度不同，答案完全不同。

现在点在 50 wt% Ni、1100 °C。这个温度已经低于固相线，所以整块合金都是 **α 固溶体**，质量分数 100%。相律 F = C − P + 1 = 2 − 1 + 1 = 2：温度和成分都可以改，点可以在这块蓝色区域里随便走。

请你自己做三件事：

1. 把温度拖回 1400 °C，读出「只有液体」。
2. 拖到大约 1240 °C，读出「液体和固体共存」。
3. 再拖到 1100 °C，固体吃掉全部液体。

**相图的用处**到这里已经出现了：它回答的不是「这是什么合金」，而是「**此刻**有哪些相」。热处理、凝固、钎焊，问的都是这个问题。
""",
        takeaway_zh="单相区：100% 该相。先会读点，再谈结线。",
    ),
    TutorialStep(
        id="lever",
        title_zh="3. 结线与杠杆定律",
        diagram_id="cu_ni",
        x=50.0,
        T=1240.0,
        isopleth_x=50.0,
        body_md="""
双相区不能只说「有两个相」——还要说清 **各是什么成分、各有多少**。

过当前点画一条 **水平线**（等温），两端分别碰到液相线和固相线。这根线叫 **结线**：

- 左端 = 此刻液体的成分
- 右端 = 此刻固体的成分
- 总成分是结线上的一个支点

**杠杆定律**和天平一样：离谁远，谁的质量分数就大。

\\[
w_{\\alpha} = (x_L - x) / (x_L - x_{\\alpha}), \\quad w_L = (x - x_{\\alpha}) / (x_L - x_{\\alpha})
\\]

把成分滑块往左拖，靠近液相线：液体变多，固体变少，直到边界上变成 100% 液体。往右拖到固相线，变成 100% 固体。

相律变成 F = 1：温度一旦选定，两相成分就被钉死，你只能用总成分改变质量分数。这就是为什么双相区需要结线，而单相区不需要。
""",
        takeaway_zh="双相区 = 水平结线 + 杠杆。边界上是 100% 该边界相。",
    ),
    TutorialStep(
        id="isopleth",
        title_zh="4. 竖线就是冷却过程",
        diagram_id="pb_sn",
        x=40.0,
        T=220.0,
        isopleth_x=40.0,
        body_md="""
真正做材料时，成分往往已经定了（一块焊料、一根钢、一炉钛锭）。过程是 **温度在变**。相图上这就是一条 **竖线**，叫等成分线或冷却线。

右侧换成 Pb–Sn 共晶图。40 wt% Sn 是亚共晶焊料。从液体往下走：

1. 先穿过液相线，进入 L+α：先析出铅基晶体，液体沿液相线变富锡。
2. 碰到 183 °C 共晶水平线，剩余液体按 **L → α+β** 一次性变成细密两相，温度暂时不下降。
3. 再往下进入 α+β，溶解度曲线让两相成分继续微调。

共晶点（61.9 wt% Sn）几乎没有凝固温度区间，所以传统焊料选在这附近。请把冷却线拖到 61.9，看序列如何变成「液体 → 共晶 → α+β」，再拖到 80，看过共晶如何先出 β。

**相图在这里的用处**：它把「降温」翻译成「先出什么、在哪个温度发生不变反应、最后剩下什么」。
""",
        takeaway_zh="竖线 = 固定成分的热历史。水平线 = 共晶/包晶/共析。",
    ),
    TutorialStep(
        id="steel",
        title_zh="5. 钢铁相图怎么用",
        diagram_id="fe_c",
        x=0.40,
        T=800.0,
        isopleth_x=0.40,
        body_md="""
Fe–Fe₃C 看起来挤，是因为它把三种不变反应叠在一张图上。读的时候只抓四条线：

| 线 | 温度 | 反应 | 你用它干什么 |
|---|---|---|---|
| 包晶 | 1495 °C | L+δ → γ | 低碳钢凝固 |
| 共晶 | 1148 °C | L → γ+Fe₃C | 钢 / 铸铁分界在 2.11 wt% C |
| A3 / Acm | 斜线 | γ 开始析出 α 或 Fe₃C | 正火、退火温度 |
| 共析 A1 | 727 °C | γ → α+Fe₃C | 珠光体；钢热处理最常用的水平线 |

当前点 0.40 wt% C、800 °C：这是 **亚共析钢**，落在 α+γ。结线左边是几乎不溶碳的铁素体，右边是更富碳的奥氏体。杠杆告诉你先共析铁素体已经占了一部分，剩下的奥氏体还在走向共析点 S（0.76 wt%）。

把温度拖到 900 °C 以上，进入 **奥氏体单相区**——这就是「奥氏体化」。再拖到 720 °C 以下，变成 α+Fe₃C，也就是铁素体+珠光体。

把成分拖过 2.11，地图立刻改口叫 **铸铁**。5 wt% C、1000 °C 是 γ+Fe₃C；再往上穿过 1148 °C 才是带液体的铸造窗口。

本图采用教材常用数：共析 **0.76 wt% C / 727 °C**，共晶 **4.30 wt% / 1148 °C**。不同手册会差 0.02–0.04 wt% 或几度，解释器跟这张图用同一套。
""",
        takeaway_zh="钢看 0.76 与 2.11；热处理看 A3/Acm 和 727 °C 的 A1。",
    ),
    TutorialStep(
        id="titanium",
        title_zh="6. 钛合金相图怎么用",
        diagram_id="ti_v",
        x=8.0,
        T=600.0,
        isopleth_x=8.0,
        body_md="""
钛合金的第一问不是共晶，而是 **β transus**：加热到哪一温度，α 全部消失、只剩 BCC 的 β。

V、Mo、Nb 都是 β 稳定元素，会把 transus 压低。这张 Ti–V 示意就是在讲这件事（它不是 Ti-6Al-4V 的精确截面，但窗口的读法相同）。

当前点 8 wt% V、600 °C 落在 **α+β**。结线左边是溶了少量 V 的 α，右边是更富 V 的 β。杠杆给出两相比例——双相钛合金锻造、固溶，用的就是这个比例。

把温度拖到 transus 以上，进入 β 单相：这是 β 退火或从 β 区淬火的窗口。把成分拖到 22 wt% 附近，transus 落到室温，读法变成 β 钛合金。把成分拖回 1 wt%，室温几乎是单相 α。

所以钛合金相图的日常用法就三句话：

1. 先读你的成分对应的 **β transus**。
2. 热加工温度在 transus 上还是下，决定你走 β 还是 α+β。
3. 双相区里用结线和杠杆，读 α/β 各占多少。
""",
        takeaway_zh="钛合金：先找 β transus，再决定站在 α、α+β 还是 β。",
    ),
)


def get_step(index: int) -> TutorialStep:
    return STEPS[index]


def step_titles() -> list[str]:
    return [s.title_zh for s in STEPS]


def initial_controls() -> dict[str, object]:
    """First-load point: tutorial step 0, so the beginner path drives the same diagram."""
    step = STEPS[0]
    return {
        "diagram_id": step.diagram_id,
        "x": step.x,
        "T": step.T,
        "iso_x": step.isopleth_x,
        "tutorial_idx": 0,
        "follow": True,
    }
