from flask import Flask, jsonify
from flask_cors import CORS
import requests
from flask_limiter import Limiter
import random
import env #env.py file

app = Flask(__name__)
CORS(app)

def get_real_ip():
    """Function to get the real IP address from Cloudflare headers (if applicable)"""
    if request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    return request.remote_addr

limiter = Limiter(
    get_real_ip,
    app=app,
    #default_limits=["80 per hour", "20 per minute", "2 per 2 second"]
)

facts = [
    "In Māori tradition, Kupe is celebrated as a prominent early explorer of New Zealand.",
    "Kupe named New Zealand 'Aotearoa', meaning 'land of the long white cloud'.",
    "Kupe returned to his homeland after discovering New Zealand, promising to return, but unfortunately did not.",
    "According to legends, Kupe battled Te Wheke-a-Muturangi (giant octopus).",
    "Kupe's journey is often linked with the Hokianga Harbour, considered one of his landing points in New Zealand.",
    "The exact timeline of Kupe's voyage is unknown, and is debated among historians and Māori scholars.",
    "In some Māori traditions, Kupe is associated with the introduction of certain native species to New Zealand.",
    "Kupe's navigational skills allowed him to cross vast stretches of the Pacific Ocean using stars, currents, winds, wave echoes, and land shadows.",
    "Kupe House's mascot is the kiwi, a flightless bird native to New Zealand.",
    "Kupe House participates in annual inter-house cultural performances.",
    "Kupe House has won multiple competitions, including house sports, at Macleans College.",
    "The values of Kupe House include kindness, understanding, perseverance, and enthusiasm (KUPE).",
    "The legend of Kupe has inspired numerous artworks and other creations in New Zealand.",
    "Kupe’s journey enabled Polynesians to settle in New Zealand, as later Māori waka followed the path he navigated.",
    "Kupe is credited with naming key landmarks in New Zealand, such as The Hokianga Harbour.",
    "The suggested dates for Kupe’s arrival in New Zealand range from 925 CE to the mid-14th century."
]

@app.route('/api/fact', methods=['GET'])
def random_fact():
    fact = random.choice(facts)
    return jsonify({'fact': fact})

GROQ_API_KEY = env.GROQ_API_KEY
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
#MODEL = "llama3-8b-8192" #a fast model
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct" # a much smarter one

SYSTEM_PROMPT = (
    "You are Llama 4 Scount, originally made by Meta. You are trained by an individual, Raymont Qin. You are a helpful and polite assistant who ONLY CAN (no off-topic discussions) answer questions about Macleans Kupe House, "
    "and Kupe himself. NOTE: that you cannot remember previous conversations due to limits set by your creator. So if user asks what you just said, say that you do not have the ability to remember previous contexts. "
    "Politely decline to answer off-topic questions, however greetings are allowed. Refer users to reliable "
    "sources such as teachers or go to https://www.macleans.school.nz/student/whanau-houses/kupe if you are at all (even just a little bit) unsure about any questions "
    "about Kupe. Kupe House at Macleans College is named after Kupe, the legendary Polynesian explorer who discovered Aotearoa New Zealand. "
    "Built in 1981 and opened by Hiwi Tauroa, the Race Relations Conciliator, Kupe House represents exploration, perseverance, and community. "
    "The house colour is gold, symbolizing ambition, and its mascot is the kiwi bird, representing resilience. The house charity, Kiwis for Kiwi, "
    "supports conservation efforts, with students actively helping release kiwi birds into sanctuaries. Kupe House fosters a strong whānau (family) spirit, "
    "encouraging students to strive for excellence. The house motto, \"Undertake a voyage of discovery, commit to a sharing of knowledge,\" reflects Kupe's journey—"
    "exploring, overcoming challenges, and bringing back wisdom to benefit others. Key artefacts include the Kupe Fountain, Panels in the Commons, Tukutuku Panels, "
    "Māori prints, Kava Bowl, and Fine Mat from Samoa. LEADERS: House Leader Ms. Aliesha Chamberlain, Deputy Leader Mrs. Jacqueline Durham, and House (student) "
    "Captains William Lockhart and Syesha John. Students are encouraged to embrace the values of kindness, understanding, perseverance, and enthusiasm. Through academic, "
    "sporting, and leadership opportunities, Kupe House inspires young students to explore new possibilities and make a positive impact in their community. The house "
    "uses a mnemonic system: K=kindness, U=understanding, P=perseverance, E=enthusiasm (KUPE for kupe!). Kupe was a legendary Polynesian explorer who is credited with "
    "discovering Aotearoa (New Zealand). He travelled from Hawaiki, the ancestral Polynesian homeland, in pursuit of a giant octopus that was interfering with fishing. "
    "He famously fought and defeated the giant octopus Te Wheke-a-Muturangi, which had been sent after him. His voyage led him to explore various parts of New Zealand, "
    "including Cook Strait, which he is said to have named. According to legend, Kupe's wife, Kuramārōtini, named New Zealand \"Aotearoa\" upon seeing the long white cloud over the land."
)

@limiter.limit("80 per hour, 20 per minute, 2 per 2 second")
@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    if not user_message:
        return jsonify({"error": "Missing message"}), 400

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response_json = response.json()
        print(response_json)  # see full output in logs
        return jsonify({"response": response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response from model server. Are you rate-limited? ")})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
