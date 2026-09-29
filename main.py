import os
import json
import random
import gzip
import ssl
import http.client
import base64
from io import BytesIO
from datetime import datetime

import requests
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from flask import Flask, request, jsonify, render_template_string

import MajoRLoGinrEq_pb2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
PORT = int(os.environ.get("PORT", 8080))

app = Flask(__name__)


def encrypt_proto(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))


def decode_jwt(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        def b64(s):
            s += '=' * (-len(s) % 4)
            return json.loads(base64.urlsafe_b64decode(s).decode('utf-8'))
        return {"header": b64(parts[0]), "payload": b64(parts[1])}
    except Exception:
        return None


def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    data = {
        "uid": str(uid),
        "password": str(password),
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        if r.status_code == 200:
            j = r.json()
            return j.get('access_token'), j.get('open_id')
        return None, None
    except Exception:
        return None, None


def inspect_access_token(access_token: str):
    url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            j = r.json()
            uid = str(j.get("uid", ""))
            open_id = j.get("open_id", "")
            if uid and open_id:
                return uid, open_id
        return None, None
    except Exception:
        return None, None


def major_login_protobuf(access_token, open_id):
    try:
        m = MajoRLoGinrEq_pb2.MajorLogin()
        m.event_time = str(datetime.now())[:-7]
        m.game_name = "free fire"
        m.platform_id = 2
        m.client_version = "1.126.2"
        m.client_version_code = "2024010012"
        m.system_software = "Android OS 11 / API-30 (RQ3A.210805.001)"
        m.system_hardware = "Handheld"
        m.device_type = "Handheld"
        m.telecom_operator = "Verizon"
        m.network_operator_a = "Verizon"
        m.network_type = "WIFI"
        m.network_type_a = "WIFI"
        m.screen_width = 1080
        m.screen_height = 2400
        m.screen_dpi = "440"
        m.processor_details = "ARMv8"
        m.cpu_type = 2
        m.cpu_architecture = "64"
        m.memory = 6144
        m.gpu_renderer = "Adreno (TM) 650"
        m.gpu_version = "OpenGL ES 3.2 V@1.50"
        m.graphics_api = "OpenGLES3"
        m.unique_device_id = f"Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c{random.randint(10,99)}"
        m.client_ip = ""
        m.language = "en"
        m.open_id = open_id
        m.open_id_type = "4"
        m.login_open_id_type = 4
        m.access_token = access_token
        m.login_by = 3
        m.platform_sdk_id = 2
        m.origin_platform_type = "4"
        m.primary_platform_type = "4"

        mem = m.memory_available
        mem.version = 55
        mem.hidden_value = 81

        m.external_storage_total = 128512
        m.external_storage_available = random.randint(38000, 52000)
        m.internal_storage_total = 110731
        m.internal_storage_available = random.randint(18000, 32000)
        m.game_disk_storage_total = 26628
        m.game_disk_storage_available = random.randint(18000, 25000)
        m.external_sdcard_total_storage = 119234
        m.external_sdcard_avail_storage = random.randint(25000, 60000)
        m.library_path = f"/data/app/~~{random.randint(100,999)}/base.apk"
        m.library_token = "hash|base.apk"
        m.client_using_version = "7428b253defc164018c604a1ebbfebdf"
        m.supported_astc_bitset = 16383
        m.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
        m.loading_time = random.randint(9000, 18000)
        m.release_channel = "android"
        m.channel_type = 3
        m.reg_avatar = 1
        m.if_push = 1
        m.is_vpn = 0
        m.android_engine_init_flag = 110009

        encrypted = encrypt_proto(m.SerializeToString())

        context = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=15)
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        conn.request("POST", "/MajorLogin", body=encrypted, headers=headers)
        response = conn.getresponse()
        raw = response.read()

        if response.getheader('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=BytesIO(raw)) as f:
                raw = f.read()
        conn.close()

        if response.status in [200, 201]:
            return raw
        return None
    except Exception:
        return None


def parse_major_response(raw_bytes):
    """Try JSON first; fall back to hex/protobuf."""
    if raw_bytes is None:
        return None

    try:
        text = raw_bytes.decode('utf-8', errors='ignore').strip()
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)
    except Exception:
        pass

    try:
        cleaned = ''.join(c for c in raw_bytes.decode('utf-8', errors='ignore') if c.isprintable() or c in '\n\r\t')
        cleaned = cleaned.strip()
        if cleaned.startswith('{') and cleaned.endswith('}'):
            return json.loads(cleaned)
    except Exception:
        pass

    try:
        marker = raw_bytes.find(b'{')
        if marker != -1:
            end = raw_bytes.rfind(b'}')
            if end > marker:
                return json.loads(raw_bytes[marker:end+1].decode('utf-8', errors='ignore'))
    except Exception:
        pass

    return None


def build_result(uid, open_id, access_token):
    raw = major_login_protobuf(access_token, open_id)
    if raw is None:
        return {"success": False, "message": "MajorLogin failed. Account may be banned."}

    data = parse_major_response(raw)
    if not data:
        return {"success": False, "message": "Failed to parse MajorLogin response."}

    token = data.get("token")
    if not token:
        return {"success": False, "message": "No JWT token received."}

    decoded = decode_jwt(token) or {}
    payload = decoded.get("payload", {})
    region = (
        data.get("notiRegion")
        or data.get("lockRegion")
        or payload.get("noti_region")
        or "IND"
    )

    return {
        "success": True,
        "account_uid": str(data.get("accountId")),
        "Uid": str(uid),
        "jwt_decoded": decoded,
        "platform_type_used": 8,
        "region": region,
        "lock_region": data.get("lockRegion"),
        "noti_region": data.get("notiRegion"),
        "ip_region": data.get("ipRegion"),
        "agora_environment": data.get("agoraEnvironment"),
        "ttl": data.get("ttl"),
        "server_url": data.get("serverUrl"),
        "ip_city": data.get("ipCity"),
        "kts": data.get("kts"),
        "ak": data.get("ak"),
        "aiv": data.get("aiv"),
        "ff_anti_url": data.get("ffAntiUrl"),
        "ff_anti_config": data.get("ffAntiConfigDesc"),
        "connection_seed": data.get("connectionSeed"),
        "timestamp": int(datetime.now().timestamp()),
        "token": token,
        "token_access": access_token,
        "url": f"https://client.{str(region).lower()}.freefiremobile.com",
    }


def gen_from_uid_pass(uid, password):
    if not uid or not password:
        return {"success": False, "message": "UID and Password are required."}
    if not uid.isdigit() or len(uid) < 8:
        return {"success": False, "message": "Invalid UID format."}

    access_token, open_id = get_access_token(uid, password)
    if not access_token or not open_id:
        return {"success": False, "message": "Invalid UID or Password."}

    return build_result(uid, open_id, access_token)


def gen_from_access_token(access_token):
    if not access_token or len(access_token) < 20:
        return {"success": False, "message": "Invalid access token."}

    uid, open_id = inspect_access_token(access_token)
    if not uid or not open_id:
        return {"success": False, "message": "Access token is invalid or expired."}

    return build_result(uid, open_id, access_token)


HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Obscura JWT Generator</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#07070b;--panel:#0e0e14;--panel-2:#14141c;
  --border:#1e1e2a;--text:#e6e6ef;--muted:#6b6b80;
  --accent:#7c5cff;--accent-2:#ff3d81;--ok:#22d67a;--err:#ff4d6d;
}
html,body{height:100%}
body{
  background:var(--bg);color:var(--text);
  font-family:'Space Grotesk',sans-serif;
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  padding:24px 16px;position:relative;overflow-x:hidden;
}
body::before{
  content:"";position:fixed;inset:0;
  background:
    radial-gradient(900px 500px at 15% -10%, rgba(124,92,255,0.18), transparent 60%),
    radial-gradient(800px 500px at 90% 110%, rgba(255,61,129,0.14), transparent 60%);
  pointer-events:none;z-index:0;
}
body::after{
  content:"";position:fixed;inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
  background-size:32px 32px;
  mask-image:radial-gradient(ellipse at center, black 40%, transparent 80%);
  pointer-events:none;z-index:0;
}
.wrap{
  position:relative;z-index:1;width:100%;max-width:640px;
  background:linear-gradient(180deg, rgba(20,20,28,0.9), rgba(14,14,20,0.95));
  border:1px solid var(--border);border-radius:22px;padding:32px 28px;
  backdrop-filter:blur(20px);
  box-shadow:0 30px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.03);
}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:6px}
.dot{width:10px;height:10px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--accent-2));
  box-shadow:0 0 16px rgba(124,92,255,0.7);}
