import csv

COLUMNS = ['id', 'url', 'text', 'label', 'subreddit', 'notes']

def read_csv(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def extract_subreddit(url):
    try:
        return 'r/' + url.split('/r/')[1].split('/')[0]
    except IndexError:
        return ''

existing = {row['id']: row for row in read_csv('data.csv') if row.get('type') != 'comment'}

raw_rows = read_csv('dataset_raw.csv')

merged = []
for row in raw_rows:
    subreddit = extract_subreddit(row['url'])
    if row['id'] in existing:
        out = {col: existing[row['id']].get(col, '') for col in COLUMNS}
        out['subreddit'] = subreddit
        merged.append(out)
    else:
        out = {col: row.get(col, '') for col in COLUMNS}
        out['subreddit'] = subreddit
        merged.append(out)

with open('data.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(merged)

print(f"Written {len(merged)} rows to data.csv")
