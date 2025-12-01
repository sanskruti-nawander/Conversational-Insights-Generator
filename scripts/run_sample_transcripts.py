# scripts/run_sample_transcripts.py
import asyncio
import httpx

API_URL = "http://127.0.0.1:8000/analyze_call"

SAMPLE_TRANSCRIPTS = [
    # 1) Pre-Due
    """Agent: Hello, main Maya bol rahi hoon, Apex Finance se. Kya main Mr. Sharma se baat kar sakti hoon?
Customer: Haan, main bol raha hoon. Kya hua?
Agent: Sir, aapka personal loan ka EMI due date 3rd of next month hai. Just calling for a friendly reminder. Aapka payment ready hai na?
Customer: Oh okay. Haan, salary aa jayegi tab tak, I will definitely pay it on time. Don’t worry.
Agent: Thank you, sir. Payment time pe ho jaye to aapka credit score bhi maintain rahega. Have a good day!""",

    # 2) Pre-Due
    """Agent: Namaste. Main Priyanka, City Bank credit card department se. Aapka minimum due ₹8,500 hai, jo 10th ko due ho raha hai.
Customer: Ji, pata hai. I think main poora amount nahi de paunga, but minimum toh kar dunga.
Agent: Sir, poora payment karna best hai, par minimum due must hai to avoid late fees. Koi issue toh nahi hai payment mein?
Customer: Nahi, no issue. I’ll clear it by the 8th.
Agent: Great! Thank you for the confirmation.""",

    # 3) Post-Due (D+7)
    """Agent: Hello Mr. Verma, main Aman bol raha hoon. Aapka personal loan EMI 7 days se overdue hai. Aapne payment kyun nahi kiya?
Customer: Dekhiye, thoda emergency aa gaya tha. Mera bonus expected hai next week.
Agent: Sir, aapko pata hai ki is par penalty lag rahi hai. Aap exact date batayiye, kab tak confirm payment ho jayega?
Customer: Wednesday ko pakka kar dunga. Promise to Pay le lo Wednesday ka.
Agent: Okay, main aapka PTP book kar raha hoon next Wednesday ke liye. Please ensure payment is done to stop further charges.""",

    # 4) Post-Due (D+15)
    """Agent: Good afternoon, Ms. Jain. Aapke credit card ka minimum due 15 din se pending hai.
Customer: Oh, I forgot completely. Office mein kaam zyada tha.
Agent: Ma'am, aapka total outstanding ab ₹45,000 ho gaya hai, including late fees. Aap aaj hi ₹8,500 ka minimum payment kar dijiye.
Customer: Aaj toh nahi ho payega. Sunday ko final karungi.
Agent: Sunday is fine, ma’am, but late fees already apply ho chuki hain. Please make sure payment ho jaye.""",

    # 5) Post-Due (D+25)
    """Agent: Mr. Khan, aapka loan account NPA hone ke risk par hai. 25 days ho gaye hain. Ye serious matter hai.
Customer: Main out of station hoon, server issue hai mere bank mein.
Agent: Sir, aap online transfer kar sakte hain, ya phir family member se karwa dijiye. Account status kharab ho raha hai.
Customer: Thik hai, thik hai. Main next 3 hours mein try karta hoon.
Agent: Sir, try nahi, I need a guarantee. Kya main 3 hours mein confirmation call karun?
Customer: Haan, call kar lo.""",

    # 6) Recovery (D+60)
    """Agent: Mr. Reddy, main Legal Department se baat kar raha hoon. Aapka loan 60 days se default mein hai.
Humari team aapki location par visit karne ki planning kar rahi hai.
Customer: Please, visit mat bhejo. Meri job chali gayi hai. I need time!
Agent: Sir, time humne bahut diya hai. Aap kitna amount abhi immediately de sakte hain?
Customer: Abhi main sirf ₹10,000 de sakta hoon. Baaki next month.
Agent: Okay, ₹10,000 ka token payment kar dijiye. Hum aapki file temporary hold par rakhenge.""",

    # 7) Recovery (D+90)
    """Agent: Ma'am, aapka account write-off hone ki verge par hai. 90 days ho gaye hain. Aapka total due ₹1.5 lakh hai.
Customer: Main itna paisa nahi de sakti. Please settlement option do.
Agent: Settlement ke liye aapko pehle minimum 30% upfront dena hoga. Kya aap eligible hain?
Customer: Mujhe details mail kar do. Main check karti hoon.
Agent: Main aapko final warning de raha hoon. Agar aapne action nahi liya toh legal notice jayega.""",

    # 8) Recovery (D+120)
    """Agent: Mr. Singh, aapka case external agency ko assign ho chuka hai. Hum final discussion ke liye call kar rahe hain. Aapki property par charge hai.
Customer: No, no, personal loan par koi charge nahi hai. Stop threatening!
Agent: Sir, as per the loan agreement, hum action le sakte hain. Aap aaj ₹25,000 transfer kijiye for account regularization.
Customer: I’ll talk to my lawyer.
Agent: That’s your right, sir, but payment is mandatory.""",

    # 9) Recovery (D+60, Dispute)
    """Agent: Hello, Mr. Kumar. 60 days outstanding hai. What is the payment plan?
Customer: Maine aapko pehle hi bataya tha, ek transaction fraud tha. Jab tak woh resolve nahi hoga, main payment nahi karunga.
Agent: Sir, dispute department separate hai. Aapka due amount legal hai. You must pay the undisputed amount first.
Customer: No, pehle dispute resolve karo!
Agent: Sir, both processes parallel run karte hain. Please minimum due aaj pay kar dijiye.""",

    # 10) Recovery (D+75, Hardship)
    """Agent: Ms. Pooja, hum aapko 75 days se call kar rahe hain. Aap cooperate nahi kar rahe.
Customer: Meri mother hospital mein hain. Serious financial hardship hai. I am requesting a restructuring of the loan.
Agent: Ma’am, we understand the situation. Lekin restructuring ke liye aapko hardship application fill karni hogi
aur last 3 months ka bank statement dena hoga.
Customer: Okay, send me the form.
Agent: Thank you, ma’am. Please complete the process quickly, warna account recovery stage par chala jayega."""
]


async def call_one(client: httpx.AsyncClient, idx: int, transcript: str, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        print(f"\n=== Calling sample #{idx} (attempt {attempt}) ===")
        resp = await client.post(API_URL, json={"transcript": transcript})
        print("Status:", resp.status_code)

        if resp.status_code == 200:
            data = resp.json()
            print("Record ID:", data["id"])
            print("Insights:", data["insights"])
            return True

        # Print error body
        print("Error body:", resp.text)

        # If it's the LLM 429 case, we can retry; otherwise just give up
        if "RESOURCE_EXHAUSTED" not in resp.text:
            break

    return False


async def run():
    failed_indices = []
    async with httpx.AsyncClient() as client:
        for idx, transcript in enumerate(SAMPLE_TRANSCRIPTS, start=1):
            ok = await call_one(client, idx, transcript)
            if not ok:
                failed_indices.append(idx)

    print("\n=== Done ===")
    if failed_indices:
        print("These samples still failed after retries:", failed_indices)
    else:
        print("All samples succeeded!")


if __name__ == "__main__":
    asyncio.run(run())
