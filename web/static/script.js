/* The map is driven by the Flask API; no railway status is invented here. */
const POLL_INTERVAL = 700;
const TRAIN_MOVE_TIME = 3800;
const trackGeometry = {
  TR1:{start:{x:130,y:180},end:{x:400,y:180}}, TR2:{start:{x:400,y:180},end:{x:650,y:180}},
  TR3:{start:{x:400,y:350},end:{x:650,y:350}}, TR4:{start:{x:130,y:350},end:{x:400,y:350}},
  TR5:{start:{x:650,y:180},end:{x:900,y:180}}, TR6:{start:{x:650,y:350},end:{x:900,y:350}},
  TR7:{start:{x:900,y:180},end:{x:1060,y:180}}, TR8:{start:{x:900,y:350},end:{x:1060,y:350}},
  TR9:{start:{x:300,y:520},end:{x:650,y:520}}, TR10:{start:{x:650,y:520},end:{x:1060,y:520}}
};
let selectedScenario = "normal", eventCount = 0, storyQueue = [], storyRunning = false, rejectionExplained = false, completionAnnounced = false, completionPending = false, scenarioCatalog = {};

async function loadStatus() {
  try {
    const response = await fetch("/api/status", {cache:"no-store"});
    if (!response.ok) throw new Error("Status unavailable");
    const data = await response.json();
    updateBrief(data.simulation_started ? data.scenario : (scenarioCatalog[selectedScenario] || data.scenario));
    updateTrains(data.trains.filter(t => data.focus.trains.includes(t.id))); updateTracks(data.tracks.filter(t => data.focus.tracks.includes(t.id)));
    updateSignals(data.signals.filter(s => data.focus.signals.includes(s.id))); updateMap(data); updateMapStatus(data); updateEvents(data.events); collectEvents(data.events);
    const button = document.getElementById("start-button");
    if (data.complete) { button.disabled = false; button.textContent = "↻ RUN AGAIN"; completionPending = true; announceCompletionWhenReady(); }
    else if (data.simulation_started) { button.disabled = true; button.textContent = "● SCENARIO RUNNING"; }
  } catch (error) { console.error(error); }
}

