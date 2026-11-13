(() => {
const cfg=window.RELAYCHAT, buttons=[...document.querySelectorAll(".room-button")];
const title=document.getElementById("room-title"), desc=document.getElementById("room-description");
const area=document.getElementById("messages"), form=document.getElementById("message-form");
const input=document.getElementById("message-input"), sendBtn=document.getElementById("send-button");
const count=document.getElementById("online-count"), pill=document.getElementById("connection-pill");
const label=document.getElementById("connection-label"), toast=document.getElementById("toast");
const charCount=document.getElementById("char-count");
let ws=null, active=null, retry=null, toastTimer=null;
function notify(msg){toast.textContent=msg;toast.classList.add("visible");clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove("visible"),3000);}
function status(ok){pill.classList.toggle("connected",ok);label.textContent=ok?"Connected":"Reconnecting";}
function send(obj){if(ws&&ws.readyState===WebSocket.OPEN)ws.send(JSON.stringify(obj));else notify("Connection is not ready yet.");}
function connect(){
 clearTimeout(retry); ws=new WebSocket(cfg.websocketUrl);
 ws.addEventListener("open",()=>{status(true);if(active)send({type:"join",room_id:active.id});});
 ws.addEventListener("message",ev=>{let d;try{d=JSON.parse(ev.data)}catch{return}
  if(d.type==="history"&&d.room_id===active?.id){renderHistory(d.messages||[]);input.disabled=false;sendBtn.disabled=false;input.placeholder=`Message #${active.name}`;input.focus();}
  else if(d.type==="message"&&d.message)append(d.message);
  else if(d.type==="online_count"&&d.room_id===active?.id)count.textContent=`${d.count} HERE`;
  else if(d.type==="error")notify(d.message||"Something went wrong.");
 });
 ws.addEventListener("close",()=>{status(false);input.disabled=true;sendBtn.disabled=true;retry=setTimeout(connect,1800);});
 ws.addEventListener("error",()=>{status(false);ws.close();});
}
function choose(room){
 active=room;buttons.forEach(b=>b.classList.toggle("active",Number(b.dataset.roomId)===room.id));
 title.textContent="# "+room.name;desc.textContent=room.description;count.textContent="LOADING";
 input.disabled=true;sendBtn.disabled=true;input.placeholder="Loading conversation…";area.replaceChildren();
 send({type:"join",room_id:room.id});
}
function renderHistory(list){
 area.replaceChildren();
 if(!list.length){const e=document.createElement("div");e.className="empty-room";e.innerHTML="<span>✳</span><strong>It’s quiet in here.</strong><p>Start the conversation with the first message.</p>";area.append(e);return;}
 list.forEach(append);area.scrollTop=area.scrollHeight;
}
function append(m){
 if(!active)return;
 document.getElementById("welcome-card")?.remove();
 const item=document.createElement("article");item.className="message-item"+(m.username===cfg.username?" own-message":"");
 const avatar=document.createElement("div");avatar.className="message-avatar";avatar.textContent=(m.username||"?")[0].toUpperCase();
 const body=document.createElement("div");body.className="message-body";
 const meta=document.createElement("div");meta.className="message-meta";
 const name=document.createElement("strong");name.textContent=m.username||"Unknown";
 const time=document.createElement("time");time.textContent=formatTime(m.sent_at);meta.append(name,time);
 const text=document.createElement("p");text.textContent=m.content;body.append(meta,text);item.append(avatar,body);area.append(item);area.scrollTop=area.scrollHeight;
}
function formatTime(v){if(!v)return"now";const d=new Date(v.replace(" ","T")+"Z");return Number.isNaN(d.getTime())?v:d.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});}
buttons.forEach(b=>b.addEventListener("click",()=>choose({id:Number(b.dataset.roomId),name:b.dataset.roomName,description:b.dataset.roomDescription})));
form.addEventListener("submit",e=>{e.preventDefault();const content=input.value.trim();if(!content||!active)return;send({type:"message",content});input.value="";charCount.textContent="0 / 1000";input.focus();});
input.addEventListener("input",()=>charCount.textContent=`${input.value.length} / 1000`);
connect();
})();