#!/usr/bin/env python3
"""
Brazzein iGEM Wiki — 自包含单文件构建器
用法:  python build_single.py
读取同目录的 content.yaml，生成根目录 index.html（内联 CSS，客户端切页）。
模板与样式已内嵌在本文件中，无需 templates/ 或 assets/ 目录。
日常只需修改 content.yaml，GitHub Actions 会自动重跑本脚本并部署。
"""
from pathlib import Path
import yaml
from jinja2 import Environment, select_autoescape

PAGES = [
    ("home",            "index.html",           "Home",            "home"),
    ("project",         "project.html",         "Project",         "split"),
    ("design",          "design.html",          "Design",          "cards"),
    ("parts",           "parts.html",           "Parts",           "parts"),
    ("model",           "model.html",           "Model",           "model"),
    ("engineering",     "engineering.html",     "Engineering",     "dbtl"),
    ("results",         "results.html",         "Results",         "stats"),
    ("notebook",        "notebook.html",        "Notebook",        "timeline"),
    ("human_practices", "human-practices.html", "Human Practices", "prose"),
    ("safety",          "safety.html",          "Safety",          "prose"),
    ("team",            "team.html",            "Team",            "team"),
    ("attributions",    "attributions.html",    "Attributions",    "prose"),
]

CSS = r"""/* =====================================================================
   Brazzein iGEM Wiki — 自托管样式（不依赖 CDN，符合 iGEM 资源限制）
   配色：浆果墨 / 蜂蜜琥珀 / 浆果红 / 植物绿，铺于暖纸底
   字体：系统衬线作标题、系统无衬线作正文（可后续替换为自托管字体）
   ===================================================================== */
:root{
  --paper:#faf5ee; --paper2:#f3e9da;
  --ink:#2e1a22; --ink-soft:#6a5158;
  --honey:#dc8a2e; --honey-deep:#b86d18;
  --berry:#b4344a; --green:#3d6b4f;
  --card:#fffdf9; --line:rgba(46,26,34,.12);
  --serif:Georgia,"Iowan Old Style","Palatino Linotype",Palatino,"Times New Roman",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --wrap:1120px;
}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{background:var(--paper); color:var(--ink); font-family:var(--sans); line-height:1.6; -webkit-font-smoothing:antialiased;}
a{color:inherit; text-decoration:none;}
.wrap{max-width:var(--wrap); margin:0 auto; padding:0 26px;}
.eyebrow{font-size:12px; font-weight:700; letter-spacing:.22em; text-transform:uppercase; color:var(--honey-deep);}
h2{font-family:var(--serif); font-weight:600; font-size:clamp(30px,5vw,46px); line-height:1.06; letter-spacing:-.5px;}
.lead{font-size:18px; color:var(--ink-soft); max-width:62ch; margin-top:14px;}

/* ---------- nav ---------- */
header{position:sticky; top:0; z-index:50; background:rgba(250,245,238,.86); backdrop-filter:blur(12px); border-bottom:1px solid var(--line);}
.nav{display:flex; align-items:center; justify-content:space-between; height:64px;}
.logo{font-family:var(--serif); font-weight:700; font-size:22px; letter-spacing:-.5px; display:flex; align-items:center; gap:9px;}
.logo .dot{width:11px; height:11px; border-radius:50%; background:var(--berry); box-shadow:0 0 0 4px rgba(180,52,74,.16);}
.nav-links{display:flex; gap:24px; font-size:14.5px; font-weight:500;}
.nav-links a{color:var(--ink-soft); transition:color .15s; padding-bottom:2px; border-bottom:2px solid transparent;}
.nav-links a:hover{color:var(--ink);}
.nav-links a.active{color:var(--ink); border-bottom-color:var(--honey);}
.menu-btn{display:none; background:none; border:none; font-size:26px; color:var(--ink); cursor:pointer;}

/* ---------- hero ---------- */
.hero{padding:78px 0 70px;}
.hero-grid{display:grid; grid-template-columns:1.15fr .85fr; gap:44px; align-items:center;}
.hero h1{font-family:var(--serif); font-weight:700; font-size:clamp(44px,8vw,84px); line-height:1; letter-spacing:-2px; margin:14px 0 18px;}
.hero h1 em{font-style:italic; font-weight:600; color:var(--berry);}
.hero p{font-size:19px; color:var(--ink-soft); max-width:46ch; margin-bottom:28px;}
.cta{display:flex; gap:12px; flex-wrap:wrap;}
.btn{display:inline-block; padding:13px 24px; border-radius:999px; font-weight:600; font-size:15px; transition:transform .12s;}
.btn:active{transform:scale(.97);}
.btn-solid{background:var(--ink); color:var(--paper);}
.btn-ghost{border:1.5px solid var(--line); color:var(--ink);}

/* signature: sweetness stat */
.sweet{background:linear-gradient(165deg,var(--honey),var(--honey-deep)); color:#fff; border-radius:22px; padding:34px 30px; box-shadow:0 24px 60px -24px rgba(184,109,24,.6);}
.sweet .k{font-size:13px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; opacity:.85;}
.sweet .big{font-family:var(--serif); font-weight:700; font-size:clamp(58px,12vw,92px); line-height:.9; margin:6px 0 2px;}
.sweet .big small{font-size:.42em; font-weight:600;}
.sweet .sub{font-size:15px; opacity:.92; line-height:1.5; border-top:1px solid rgba(255,255,255,.28); margin-top:18px; padding-top:16px;}
.sweet .bars{display:flex; align-items:flex-end; gap:8px; height:54px; margin-top:18px;}
.sweet .bar{flex:1; background:rgba(255,255,255,.32); border-radius:4px 4px 0 0;}
.sweet .bar.lit{background:#fff;}

/* ---------- page header ---------- */
.page-head{padding:64px 0 8px;}
.page-head h2{margin:12px 0 0;}

/* ---------- content block ---------- */
.block{padding:40px 0 70px;}

.split{display:grid; grid-template-columns:1fr 1fr; gap:24px;}
.panel{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:30px;}
.panel h3{font-family:var(--serif); font-size:23px; font-weight:600; margin-bottom:10px;}
.panel.problem{border-left:4px solid var(--berry);}
.panel.solution{border-left:4px solid var(--green);}
.panel p{color:var(--ink-soft); font-size:15.5px;}
.panel ul{list-style:none; margin-top:14px; font-size:15px;}
.panel li{padding:7px 0 7px 24px; position:relative; color:var(--ink-soft);}
.panel li::before{content:""; position:absolute; left:2px; top:14px; width:7px; height:7px; border-radius:50%; background:var(--honey);}

.cards{display:grid; grid-template-columns:repeat(2,1fr); gap:20px;}
.card-i{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:26px; transition:transform .18s, box-shadow .18s;}
.card-i:hover{transform:translateY(-3px); box-shadow:0 18px 40px -22px rgba(46,26,34,.35);}
.card-i .num{font-family:var(--serif); font-style:italic; font-size:15px; color:var(--honey-deep);}
.card-i h3{font-family:var(--serif); font-size:22px; font-weight:600; margin:6px 0 10px;}
.card-i p{font-size:14.5px; color:var(--ink-soft);}

.dbtl{display:grid; grid-template-columns:repeat(4,1fr);}
.dbtl-step{text-align:center; padding:0 14px; position:relative;}
.dbtl-step .ring{width:78px; height:78px; margin:0 auto 16px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:var(--serif); font-weight:700; font-size:30px; color:#fff; position:relative; z-index:2;}
.dbtl-step:nth-child(1) .ring{background:var(--berry);}
.dbtl-step:nth-child(2) .ring{background:var(--honey);}
.dbtl-step:nth-child(3) .ring{background:var(--green);}
.dbtl-step:nth-child(4) .ring{background:var(--ink);}
.dbtl-step::after{content:"\2192"; position:absolute; right:-8px; top:28px; font-size:22px; color:var(--ink-soft); z-index:1;}
.dbtl-step:last-child::after{content:"";}
.dbtl-step h4{font-size:16px; font-weight:600; margin-bottom:5px;}
.dbtl-step p{font-size:13.5px; color:var(--ink-soft);}

.stats{display:grid; grid-template-columns:repeat(3,1fr); gap:20px;}
.stat{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:26px;}
.stat .v{font-family:var(--serif); font-weight:700; font-size:42px; line-height:1; color:var(--berry);}
.stat .l{font-size:13px; color:var(--ink-soft); margin-top:8px;}
.note{display:inline-block; margin-top:22px; font-size:13px; color:var(--honey-deep); background:rgba(220,138,46,.1); border:1px dashed var(--honey); border-radius:8px; padding:8px 14px;}

.twocol{display:grid; grid-template-columns:1fr 1fr; gap:30px;}
.twocol p{color:var(--ink-soft); font-size:16px;}

.team-grid{display:grid; grid-template-columns:repeat(4,1fr); gap:18px;}
.member{text-align:center;}
.avatar{aspect-ratio:1; border-radius:14px; background:linear-gradient(150deg,var(--paper2),#e7d6c2); display:flex; align-items:center; justify-content:center; font-family:var(--serif); font-size:34px; color:var(--ink-soft); margin-bottom:10px;}
.member .n{font-weight:600; font-size:15px;}
.member .r{font-size:13px; color:var(--ink-soft);}

/* footer */
footer{background:var(--ink); color:#e9ddd6; padding:54px 0 34px; margin-top:10px;}
footer .ft{display:flex; justify-content:space-between; flex-wrap:wrap; gap:24px;}
footer .logo{color:#fff;}
footer .ft-tag{max-width:30ch; margin-top:12px; font-size:14px; color:#cdbcb2;}
footer a{color:#cdbcb2;} footer a:hover{color:#fff;}
footer .cols{display:flex; gap:54px; flex-wrap:wrap; font-size:14px;}
footer .cols b{display:block; color:#fff; margin-bottom:10px; font-size:13px; letter-spacing:.08em; text-transform:uppercase;}
footer .cols a{display:block; padding:4px 0;}
.copy{border-top:1px solid rgba(255,255,255,.14); margin-top:34px; padding-top:20px; font-size:13px; color:#a89a90; display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;}

/* reveal */
.reveal{opacity:0; transform:translateY(18px); transition:opacity .6s, transform .6s;}
.reveal.in{opacity:1; transform:none;}

@media(max-width:860px){
  .hero-grid,.split,.twocol{grid-template-columns:1fr;}
  .cards{grid-template-columns:1fr;}
  .dbtl{grid-template-columns:1fr 1fr; gap:30px 0;}
  .dbtl-step::after{display:none;}
  .stats{grid-template-columns:1fr;}
  .team-grid{grid-template-columns:1fr 1fr;}
  .nav-links{display:none; position:absolute; top:64px; left:0; right:0; flex-direction:column; background:var(--paper); padding:14px 26px 22px; border-bottom:1px solid var(--line); gap:0;}
  .nav-links.open{display:flex;}
  .nav-links a{padding:11px 0; border-bottom:1px solid var(--line);}
  .nav-links a.active{border-bottom-color:var(--line);}
  .menu-btn{display:block;}
}
@media (prefers-reduced-motion:reduce){ .reveal{opacity:1; transform:none; transition:none;} html{scroll-behavior:auto;} }

/* ---------- parts table ---------- */
.table-wrap{overflow-x:auto; border:1px solid var(--line); border-radius:16px; background:var(--card);}
table.parts{width:100%; border-collapse:collapse; font-size:14.5px; min-width:560px;}
table.parts th{text-align:left; font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-soft); padding:16px 18px; border-bottom:1px solid var(--line); background:var(--paper2);}
table.parts td{padding:15px 18px; border-bottom:1px solid var(--line); color:var(--ink-soft); vertical-align:top;}
table.parts tr:last-child td{border-bottom:none;}
table.parts .pid{font-family:ui-monospace,"SF Mono",monospace; color:var(--berry); white-space:nowrap;}
table.parts .tag{display:inline-block; font-size:12px; padding:3px 10px; border-radius:999px; background:rgba(61,107,79,.12); color:var(--green); font-weight:600;}

/* ---------- notebook timeline ---------- */
.timeline{position:relative; max-width:760px; padding-left:8px;}
.timeline::before{content:""; position:absolute; left:60px; top:8px; bottom:8px; width:2px; background:var(--line);}
.tl-item{display:grid; grid-template-columns:64px 1fr; gap:24px; padding:14px 0; position:relative;}
.tl-date{font-family:var(--serif); font-weight:700; font-size:18px; color:var(--honey-deep); text-align:right; padding-top:2px;}
.tl-body{position:relative;}
.tl-body::before{content:""; position:absolute; left:-30px; top:7px; width:13px; height:13px; border-radius:50%; background:var(--honey); box-shadow:0 0 0 4px var(--paper);}
.tl-body h4{font-size:17px; font-weight:600; margin-bottom:4px;}
.tl-body p{font-size:14.5px; color:var(--ink-soft);}
@media(max-width:860px){
  .timeline::before{left:46px;}
  .tl-item{grid-template-columns:46px 1fr; gap:18px;}
  .tl-date{font-size:15px;}
  .tl-body::before{left:-24px;}
}
"""

