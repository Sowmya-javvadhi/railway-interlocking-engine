import streamlit as st

from models import (
    RailwayNetwork,
    Station,
    Track,
    Signal,
    Train,
    Route
)

from engine.event_queue import EventQueue
from engine.interlocking import InterlockingEngine
from engine.train_simulator import TrainSimulator


st.set_page_config(
    page_title="Railway Interlocking System",
    page_icon="🚂",
    layout="wide"
)


# ==================================================
# NETWORK CREATION
# ==================================================

def create_network():

    network = RailwayNetwork()

    network.add_station(
        Station("S1", "Station A")
    )

    network.add_station(
        Station("S2", "Station B")
    )

    network.add_station(
        Station("S3", "Station C")
    )

    network.add_track(
        Track(
            "TR1",
            "Station A",
            "Junction J1"
        )
    )

    network.add_track(
        Track(
            "TR2",
            "Junction J1",
            "Station B"
        )
    )

    network.add_track(
        Track(
            "TR3",
            "Junction J1",
            "Station C"
        )
    )

    network.add_signal(
        Signal("SIG1")
    )

    network.add_signal(
        Signal("SIG2")
    )

    network.add_signal(
        Signal("SIG3")
    )

    return network


# ==================================================
# SESSION STATE
# ==================================================

if "network" not in st.session_state:

    st.session_state.network = create_network()

    st.session_state.event_queue = EventQueue()

    st.session_state.interlocking = InterlockingEngine(
        st.session_state.network,
        st.session_state.event_queue
    )

    st.session_state.simulator = TrainSimulator(
        st.session_state.interlocking
    )

    st.session_state.route_1 = Route(
        "R1",
        "Station A",
        "Station B",
        ["TR1", "TR2"]
    )

    st.session_state.route_2 = Route(
        "R2",
        "Station A",
        "Station C",
        ["TR1", "TR3"]
    )

    st.session_state.train_1 = Train(
        "T1",
        "Station A",
        "Station B",
        speed=2
    )

    st.session_state.train_2 = Train(
        "T2",
        "Station A",
        "Station C",
        speed=2
    )


# ==================================================
# REFERENCES
# ==================================================

network = st.session_state.network

event_queue = st.session_state.event_queue

interlocking = st.session_state.interlocking

simulator = st.session_state.simulator

train_1 = st.session_state.train_1
train_2 = st.session_state.train_2

route_1 = st.session_state.route_1
route_2 = st.session_state.route_2


# ==================================================
# HEADER
# ==================================================

st.title(
    "🚂 Automated Railway Interlocking System"
)

st.subheader(
    "Real-Time Railway Control Dashboard"
)

st.write(
    "Monitor trains, tracks, signals and active routes."
)

st.divider()


# ==================================================
# LIVE DASHBOARD
# ==================================================

