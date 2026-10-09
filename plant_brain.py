"""LangChain, FAISS Vector RAG, and Multi-Provider LLM Engine for Nabta.

Built following Generative AI Internship coursework (Lec 2: HuggingFace/LLMs, Lec 3: RAG, Lec 4: LangChain, Lec 5: Model Quantization/Failover).
"""
import base64
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "data" / "plant_knowledge.json"

_VECTORSTORE = None


def load_knowledge():
    try:
        if KNOWLEDGE_PATH.exists():
            data = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def get_vectorstore():
    """Build or return cached FAISS vector database (Lec 3 RAG)."""
    global _VECTORSTORE
    if _VECTORSTORE is not None:
        return _VECTORSTORE

    docs_data = load_knowledge()
    if not docs_data:
        return None

    try:
        from langchain_core.documents import Document
        from langchain_community.vectorstores import FAISS

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        except Exception:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            except Exception:
                from langchain_community.embeddings import FakeEmbeddings
                embeddings = FakeEmbeddings(size=384)

        documents = [
            Document(
                page_content=f"{doc.get('title', '')}: {doc.get('text', '')}",
                metadata={
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "tags": doc.get("tags", []),
                },
            )
            for doc in docs_data
        ]
        _VECTORSTORE = FAISS.from_documents(documents, embeddings)
        return _VECTORSTORE
    except Exception:
        return None


def retrieve_context(question, top_k=3):
    """Semantic Vector Retrieval (Lec 3) with transparent keyword fallback."""
    vs = get_vectorstore()
    if vs is not None:
        try:
            results = vs.similarity_search(question, k=top_k)
            return [
                {
                    "title": doc.metadata.get("title", "Plant Note"),
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", "General guidance"),
                }
                for doc in results
            ]
        except Exception:
            pass

    docs = load_knowledge()
    terms = {t.lower().strip(".,?!:;()[]{}\"'") for t in question.split() if len(t) > 2}
    ranked = []
    for doc in docs:
        haystack = (
            str(doc.get("title", "")) + " " + str(doc.get("text", "")) + " "
            + " ".join(doc.get("tags", []))
        ).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            ranked.append((score, doc))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in ranked[:top_k]]


def _demo_answer(question, retrieved, has_image, service_issue=False):
    q = question.lower()
    if any(x in q for x in ["yellow", "turning yellow", "leaves", "wilting", "drooping"]):
        body = """Yellow leaves or wilting are **symptoms, not a diagnosis**. Possible causes include watering stress, poor drainage, pests, heat, nutrient issues, or normal aging.

**Try these low-risk checks first**
1. Feel the soil a few centimetres below the surface. If it is still wet, pause before watering again; if it is dry, water thoroughly and let excess drain.
2. Check that the pot has drainage holes and that water is not standing in a saucer.
3. Look under leaves and along stems for insects, webbing, sticky residue, or spots.

Tell me the plant name (if known), how much direct sun it gets, and how often you water it."""
    elif any(x in q for x in ["identify", "what kind", "what plant", "name this", "which plant", "tree", "leaf"]):
        body = """I can help identify your plant or tree! To give an accurate estimate, I examine leaf shape, margins, venation, bark, and growth habit.

A clear photo showing both the overall tree/plant and a close-up of its leaves helps narrow down the exact species."""
    elif any(x in q for x in ["egypt", "cairo", "balcony", "rooftop", "water", "grow", "plant", "seed", "garden", "herb"]):
        body = """For growing in Egypt, plan around heat, strong sunlight, wind exposure, and efficient water use.

- Choose plants that suit the light and heat at your actual growing spot.
- Use a container with drainage holes and a suitable potting mix.
- Check soil moisture before watering instead of following a fixed daily schedule.

What are you hoping to grow, and is the spot indoors, on a balcony, on a rooftop, or in a garden?"""
    else:
        body = "I can help with plant identification, care routines, growing problems, and beginner gardening. Tell me what you are growing, where it is placed, and what you have noticed."

    notes = "\n\n**Relevant knowledge notes (RAG)**\n" + "\n".join(
        f"- **{d.get('title', 'Plant-care note')}** — {d.get('source', 'General guidance')}"
        for d in retrieved
    ) if retrieved else "\n\n*This answer uses general starter guidance; the local knowledge base has no closely matching note yet.*"
    service_note = "\n\n*Live AI is temporarily rate-limited or unavailable. Displaying local guidance response.*" if service_issue else ""
    return body + notes + service_note


