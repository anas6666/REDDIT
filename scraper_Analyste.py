import praw
import pandas as pd
import time
import re
from collections import Counter
from datetime import datetime


import os

reddit = praw.Reddit(
client_id=os.environ["REDDIT_CLIENT_ID"],
client_secret=os.environ["REDDIT_CLIENT_SECRET"],
password=os.environ["REDDIT_PASSWORD"],
user_agent=os.environ["REDDIT_USER_AGENT"],
username=os.environ["REDDIT_USERNAME"],
)

# =========================

# TARGET SUBREDDITS

# =========================

target_subreddits = [
"marketing",
"PPC",
"SEO",
"digital_marketing",
"FacebookAds",
"googleads",
"analytics",
"agency",
"smallbusiness",
"entrepreneur",
"startups",
"SaaS",
"indiehackers",
"sales",
"ecommerce",
"Shopify",
"AmazonSeller",
"Emailmarketing",
"socialmedia",
"marketingautomation",
"growthhacking",
"businessintelligence",
"PowerBI",
"LookerStudio",
"tableau",
"excel",
"analyticsengineering",
"dataengineering",
"nocode",
"automation",
"crm",
"hubspot",
"webdev",
"agencyowners",
"consulting",
]

# =========================

# KEYWORDS

# =========================

keywords = [
# BI pain
"power bi too complex",
"looker studio too hard",
"dashboard",
"business intelligence",
"reporting",
"analytics",


# non technical
"non technical",
"non analyst",
"small business owner",
"easy dashboard",
"without coding",
"without sql",
"no code analytics",

# frustration
"confusing",
"complex",
"hard to use",
"hate reporting",
"takes hours",
"manual work",
"frustrating",

# intent
"looking for",
"need a tool",
"is there a tool",
"any recommendations",
"alternative to",
"what do you use",
"how do you automate",
"workflow",

# existing tools
"power bi",
"tableau",
"metabase",
"looker studio",
"zoho analytics",


]

# =========================

# SEARCH QUERIES

# =========================

search_queries = [
"power bi too complex",
"business intelligence for non technical users",
"easy dashboard software",
"simple analytics tool",
"dashboard for small business",
"looker studio alternative",
"tableau alternative",
"reporting tool for clients",
"non technical analytics",
"business owner dashboard",
"easy reporting software",
"analytics without sql",
"simple KPI dashboard",
"manual reporting pain",
"help with dashboards",
]

# =========================

# RESULTS

# =========================

results = []

# =========================

# HELPERS

# =========================

def contains_keywords(text):
    text = text.lower()
    return any(k.lower() in text for k in keywords)

# =========================

# SCRAPING

# =========================

for sub_name in target_subreddits:   
    
    print(f"\\n🔍 Searching r/{sub_name}")
    
    try:
        subreddit = reddit.subreddit(sub_name)
    
        for query in search_queries:
    
            print(f"   → Query: {query}")
    
            try:
                for submission in subreddit.search(
                    query,
                    sort="relevance",
                    limit=50
                ):
    
                    if submission.stickied:
                        continue
    
                    full_text = (
                        submission.title + " " + submission.selftext
                    ).lower()
    
                    if not contains_keywords(full_text):
                        continue
    
                    # COMMENTS
                    submission.comments.replace_more(limit=0)
    
                    comments = []
    
                    for comment in submission.comments.list()[:40]:
                        comments.append(comment.body)
    
                    all_comments = "\\n\\n".join(comments)
    
                    results.append({
                        "subreddit": sub_name,
                        "query": query,
                        "title": submission.title,
                        "score": submission.score,
                        "comments_count": submission.num_comments,
                        "created_utc": submission.created_utc,
                        "url": submission.url,
                        "text": submission.selftext,
                        "all_comments": all_comments
                    })
    
                    print(f"      ✅ {submission.title[:90]}")
    
                    time.sleep(1)
    
            except Exception as e:
                print(f"Search error: {e}")
    
    except Exception as e:
        print(f"Subreddit error: {e}")


# =========================

# DATAFRAME

# =========================

# =========================
# DATAFRAME
# =========================

ILLEGAL_CHARACTERS_RE = re.compile(
    r'[\x00-\x08\x0B-\x0C\x0E-\x1F]'
)

def clean_excel_text(value):
    if isinstance(value, str):
        value = ILLEGAL_CHARACTERS_RE.sub("", value)
        return value[:32000]  # Excel cell limit protection
    return value

df = pd.DataFrame(results)

# CLEAN INVALID EXCEL CHARACTERS
df = df.map(clean_excel_text)

if len(df) == 0:
    print("❌ No posts found")
    exit()

# REMOVE DUPLICATES

df.drop_duplicates(
subset=["title"],
inplace=True
)

# SORT

df.sort_values(
by=["score", "comments_count"],
ascending=False,
inplace=True
)

# =========================

# SAVE CSV

# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M")

csv_name = f"bi_tool_reddit_results_{timestamp}.csv"
excel_name = f"bi_tool_reddit_results_{timestamp}.xlsx"

df.to_csv(
csv_name,
index=False,
encoding="utf-8-sig"
)

# =========================

# SIMPLE ANALYSIS

# =========================

all_text = " ".join(
df["title"].astype(str).tolist()
).lower()

words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text)

stopwords = {
"that", "this", "with", "from",
"have", "what", "your", "does",
"need", "tool", "using", "business",
"analytics", "dashboard", "reporting"
}

filtered_words = [
w for w in words
if w not in stopwords
]

top_words = Counter(filtered_words).most_common(100)

analysis_df = pd.DataFrame(
top_words,
columns=["word", "count"]
)

# =========================

# SAVE EXCEL

# =========================

with pd.ExcelWriter(excel_name, engine="openpyxl") as writer:

    df.to_excel(
        writer,
        sheet_name="Posts",
        index=False
    )
    
    analysis_df.to_excel(
        writer,
        sheet_name="Top Terms",
        index=False
    )


print(f"\n✅ Saved {len(df)} posts")
print(f"✅ CSV: {csv_name}")
print(f"✅ Excel: {excel_name}")
