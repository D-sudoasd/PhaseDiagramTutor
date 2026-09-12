# 相图导读

中文交互相图工作台：把二元 **T–x 相图**读成「现在有哪些相、各是什么成分、各占多少」，再沿等成分竖线看凝固/热处理会穿过什么。

面向金属材料研究者。**不是 CALPHAD，也不是 Thermo-Calc。** 内置曲线是教学拓扑：不变点用一套自洽的教材常用数，用来建立点 / 结线 / 杠杆 / 冷却线，而不是替代商业相图计算。

## 运行

需要 Python 3.10+。

```powershell
git clone https://github.com/D-sudoasd/PhaseDiagramTutor.git
cd PhaseDiagramTutor
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\streamlit run app.py
```

或：

```powershell
.\run.ps1
```

测试：

```powershell
.\.venv\Scripts\python -m pytest
```

浏览器打开后：选一张图或走「导学路径」；拖动成分/温度，或在图上点一下。右侧三块始终可见——**现在有哪些相**、**结线与杠杆定律**、**沿冷却线往下走**。长说明在展开栏里，不盖住相区。

## 内置相图

| 图 | 用来建立什么直觉 |
|---|---|
| Cu–Ni 完全互溶 | 液相线 / 固相线、单相区 |
| Pb–Sn 简单共晶 | 共晶水平线、先析出相 |
| 简单包晶（示意） | L+α → β |
| Fe–Fe₃C 亚稳相图 | 钢 / 铸铁、珠光体、奥氏体化 |
| Ti–V β 稳定示意 | β transus、α+β 窗口（不是 Ti-6Al-4V 精确截面） |

Fe–Fe₃C 与解释器共用同一套数，不混手册：

- 共析 0.76 wt% C / 727 °C
- 共晶 4.30 wt% C / 1148 °C
- 包晶 1495 °C（δ 0.09、γ 0.17、L 0.53 wt% C）
- E 点 2.11 wt% C（钢 / 铸铁分界）

## 结构

```
app.py                 Streamlit 入口（中文工作台）
src/phase_tutor/
  interpreter.py       相区、结线、杠杆、相律、冷却线（无 UI）
  figure.py            Plotly 相图 + 结线/杠杆标注
  readout.py           中文读出与冷却跳转温度
  diagrams/            五张内置 T–x 几何
  tutorial.py          导学六步（同一套解释器）
tests/                 pytest + Streamlit AppTest
```

解释器与作图分离：界面只展示 `interpret` / `walk_isopleth` 的结果。

## 范围

- 做：二元 T–x 读点、结线、杠杆定律、等成分冷却、共晶/包晶/共析。
- 不做：三元相图、TTT/CCT、Gibbs 能量、商业牌号精确截面。

## 许可

MIT。见 [LICENSE](LICENSE)。