function updateBrief(s) {
  if (!s) return;
  document.getElementById("scenario-title").textContent = s.title;
  document.getElementById("scenario-summary").textContent = s.summary;
  document.getElementById("scenario-problem").textContent = s.problem;
  document.getElementById("scenario-risk").textContent = s.risk;
  document.getElementById("scenario-action").textContent = s.action;
  document.getElementById("scenario-result").textContent = s.result;
}
function updateTrains(trains) {
  document.getElementById("train-list").innerHTML = trains.map(t => `<div class="train-card ${stateClass(t.state)}"><strong>🚆 ${esc(t.id)}</strong><span>${esc(t.source)} → ${esc(t.destination)}</span><span>Current track: ${esc(t.track || "Station")}</span><span class="train-state">${esc(t.state.replaceAll("_", " "))}</span></div>`).join("");
}
function updateTracks(tracks) {
  document.getElementById("track-list").innerHTML = tracks.map(t => `<div class="track-card ${t.status.toLowerCase()}"><strong>${esc(t.id)}</strong><span>${esc(t.source)} → ${esc(t.destination)}</span><span class="track-status">${esc(t.status)}</span><span>${t.train ? "🚆 " + esc(t.train) : "No train"}</span></div>`).join("");
}
function updateSignals(signals) {
  document.getElementById("signal-list").innerHTML = signals.map(s => `<div class="signal-card ${s.state.toLowerCase()}"><strong>${esc(s.id)}</strong><span class="signal-state">${esc(s.state)}</span></div>`).join("");
}
function updateMap(data) {
  data.tracks.forEach(t => { const el = document.getElementById("svg-" + t.id); if (el) el.setAttribute("class", "svg-track " + t.status.toLowerCase() + (data.focus.tracks.includes(t.id) ? "" : " inactive")); });
  data.signals.forEach(s => { const el = document.getElementById("map-signal-" + s.id); if (el) el.setAttribute("class", "svg-signal " + s.state.toLowerCase()); });
  data.trains.forEach(t => { const marker = document.getElementById("train-" + t.id); if (!marker) return; marker.classList.toggle("waiting", t.state === "WAITING_FOR_TRACK"); if (t.state === "WAITING_FOR_TRACK") marker.classList.add("moving"); });
}
function updateMapStatus(data) {
  const occupied = data.tracks.filter(t => t.status === "OCCUPIED").length, reserved = data.tracks.filter(t => t.status === "RESERVED").length;
  document.getElementById("map-status").innerHTML = `<span>● ${completionAnnounced ? "SCENARIO COMPLETE" : "LIVE NETWORK"}</span><span>${data.scenario.title}</span><span>🚆 ${data.trains.filter(t => data.focus.trains.includes(t.id) && t.state !== "ARRIVED").length} active</span><span>🛤️ ${occupied} occupied · ${reserved} reserved</span>`;
}
function updateEvents(events) {
  const node = document.getElementById("event-list");
  node.innerHTML = events.slice().reverse().map(e => `<div class="event-item"><strong>${esc(e.time)}</strong><span>${esc(humanEvent(e))}<br><small>${esc(e.type)} · ${esc(e.train || "SYSTEM")}</small></span></div>`).join("") || '<div class="loading">Waiting for the selected scenario...</div>';
}
function collectEvents(events) {
  if (events.length < eventCount) { eventCount = 0; storyQueue = []; rejectionExplained = false; }
  events.slice(eventCount).forEach(e => {
    const meaningful = e.type === "ROUTE_GRANTED" || e.type === "ROUTE_REJECTED" || e.type === "TRAIN_MOVED" || e.type === "TRAIN_ARRIVED" || (e.type === "TRACK_RELEASED" && /^TR\d+$/.test(e.resource || ""));
    if (meaningful && (e.type !== "ROUTE_REJECTED" || !rejectionExplained)) storyQueue.push(e);
    if (e.type === "ROUTE_REJECTED") rejectionExplained = true;
  });
  eventCount = events.length; runStory();
}
async function runStory() {
  if (storyRunning) return; storyRunning = true;
  while (storyQueue.length) { const event = storyQueue.shift(); await present(event); await sleep(storyPause(event)); }
  storyRunning = false; announceCompletionWhenReady();
}
function storyPause(event) { return event.type === "ROUTE_REJECTED" ? 4500 : event.type === "ROUTE_GRANTED" ? 2000 : event.type === "TRACK_RELEASED" ? 1200 : 500; }
function announceCompletionWhenReady() {
  if (!completionPending || completionAnnounced || storyRunning || storyQueue.length) return;
  completionAnnounced = true;
  showDialogue("🏁", "SIMULATION COMPLETE", "All trains in this scenario arrived safely. Tracks are free and the signals have returned to RED.", "success");
}
async function present(e) {
  const presentation = storyFor(e); showDialogue(presentation.icon, presentation.title, presentation.text, presentation.kind);
  if (e.type === "TRAIN_STARTED") placeTrain(e.train);
  if (e.type === "TRAIN_MOVED") await moveTrain(e.train, e.resource);
  if (e.type === "TRAIN_ARRIVED") hideTrain(e.train);
}
function storyFor(e) {
  if (e.type === "ROUTE_GRANTED") return {icon:"✅",title:`Route ${e.resource} granted — signal cleared`,text:`${e.train} has reserved every required track. The associated signal is GREEN, so the train may now proceed.`,kind:"success"};
  if (e.type === "ROUTE_REJECTED") { const track=(e.message.match(/TR\d+/) || ["the required track"])[0]; const deadlock=selectedScenario === "deadlock"; return {icon:"⚠️",title:deadlock ? "UNSAFE STAND-OFF PREVENTED" : "COLLISION RISK DETECTED",text:deadlock ? `${e.train} also needs ${track}. The interlocking keeps ${e.train} at its station because another route already protects that exit section.` : `${e.train} also needs ${track}, but it is unavailable. The interlocking rejects the request and holds ${e.train} safely instead of allowing a collision.`,kind:"danger"}; }
  if (e.type === "TRAIN_MOVED") return {icon:"🚆",title:`${e.train} enters ${e.resource}`,text:`${e.resource} is now occupied by ${e.train}. The train is moving through the protected section.`,kind:""};
  if (e.type === "TRACK_RELEASED") return {icon:"🔓",title:selectedScenario === "waiting" && e.resource === "TR1" ? "TR1 IS FREE — T2 MAY PROCEED" : `${e.resource} released`,text:selectedScenario === "waiting" && e.resource === "TR1" ? "T1 has cleared TR1. The hold on T2 is lifted, so the interlocking can now check and grant T2's safe route." : `${e.message}. This resource can now be used safely by another route.`,kind:"success"};
  if (e.type === "TRAIN_ARRIVED") return {icon:"🏁",title:`${e.train} arrived safely`,text:`The route is clear and the interlocking has returned its resources to service.`,kind:"success"};
  return {icon:"🚦",title:`${e.train || "System"} is ready`,text:e.message || "The interlocking is monitoring the network.",kind:""};
}
function humanEvent(e) { return storyFor(e).title + ": " + storyFor(e).text; }
function showDialogue(icon, title, text, kind="") { const d = document.getElementById("map-dialogue"); d.className = "map-dialogue " + kind; d.innerHTML = `<div class="dialogue-icon">${icon}</div><div><strong>${esc(title)}</strong><p>${esc(text)}</p></div>`; }
function placeTrain(id) { const m=document.getElementById("train-"+id), g=trackGeometry[id === "T2" ? "TR1" : "TR1"]; if (!m || !g) return; m.classList.add("moving"); m.style.transition="none"; m.style.transform=`translate(${g.start.x}px,${g.start.y}px)`; }
function moveTrain(id, track) { return new Promise(resolve => { const m=document.getElementById("train-"+id), g=trackGeometry[track]; if (!m || !g) return resolve(); m.classList.add("moving"); m.classList.remove("waiting"); m.style.transition="none"; m.style.transform=`translate(${g.start.x}px,${g.start.y}px)`; m.getBoundingClientRect(); m.style.transition=`transform ${TRAIN_MOVE_TIME}ms cubic-bezier(.45,0,.55,1)`; m.style.transform=`translate(${g.end.x}px,${g.end.y}px)`; setTimeout(resolve, TRAIN_MOVE_TIME + 100); }); }
function hideTrain(id) { const m=document.getElementById("train-"+id); if (m) m.classList.remove("moving", "waiting"); }
async function selectScenario() { const b=document.getElementById("start-button"); if (b.disabled) { document.getElementById("scenario-selector").value=selectedScenario; return; } selectedScenario = document.getElementById("scenario-selector").value; updateBrief(scenarioCatalog[selectedScenario]); completionAnnounced=false; await resetSimulation(); showDialogue("🚦", "Scenario selected", scenarioCatalog[selectedScenario].summary); }
async function resetSimulation() { const response=await fetch("/api/reset", {method:"POST"}); if (!response.ok) return; eventCount=0; storyQueue=[]; rejectionExplained=false; completionAnnounced=false; completionPending=false; const b=document.getElementById("start-button"); b.disabled=false; b.textContent="▶ START SCENARIO"; loadStatus(); }
async function startSimulation() { const b=document.getElementById("start-button"); if (b.textContent.includes("RUN AGAIN")) { await resetSimulation(); return startSimulation(); } b.disabled=true; const r=await fetch("/api/start", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({scenario:selectedScenario})}); const d=await r.json(); if (!d.success) { b.disabled=false; showDialogue("⚠️","Scenario could not start",d.message,"warning"); } else { b.textContent="● SCENARIO RUNNING"; const s=scenarioCatalog[selectedScenario]; showDialogue(selectedScenario === "normal" ? "🔍" : "⚠️", selectedScenario === "normal" ? "SAFETY CHECK BEGINS" : "SAFETY RISK IDENTIFIED", `${s.risk} Action: ${s.action}`, selectedScenario === "normal" ? "warning" : "danger"); } loadStatus(); }
function stateClass(s) { return s === "WAITING_FOR_TRACK" ? "waiting" : s === "ARRIVED" ? "arrived" : s.includes("STOP") ? "danger" : ""; }
function esc(v) { return String(v ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;"); }
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
async function loadScenarios() { const response=await fetch("/api/scenarios"); scenarioCatalog=await response.json(); updateBrief(scenarioCatalog[selectedScenario]); }
loadScenarios(); loadStatus(); setInterval(loadStatus, POLL_INTERVAL);
