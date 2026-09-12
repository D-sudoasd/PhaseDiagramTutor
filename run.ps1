# 启动相图导读（工作副本：E:\Vibe_coding\PhaseDiagramTutor）
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    py -3 -m venv .venv
    .\.venv\Scripts\python -m pip install -r requirements.txt
}
.\.venv\Scripts\streamlit run app.py --server.headless true