.brand h1{font-size:20px;font-weight:700;letter-spacing:0.5px;
  background:linear-gradient(90deg,#fff 0%,#b9a8ff 60%,#ff8fb8 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.brand small{color:var(--muted);font-size:11px;font-weight:400;
  margin-left:auto;letter-spacing:1.5px;text-transform:uppercase;
  font-family:'JetBrains Mono',monospace;}
.tabs{display:grid;grid-template-columns:1fr 1fr;gap:6px;
  background:var(--panel-2);padding:5px;border-radius:12px;
  border:1px solid var(--border);margin:22px 0 20px;}
.tab{padding:11px 14px;text-align:center;border-radius:9px;
  font-size:13px;font-weight:500;color:var(--muted);
  cursor:pointer;transition:all 0.25s ease;user-select:none;letter-spacing:0.3px;}
.tab:hover{color:#cfcfdd}
.tab.active{background:linear-gradient(135deg,rgba(124,92,255,0.9),rgba(255,61,129,0.85));
  color:#fff;box-shadow:0 6px 20px rgba(124,92,255,0.35);}
.field{margin-bottom:14px}
.field label{display:block;font-size:11px;font-weight:500;letter-spacing:1.6px;
  text-transform:uppercase;color:var(--muted);margin-bottom:7px;
  font-family:'JetBrains Mono',monospace;}
.field input,.field textarea{
  width:100%;padding:14px 15px;background:var(--panel-2);
  border:1px solid var(--border);border-radius:11px;color:var(--text);
  font-family:'JetBrains Mono',monospace;font-size:13px;outline:none;
  transition:all 0.25s ease;resize:vertical;}
.field input::placeholder,.field textarea::placeholder{color:#3a3a4d}
.field input:focus,.field textarea:focus{
  border-color:rgba(124,92,255,0.6);
  box-shadow:0 0 0 3px rgba(124,92,255,0.12);background:#15151f;}
.btn{width:100%;padding:15px;margin-top:6px;border:none;border-radius:11px;
  font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:600;
  letter-spacing:1.8px;text-transform:uppercase;cursor:pointer;
  background:linear-gradient(135deg,#7c5cff,#ff3d81);color:#fff;
  position:relative;overflow:hidden;transition:transform 0.2s ease, box-shadow 0.25s ease;}
.btn:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 14px 34px rgba(124,92,255,0.4);}
.btn:active:not(:disabled){transform:translateY(0)}
.btn:disabled{opacity:0.5;cursor:not-allowed}
.btn .sp{display:inline-block;width:12px;height:12px;
  border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;
  border-radius:50%;animation:spin 0.7s linear infinite;
  margin-right:8px;vertical-align:-2px;}
@keyframes spin{to{transform:rotate(360deg)}}
.out{margin-top:20px;border-radius:14px;background:var(--panel-2);
  border:1px solid var(--border);overflow:hidden;display:none;}
.out.show{display:block;animation:fade 0.35s ease}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.out-head{padding:13px 16px;display:flex;align-items:center;gap:9px;
  border-bottom:1px solid var(--border);font-size:13px;font-weight:500;}
.out-head .ic{width:8px;height:8px;border-radius:50%;background:var(--ok);
  box-shadow:0 0 10px var(--ok);}
.out-head .ic.err{background:var(--err);box-shadow:0 0 10px var(--err)}
.out-head .msg{color:#cfcfdd}
.out-body{padding:6px 16px 14px}
.row{display:flex;justify-content:space-between;gap:12px;
  padding:8px 0;border-bottom:1px dashed rgba(255,255,255,0.05);
  font-size:12px;align-items:center;}
.row:last-child{border-bottom:none}
.row .k{color:var(--muted);font-family:'JetBrains Mono',monospace;
  font-size:11px;letter-spacing:0.5px;flex-shrink:0;}
.row .v{color:#d8d8e6;text-align:right;word-break:break-all;
  font-family:'JetBrains Mono',monospace;font-size:11px;}
.row .v.tok{color:#c4b1ff}
.row .v.hl{color:#ff8fb8}
.actions{display:flex;gap:8px;padding:12px 16px 14px;border-top:1px solid var(--border)}
.actions button{flex:1;padding:10px;border-radius:9px;
  background:rgba(255,255,255,0.04);border:1px solid var(--border);
  color:#c7c7d6;font-family:'Space Grotesk',sans-serif;
  font-size:11px;font-weight:500;letter-spacing:1.2px;
  text-transform:uppercase;cursor:pointer;transition:all 0.2s ease;}
.actions button:hover{background:rgba(124,92,255,0.14);
  border-color:rgba(124,92,255,0.4);color:#fff}
.actions button.done{color:var(--ok);border-color:rgba(34,214,122,0.4);
  background:rgba(34,214,122,0.08)}
.raw{padding:0 16px 14px;}
.raw summary{cursor:pointer;color:var(--muted);font-size:11px;
  letter-spacing:1px;font-family:'JetBrains Mono',monospace;
  text-transform:uppercase;user-select:none;}
.raw pre{margin-top:8px;background:#0a0a10;border:1px solid var(--border);
  border-radius:9px;padding:12px;max-height:260px;overflow:auto;
  font-size:11px;line-height:1.55;color:#b9b9cc;
  font-family:'JetBrains Mono',monospace;}
.footer{text-align:center;margin-top:20px;color:#2e2e3e;
  font-size:10px;letter-spacing:2.5px;font-family:'JetBrains Mono',monospace;
  text-transform:uppercase;}
.footer b{color:#6b6b80;font-weight:500}
@media (max-width:520px){
  .wrap{padding:26px 18px;border-radius:18px}
  .brand h1{font-size:17px}
  .tabs{grid-template-columns:1fr}
  .row{flex-direction:column;align-items:flex-start;gap:3px}
  .row .v{text-align:left;max-width:100%}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand">
    <span class="dot"></span>
    <h1>Obscura JWT</h1>
    <small>v2.1</small>
  </div>

  <div class="tabs">
    <div class="tab active" data-mode="uid">UID + Password</div>
    <div class="tab" data-mode="token">Access Token</div>
  </div>

  <div id="uidFields">
    <div class="field">
      <label>UID</label>
      <input type="text" id="uid" placeholder="Enter Free Fire UID" autocomplete="off">
    </div>
    <div class="field">
      <label>Password</label>
      <input type="password" id="password" placeholder="Enter Free Fire Password" autocomplete="off">
    </div>
  </div>

  <div id="tokenFields" style="display:none">
    <div class="field">
      <label>Access Token</label>
      <textarea id="access_token" rows="3" placeholder="Paste Garena access token"></textarea>
    </div>
  </div>

  <button class="btn" id="go" onclick="run()">Generate JWT</button>

  <div class="out" id="out">
    <div class="out-head">
      <span class="ic" id="ic"></span>
      <span class="msg" id="msg">—</span>
    </div>
    <div class="out-body" id="body"></div>
    <div class="actions">
      <button onclick="copyToken()" id="btnTok">Copy Token</button>
      <button onclick="copyAll()" id="btnAll">Copy All</button>
    </div>
    <details class="raw">
      <summary>Raw Response</summary>
      <pre id="raw"></pre>
    </details>
  </div>

  <div class="footer">Dev <b>@ObscuraApis</b></div>
</div>

<script>
let mode = "uid";
let last = null;

document.querySelectorAll(".tab").forEach(t=>{
  t.onclick = () => {
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    mode = t.dataset.mode;
    document.getElementById("uidFields").style.display = mode==="uid" ? "block":"none";
    document.getElementById("tokenFields").style.display = mode==="token" ? "block":"none";
  };
});

async function run(){
  const go = document.getElementById("go");
  const out = document.getElementById("out");

  let payload = {};
  if(mode==="uid"){
    const uid = document.getElementById("uid").value.trim();
    const pw = document.getElementById("password").value.trim();
    if(!uid || !pw){ show(false,"UID and Password are required.",{}); return; }
    payload = {uid, password: pw};
  } else {
    const tok = document.getElementById("access_token").value.trim();
    if(!tok){ show(false,"Access token is required.",{}); return; }
    payload = {access_token: tok};
  }

  go.disabled = true;
  go.innerHTML = '<span class="sp"></span>Generating';
  out.classList.remove("show");

  try{
    const r = await fetch("/NIROB",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    last = d;
    show(d.success, d.message || (d.success?"Success":"Failed"), d);
  } catch(e){
    show(false, "Network error", {});
  } finally {
    go.disabled = false;
    go.textContent = "Generate JWT";
  }
}

function show(ok, msgText, d){
  const out = document.getElementById("out");
  const ic = document.getElementById("ic");
  const msg = document.getElementById("msg");
  const body = document.getElementById("body");
  const raw = document.getElementById("raw");

  ic.className = "ic" + (ok ? "" : " err");
  msg.textContent = msgText;

  if(!ok){
    body.innerHTML = "";
    raw.textContent = JSON.stringify(d, null, 2);
    out.classList.add("show");
    return;
  }

  const jd = d.jwt_decoded || {};
  const pl = jd.payload || {};
  const rows = [
    ["Account UID", d.account_uid, "hl"],
    ["UID", d.Uid],
    ["Nickname", pl.nickname],
    ["Region", d.region],
    ["Lock Region", d.lock_region || pl.lock_region],
    ["Noti Region", d.noti_region || pl.noti_region],
    ["IP Region", d.ip_region],
    ["Country", pl.country_code],
    ["Platform", d.platform_type_used],
    ["Emulator", String(pl.is_emulator)],
    ["Release", pl.release_version],
    ["TTL", d.ttl],
    ["Expires", pl.exp],
    ["Server URL", d.server_url, "tok"],
    ["IP City", d.ip_city],
    ["Anti URL", d.ff_anti_url, "tok"],
    ["KTS", d.kts],
    ["AK", d.ak, "tok"],
    ["AIV", d.aiv, "tok"],
    ["Connection Seed", d.connection_seed, "tok"],
    ["Token", d.token, "tok"],
  ];

  body.innerHTML = rows.map(([k,v,cls])=>{
    if(v===undefined||v===null||v==="") v = "—";
    return `<div class="row"><span class="k">${k}</span><span class="v ${cls||''}">${v}</span></div>`;
  }).join("");

  raw.textContent = JSON.stringify(d, null, 2);
  out.classList.add("show");
}

function copyToken(){
  if(!last || !last.token) return;
  navigator.clipboard.writeText(last.token).then(()=>flash("btnTok","Copied"));
}
function copyAll(){
  if(!last) return;
  navigator.clipboard.writeText(JSON.stringify(last,null,2)).then(()=>flash("btnAll","Copied"));
}
function flash(id, txt){
  const b = document.getElementById(id);
  const o = b.textContent;
  b.textContent = txt; b.classList.add("done");
  setTimeout(()=>{b.textContent = o; b.classList.remove("done");}, 1500);
}
</script>
</body>
</html>'''


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/NIROB", methods=["GET", "POST"])
def nirob():
    if request.method == "GET":
        uid = request.args.get("uid", "").strip()
        password = request.args.get("password", "").strip()
        access_token = request.args.get("access_token", "").strip()
    else:
        data = request.get_json(silent=True) or {}
        uid = str(data.get("uid", "")).strip()
        password = str(data.get("password", "")).strip()
        access_token = str(data.get("access_token", "")).strip()

    if access_token:
        response = gen_from_access_token(access_token)
    elif uid and password:
        response = gen_from_uid_pass(uid, password)
    else:
        response = {"success": False, "message": "Provide uid+password or access_token."}

    resp = jsonify(response)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/api", methods=["GET", "POST"])
def api():
    return nirob()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
