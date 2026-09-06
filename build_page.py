# -*- coding: utf-8 -*-
"""Parse lists, filter out gambling & DPRK entries, generate a polished light single-page HTML."""
import json
import re

BASE = r"E:\work\blocked-sites-in-south-korea-main"
DATA_DIR = BASE + r"\blocked-sites-in-south-korea-main"
FILES = {"list.txt": DATA_DIR + r"\list.txt", "kr.list": DATA_DIR + r"\kr.list"}
OUT = BASE + r"\index.html"

# ---------- 1. parse & dedupe (original file order preserved) ----------
raw_count = 0
seen = {}
order = []
for fname, fpath in FILES.items():
    with open(fpath, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    raw_count += len(lines)
    for d in lines:
        norm = d.lower()
        if norm not in seen:
            seen[norm] = d
            order.append(norm)

# ---------- 2. categorize ----------
gambling_kw = re.compile(
    r"(bet|casion|casino|poker|xbahis|iqoption|exness|bwin|wager|toto|slot|lottery|betmaster|1xbet)",
    re.I,
)
dprk_kw = re.compile(r"(uriminzokkiri|kcna|rodong|naenara|dprk)", re.I)

gambling, dprk, kept = [], [], []
for d in order:
    if dprk_kw.search(d):
        dprk.append(d)
    elif gambling_kw.search(d):
        gambling.append(d)
    else:
        kept.append(d)

payload = json.dumps(kept, ensure_ascii=False, separators=(",", ":"))

template = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>学习资料</title>
<style>
  :root{
    --bg:#f7f8fc; --panel:#ffffff; --line:#e8ecf4;
    --text:#0f172a; --muted:#64748b; --faint:#94a3b8;
    --accent:#3b82f6; --accent-dark:#2563eb; --accent-soft:#eff6ff;
    --radius:14px;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  html{scroll-behavior:smooth;}
  body{
    background:var(--bg); color:var(--text);
    font-family:"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
    line-height:1.6; min-height:100vh;
  }
  /* soft top glow */
  body::before{
    content:""; position:fixed; inset:0 0 auto 0; height:320px; z-index:-1;
    background:linear-gradient(180deg,#eaf1ff 0%, rgba(234,241,255,0) 100%);
    pointer-events:none;
  }
  .wrap{max-width:1080px; margin:0 auto; padding:36px 20px 90px;}

  header{text-align:center; padding:28px 0 8px;}
  .kicker{
    display:inline-flex; align-items:center; gap:6px;
    font-size:11px; letter-spacing:3px; color:var(--accent-dark);
    background:var(--accent-soft); border:1px solid #dbeafe;
    padding:5px 16px; border-radius:999px; font-weight:600;
  }
  h1{
    font-size:40px; font-weight:800; letter-spacing:2px; margin-top:18px;
    background:linear-gradient(135deg,#0f172a 30%,#3b82f6 100%);
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  }
  .sub{color:var(--muted); margin-top:10px; font-size:14px;}

  .controls{
    position:sticky; top:12px; z-index:20;
    margin:30px 0 18px;
    background:rgba(255,255,255,.85); backdrop-filter:blur(12px);
    border:1px solid var(--line); border-radius:16px;
    padding:10px 14px;
    display:flex; align-items:center; gap:12px;
    box-shadow:0 6px 24px rgba(15,23,42,.06);
  }
  .search-wrap{position:relative; flex:1 1 260px; display:flex; align-items:center;}
  .search-wrap svg{
    position:absolute; left:14px; width:16px; height:16px;
    stroke:var(--faint); pointer-events:none;
  }
  #search{
    width:100%; background:#fff; border:1px solid var(--line);
    color:var(--text); padding:12px 14px 12px 40px;
    border-radius:10px; font-size:14px; outline:none; transition:border-color .15s, box-shadow .15s;
  }
  #search::placeholder{color:var(--faint);}
  #search:focus{border-color:var(--accent); box-shadow:0 0 0 4px rgba(59,130,246,.12);}
  .result-info{
    flex-shrink:0; font-size:12px; color:var(--accent-dark);
    background:var(--accent-soft); padding:6px 12px; border-radius:999px;
    font-variant-numeric:tabular-nums; white-space:nowrap;
  }

  #list{display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:10px;}
  .item{
    display:flex; align-items:center; gap:10px;
    background:var(--panel); border:1px solid var(--line); border-radius:10px;
    padding:10px 14px;
    transition:transform .15s ease, border-color .15s ease, box-shadow .15s ease;
  }
  .item:hover{
    border-color:#93c5fd; transform:translateY(-1px);
    box-shadow:0 6px 18px rgba(59,130,246,.10);
  }
  .item a{
    color:var(--text); text-decoration:none; font-size:13.5px;
    font-family:Consolas,"SF Mono",Menlo,monospace;
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1;
  }
  .item a:hover{color:var(--accent-dark);}
  .copy{
    flex-shrink:0; background:transparent; border:1px solid transparent;
    color:var(--faint); font-size:11px; padding:4px 10px; border-radius:6px;
    cursor:pointer; transition:all .15s;
  }
  .item:hover .copy{border-color:var(--line); color:var(--muted); background:#fff;}
  .copy:hover{color:#fff; background:var(--accent); border-color:var(--accent);}
  .copy.copied{color:#059669; border-color:#a7f3d0; background:#ecfdf5;}
  .empty{
    grid-column:1/-1; text-align:center; color:var(--muted);
    padding:60px 0; font-size:14px;
  }
  .empty::before{
    content:""; display:block; width:48px; height:48px; margin:0 auto 14px;
    border-radius:50%; background:var(--accent-soft);
  }

  #toTop{
    position:fixed; right:26px; bottom:26px; width:42px; height:42px;
    border-radius:50%; border:1px solid var(--line); background:#fff;
    color:var(--muted); cursor:pointer; font-size:16px;
    box-shadow:0 4px 14px rgba(15,23,42,.10);
    opacity:0; pointer-events:none; transition:opacity .2s, transform .2s;
    transform:translateY(6px); z-index:30;
  }
  #toTop.show{opacity:1; pointer-events:auto; transform:translateY(0);}
  #toTop:hover{color:var(--accent-dark); border-color:#93c5fd;}

  footer{
    color:var(--faint); font-size:12px; text-align:center;
    margin-top:48px; border-top:1px solid var(--line); padding-top:20px;
  }

  @media (max-width:640px){
    h1{font-size:28px;}
    #list{grid-template-columns:1fr;}
    .controls{flex-direction:column; align-items:stretch;}
    .result-info{text-align:center;}
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="kicker">REFERENCE LIST</span>
    <h1>学习资料</h1>
    <div class="sub">学习资料汇总 · 共 __TOTAL__ 条</div>
  </header>

  <div class="controls">
    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round">
        <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
      </svg>
      <input id="search" type="text" placeholder="搜索…" autocomplete="off">
    </div>
    <span class="result-info" id="result-info"></span>
  </div>

  <div id="list"></div>

  <footer>本页面为学习资料整理用途，已去重排序。</footer>
</div>

<button id="toTop" title="回到顶部" aria-label="回到顶部">↑</button>

<script>
const ITEMS = __DATA__;

const listEl = document.getElementById("list");
const infoEl = document.getElementById("result-info");
const searchEl = document.getElementById("search");
const toTop = document.getElementById("toTop");

function render(){
  const q = searchEl.value.trim().toLowerCase();
  listEl.innerHTML = "";
  let shown = 0;
  const frag = document.createDocumentFragment();
  for(const d of ITEMS){
    if(q && !d.includes(q)) continue;
    shown++;
    frag.appendChild(dom(d));
  }
  if(!shown){
    const e = document.createElement("div");
    e.className = "empty";
    e.textContent = "没有匹配的内容";
    frag.appendChild(e);
  }
  listEl.appendChild(frag);
  infoEl.textContent = "显示 " + shown + " / " + ITEMS.length + " 条";
}

function dom(d){
  const div = document.createElement("div");
  div.className = "item";
  const a = document.createElement("a");
  a.href = "https://" + d;
  a.target = "_blank";
  a.rel = "noopener noreferrer nofollow";
  a.textContent = d;
  a.title = d;
  const btn = document.createElement("button");
  btn.className = "copy";
  btn.textContent = "复制";
  btn.onclick = function(ev){
    ev.preventDefault();
    navigator.clipboard.writeText(d).then(()=>{
      btn.textContent = "已复制";
      btn.classList.add("copied");
      setTimeout(()=>{ btn.textContent = "复制"; btn.classList.remove("copied"); }, 1200);
    });
  };
  div.appendChild(a);
  div.appendChild(btn);
  return div;
}

let timer = null;
searchEl.addEventListener("input", ()=>{
  clearTimeout(timer);
  timer = setTimeout(render, 100);
});

window.addEventListener("scroll", ()=>{
  toTop.classList.toggle("show", window.scrollY > 400);
});
toTop.addEventListener("click", ()=>window.scrollTo({top:0, behavior:"smooth"}));

render();
</script>
</body>
</html>
"""

html = template.replace("__DATA__", payload).replace("__TOTAL__", str(len(kept)))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("OK kept=%d html=%d bytes" % (len(kept), len(html)))
