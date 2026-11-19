import pandas as pd
from preprocess import preprocess_text

# 1. Load the raw dataset
df = pd.read_csv("all_tickets_processed_improved_v3.csv")

# 2. Inspect it first
print("Shape before cleaning:", df.shape)
print("Columns:", df.columns.tolist())
print("\nMissing values:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())
print("\nCategory counts (before):\n", df["Topic_group"].value_counts())

# 3. Rename columns
df = df.rename(columns={"Document": "ticket", "Topic_group": "category"})

# 4. Remove missing values and duplicates
df = df.dropna()
df = df.drop_duplicates()
df = df.drop_duplicates(subset="ticket")

# 5. Tidy the text
df["ticket"] = df["ticket"].astype(str).str.strip()
df["category"] = df["category"].astype(str).str.strip()

# 6. Remove very short tickets
df = df[df["ticket"].str.len() >= 20]

# 7. Clean the text (footer removal, noise words, repeats, first 40 words)
df["clean_ticket"] = df["ticket"].apply(preprocess_text)

# 8. Remove tickets with fewer than 3 meaningful words left
df = df[df["clean_ticket"].str.split().str.len() >= 3]

# 9. Remove duplicates created by cleaning
df = df.drop_duplicates(subset="clean_ticket")

# 10. Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 11. Summary and save
print("\nShape after cleaning:", df.shape)
print("\nCategory counts (after):\n", df["category"].value_counts())
print("\nAverage words per cleaned ticket:",
      round(df["clean_ticket"].str.split().str.len().mean(), 1))
print("\nSamples (before -> after):")
for i in range(3):
    print("\nORIGINAL:", df["ticket"][i][:200])
    print("CLEANED :", df["clean_ticket"][i])

df.to_csv("tickets_clean.csv", index=False)
print("\nSaved tickets_clean.csv")