def build_langchain_prompt(question, context, history, docs, has_image=False):
    """Construct prompt structure using LangChain template principles & Unbiased Vision Analysis (Lec 4)."""
    docs_text = "\n\n".join(
        f"TITLE: {d.get('title')}\nCONTENT: {d.get('text')}\nSOURCE: {d.get('source')}"
        for d in docs
    )
    history_text = "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}"
        for m in history[-10:]
        if m.get("content")
    )

    vision_instructions = ""
    if has_image:
        vision_instructions = """
BOTANICAL VISION ANALYSIS PROTOCOL (A photo is attached):
Examine the image carefully as an objective, unbiased botanical expert. DO NOT assume or default to any specific plant species.

1. VISUAL OBSERVATIONS:
   - Category: Is it a tree, shrub, herb, succulent, vine, or indoor plant?
   - Leaf Analysis: Describe exact leaf shape (e.g. oval, lanceolate, palmate, compound, needle-like, heart-shaped), margins (smooth, serrated, lobed), venation (parallel, pinnate, palmate), and arrangement.
   - Other Features: Note any visible bark, flowers, fruit, stems, or unique traits.

2. UNBIASED SPECIES IDENTIFICATION:
   - Identify the specific plant or tree species shown in the photo. Give both the common name and scientific name.
   - If the image is unclear or shows a feature common to multiple species, list the Top 2-3 most likely candidate matches with confidence levels and explain how to distinguish them.

3. PHYSICAL VERIFICATION CLUES:
   - Provide 2 specific physical details the user can inspect on their physical plant to confirm the identification.

4. EGYPT-SPECIFIC CARE ADVICE:
   - Provide practical care steps for this specific plant in Egypt's climate (sunlight hours, heat tolerance, watering frequency, pot drainage).
"""

    return f"""You are Nabta, a careful, friendly plant-care assistant helping people grow plants in Egypt.
Mission: help make Egypt greener through practical, safe, water-conscious growing advice.
Use plain language and explain unfamiliar gardening terms. Treat beginners respectfully; do not assume expertise.
Use the conversation to remember details the user has already shared, such as experience, city, plant, light, watering, pot, budget, and goals. Do not ask them to repeat details already given.
Do not invent plant species, local weather, source citations, or facts not supported by retrieved notes. Distinguish retrieved knowledge from general advice.
Avoid recommending pesticides or chemical treatments unless clearly justified; prefer observation and low-risk care steps first.
Do not give a rigid watering schedule without enough information about species, pot, soil, and conditions. Encourage checking soil moisture and drainage.
If key details are missing, answer what can safely be answered and ask no more than two useful follow-up questions.
{vision_instructions}

User context: {json.dumps(context or {}, ensure_ascii=False)}

Retrieved plant-care knowledge (Vector RAG):
{docs_text or "No matching retrieved note. Do not invent citations."}

Recent conversation history:
{history_text or "No earlier messages."}

User's current question: {question}
""".strip()


def call_gemini(prompt, image_bytes=None, image_mime=None):
    """Primary provider: Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    parts = [prompt]
    if image_bytes:
        mime = image_mime if image_mime in {"image/jpeg", "image/png", "image/webp"} else "image/jpeg"
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime))

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    response = client.models.generate_content(
        model=model_name,
        contents=parts,
        config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=1400),
    )
    text = getattr(response, "text", None)
    if text and text.strip():
        return text.strip()
    return None


def call_groq_failover(prompt, image_bytes=None, image_mime=None):
    """Secondary provider: Groq API (High-speed failover for 429 Rate Limits)."""
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        models_to_try = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]

        for model in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt + ("\n(User provided a plant photo; analyze question text with high botanical detail.)" if image_bytes else "")}],
                    temperature=0.2,
                    max_tokens=1400,
                )
                if completion.choices and completion.choices[0].message.content:
                    ans = completion.choices[0].message.content.strip()
                    if image_bytes:
                        ans += "\n\n*(Note: Gemini vision API hit rate limits, so Groq processed your plant care details via failover AI.)*"
                    return ans
            except Exception:
                continue
    except Exception:
        pass
    return None


def answer_plant_question(question, context=None, history=None, image_bytes=None, image_mime=None):
    """Answer with multi-provider failover (Gemini -> Groq -> Local Demo)."""
    context = context or {}
    history = history or []
    docs = retrieve_context(question)
    prompt = build_langchain_prompt(question, context, history, docs, has_image=bool(image_bytes))

    # 1. Try Primary: Gemini API
    try:
        ans = call_gemini(prompt, image_bytes, image_mime)
        if ans:
            return ans
    except Exception:
        pass

    # 2. Try Secondary Failover: Groq API
    try:
        ans = call_groq_failover(prompt, image_bytes, image_mime)
        if ans:
            return ans
    except Exception:
        pass

    # 3. Fallback to Local Demo Answer
    return _demo_answer(question, docs, bool(image_bytes), service_issue=True)


def identify_with_image(image_bytes, question="Identify this plant", image_mime=None):
    return answer_plant_question(question, {}, [], image_bytes, image_mime)
