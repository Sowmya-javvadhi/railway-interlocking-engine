"""Flask presentation layer for the existing railway interlocking engine."""
import sys
import time
from pathlib import Path
from threading import Lock, Thread

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, render_template, request
from main import create_network
from models import Route, Train
from engine.event_processor import EventProcessor
from engine.event_queue import EventQueue
from engine.interlocking import InterlockingEngine
from engine.train_simulator import TrainSimulator

app = Flask(__name__)
state_lock = Lock()
ROUTES = {
    "R1": Route("R1", "Station A", "Station B", ["TR1", "TR2"]),
    "R2": Route("R2", "Station A", "Station C", ["TR1", "TR3"]),
    "R3": Route("R3", "Station D", "Station B", ["TR4", "TR2"]),
}
SCENARIOS = {
    "normal": {"title": "1. Normal Route", "summary": "One train travels from Station A to Station B after TR1 and TR2 are protected.", "problem": "A train needs every section of its route protected before it moves.", "risk": "Moving before every section is checked could send a train into an unsafe route.", "action": "The interlocking reserves TR1 and TR2, then clears SIG1.", "result": "T1 receives a safe route, SIG1 turns green, then the route is released after arrival.", "trains": ["T1"], "tracks": ["TR1", "TR2"], "signals": ["SIG1"]},
    "collision": {"title": "2. Collision Prevention", "summary": "T1 and T2 request routes that both need TR1 at nearly the same time.", "problem": "Two trains cannot safely occupy the same first track section.", "risk": "If both trains entered TR1, they could collide on the shared section.", "action": "The interlocking gives TR1 to T1 and rejects T2's conflicting request.", "result": "T1 enters TR1; T2 is rejected and held safely until that shared resource is free.", "trains": ["T1", "T2"], "tracks": ["TR1", "TR2", "TR3"], "signals": ["SIG1", "SIG2"]},
    "waiting": {"title": "3. Waiting & Track Release", "summary": "T2 remains at Station A until T1 has visibly cleared TR1, then it receives its own safe route.", "problem": "A train must wait rather than enter a section that is still occupied.", "risk": "Starting T2 before TR1 is released would create a conflict with T1.", "action": "The dispatcher holds T2 at Station A until the real track-release event occurs.", "result": "T1 releases TR1 first. Only then does T2 receive SIG2 green and begin its route.", "trains": ["T1", "T2"], "tracks": ["TR1", "TR2", "TR3"], "signals": ["SIG1", "SIG2"]},
    "deadlock": {"title": "4. Deadlock Prevention", "summary": "T3 leaves Station D first. T1 then requests the same destination section, TR2, from Station A.", "problem": "Conflicting reservations for the same exit track can create an unsafe stand-off.", "risk": "Granting both routes would allow two trains to claim the same exit section.", "action": "The interlocking grants TR2 to T3 only and keeps T1 waiting at Station A.", "result": "T3 owns TR2 first. T1 waits at Station A rather than entering an unsafe state.", "trains": ["T1", "T3"], "tracks": ["TR1", "TR2", "TR4"], "signals": ["SIG1", "SIG3"]},
}
network = event_queue = event_processor = interlocking = simulator = None
trains = []
simulation_started = False
selected_scenario = "normal"


def initialise_demo():
    """Create a fresh Flask demo around the unchanged core engine."""
    global network, event_queue, event_processor, interlocking, simulator, trains
    network = create_network()
    event_queue = EventQueue()
    event_processor = EventProcessor(event_queue)
    event_processor.start()
    interlocking = InterlockingEngine(network, event_queue)
    simulator = TrainSimulator(interlocking)
    trains = [Train("T1", "Station A", "Station B", speed=0.25), Train("T2", "Station A", "Station C", speed=0.25), Train("T3", "Station D", "Station B", speed=0.25)]


def run_scenario(scenario_id):
    """Stagger real simulator calls so engine decisions are observable."""
    t1, t2, t3 = trains
    if scenario_id == "deadlock":
        # A different approach is granted first: D -> J1 -> B via TR4/TR2.
        simulator.start_train(t3, ROUTES["R3"])
        time.sleep(1.2)
        simulator.start_train(t1, ROUTES["R1"])
    else:
        simulator.start_train(t1, ROUTES["R1"])
    if scenario_id == "collision":
        time.sleep(1.2)  # T1 is on TR1 before T2 requests the shared resource.
        simulator.start_train(t2, ROUTES["R2"])
    elif scenario_id == "waiting":
        # This lesson demonstrates the release boundary, not a second collision.
        time.sleep(4.3)
        simulator.start_train(t2, ROUTES["R2"])


def event_payload(event):
    return {"type": event.event_type.value, "train": event.train_id, "resource": event.resource_id, "message": event.message, "time": event.timestamp.strftime("%H:%M:%S")}


def status_payload():
    with state_lock:
        tracks = []
        for track in network.tracks.values():
            tracks.append({"id": track.track_id, "source": track.source, "destination": track.destination,
                           "status": "OCCUPIED" if track.occupied_by else "RESERVED" if track.reserved_by else "FREE",
                           "train": track.occupied_by or track.reserved_by})
        selected = SCENARIOS[selected_scenario]
        return {"stations": len(network.stations), "tracks": tracks,
                "signals": [{"id": s.signal_id, "state": s.state.value} for s in network.signals.values()],
                "trains": [{"id": t.train_id, "source": t.source, "destination": t.destination, "state": t.state.value, "track": t.current_track} for t in trains],
                "routes": [{"route": r, "train": t} for r, t in interlocking.active_routes.items()],
                "events": [event_payload(event) for event in event_queue.get_history(80)],
                "simulation_started": simulation_started, "scenario": {"id": selected_scenario, **selected},
                "focus": {"trains": selected["trains"], "tracks": selected["tracks"], "signals": selected["signals"]},
                "complete": simulation_started and all(t.state.value == "ARRIVED" for t in trains if t.train_id in selected["trains"])}


initialise_demo()


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/scenarios")
def scenarios():
    return jsonify(SCENARIOS)


@app.route("/api/start", methods=["POST"])
def start_simulation():
    global simulation_started, selected_scenario
    scenario_id = (request.get_json(silent=True) or {}).get("scenario", selected_scenario)
    if scenario_id not in SCENARIOS:
        return jsonify(success=False, message="Unknown scenario"), 400
    with state_lock:
        if simulation_started:
            return jsonify(success=False, message="A scenario is already running")
        selected_scenario, simulation_started = scenario_id, True
        Thread(target=run_scenario, args=(scenario_id,), daemon=True, name="FlaskScenario").start()
    return jsonify(success=True, message=f"{SCENARIOS[scenario_id]['title']} started")


@app.route("/api/reset", methods=["POST"])
def reset_simulation():
    global simulation_started
    with state_lock:
        scenario_trains = SCENARIOS[selected_scenario]["trains"]
        if simulation_started and any(t.state.value != "ARRIVED" for t in trains if t.train_id in scenario_trains):
            return jsonify(success=False, message="Wait for the current scenario to finish before resetting"), 409
        # Existing train threads retain their old engine; this swaps in a fresh
        # Flask demo lifecycle without changing shared simulation code.
        initialise_demo()
        simulation_started = False
    return jsonify(success=True, message="Flask demonstration reset")


@app.route("/api/status")
def system_status():
    return jsonify(status_payload())


@app.route("/api/health")
def health():
    return jsonify(status="ONLINE", system="Railway Interlocking Flask Dashboard")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
