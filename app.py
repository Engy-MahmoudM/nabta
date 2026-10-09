import json
import os
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from plant_brain import answer_plant_question

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROFILES_PATH = DATA_DIR / "plants.json"
CHAT_HISTORY_PATH = DATA_DIR / "chat_history.json"
load_dotenv(BASE_DIR / ".env")

st.set_page_config(
    page_title="Nabta — Grow Egypt Greener",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root{--forest:#163f35;--forest2:#214f40;--leaf:#397653;--sage:#dce8d0;--lime:#d2e7a9;--cream:#f7f7f0;--ink:#20332b;--muted:#65766b;--line:#e1e8dc;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:linear-gradient(180deg,#f8f8f2 0%,#f1f5ec 100%)}
.block-container{max-width:1250px;padding-top:1.7rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#163f35 0%,#102f28 100%);border-right:1px solid #315b4c}
[data-testid="stSidebar"] *{color:#f4f7ee}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#d2e0d3}
[data-testid="stSidebar"] [data-testid="stRadio"] label{border-radius:12px;padding:.35rem .55rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#ffffff12}
.brand-mark{display:flex;align-items:center;gap:.7rem;padding:.2rem 0 .4rem}
.brand-icon{width:42px;height:42px;border-radius:14px;background:#d2e7a9;color:#163f35;display:flex;align-items:center;justify-content:center;font-size:1.5rem}
.brand-name{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:#fff;line-height:1.05}
.brand-tag{font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:#c8d9c5;margin-top:.25rem}
.hero{background:radial-gradient(circle at 90% 15%,#7da46b55 0,transparent 28%),linear-gradient(120deg,#143b31 0%,#245c43 58%,#527d4c 100%);color:#fff;padding:2.7rem 2.8rem;border-radius:28px;margin:0 0 1.45rem;position:relative;overflow:hidden;box-shadow:0 18px 50px #163f3518}
.hero:after{content:'✳';position:absolute;right:5%;bottom:-80px;font-size:18rem;line-height:1;color:#ffffff09;pointer-events:none}
.hero .eyebrow{letter-spacing:.17em;text-transform:uppercase;font-size:.73rem;font-weight:700;color:#d8e9b7;margin-bottom:.8rem}
.hero h1{color:#fff!important;font-family:'Playfair Display',serif;font-size:clamp(2.4rem,4vw,3.7rem);line-height:1.06;margin:0;max-width:750px}
.hero p{color:#e8f0e4!important;font-size:1.04rem;line-height:1.75;max-width:720px;margin:.95rem 0 0}
.hero-pill{display:inline-block;border:1px solid #d5e7c177;background:#ffffff0b;color:#edf5e6;border-radius:999px;padding:.48rem .85rem;font-size:.79rem;margin-top:1.25rem}
.feature-card{height:100%;background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.2rem 1.2rem 1.25rem;box-shadow:0 7px 24px #173e2d08}
.feature-top{font-size:.72rem;letter-spacing:.14em;font-weight:700;color:#557b51;text-transform:uppercase}
.feature-title{font-family:'Playfair Display',serif;color:#183f33!important;font-size:1.35rem;font-weight:600;margin:.45rem 0 .35rem}
.feature-copy{color:#586b60!important;font-size:.91rem;line-height:1.6}
.section-title{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:600;color:#173f34;margin:.6rem 0 .25rem}
.section-sub{color:#65766b;font-size:.96rem;line-height:1.65;margin-bottom:1.1rem}
.eyebrow-dark{font-size:.72rem;text-transform:uppercase;letter-spacing:.15em;font-weight:700;color:#668b59}
.tip-card{background:#eaf2e2;border:1px solid #d7e6ca;border-left:4px solid #77a15d;border-radius:14px;padding:1rem 1.15rem;color:#304e3b;line-height:1.65}
.info-card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.2rem 1.3rem;color:#253c30;line-height:1.7}
.info-card h3{font-family:'Playfair Display',serif;color:#173f34;margin-top:0}
div[data-testid="stChatMessage"]{background:#173f35!important;border:1px solid #2d5c4b!important;border-radius:18px!important;padding:1rem 1.05rem!important;margin:.65rem 0!important;box-shadow:0 5px 18px #123b2c12}
div[data-testid="stChatMessage"] *{color:#f5f7ef!important}
div[data-testid="stChatMessage"] a{color:#d5e9a9!important;text-decoration:underline}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p{line-height:1.75}
div[data-testid="stChatMessage"] code{background:#ffffff16!important;color:#eff6e9!important}
[data-testid="stChatInput"]{border:1px solid #cddbc9!important;border-radius:18px!important;background:#fff!important;box-shadow:0 8px 24px #173e2d0d!important}
[data-testid="stChatInput"] textarea{color:#20332b!important}
[data-testid="stChatInput"] textarea::placeholder{color:#78867c!important}
[data-testid="stFileUploader"]{background:#fff;border:1px dashed #a9c29f;border-radius:14px;padding:.6rem}
.stButton button,.stDownloadButton button{border-radius:12px;font-weight:700;min-height:2.6rem}
.stButton button[kind="primary"]{background:#24664c;border-color:#24664c;color:#fff}
.stButton button[kind="primary"]:hover{background:#174b37;border-color:#174b37}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1rem}
[data-testid="stMetricLabel"]{color:#66796c!important}
[data-testid="stMetricValue"]{color:#214f3e!important}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:14px}
hr{border-color:#dfe7da}
.small-note{font-size:.82rem;color:#748177}
@media(max-width:700px){.hero{padding:1.7rem 1.35rem;border-radius:20px}.hero h1{font-size:2.35rem}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)


def load_profiles():
    try:
        if PROFILES_PATH.exists():
            data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        pass
    return []


def save_profiles(profiles):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = PROFILES_PATH.with_suffix(".tmp")
    temp_path.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(PROFILES_PATH)


def load_chat_history():
    """Load persistent chat history across sessions."""
    try:
        if CHAT_HISTORY_PATH.exists():
            data = json.loads(CHAT_HISTORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [m for m in data if isinstance(m, dict) and "role" in m and "content" in m]
    except Exception:
        pass
    return []


def save_chat_history(messages):
    """Save persistent chat history to disk."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        clean = [{"role": m["role"], "content": m["content"]} for m in messages if isinstance(m, dict)]
        temp_path = CHAT_HISTORY_PATH.with_suffix(".tmp")
        temp_path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(CHAT_HISTORY_PATH)
    except Exception:
        pass


def reset_chat():
    st.session_state.messages = []
    st.session_state.last_image_bytes = None
    save_chat_history([])


if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
if "last_image_bytes" not in st.session_state:
    st.session_state.last_image_bytes = None

with st.sidebar:
    st.markdown('<div class="brand-mark"><div class="brand-icon">🌿</div><div><div class="brand-name">Nabta</div><div class="brand-tag">Grow Egypt greener</div></div></div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("EXPLORE NABTA", ["Plant Companion", "My Plants", "Care Planner", "About Nabta"], label_visibility="visible")
    st.markdown("---")
    st.markdown("### 🌞 Made for growing in Egypt")
    st.caption("Thoughtful advice for sunny balconies, warm rooftops, small gardens, and water-conscious growing.")
    st.markdown("---")
    st.markdown("**Our promise**")
    st.caption("Practical steps, beginner-friendly explanations, and honest uncertainty when a photo or symptom is not enough to know for sure.")
    st.markdown("<div style='padding-top:1rem;color:#b9d0bc;font-size:.75rem'>A little greener, every day. 🇪🇬</div>", unsafe_allow_html=True)

if page == "Plant Companion":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">A little greener, every day</div>
      <h1>Meet your plant’s<br>new best friend.</h1>
      <p>Identify plants, understand their needs, and bring more green to Egyptian homes, balconies, rooftops, and gardens. No green thumb required — just curiosity.</p>
      <span class="hero-pill">🌱 Plant care · Photo questions · Water-wise growing for Egypt</span>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown('<div class="feature-card"><div class="feature-top">01 · Identify</div><div class="feature-title">Know your plant</div><div class="feature-copy">Share a photo and explore likely plant matches, with clear notes when identification is uncertain.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card"><div class="feature-top">02 · Understand</div><div class="feature-title">Find the why</div><div class="feature-copy">Make sense of yellow leaves, watering issues, sunlight, pests, and other growing questions.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="feature-card"><div class="feature-top">03 · Grow</div><div class="feature-title">Build your routine</div><div class="feature-copy">Get manageable next steps for your space, experience level, and water availability.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your growing journey starts here</div><div class="section-sub">Ask in your own words. You can attach a plant photo to the same message, and Nabta will use your conversation to tailor its advice.</div>', unsafe_allow_html=True)
    
    # Quick suggestion chips
    st.markdown("**Quick questions to try:**")
    sc1, sc2, sc3 = st.columns(3)
    chip_question = None
    if sc1.button("🌱 Balcony herbs in Cairo", use_container_width=True):
        chip_question = "I'm a beginner in Cairo. What herbs can I grow on a sunny balcony without wasting water?"
    if sc2.button("🍂 Yellow basil leaves", use_container_width=True):
        chip_question = "My basil leaves are turning yellow. How do I fix it?"
    if sc3.button("💧 Rooftop watering tips", use_container_width=True):
        chip_question = "How often should I water my rooftop plants during Egyptian summer heat?"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🌿" if msg["role"] == "assistant" else None):
            if msg.get("image_preview"):
                st.image(msg["image_preview"], caption="Photo shared in this message", width=220)
            st.markdown(msg["content"])
            
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🌿"):
            st.markdown("**Ahlan! I’m Nabta.** 🌱\n\nAre you growing your very first plant, or looking after a whole garden? Ask me anything — from identifying a plant to helping it recover. If you have a photo, attach it with your question.\n\n*For example: “I’m a beginner in Alexandria. What herbs can I grow on a sunny balcony without wasting water?”*")

    try:
        prompt = st.chat_input(
            "Ask Nabta anything about your plant…",
            accept_file="multiple",
            file_type=["png", "jpg", "jpeg", "webp"],
            key="nabta_chat_input",
        )
    except TypeError:
        # Compatibility fallback for older Streamlit installations.
        prompt = st.chat_input("Ask Nabta anything about your plant…")

    if chip_question:
        prompt = chip_question

    if prompt:
        if isinstance(prompt, str):
            question = prompt.strip()
            uploads = []
        else:
            question = (getattr(prompt, "text", "") or "").strip()
            uploads = getattr(prompt, "files", []) or []
        image_bytes = None
        image_mime = None
        image_preview = None
        if uploads:
            uploaded = uploads[0]
            image_bytes = uploaded.getvalue()
            image_mime = getattr(uploaded, "type", None) or "image/jpeg"
            image_preview = image_bytes
            if len(uploads) > 1:
                st.caption("Nabta uses the first attached image per message for now. You can send another photo in a follow-up message.")
        if not question and not image_bytes:
            st.warning("Write a question or attach a plant photo to get started.")
        else:
            display_question = question or "Please identify this plant and tell me how to care for it."
            user_msg = {"role": "user", "content": display_question}
            if image_preview:
                user_msg["image_preview"] = image_preview
            st.session_state.messages.append(user_msg)
            with st.chat_message("user"):
                if image_preview:
                    st.image(image_preview, caption="Photo attached", width=220)
                st.markdown(display_question)
            with st.chat_message("assistant", avatar="🌿"):
                with st.spinner("Nabta is thinking through your plant’s needs…"):
                    answer = answer_plant_question(
                        display_question,
                        context={"location": "Egypt; exact city and conditions not yet confirmed", "experience": "Infer from conversation; ask if needed"},
                        history=st.session_state.messages[:-1],
                        image_bytes=image_bytes,
                        image_mime=image_mime,
                    )
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            save_chat_history(st.session_state.messages)
            st.rerun()

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("＋ New conversation", use_container_width=True):
            reset_chat()
            st.rerun()
    with col_b:
        st.markdown('<div class="small-note" style="padding:.65rem 0">Tip: mention your city, sunlight, pot size, and watering routine when you know them. Nabta will ask follow-up questions when details are missing. Chat memory is saved automatically.</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="tip-card">💧 <b>Nabta’s water-wise reminder:</b> Check the soil before watering. Heat and wind can dry pots quickly, but a fixed daily schedule can still cause overwatering. Let the plant, its pot, and its soil guide you.</div>', unsafe_allow_html=True)

elif page == "My Plants":
    st.markdown('<div class="eyebrow-dark">Your garden, in one place</div><div class="section-title">Your little green family</div><div class="section-sub">Save what you are growing, notice changes, and keep useful notes as your plants thrive.</div>', unsafe_allow_html=True)
    total_updates = sum(len(p.get("updates", [])) for p in st.session_state.profiles)
    a, b = st.columns(2)
    a.metric("Plants in your garden", len(st.session_state.profiles))
    b.metric("Progress notes", total_updates)
    with st.form("add_plant", clear_on_submit=True):
        st.markdown("#### Add a plant")
        c1, c2 = st.columns(2)
        name = c1.text_input("Plant nickname *", placeholder="e.g., Balcony basil")
        species = c2.text_input("Plant type (if known)", placeholder="e.g., Basil / not sure yet")
        c3, c4 = st.columns(2)
        location = c3.selectbox("Growing spot", ["Balcony", "Rooftop", "Indoor room", "Garden", "Farm / allotment", "Other"])
        light = c4.selectbox("Light", ["Not sure", "Bright indirect light", "A few hours of direct sun", "6+ hours of direct sun", "Mostly shade"])
        watering = st.selectbox("Watering approach", ["Check soil before watering", "Daily", "Every few days", "Weekly", "Not sure"])
        notes = st.text_area("Notes or symptoms", placeholder="Yellow lower leaves, recently repotted, new growth…")
        submitted = st.form_submit_button("＋ Save to my garden", type="primary")
        if submitted:
            if not name.strip():
                st.warning("Give your plant a nickname first.")
            else:
                st.session_state.profiles.append({"id": str(uuid.uuid4()), "name": name.strip(), "species": species.strip(), "location": location, "light": light, "watering": watering, "notes": notes.strip(), "created": str(date.today()), "updates": []})
                save_profiles(st.session_state.profiles)
                st.success(f"{name.strip()} was added to your garden.")
                st.rerun()
    st.markdown("---")
    if st.session_state.profiles:
        for idx, plant in enumerate(list(st.session_state.profiles)):
            with st.expander(f"🌱 {plant['name']}  ·  {plant.get('species') or 'Plant type not known yet'}"):
                st.write(f"**Growing spot:** {plant.get('location', 'Not specified')}  ·  **Light:** {plant.get('light', 'Not sure')}  ·  **Watering:** {plant.get('watering', 'Not sure')}")
                if plant.get("notes"):
                    st.write(f"**Notes:** {plant['notes']}")
                update = st.text_area("Progress note", key=f"update_{plant['id']}", placeholder="What changed since your last check?")
                ca, cb = st.columns(2)
                if ca.button("Save progress note", key=f"save_{plant['id']}"):
                    plant.setdefault("updates", []).append({"date": str(date.today()), "note": update.strip()})
                    save_profiles(st.session_state.profiles)
                    st.success("Progress saved.")
                    st.rerun()
                if cb.button("Remove plant", key=f"delete_{plant['id']}"):
                    st.session_state.profiles = [p for p in st.session_state.profiles if p.get("id") != plant.get("id")]
                    save_profiles(st.session_state.profiles)
                    st.rerun()
                for upd in reversed(plant.get("updates", [])):
                    st.caption(f"{upd.get('date', '')} — {upd.get('note', '')}")
    else:
        st.markdown('<div class="info-card"><h3>Your garden is waiting 🌱</h3>Start with one plant. Add its name, growing spot, and any observations, then save updates as you learn what helps it thrive.</div>', unsafe_allow_html=True)

elif page == "Care Planner":
    st.markdown('<div class="eyebrow-dark">Small steps, healthier plants</div><div class="section-title">A plan you can actually follow</div><div class="section-sub">Tell Nabta what you want to grow and the conditions you have. It will create a beginner-friendly starting plan you can refine in chat.</div>', unsafe_allow_html=True)
    with st.form("care_plan_form"):
        plant_type = st.text_input("What are you growing?", placeholder="e.g., basil, tomato, jasmine — or ‘not sure yet’")
        c1, c2 = st.columns(2)
        climate = c1.selectbox("Growing environment", ["Hot sunny balcony", "Shaded balcony", "Indoor near a window", "Open garden", "Windy rooftop", "Other / not sure"])
        goal = c2.selectbox("Main goal", ["Start from seed", "Keep an existing plant healthy", "Help a struggling plant", "Grow edible plants", "Use less water", "Create a small garden"])
        water = st.selectbox("Water access", ["Limited water", "Normal household water access", "Drip irrigation / regular supply", "Not sure"])
        experience = st.selectbox("Your experience", ["Complete beginner", "Some experience", "Experienced gardener"])
        make_plan = st.form_submit_button("Create my growing plan", type="primary")
    if make_plan:
        q = f"Create a practical care plan for {plant_type or 'a plant not yet identified'} in Egypt. Environment: {climate}. Goal: {goal}. Water access: {water}. Experience: {experience}. Give first steps, light, watering method, soil/drainage, heat precautions, and what to monitor. Clearly label general guidance and ask at most two follow-up questions if needed. Do not invent species-specific facts."
        with st.spinner("Putting your plan together…"):
            plan = answer_plant_question(q, {"location": climate, "experience": experience, "water_access": water}, [], None)
        st.markdown("### Your starter plan")
        st.markdown(plan)
        if st.button("Continue in Plant Companion", type="primary"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.messages.append({"role": "assistant", "content": plan})
            save_chat_history(st.session_state.messages)
            st.rerun()
    st.markdown('<div class="tip-card">🌤️ <b>Remember:</b> Egypt’s heat, wind, and seasonal sunlight can change how quickly containers dry out. A good plan responds to the plant and its conditions instead of relying on one watering schedule for everything.</div>', unsafe_allow_html=True)

elif page == "About Nabta":
    st.markdown('<div class="eyebrow-dark">Our roots, our future</div><div class="section-title">A greener Egypt starts at home.</div><div class="section-sub">Nabta makes plant care feel less intimidating, one question and one growing space at a time.</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><h3>Why the name Nabta?</h3>“Nabta” (نبتة) means a plant. We believe greener neighbourhoods do not have to begin with large gardens. A pot on a balcony, herbs on a windowsill, shade on a rooftop, or a cared-for community space can all be a beginning.</div>', unsafe_allow_html=True)
    st.markdown(" ")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="info-card"><h3>🌞 Designed with Egypt in mind</h3>Heat, intense sunlight, rooftop wind, and limited water can make growing feel difficult. Nabta encourages users to consider the actual growing spot, choose suitable plants, check soil moisture, and avoid wasting water.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-card"><h3>🌱 Made for beginners</h3>You do not need to know botanical terms. Ask naturally, share a photo, describe what you notice, and learn step by step. Nabta should explain why it recommends an action, not just give a list of instructions.</div>', unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown('<div class="section-title" style="font-size:1.55rem">How Nabta works</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown('<div class="feature-card"><div class="feature-top">Step 01</div><div class="feature-title">You ask</div><div class="feature-copy">Share a question, a photo, or observations about your plant and its environment.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card"><div class="feature-top">Step 02</div><div class="feature-title">Nabta looks for clues</div><div class="feature-copy">The assistant uses vector-based RAG, conversation history, and resilient LLMs to form a helpful answer.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="feature-card"><div class="feature-top">Step 03</div><div class="feature-title">You grow with confidence</div><div class="feature-copy">Get practical next steps, learn what to monitor, and keep progress notes in My Plants.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="font-size:1.55rem">Our principles</div>', unsafe_allow_html=True)
    st.markdown("- **Helpful, not intimidating:** plain language and manageable actions for first-time growers.\n- **Water-conscious:** check soil and growing conditions instead of prescribing rigid schedules.\n- **Honest about uncertainty:** a photo or symptom may not be enough to confirm a species, disease, or nutrient problem.\n- **Rooted in community:** encourage greener balconies, rooftops, gardens, and shared spaces across Egypt.")
    st.markdown('<div class="tip-card">🌿 <b>A note on plant health:</b> Nabta is an educational assistant, not a substitute for a qualified local agricultural specialist. For severe crop damage, suspected disease outbreaks, or pesticide decisions, verify advice with a trusted local expert.</div>', unsafe_allow_html=True)
