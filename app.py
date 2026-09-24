import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Kallpa Motos - Motocross",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background: #080b12; }
    header { visibility: hidden; }
    .block-container { padding: 0.6rem 0.8rem 0; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)

game = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
body{margin:0;background:#080b12;color:#fff;font-family:Arial,Helvetica,sans-serif;overflow:hidden}
.wrap{width:100%;max-width:1250px;margin:auto}
.top{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:linear-gradient(90deg,#111827,#0b1220);border:1px solid #263247;border-radius:14px 14px 0 0}
.logo{font-weight:900;letter-spacing:1px;font-size:24px}.logo span{color:#ffcf00}
.stats{display:flex;gap:18px;font-weight:700}.stats b{color:#ffcf00}
canvas{width:100%;height:auto;display:block;background:#9bd8ff;border:1px solid #263247;border-top:0}
.help{text-align:center;color:#b9c2d0;font-size:13px;padding:8px}
button{background:#ffcf00;border:0;border-radius:10px;padding:10px 18px;font-weight:900;cursor:pointer}
.overlay{position:fixed;inset:0;background:rgba(3,6,12,.74);display:flex;align-items:center;justify-content:center;z-index:10}
.card{background:#101827;border:1px solid #334155;border-radius:18px;padding:28px;text-align:center;box-shadow:0 20px 80px #0009;max-width:430px}
.card h1{margin:0 0 8px;font-size:38px}.card p{color:#cbd5e1}
.hidden{display:none}
.mobile{display:none;justify-content:center;gap:12px;padding:10px}
.mobile button{width:75px;height:48px;font-size:20px}
@media(max-width:700px){.stats{gap:8px;font-size:12px}.logo{font-size:17px}.mobile{display:flex}}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <div class="logo">🏍️ KALLPA <span>MOTOS</span></div>
    <div class="stats">Puntos: <b id="score">0</b> | Récord: <b id="best">0</b> | Velocidad: <b id="speed">1</b>x</div>
  </div>
  <canvas id="game" width="1200" height="600"></canvas>
  <div class="mobile">
    <button id="left">◀</button><button id="jump">⬆ SALTAR</button><button id="right">▶</button>
  </div>
  <div class="help">ESPACIO / ↑ = saltar &nbsp; • &nbsp; ← → = inclinar la moto &nbsp; • &nbsp; P = pausa &nbsp; • &nbsp; R = reiniciar</div>
</div>

<div id="start" class="overlay">
 <div class="card">
   <div style="font-size:58px">🏍️</div>
   <h1>KALLPA MOTOS</h1>
   <p>¡Supera los obstáculos, salta las rampas y consigue la mayor puntuación!</p>
   <button onclick="startGame()">EMPEZAR</button>
 </div>
</div>
<div id="over" class="overlay hidden">
 <div class="card">
   <div style="font-size:58px">💥</div>
   <h1>¡CAÍSTE!</h1>
   <p>Puntuación: <b id="finalScore">0</b></p>
   <button onclick="restart()">JUGAR DE NUEVO</button>
 </div>
</div>

<script>
const c=document.getElementById("game"),ctx=c.getContext("2d");
const W=c.width,H=c.height,ground=500;
let running=false,paused=false,score=0,best=Number(localStorage.kallpaBest||0);
let speed=7,frame=0,world=0,angle=0;
const keys={left:false,right:false};
const bike={x:210,y:450,vy:0,rot:0,onGround:true};
let obstacles=[];

document.getElementById("best").textContent=best;
function resize(){ /* canvas scales with CSS */ }
function reset(){
 score=0; frame=0; world=0; speed=7; angle=0;
 bike.x=210;bike.y=ground-48;bike.vy=0;bike.rot=0;bike.onGround=true;
 obstacles=[];
 for(let i=0;i<7;i++) addObstacle(720+i*260);
 document.getElementById("score").textContent=0;
 document.getElementById("over").classList.add("hidden");
}
function addObstacle(x){
 const types=["rock","barrel","ramp","rock"];
 const type=types[Math.floor(Math.random()*types.length)];
 obstacles.push({x,y:ground-(type==="ramp"?25:28),type,w:type==="ramp"?90:38,h:type==="ramp"?25:38});
}
function startGame(){document.getElementById("start").classList.add("hidden");reset();running=true;requestAnimationFrame(loop)}
function restart(){reset();running=true;requestAnimationFrame(loop)}
function gameOver(){
 running=false;
 best=Math.max(best,score);localStorage.kallpaBest=best;
 document.getElementById("best").textContent=best;
 document.getElementById("finalScore").textContent=score;
 document.getElementById("over").classList.remove("hidden");
}
function jump(){if(running&&!paused&&bike.onGround){bike.vy=-17;bike.onGround=false}}
function key(e,down){
 if(["ArrowUp","Space"].includes(e.code)){e.preventDefault();if(down)jump()}
 if(e.code==="ArrowLeft")keys.left=down;
 if(e.code==="ArrowRight")keys.right=down;
 if(e.code==="KeyP"&&down)paused=!paused;
 if(e.code==="KeyR"&&down)restart();
}
addEventListener("keydown",e=>key(e,true));addEventListener("keyup",e=>key(e,false));
document.getElementById("jump").onclick=jump;
document.getElementById("left").onpointerdown=()=>keys.left=true;
document.getElementById("left").onpointerup=()=>keys.left=false;
document.getElementById("right").onpointerdown=()=>keys.right=true;
document.getElementById("right").onpointerup=()=>keys.right=false;

function drawBackground(){
 ctx.fillStyle="#9bd8ff";ctx.fillRect(0,0,W,H);
 // sun
 ctx.fillStyle="#ffe27a";ctx.beginPath();ctx.arc(1020,100,48,0,Math.PI*2);ctx.fill();
 // mountains
 ctx.fillStyle="#79b98b";ctx.beginPath();ctx.moveTo(0,390);ctx.lineTo(190,190);ctx.lineTo(330,390);ctx.lineTo(520,160);ctx.lineTo(730,390);ctx.lineTo(900,210);ctx.lineTo(1200,390);ctx.lineTo(1200,500);ctx.lineTo(0,500);ctx.fill();
 // ground
 ctx.fillStyle="#9b6b3f";ctx.fillRect(0,ground,W,H-ground);
 ctx.fillStyle="#3e9a45";ctx.fillRect(0,ground,W,12);
 // track
 ctx.strokeStyle="#6e492d";ctx.lineWidth=4;
 for(let x=-((world*1.5)%90);x<W;x+=90){ctx.beginPath();ctx.moveTo(x,535);ctx.lineTo(x+45,535);ctx.stroke()}
}
function drawBike(){
 ctx.save();ctx.translate(bike.x,bike.y);ctx.rotate(bike.rot);
 // shadow
 ctx.restore();
 ctx.save();ctx.translate(bike.x,bike.y);ctx.rotate(bike.rot);
 // wheels
 for(const wx of [-34,34]){ctx.fillStyle="#16181d";ctx.beginPath();ctx.arc(wx,35,18,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#d5d8dd";ctx.lineWidth=3;ctx.beginPath();ctx.arc(wx,35,9,0,Math.PI*2);ctx.stroke()}
 // frame
 ctx.strokeStyle="#ffcf00";ctx.lineWidth=7;ctx.beginPath();ctx.moveTo(-34,32);ctx.lineTo(0,5);ctx.lineTo(34,32);ctx.lineTo(10,30);ctx.lineTo(-34,32);ctx.stroke();
 // fork
 ctx.strokeStyle="#ddd";ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(15,5);ctx.lineTo(34,32);ctx.stroke();
 // body
 ctx.fillStyle="#ef4444";ctx.beginPath();ctx.moveTo(-8,-8);ctx.lineTo(18,-5);ctx.lineTo(28,8);ctx.lineTo(-2,8);ctx.closePath();ctx.fill();
 // rider
 ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(-3,-25,12,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle="#111827";ctx.lineWidth=10;ctx.beginPath();ctx.moveTo(-4,-14);ctx.lineTo(-15,8);ctx.stroke();
 ctx.restore();
}
function drawObstacle(o){
 ctx.save();ctx.translate(o.x,o.y);
 if(o.type==="rock"){ctx.fillStyle="#555b63";ctx.beginPath();ctx.moveTo(-22,28);ctx.lineTo(-16,2);ctx.lineTo(0,-8);ctx.lineTo(21,8);ctx.lineTo(25,28);ctx.closePath();ctx.fill()}
 if(o.type==="barrel"){ctx.fillStyle="#e84a2e";ctx.fillRect(-18,-5,36,38);ctx.strokeStyle="#ffd166";ctx.lineWidth=4;ctx.strokeRect(-18,-5,36,38);ctx.beginPath();ctx.moveTo(-18,8);ctx.lineTo(18,8);ctx.moveTo(-18,22);ctx.lineTo(18,22);ctx.stroke()}
 if(o.type==="ramp"){ctx.fillStyle="#f59e0b";ctx.beginPath();ctx.moveTo(-45,25);ctx.lineTo(45,25);ctx.lineTo(45,-2);ctx.closePath();ctx.fill()}
 ctx.restore();
}
function collide(o){
 const bx=bike.x, by=bike.y+15;
 return Math.abs(bx-o.x)<(o.w/2+35) && by>o.y-18 && by<o.y+42;
}
function loop(){
 if(!running)return;
 if(!paused){
   frame++;world+=speed;
   speed=Math.min(13,7+score/180);
   bike.vy+=0.72;bike.y+=bike.vy;
   bike.onGround=false;
   if(bike.y>=ground-48){bike.y=ground-48;bike.vy=0;bike.onGround=true}
   if(keys.left)bike.rot-=0.055;if(keys.right)bike.rot+=0.055;
   if(bike.onGround)bike.rot*=0.75;
   obstacles.forEach(o=>o.x-=speed);
   if(obstacles.length<8) addObstacle(1250+Math.random()*300);
   obstacles=obstacles.filter(o=>o.x>-120);
   for(const o of obstacles)if(collide(o)){gameOver();return}
   score++;
   document.getElementById("score").textContent=score;
   document.getElementById("speed").textContent=(speed/7).toFixed(1);
 }
 drawBackground();
 obstacles.forEach(drawObstacle);
 drawBike();
 if(paused){ctx.fillStyle="#0009";ctx.fillRect(0,0,W,H);ctx.fillStyle="#fff";ctx.font="bold 52px Arial";ctx.textAlign="center";ctx.fillText("PAUSA",W/2,270)}
 requestAnimationFrame(loop);
}
</script>
</body>
</html>
"""
components.html(game, height=720, scrolling=False)
