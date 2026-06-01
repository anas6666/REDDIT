import praw
import pandas as pd
import time
import re
from collections import Counter
import os

# =========================

# REDDIT API (GITHUB SECRETS)

# =========================

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
"marketing","PPC","SEO","digital_marketing","FacebookAds","googleads",
"analytics","dataisbeautiful","bigseo","agency","smallbusiness",
"entrepreneur","startups","SaaS","indiehackers","sales","ecommerce",
"Shopify","AmazonSeller","webmarketing","Emailmarketing",
"content_marketing","socialmedia","adops","marketingautomation",
"growthhacking","businessintelligence","PowerBI","LookerStudio",
"tableau","excel","analyticsengineering","dataengineering"
]

# =========================

# KEYWORDS

# =========================

keywords = [
"csv","spreadsheet","excel","google sheets","reporting","dashboard",
"client reporting","manual","time consuming","messy","frustrating",
"hate","takes hours","wasting time","broken","merge data",
"combine data","clean data","normalize","schema","mapping",
"meta ads","facebook ads","google ads","shopify","hubspot",
"looking for","need a tool","is there a tool","automation",
"workflow","alternative to","any solution"
]

# =========================

# SEARCH QUERIES

# =========================

search_queries = [
"csv reporting","marketing reporting automation","merge csv data",
"client reporting","facebook ads csv","google ads reporting",
"dashboard automation","looker studio alternative",
"power bi too complex","manual reporting","analytics workflow",
"broken csv schema","marketing reporting takes hours"
]

results = []

def contains_keywords(text):
    text = text.lower()
    return any(k in text for k in keywords)

# =========================

# SCRAPE

# =========================

for sub in target_subreddits:
    print(f"\n🔍 r/{sub}")
    subreddit = reddit.subreddit(sub)
    
    
    for query in search_queries:
        print(f"   → {query}")
    
        try:
            for post in subreddit.search(query, limit=30):
    
                if post.stickied:
                    continue
    
                text = (post.title + " " + post.selftext).lower()
    
                if not contains_keywords(text):
                    continue
    
                post.comments.replace_more(limit=0)
    
                comments = [
                    c.body for c in post.comments.list()[:30]
                ]
    
                results.append({
                    "subreddit": sub,
                    "query": query,
                    "title": post.title,
                    "score": post.score,
                    "comments": post.num_comments,
                    "url": post.url,
                    "created_utc": post.created_utc,
                    "text": post.selftext,
                    "top_comments": "\n\n".join(comments)
                })
    
                print(f"   ✅ {post.title[:80]}")
    
                time.sleep(1)
    
        except Exception as e:
            print("Error:", e)


# =========================

# SAVE DATA

# =========================

df = pd.DataFrame(results)

if df.empty:
    print("No data scraped")
    exit()

df.drop_duplicates(subset=["title"], inplace=True)

csv_file = "reddit_marketing_data.csv"
excel_file = "reddit_marketing_data.xlsx"

df.to_csv(csv_file, index=False, encoding="utf-8-sig")

df.to_excel(excel_file, index=False)

# =========================

# ANALYSIS

# =========================

text_all = " ".join(df["title"].astype(str)).lower()
words = re.findall(r'\b[a-zA-Z]{4,}\b', text_all)

stopwords = {
"that","this","with","from","have","what","your","does",
"need","tool","using","marketing","reporting"
}

filtered = [w for w in words if w not in stopwords]

top_words = Counter(filtered).most_common(50)

pd.DataFrame(top_words, columns=["word","count"]).to_csv(
"top_terms.csv",
index=False,
encoding="utf-8-sig"
)

print("\n✅ DONE")