@st.fragment(run_every="1s")
def live_dashboard():

    # ==============================================
    # SYSTEM METRICS
    # ==============================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Stations",
            len(network.stations)
        )

    with col2:

        st.metric(
            "Tracks",
            len(network.tracks)
        )

    with col3:

        st.metric(
            "Signals",
            len(network.signals)
        )

    with col4:

        st.metric(
            "Active Routes",
            len(interlocking.active_routes)
        )


    st.divider()


    # ==============================================
    # TRAIN CONTROLS
    # ==============================================

    st.subheader("🚂 Train Controls")

    col1, col2 = st.columns(2)


    # ----------------------------------------------
    # TRAIN T1
    # ----------------------------------------------

    with col1:

        st.write("### Train T1")

        st.write(
            f"**Route:** "
            f"{route_1.source} → "
            f"{route_1.destination}"
        )

        st.write(
            f"**Status:** "
            f"{train_1.state.value}"
        )

        if train_1.current_track:

            st.write(
                f"**Current Track:** "
                f"{train_1.current_track}"
            )

        else:

            st.write(
                "**Current Track:** NONE"
            )


        if st.button(
            "▶ Start T1",
            disabled=(
                train_1.thread is not None
                or train_1.state.value == "ARRIVED"
            ),
            key="start_t1"
        ):

            simulator.start_train(
                train_1,
                route_1
            )


    # ----------------------------------------------
    # TRAIN T2
    # ----------------------------------------------

    with col2:

        st.write("### Train T2")

        st.write(
            f"**Route:** "
            f"{route_2.source} → "
            f"{route_2.destination}"
        )

        st.write(
            f"**Status:** "
            f"{train_2.state.value}"
        )

        if train_2.current_track:

            st.write(
                f"**Current Track:** "
                f"{train_2.current_track}"
            )

        else:

            st.write(
                "**Current Track:** NONE"
            )


        if st.button(
            "▶ Start T2",
            disabled=(
                train_2.thread is not None
                or train_2.state.value == "ARRIVED"
            ),
            key="start_t2"
        ):

            simulator.start_train(
                train_2,
                route_2
            )


    st.divider()


    # ==============================================
    # TRAIN STATUS
    # ==============================================

    st.subheader("🚆 Train Status")

    train_col1, train_col2 = st.columns(2)


    # ----------------------------------------------
    # T1 STATUS
    # ----------------------------------------------

    with train_col1:

        if train_1.state.value == "ARRIVED":

            st.success(
                f"🟢 T1 — ARRIVED at "
                f"{train_1.destination}"
            )

        elif train_1.state.value == "MOVING":

            st.info(
                f"🔵 T1 — MOVING on "
                f"{train_1.current_track}"
            )

        elif train_1.state.value == "WAITING_FOR_TRACK":

            st.warning(
                "🟡 T1 — WAITING FOR TRACK"
            )

        elif train_1.state.value == "EMERGENCY_STOP":

            st.error(
                "🔴 T1 — EMERGENCY STOP"
            )

        elif train_1.state.value == "ROUTE_REQUESTED":

            st.warning(
                "🟡 T1 — ROUTE REQUESTED"
            )

        elif train_1.state.value == "ROUTE_GRANTED":

            st.info(
                "🔵 T1 — ROUTE GRANTED"
            )

        else:

            st.write(
                f"⚪ T1 — "
                f"{train_1.state.value}"
            )


    # ----------------------------------------------
    # T2 STATUS
    # ----------------------------------------------

    with train_col2:

        if train_2.state.value == "ARRIVED":

            st.success(
                f"🟢 T2 — ARRIVED at "
                f"{train_2.destination}"
            )

        elif train_2.state.value == "MOVING":

            st.info(
                f"🔵 T2 — MOVING on "
                f"{train_2.current_track}"
            )

        elif train_2.state.value == "WAITING_FOR_TRACK":

            st.warning(
                "🟡 T2 — WAITING FOR TRACK"
            )

        elif train_2.state.value == "EMERGENCY_STOP":

            st.error(
                "🔴 T2 — EMERGENCY STOP"
            )

        elif train_2.state.value == "ROUTE_REQUESTED":

            st.warning(
                "🟡 T2 — ROUTE REQUESTED"
            )

        elif train_2.state.value == "ROUTE_GRANTED":

            st.info(
                "🔵 T2 — ROUTE GRANTED"
            )

        else:

            st.write(
                f"⚪ T2 — "
                f"{train_2.state.value}"
            )


    st.divider()


    # ==============================================
    # TRACK STATUS
    # ==============================================

    st.subheader("🛤️ Track Status")

    track_columns = st.columns(
        len(network.tracks)
    )


    for column, track in zip(
        track_columns,
        network.tracks.values()
    ):

        with column:

            st.write(
                f"### {track.track_id}"
            )

            st.caption(
                f"{track.source} → "
                f"{track.destination}"
            )


            if track.occupied_by:

                st.error(
                    f"🔴 OCCUPIED\n\n"
                    f"Train: {track.occupied_by}"
                )

            elif track.reserved_by:

                st.warning(
                    f"🟡 RESERVED\n\n"
                    f"Train: {track.reserved_by}"
                )

            else:

                st.success(
                    "🟢 FREE"
                )


    st.divider()


    # ==============================================
    # SIGNAL STATUS
    # ==============================================

    st.subheader("🚦 Signal Status")

    signal_columns = st.columns(
        len(network.signals)
    )


    for column, signal in zip(
        signal_columns,
        network.signals.values()
    ):

        with column:

            st.write(
                f"### {signal.signal_id}"
            )


            if signal.state.value == "GREEN":

                st.success(
                    "🟢 GREEN"
                )

            elif signal.state.value == "YELLOW":

                st.warning(
                    "🟡 YELLOW"
                )

            else:

                st.error(
                    "🔴 RED"
                )


    st.divider()


    # ==============================================
    # ACTIVE ROUTES
    # ==============================================

    st.subheader("🔀 Active Routes")

    if interlocking.active_routes:

        for route_id, train_id in (
            interlocking.active_routes.items()
        ):

            st.info(
                f"Route **{route_id}** → "
                f"Train **{train_id}**"
            )

    else:

        st.write(
            "No active routes."
        )


    st.divider()


    # ==============================================
    # EVENT LOG
    # ==============================================

    st.subheader("📡 Event Log")

    events = event_queue.get_history(20)


    if not events:

        st.write(
            "No events recorded yet."
        )

    else:

        for event in reversed(events):

            st.write(
                f"**{event.timestamp.strftime('%H:%M:%S')}** "
                f"| **{event.event_type.value}** "
                f"| Train: `{event.train_id or '-'}` "
                f"| Resource: `{event.resource_id or '-'}`"
            )

            if event.message:

                st.caption(
                    event.message
                )


    st.divider()


    # ==============================================
    # SYSTEM STATUS
    # ==============================================

    if (
        train_1.state.value == "EMERGENCY_STOP"
        or
        train_2.state.value == "EMERGENCY_STOP"
    ):

        st.error(
            "🚨 SYSTEM ALERT — "
            "Emergency stop active"
        )

    elif (
        train_1.state.value == "MOVING"
        or
        train_2.state.value == "MOVING"
        or
        train_1.state.value == "WAITING_FOR_TRACK"
        or
        train_2.state.value == "WAITING_FOR_TRACK"
    ):

        st.info(
            "🔵 SYSTEM ACTIVE — "
            "Train movement in progress"
        )

    else:

        st.success(
            "✅ SYSTEM OPERATIONAL"
        )


# ==================================================
# START LIVE DASHBOARD
# ==================================================

live_dashboard()