TEMPLATE = r"""{# 共用渲染宏：根据 kind 渲染一个栏目的正文。多页版和单文件版都 import 它。 #}
{% macro section(kind, data, site, page_title, with_head=True) %}

{% if kind == "home" %}
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">iGEM {{ site.year }} · Sweet Proteins</span>
      <h1>{{ data.hero_title_pre }} <em>{{ data.hero_title_em }}</em></h1>
      <p>{{ data.hero_lead }}</p>
      <div class="cta">
        <a href="project.html" data-go="project.html" class="btn btn-solid">Explore the project</a>
        <a href="team.html" data-go="team.html" class="btn btn-ghost">Meet the team</a>
      </div>
    </div>
    <div class="sweet reveal">
      <div class="k">Sweetness, gram for gram</div>
      <div class="big">{{ data.sweetness_value }}<small>{{ data.sweetness_unit }}</small></div>
      <div class="bars">
        <div class="bar" style="height:6%"></div><div class="bar" style="height:14%"></div>
        <div class="bar" style="height:30%"></div><div class="bar" style="height:55%"></div>
        <div class="bar lit" style="height:100%"></div>
      </div>
      <div class="sub">{{ data.sweetness_caption }}</div>
    </div>
  </div>
</section>

{% else %}
{% if with_head %}
<section class="page-head">
  <div class="wrap">
    <span class="eyebrow">{{ page_title }}</span>
    <h2>{{ data.heading }}</h2>
    {% if data.lead %}<p class="lead">{{ data.lead }}</p>{% endif %}
  </div>
</section>
{% endif %}

{% if kind == "split" %}
<section class="block"><div class="wrap split">
  <div class="panel problem reveal"><h3>{{ data.problem.title }}</h3><p>{{ data.problem.intro }}</p>
    <ul>{% for p in data.problem.points %}<li>{{ p }}</li>{% endfor %}</ul></div>
  <div class="panel solution reveal"><h3>{{ data.solution.title }}</h3><p>{{ data.solution.intro }}</p>
    <ul>{% for p in data.solution.points %}<li>{{ p }}</li>{% endfor %}</ul></div>
</div></section>

{% elif kind == "cards" %}
<section class="block"><div class="wrap cards">
  {% for c in data.pillars %}
  <div class="card-i reveal"><div class="num">Pillar {{ loop.index }}</div><h3>{{ c.title }}</h3><p>{{ c.text }}</p></div>
  {% endfor %}
</div></section>

{% elif kind == "model" %}
<section class="block"><div class="wrap">
  {% if data.intro %}<p class="lead" style="margin-bottom:30px">{{ data.intro }}</p>{% endif %}
  <div class="cards">
  {% for c in data.approaches %}
  <div class="card-i reveal"><h3>{{ c.title }}</h3><p>{{ c.text }}</p></div>
  {% endfor %}
  </div>
</div></section>

{% elif kind == "parts" %}
<section class="block"><div class="wrap">
  {% if data.intro %}<p class="lead" style="margin-bottom:26px">{{ data.intro }}</p>{% endif %}
  <div class="table-wrap"><table class="parts">
    <thead><tr><th>Part ID</th><th>Name</th><th>Type</th><th>Description</th></tr></thead>
    <tbody>
    {% for p in data['items'] %}
    <tr><td class="pid">{{ p.id }}</td><td>{{ p.name }}</td><td><span class="tag">{{ p.type }}</span></td><td>{{ p.desc }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div>
</div></section>

{% elif kind == "dbtl" %}
<section class="block"><div class="wrap"><div class="dbtl reveal">
  {% for s in data.dbtl %}
  <div class="dbtl-step"><div class="ring">{{ s.letter }}</div><h4>{{ s.title }}</h4><p>{{ s.text }}</p></div>
  {% endfor %}
</div></div></section>

{% elif kind == "stats" %}
<section class="block"><div class="wrap">
  <div class="stats">
  {% for s in data.stats %}
  <div class="stat reveal"><div class="v">{{ s.value }}</div><div class="l">{{ s.label }}</div></div>
  {% endfor %}
  </div>
  {% if data.note %}<span class="note">{{ data.note }}</span>{% endif %}
</div></section>

{% elif kind == "timeline" %}
<section class="block"><div class="wrap"><div class="timeline">
  {% for e in data.entries %}
  <div class="tl-item reveal"><div class="tl-date">{{ e.date }}</div><div class="tl-body"><h4>{{ e.title }}</h4><p>{{ e.text }}</p></div></div>
  {% endfor %}
</div></div></section>

{% elif kind == "prose" %}
<section class="block"><div class="wrap twocol reveal">
  {% for para in data.paragraphs %}<p>{{ para }}</p>{% endfor %}
</div></section>

{% elif kind == "team" %}
<section class="block"><div class="wrap team-grid reveal">
  {% for m in data.members %}
  <div class="member"><div class="avatar">{{ m.name[1] if m.name[0]=='[' else m.name[0] }}</div><div class="n">{{ m.name }}</div><div class="r">{{ m.role }}</div></div>
  {% endfor %}
</div></section>
{% endif %}

{% endif %}
{% endmacro %}
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ site.project_name }} · iGEM {{ site.year }}</title>
<style>
{{ css }}
[hidden]{display:none !important;}
.page{animation:fade .35s ease;}
@keyframes fade{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
</style>
</head>
<body>

<header>
  <div class="wrap nav">
    <a href="#home" data-page="home" class="logo"><span class="dot"></span>{{ site.project_name }}</a>
    <nav class="nav-links" id="menu">
      {% for p in pages %}
      <a href="#{{ p.slug }}" data-page="{{ p.slug }}"{% if loop.first %} class="active"{% endif %}>{{ p.label }}</a>
      {% endfor %}
    </nav>
    <button class="menu-btn" id="mbtn" aria-label="Menu">☰</button>
  </div>
</header>

<main>
{% for p in pages %}
<div class="page" id="page-{{ p.slug }}"{% if not loop.first %} hidden{% endif %}>
{{ section(p.kind, p.data, site, p.label) }}
</div>
{% endfor %}
</main>

<footer>
  <div class="wrap">
    <div class="ft">
      <div>
        <div class="logo"><span class="dot"></span>{{ site.project_name }}</div>
        <p class="ft-tag">{{ site.tagline }} iGEM {{ site.year }}.</p>
      </div>
      <div class="cols">
        <div><b>Project</b>
          <a href="#project" data-page="project">Description</a>
          <a href="#design" data-page="design">Design</a>
          <a href="#engineering" data-page="engineering">Engineering</a>
          <a href="#results" data-page="results">Results</a></div>
        <div><b>Team</b>
          <a href="#team" data-page="team">Members</a>
          <a href="#human_practices" data-page="human_practices">Human Practices</a>
          <a href="#safety" data-page="safety">Safety</a>
          <a href="#attributions" data-page="attributions">Attributions</a></div>
        <div><b>iGEM</b><a href="https://igem.org" target="_blank" rel="noopener">igem.org</a></div>
      </div>
    </div>
    <div class="copy">
      <span>© {{ site.year }} {{ site.team_name }} · Content licensed under CC BY 4.0</span>
      <span>Made for the iGEM competition</span>
    </div>
  </div>
</footer>

<script>
(function(){
  var pages=document.querySelectorAll('.page');
  var links=document.querySelectorAll('[data-page]');
  var menu=document.getElementById('menu'), mbtn=document.getElementById('mbtn');

  function show(slug){
    var found=false;
    pages.forEach(function(p){
      var on=(p.id==='page-'+slug);
      p.hidden=!on; if(on)found=true;
    });
    if(!found){ // fallback to home
      slug='home';
      pages.forEach(function(p){p.hidden=(p.id!=='page-home');});
    }
    document.querySelectorAll('.nav-links a').forEach(function(a){
      a.classList.toggle('active', a.getAttribute('data-page')===slug);
    });
    window.scrollTo(0,0);
    // re-trigger reveal
    document.querySelectorAll('#page-'+slug+' .reveal').forEach(function(el){el.classList.add('in');});
  }

  function go(slug){ if(location.hash.slice(1)!==slug){location.hash=slug;} else {show(slug);} }

  document.addEventListener('click',function(e){
    var a=e.target.closest('[data-page],[data-go]');
    if(!a)return;
    e.preventDefault();
    var slug=a.getAttribute('data-page');
    if(!slug){ var g=a.getAttribute('data-go')||''; slug=g.replace('.html','').replace('index','home'); }
    if(menu)menu.classList.remove('open');
    go(slug);
  });

  if(mbtn){mbtn.addEventListener('click',function(){menu.classList.toggle('open');});}
  window.addEventListener('hashchange',function(){show(location.hash.slice(1)||'home');});
  show(location.hash.slice(1)||'home');
})();
</script>
</body>
</html>
"""

def main():
    content = yaml.safe_load(Path("content.yaml").read_text(encoding="utf-8"))
    env = Environment(autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    tpl = env.from_string(TEMPLATE)
    pages = []
    for section, fname, label, kind in PAGES:
        slug = "home" if fname == "index.html" else fname.replace(".html", "")
        pages.append({"slug": slug, "label": label, "kind": kind,
                      "data": content.get(section, {})})
    html = tpl.render(site=content["site"], css=CSS, pages=pages)
    Path("index.html").write_text(html, encoding="utf-8")
    print(f"  built index.html ({len(html.encode())/1024:.1f} KB, {len(pages)} sections)")

if __name__ == "__main__":
    main()
