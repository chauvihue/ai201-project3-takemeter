"""Apply labels to data.csv based on ID mapping."""
import csv

LABELS = {
    # Jerome Powell post + comment
    "1rzdf36":     "economy",
    "1rzdf36_c0":  "hot_takes",
    # Corporations Reeling post + comments
    "1u3fnx3":     "articles",
    "1u3fnx3_c0":  "work",
    "1u3fnx3_c1":  "work",
    "1u3fnx3_c2":  "work",
    "1u3fnx3_c3":  "work",
    # AI isn't paying off post + comments
    "1tbjakc":     "articles",
    "1tbjakc_c0":  "economy",
    "1tbjakc_c1":  "economy",
    "1tbjakc_c2":  "hot_takes",
    "1tbjakc_c3":  "hot_takes",
    # AI Gold Rush Is Cover for a Class War post + comments
    "1rpcw5h":     "articles",
    "1rpcw5h_c0":  "society",
    "1rpcw5h_c1":  "society",
    "1rpcw5h_c2":  "hot_takes",
    "1rpcw5h_c3":  "society",
    # Stock market dot-com bubble post + comments
    "1ttx0ej":     "articles",
    "1ttx0ej_c0":  "economy",
    "1ttx0ej_c1":  "society",
    "1ttx0ej_c2":  "society",
    "1ttx0ej_c3":  "hot_takes",
    # Making sense of Friday global selloff post + comments
    "1tye9zk":     "economy",
    "1tye9zk_c0":  "economy",
    "1tye9zk_c1":  "economy",
    "1tye9zk_c2":  "economy",
    "1tye9zk_c3":  "economy",
    # Biggest Bubble in History post + comments
    "1ucu0jp":     "questions",
    "1ucu0jp_c0":  "hot_takes",
    "1ucu0jp_c1":  "hot_takes",
    "1ucu0jp_c2":  "hot_takes",
    "1ucu0jp_c3":  "hot_takes",
    # How the bubble pops (Oracle) post + comments
    "1tqejhd":     "economy",
    "1tqejhd_c0":  "economy",
    "1tqejhd_c1":  "hot_takes",
    "1tqejhd_c2":  "economy",
    "1tqejhd_c3":  "hot_takes",
    # AI Startups Hallucinate Revenue Metrics post + comments
    "1tr47wp":     "articles",
    "1tr47wp_c0":  "economy",
    "1tr47wp_c1":  "hot_takes",
    # AI companies burning billions post + comments
    "1seer5u":     "hot_takes",
    "1seer5u_c0":  "hot_takes",
    "1seer5u_c1":  "hot_takes",
    "1seer5u_c2":  "hot_takes",
    "1seer5u_c3":  "hot_takes",
    # Microsoft sued by shareholders post
    "1u8m3k5":     "articles",
    # Disconnect managers vs line-workers post + comments
    "1sqsy3g":     "work",
    "1sqsy3g_c0":  "work",
    "1sqsy3g_c1":  "work",
    "1sqsy3g_c2":  "work",
    "1sqsy3g_c3":  "hot_takes",
    # AI bubble 2026 post + comments
    "1u4d4pz":     "hot_takes",
    "1u4d4pz_c0":  "economy",
    "1u4d4pz_c1":  "economy",
    "1u4d4pz_c2":  "hot_takes",
    "1u4d4pz_c3":  "work",
    # Could Anthropic's IPO pop the bubble post + comments
    "1tzulfn":     "questions",
    "1tzulfn_c0":  "economy",
    "1tzulfn_c1":  "economy",
    "1tzulfn_c2":  "economy",
    "1tzulfn_c3":  "economy",
    # OpenAI offering PE firms 17.5% guaranteed return post + comments
    "1s1ohcb":     "questions",
    "1s1ohcb_c0":  "hot_takes",
    "1s1ohcb_c1":  "hot_takes",
    "1s1ohcb_c2":  "economy",
    "1s1ohcb_c3":  "economy",
    # AI profitability mathematically impossible post + comments
    "1tzz9ic":     "economy",
    "1tzz9ic_c0":  "hot_takes",
    "1tzz9ic_c1":  "hot_takes",
    "1tzz9ic_c2":  "economy",
    "1tzz9ic_c3":  "society",
    # OpenAI shutting down Sora post + comments
    "1s2w503":     "articles",
    "1s2w503_c0":  "economy",
    "1s2w503_c1":  "hot_takes",
    # How will AI hype deflate post + comments
    "1ub21vm":     "questions",
    "1ub21vm_c0":  "economy",
    "1ub21vm_c1":  "hot_takes",
    "1ub21vm_c2":  "society",
    "1ub21vm_c3":  "society",
    # Is the AI bubble actually a normal bubble post + comments
    "1uayvoi":     "questions",
    "1uayvoi_c0":  "hot_takes",
    "1uayvoi_c1":  "economy",
    "1uayvoi_c2":  "hot_takes",
    "1uayvoi_c3":  "economy",
    # Does anyone else think bubble is about to burst post + comments
    "1u2m8xh":     "questions",
    "1u2m8xh_c0":  "economy",
    "1u2m8xh_c1":  "work",
    "1u2m8xh_c2":  "work",
    "1u2m8xh_c3":  "work",
    # AI bubble after Trump leaves post + comments
    "1u0motl":     "economy",
    "1u0motl_c0":  "hot_takes",
    "1u0motl_c1":  "economy",
    "1u0motl_c2":  "economy",
    "1u0motl_c3":  "economy",
    # Blinking New Warning Sign post + comment
    "1r9s2je":     "articles",
    "1r9s2je_c0":  "economy",
    # Where's the money coming from post + comments
    "1u1iyut":     "questions",
    "1u1iyut_c0":  "economy",
    "1u1iyut_c1":  "economy",
    "1u1iyut_c2":  "economy",
    "1u1iyut_c3":  "hot_takes",
    # Human brain energy efficient post
    "1rbkrok":     "hot_takes",
    # Reminder every company announcing AGI needs funding post
    "1sdf0ul":     "hot_takes",
    # Hypothesis AI Spending and the Economy post + comments
    "1rfwqb4":     "economy",
    "1rfwqb4_c0":  "hot_takes",
    "1rfwqb4_c1":  "hot_takes",
    "1rfwqb4_c2":  "economy",
    "1rfwqb4_c3":  "economy",
    # When people say AI is in a bubble what do they mean post + comments
    "1u5t926":     "questions",
    "1u5t926_c0":  "economy",
    "1u5t926_c1":  "economy",
    "1u5t926_c2":  "economy",
    "1u5t926_c3":  "economy",
    # Why are people buying AI hype post + comments
    "1tyqzgb":     "hot_takes",
    "1tyqzgb_c0":  "hot_takes",
    "1tyqzgb_c1":  "economy",
    "1tyqzgb_c2":  "economy",
    "1tyqzgb_c3":  "economy",
    # When do you think AI bubble will burst post + comments
    "1tzehtm":     "questions",
    "1tzehtm_c0":  "economy",
    "1tzehtm_c1":  "hot_takes",
    "1tzehtm_c2":  "economy",
    "1tzehtm_c3":  "hot_takes",
    # How do I convince my father post + comments
    "1snopda":     "questions",
    "1snopda_c0":  "economy",
    "1snopda_c1":  "economy",
    "1snopda_c2":  "hot_takes",
    "1snopda_c3":  "economy",
    # Chip stocks erase $1T post (Portuguese)
    "1ty1ygc":     "articles",
    # The AI industry has a big Chicken Little problem post
    "1r3igxj":     "articles",
    # More Tech Layoffs 52000 jobs gone post
    "1se5ahr":     "articles",
    # Confused with Michael Burry saying its a bubble post + comments
    "1rt21ie":     "questions",
    "1rt21ie_c0":  "hot_takes",
    "1rt21ie_c1":  "economy",
    "1rt21ie_c2":  "economy",
    "1rt21ie_c3":  "hot_takes",
    # Meta's Moltbook gamble post
    "1rskk83":     "articles",
    # POP THE AI BUBBLE petition post
    "1rd1tdl":     "hot_takes",
    # AI bubble has burst calling it today post + comments
    "1udogge":     "hot_takes",
    "1udogge_c0":  "economy",
    "1udogge_c1":  "hot_takes",
    "1udogge_c2":  "hot_takes",
    "1udogge_c3":  "hot_takes",
    # Welcome to a Multidimensional Economic Disaster post
    "1s5nl4a":     "hot_takes",
    # Whither the AI bubble post + comments
    "1rqqd2m":     "articles",
    "1rqqd2m_c0":  "hot_takes",
    "1rqqd2m_c1":  "hot_takes",
    # How Do I Learn to Stop Worrying post + comments
    "1qu7pvq":     "questions",
    "1qu7pvq_c0":  "economy",
    "1qu7pvq_c1":  "society",
    # If AI meant to replace workers why not managers post + comments
    "1u9srkv":     "questions",
    "1u9srkv_c0":  "hot_takes",
    "1u9srkv_c1":  "work",
    "1u9srkv_c2":  "society",
    "1u9srkv_c3":  "hot_takes",
    # Auditors Growing a Spine on Hyperscaler Accounting post
    "1r2bnf9":     "articles",
    # Like a toddler trying to shove AI post + comment
    "1pn6f7n":     "hot_takes",
    "1pn6f7n_c0":  "work",
    # My little contribution to the bubble post + comment
    "1ovnuni":     "hot_takes",
    "1ovnuni_c0":  "hot_takes",
    # Tech and AI companies are Faking Revenue post
    "1of9rh0":     "articles",
    # This subreddit is a psyop post + comments
    "1u38ez0":     "hot_takes",
    "1u38ez0_c0":  "hot_takes",
    "1u38ez0_c1":  "hot_takes",
    # AI Bubble Index post
    "1rb43qq":     "economy",
    # The A.I. Bubble A Value Investors Perspective post (articles edge case)
    "1q8bak4":     "articles",
    # OpenAI admitted AI Browser never fully safe post + comments
    "1pund9c":     "articles",
    "1pund9c_c0":  "hot_takes",
    "1pund9c_c1":  "society",
    # SPY Dec 2026 $650 Put post + comments
    "1onha1t":     "questions",
    "1onha1t_c0":  "economy",
    "1onha1t_c1":  "economy",
    # Mulaney roasts AI wonks post
    "1fo11td":     "articles",
    # AI capex capital cycles post (economy edge case)
    "1u2pm6d":     "economy",
    # Is per-seat SaaS structurally broken (AIBubble version) post + comment
    "1u1i8ls":     "society",
    "1u1i8ls_c0":  "society",
    # If AI capable of doing almost everything post
    "1rip23u":     "questions",
    # When the Internet Cooks It Serves Slop post
    "1r3ju4a":     "articles",
    # The One Indicator That Predicted Every US Recession post
    "1pppys5":     "articles",
    # Asian equity-market boom post
    "1pi0ofu":     "articles",
    # The A.I. Bubble A Value Investors Perspective (second post)
    "1pewd8h":     "articles",
    # Patrick Boyle Does OpenAI expect a Government Bailout post + comment
    "1p7dir3":     "articles",
    "1p7dir3_c0":  "economy",
    # aibubble bloomberg hashtag post
    "1o5etm4":     "articles",
    # Tech Sell-Off vs Microns Surge post
    "1udpyd7":     "questions",
    # The True Cost of AI Hidden in Big Techs Financials post
    "1uckcve":     "articles",
    # Is the adoption of AI in companies just a euphemism post
    "1u6tbo5":     "society",
    # Is per-seat SaaS structurally broken (legaltech+linked version) post
    "1u13uwq":     "society",
    # Will the public markets be kind to the AI bubble post
    "1u11pf9":     "economy",
    # Will AI get cheaper or more expensive post
    "1u0uj9z":     "questions",
    # Article from June 1 Natural News post
    "1tzjmqf":     "questions",
    # What are your thoughts on the AI bubble Indian economy post + comments
    "1tzbksa":     "questions",
    "1tzbksa_c0":  "economy",
    "1tzbksa_c1":  "economy",
    "1tzbksa_c2":  "economy",
    "1tzbksa_c3":  "economy",
    # Confused about bubbles sign in (off-topic Bubble.io)
    "1silokk":     "hot_takes",
    # Crusoe Deal Goldman Sachs AMD post
    "1r991xz":     "economy",
    # Trump Shifts Policy on Nvidia Chip Exports post
    "1pkn2db":     "articles",
    # Trump to allow selling H200 chips to China post
    "1pi4801":     "articles",
    # Panopticon Public/Private Partnership post
    "1p781wu":     "articles",
    # NVIDIA revenue vs all AI products post
    "1ozo0wo":     "questions",
    # An AI Bubble is All in Our Heads post + comments
    "1oy8l5g":     "questions",
    "1oy8l5g_c0":  "hot_takes",
    "1oy8l5g_c1":  "economy",
    "1oy8l5g_c2":  "economy",
    "1oy8l5g_c3":  "economy",
    # Planning to spend 200B Meta stock drop post
    "1omn1cd":     "hot_takes",
    # AI and Our Economic Future (hot_takes example from planning.md)
    "1udiae6":     "hot_takes",
    "1udiae6_c0":  "hot_takes",
    # AI is over (work edge case from planning.md)
    "1ud6bab":     "work",
    # AI democratized production not success (work example from planning.md)
    "1ucz990":     "work",
    "1ucz990_c0":  "economy",
    "1ucz990_c1":  "economy",
    "1ucz990_c2":  "economy",
    # US equity AI ceiling post + comments
    "1u5buer":     "economy",
    "1u5buer_c0":  "society",
    "1u5buer_c1":  "society",
    "1u5buer_c2":  "society",
    # AI companies are creating massive wealth post (society example)
    "1u3zj1c":     "society",
    # What will impress you post
    "1u2hul8":     "questions",
    # US Economy Is Collapsing From the Inside Out post
    "1pi4a61":     "articles",
    # OpenAI and Anthropic IPO is the ripoff post + comments
    "1u3yw2k":     "economy",
    "1u3yw2k_c0":  "hot_takes",
    "1u3yw2k_c1":  "hot_takes",
    "1u3yw2k_c2":  "hot_takes",
    "1u3yw2k_c3":  "hot_takes",
    # AI is a bubble but an artificially made one post
    "1rha2xx":     "society",
    # Anyone think there is an AI bubble post + comments (questions example)
    "1ud6j1r":     "questions",
    "1ud6j1r_c0":  "economy",
    "1ud6j1r_c1":  "economy",
    "1ud6j1r_c2":  "hot_takes",
    "1ud6j1r_c3":  "hot_takes",
    # The AI Bubble is about to Pop Bitcoin post + comments (economy edge case)
    "1s3kl86":     "economy",
    "1s3kl86_c0":  "economy",
    "1s3kl86_c1":  "hot_takes",
    "1s3kl86_c2":  "economy",
    "1s3kl86_c3":  "economy",
    # Removed by Reddit post
    "1tcrfq8":     "hot_takes",
}

INPUT  = "data.csv"
OUTPUT = "data.csv"

rows = []
with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rid = row["id"]
        if rid in LABELS:
            row["label"] = LABELS[rid]
        rows.append(row)

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Print distribution
from collections import Counter
dist = Counter(r["label"] for r in rows)
total = len(rows)
unlabeled = dist.get("", 0)
print(f"Total rows: {total}  |  Unlabeled: {unlabeled}")
for label in ["questions", "articles", "work", "economy", "society", "hot_takes"]:
    print(f"  {label:12s}: {dist[label]}")
