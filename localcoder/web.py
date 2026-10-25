<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LocalCoder RTX • Local-first AI coding agent</title>
<style>
:root{color-scheme:dark;font:15px system-ui;background:#071118;color:#edf3f7;--panel:#0f1d2a;--panel-2:#132535;--accent:#8ff7a9;--muted:#8ea3b6;--danger:#ff8b8b;--line:#24364a}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#122534 0%,#071118 45%,#03070b 100%)}header{border-bottom:1px solid var(--line);padding:22px 5%;display:flex;justify-content:space-between;align-items:center;background:rgba(7,17,24,.78);backdrop-filter:blur(10px);position:sticky;top:0;z-index:10}header strong{letter-spacing:.18em;font-size:12px}header .muted{color:var(--muted);letter-spacing:.16em;font-size:11px}.wrap{max-width:980px;margin:0 auto;padding:32px 5% 64px}.hero{padding:32px 0 18px}.hero h1{font-size:clamp(2.2rem,5vw,4.2rem);line-height:1.05;margin:0 0 18px;max-width:760px}.hero p{max-width:720px;color:#d9e6f1;font-size:1.08rem;line-height:1.7}.badge-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}.badge{padding:8px 12px;border-radius:999px;border:1px solid var(--line);background:rgba(143,247,169,.06);color:var(--accent);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase}.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin-top:24px}.card{background:linear-gradient(180deg,rgba(19,37,53,.96),rgba(11,20,29,.96));border:1px solid var(--line);border-radius:16px;padding:18px}.card h3{margin:0 0 12px;font-size:1.02rem}.card p{margin:0;color:var(--muted);line-height:1.6}.narrow{max-width:760px}.label{display:inline-block;padding:8px 10px;border-radius:999px;background:rgba(255,255,255,.04);border:1px solid var(--line);font-size:.7rem;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px}textarea,input,button{font:inherit}main form{margin-top:16px;background:rgba(12,19,28,.9);border:1px solid var(--line);border-radius:18px;padding:18px}.field{display:flex;flex-direction:column;gap:8px;margin-bottom:14px}.field label{color:var(--muted);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase}.field input, .field textarea{width:100%;padding:14px 16px;border-radius:10px;border:1px solid var(--line);background:#0a131d;color:#edf3f7;resize:vertical}.field textarea{min-height:120px}.row{display:flex;flex-wrap:wrap;gap:12px}.button{border:0;border-radius:10px;padding:12px 18px;cursor:pointer;font-weight:600;transition:.2s;}.button.primary{background:linear-gradient(135deg,var(--accent),#7eceff);color:#071118}.button.secondary{background:rgba(255,255,255,.03);border:1px solid var(--line);color:#edf3f7}.button:disabled{opacity:.5;cursor:not-allowed}.status{margin-top:16px;padding:12px 14px;border-radius:12px;background:rgba(143,247,169,.07);border:1px solid rgba(143,247,169,.2);color:#dfffea}.status.warn{background:rgba(255,139,139,.06);border-color:rgba(255,139,139,.2);color:#ffd7d7}.result{margin-top:18px;white-space:pre-wrap;background:#061017;border:1px solid var(--line);border-radius:14px;padding:16px;color:#dfeaf5;min-height:120px}.muted{color:var(--muted)}@media(max-width:640px){header{flex-direction:column;align-items:flex-start;gap:8px}} </style>
<header><strong>LOCALCODER / RTX</strong><span class="muted">PRIVATE · LOCAL INFERENCE</span></header>
<main class="wrap">
  <section class="hero">
    <div class="label">Local AI Coding Agent</div>
    <h1>Build software with a local LLM, real tools, and a safe workspace loop.</h1>
    <p>LocalCoder RTX turns prompts into code by reading files, editing a workspace, running commands, and recovering from failures with grounded tool feedback. It keeps the workflow local, private, and controllable.</p>
    <div class="badge-row">
      <span class="badge">Ollama</span>
      <span class="badge">Workspace tools</span>
      <span class="badge">CLI + UI</span>
      <span class="badge">Local-first</span>
    </div>
  </section>

  <section class="card-grid">
    <article class="card">
      <h3>Agent loop</h3>
      <p>Prompt → inspect → read → edit → run → repair → finish. Every action stays inside the project workspace and uses visible output for decisions.</p>
    </article>
    <article class="card">
      <h3>Safety</h3>
      <p>Commands are approved by default, file access is restricted to the workspace, and overwritten files are backed up before edits are saved.</p>
    </article>
    <article class="card">
      <h3>Research value</h3>
      <p>The project supports dataset creation, prompt testing, code-generation benchmark collection, and local LLM experimentation at the agent layer.</p>
    </article>
  </section>

  <div class="narrow">
    <form id="agent-form">
      <div class="field">
        <label for="workspace">Workspace</label>
        <input id="workspace" value="workspace" placeholder="workspace" />
      </div>
      <div class="field">
        <label for="model">Model</label>
        <input id="model" placeholder="qwen2.5-coder:3b" />
      </div>
      <div class="field">
        <label for="context">Context</label>
        <input id="context" value="4096" />
      </div>
      <div class="field">
        <label for="prompt">Prompt</label>
        <textarea id="prompt" placeholder="Build a dashboard, fix a bug, write a Python module, or refactor a project..."></textarea>
      </div>
      <div class="row">
        <button class="button primary" id="start" type="button">Start agent</button>
        <button class="button secondary" id="stop" type="button">Stop</button>
        <button class="button secondary" id="refresh" type="button">Refresh status</button>
      </div>
    </form>
    <div class="status" id="status">Ready.</div>
    <div class="status warn" id="approval" style="display:none">Waiting for approval...</div>
    <pre class="result" id="result"></pre>
  </div>
</main>
<script>
const $=id=>document.getElementById(id);const token='__TOKEN__';
async function api(path,data){const r=await fetch('/api/'+path,{method:data?'POST':'GET',headers:{'Content-Type':'application/json','X-LocalCoder-Token':token},body:data?JSON.stringify(data):undefined});const body=await r.json().catch(()=>({}));if(!r.ok) throw new Error(body.error||'Request failed');return body;}
async function health(){try{const v=await api('status');$('status').textContent=v.error? v.error+' Start Ollama, then run ollama pull '+v.default:'Ollama connected · GPU VRAM: '+(v.vram? v.vram+' GB':'not detected');$('status').classList.toggle('warn',!!v.error);$('model').value=v.default; if(!$('context').value) $('context').value='4096';}catch(e){$('status').textContent=e.message; $('status').classList.add('warn');}}
$('refresh').onclick=health;
$('start').onclick=async()=>{try{$('start').disabled=true;await api('start',{prompt:$('prompt').value,workspace:$('workspace').value,model:$('model').value,context:+$('context').value})}catch(e){$('result').textContent=e.message;} finally{$('start').disabled=false;}};
$('stop').onclick=()=>api('stop',{}).catch(e=>$('result').textContent=e.message);
for(const [id,allow] of [['yes',true],['no',false]])$(id).onclick=()=>api('approve',{allow}).catch(e=>$('result').textContent=e.message);
let last='';async function poll(){try{const s=await api('state');$('start').disabled=s.running;$('stop').disabled=!s.running;$('status').textContent=s.running?'Working…':'Ready';$('approval').style.display=s.pending?'block':'none';$('approval').textContent=s.pending? 'Approval required: '+s.pending:'Waiting for approval...';$('result').textContent=s.result||'Agent output will appear here.';last=s.result||'';}catch(e){$('status').textContent=e.message; $('status').classList.add('warn');}}
health();setInterval(poll,900);</script>
</html>
