```python
import streamlit as st
import datetime
from typing import Dict, List
import random

# --------------------------------------------------
# KONFIGURERA SIDAN
# --------------------------------------------------

st.set_page_config(
    page_title="Daily Tasks",
    page_icon="✅",
    layout="wide"
)

# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #0a1428 0%,
        #1e3a5f 25%,
        #2c5282 50%,
        #1e3a5f 75%,
        #0a1428 100%
    );
    background-attachment: fixed;
}

.stButton > button {
    background: linear-gradient(145deg, #4CAF50, #45a049);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

.stFormSubmitButton > button {
    background: linear-gradient(145deg, #2196F3, #1976D2);
    color: white;
    border-radius: 8px;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTimeInput > div > div > input {
    background: rgba(255, 255, 255, 0.9) !important;
    color: black !important;
    border-radius: 8px;
}

h1, h2, h3 {
    color: white;
}

.task-item {
    background: rgba(0, 0, 0, 0.6);
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
}

.task-completed {
    background: rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.5);
}

.stMarkdown {
    color: rgba(255, 255, 255, 0.9);
}

.stChatInput > div > div > textarea {
    background: rgba(255, 255, 255, 0.9) !important;
    color: black !important;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "total_points" not in st.session_state:
    st.session_state.total_points = 0

if "completed_today" not in st.session_state:
    st.session_state.completed_today = 0

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Hej! Jag är din produktivitetsassistent. Jag kan hjälpa dig med uppgifter, poäng och motivation."
        }
    ]

# --------------------------------------------------
# TASK FUNCTIONS
# --------------------------------------------------

def add_task(name: str, points: int, difficulty: str):
    task = {
        "id": len(st.session_state.tasks),
        "name": name,
        "points": points,
        "difficulty": difficulty,
        "completed": False,
        "created_date": datetime.date.today().isoformat(),
        "completed_date": None
    }

    st.session_state.tasks.append(task)
    st.toast(f"Uppgift '{name}' tillagd!", icon="✅")


def complete_task(task_id: int):
    for task in st.session_state.tasks:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True
            task["completed_date"] = datetime.date.today().isoformat()

            st.session_state.total_points += task["points"]
            st.session_state.completed_today += 1

            st.toast(
                f"Du fick {task['points']} poäng!",
                icon="🏆"
            )

            st.balloons()
            break


def delete_task(task_id: int):
    st.session_state.tasks = [
        task for task in st.session_state.tasks
        if task["id"] != task_id
    ]

    st.toast("Uppgift borttagen", icon="🗑️")


# --------------------------------------------------
# SLEEP CALCULATOR
# --------------------------------------------------

def calculate_sleep_recommendation(bedtime, wake_time):

    bedtime_dt = datetime.datetime.combine(
        datetime.date.today(),
        bedtime
    )

    wake_time_dt = datetime.datetime.combine(
        datetime.date.today(),
        wake_time
    )

    if wake_time_dt <= bedtime_dt:
        wake_time_dt += datetime.timedelta(days=1)

    sleep_duration = wake_time_dt - bedtime_dt
    sleep_hours = sleep_duration.total_seconds() / 3600

    optimal_bedtime = (
        wake_time_dt - datetime.timedelta(hours=8)
    ).time()

    optimal_wake = (
        bedtime_dt + datetime.timedelta(hours=8)
    ).time()

    if sleep_hours < 6:
        recommendation = (
            "Du får väldigt lite sömn. Försök att lägga dig tidigare."
        )

    elif sleep_hours < 7:
        recommendation = (
            "Du får ganska lite sömn. Försök få mer sömn."
        )

    elif sleep_hours <= 9:
        recommendation = (
            "Din sömntid ligger inom ett bra intervall."
        )

    else:
        recommendation = (
            "Du sover länge. Om du fortfarande är trött kan du försöka "
            "hitta en jämnare sömnrutin."
        )

    return {
        "duration": sleep_hours,
        "recommendation": recommendation,
        "optimal_bedtime": optimal_bedtime,
        "optimal_wake": optimal_wake
    }


# --------------------------------------------------
# CHATBOT
# --------------------------------------------------

def get_bot_response(user_message):

    message = user_message.lower()

    # Uppgifter
    if any(word in message for word in [
        "uppgift",
        "tasks",
        "task",
        "göra",
        "lista"
    ]):

        active_tasks = len([
            task
            for task in st.session_state.tasks
            if not task["completed"]
        ])

        if active_tasks > 0:
            return (
                f"Du har {active_tasks} aktiva uppgifter. "
                "Börja gärna med en liten uppgift först."
            )

        return "Du har inga aktiva uppgifter just nu."

    # Poäng
    if any(word in message for word in [
        "poäng",
        "points",
        "score",
        "statistik"
    ]):

        return (
            f"Du har {st.session_state.total_points} poäng totalt "
            f"och {st.session_state.completed_today} uppgifter klara idag."
        )

    # Sömn
    if any(word in message for word in [
        "sömn",
        "sova",
        "trött",
        "vakna"
    ]):

        return (
            "Du kan använda sömnfliken för att räkna ut hur länge "
            "du sover mellan två tider."
        )

    # Motivation
    if any(word in message for word in [
        "motivation",
        "motivera",
        "hjälp",
        "tips",
        "råd"
    ]):

        responses = [
            "Ta en uppgift i taget.",
            "Börja med den enklaste uppgiften.",
            "Det viktigaste är att komma igång.",
            "Gör 10 minuter först. Sedan kan du fortsätta."
        ]

        return random.choice(responses)

    # Hälsning
    if any(word in message for word in [
        "hej",
        "hallå",
        "tjena",
        "hello",
        "hi"
    ]):

        return (
            "Hej! Jag kan hjälpa dig hålla koll på dina tasks, "
            "poäng och sömn."
        )

    # Tack
    if any(word in message for word in [
        "tack",
        "thanks"
    ]):

        return "Varsågod!"

    # Default
    responses = [
        "Jag förstår. Berätta mer.",
        "Okej. Vad vill du göra härnäst?",
        "Jag kan hjälpa dig med tasks, poäng eller sömn.",
        "Det låter bra."
    ]

    return random.choice(responses)


# --------------------------------------------------
# TITEL
# --------------------------------------------------

st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="
        font-size: 4rem;
        background: linear-gradient(
            45deg,
            #2196F3,
            #4CAF50,
            #FF9800,
            #E91E63
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    ">
        📋 DAILY TASKS
    </h1>

    <p style="
        color: rgba(255,255,255,0.8);
        font-size: 1.2rem;
    ">
        Organisera dina uppgifter och tjäna poäng!
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# MENY
# --------------------------------------------------

menu = st.selectbox(
    "Välj kategori:",
    [
        "📝 Uppgifter",
        "😴 Sömn",
        "🤖 Chatbot"
    ]
)


# ==================================================
# UPPGIFTER
# ==================================================

if menu == "📝 Uppgifter":

    # Statistik
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏆 Totala poäng",
            st.session_state.total_points,
            f"+{st.session_state.completed_today} idag"
        )

    with col2:
        active_tasks = len([
            task
            for task in st.session_state.tasks
            if not task["completed"]
        ])

        st.metric(
            "📋 Aktiva uppgifter",
            active_tasks
        )

    with col3:
        completed_tasks = len([
            task
            for task in st.session_state.tasks
            if task["completed"]
        ])

        st.metric(
            "✅ Klara uppgifter",
            completed_tasks
        )

    st.divider()

    # Lägg till task
    st.subheader("➕ Lägg till ny uppgift")

    with st.form("add_task_form"):

        col1, col2 = st.columns([2, 1])

        with col1:
            task_name = st.text_input(
                "📝 Uppgiftens namn",
                placeholder="T.ex. Gör matteläxan"
            )

        with col2:
            difficulty = st.selectbox(
                "Svårighetsgrad",
                [
                    "Lätt",
                    "Medel",
                    "Svår"
                ]
            )

        points = {
            "Lätt": 10,
            "Medel": 25,
            "Svår": 50
        }[difficulty]

        submitted = st.form_submit_button(
            "➕ Lägg till uppgift"
        )

        if submitted:

            if task_name.strip():

                add_task(
                    task_name.strip(),
                    points,
                    difficulty
                )

                st.rerun()

            else:
                st.warning("Skriv ett namn på uppgiften först.")

    st.divider()

    # Task-lista
    st.subheader("📋 Dina uppgifter")

    if not st.session_state.tasks:

        st.info("Du har inga uppgifter ännu. Lägg till en ovan.")

    else:

        for task in st.session_state.tasks:

            if task["completed"]:

                st.markdown(
                    f"""
                    <div class="task-item task-completed">
                        <b>✅ {task["name"]}</b><br>
                        Svårighet: {task["difficulty"]} |
                        +{task["points"]} poäng<br>
                        <small>Klar!</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "🗑️ Ta bort",
                    key=f"delete_completed_{task['id']}"
                ):
                    delete_task(task["id"])
                    st.rerun()

            else:

                st.markdown(
                    f"""
                    <div class="task-item">
                        <b>⬜ {task["name"]}</b><br>
                        Svårighet: {task["difficulty"]} |
                        +{task["points"]} poäng
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button(
                        "✅ Klar",
                        key=f"complete_{task['id']}"
                    ):
                        complete_task(task["id"])
                        st.rerun()

                with col2:
                    if st.button(
                        "🗑️ Ta bort",
                        key=f"delete_{task['id']}"
                    ):
                        delete_task(task["id"])
                        st.rerun()


# ==================================================
# SÖMN
# ==================================================

elif menu == "😴 Sömn":

    st.subheader("😴 Sömnkalkylator")

    st.write(
        "Ange när du går och lägger dig och när du vaknar."
    )

    col1, col2 = st.columns(2)

    with col1:
        bedtime = st.time_input(
            "🌙 När går du och lägger dig?",
            datetime.time(23, 0)
        )

    with col2:
        wake_time = st.time_input(
            "☀️ När vaknar du?",
            datetime.time(7, 0)
        )

    if st.button("🧮 Beräkna sömn"):

        result = calculate_sleep_recommendation(
            bedtime,
            wake_time
        )

        st.divider()

        st.metric(
            "😴 Sömn",
            f"{result['duration']:.1f} timmar"
        )

        st.info(result["recommendation"])

        st.write(
            f"**Förslag:** Lägg dig runt "
            f"{result['optimal_bedtime'].strftime('%H:%M')} "
            f"och vakna runt "
            f"{result['optimal_wake'].strftime('%H:%M')}."
        )


# ==================================================
# CHATBOT
# ==================================================

elif menu == "🤖 Chatbot":

    st.subheader("🤖 Din chatbot")

    st.write(
        "Fråga mig om dina uppgifter, poäng, sömn eller motivation."
    )

    # Visa gamla meddelanden
    for message in st.session_state.chat_messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat-input
    user_message = st.chat_input(
        "Skriv ett meddelande..."
    )

    if user_message:

        # Lägg till användarens meddelande
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        # Botens svar
        bot_response = get_bot_response(
            user_message
        )

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": bot_response
            }
        )

        st.rerun()
```
