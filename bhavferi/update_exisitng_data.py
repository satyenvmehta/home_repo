import re
import pandas as pd

TMP = r"C:/tmp/"
EXISTING_FILE = TMP + "existing_folder_corrected_stname.csv"
OUTPUT_FILE = TMP + "existing_file_with_blank_filled_v3.csv"

FOLDER_COL = "foldername"


STREET_SUFFIX_MAP = {
    "DR": "DRIVE",
    "DR.": "DRIVE",
    "RD": "ROAD",
    "RD.": "ROAD",
    "ST": "STREET",
    "ST.": "STREET",
    "AVE": "AVENUE",
    "AVE.": "AVENUE",
    "BLVD": "BOULEVARD",
    "LN": "LANE",
    "CT": "COURT",
    "CIR": "CIRCLE",
    "PL": "PLACE",
    "PKWY": "PARKWAY",
    "TER": "TERRACE",
}


def is_blank(value):
    return pd.isna(value) or str(value).strip() == ""


def clean_street(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().upper()
    value = value.replace(",", "")
    value = re.sub(r"\s+", " ", value)

    words = value.split()
    words = [STREET_SUFFIX_MAP.get(w, w) for w in words]

    return " ".join(words)


# =========================================================
# Load existing file
# Keep all columns, including unique id column
# =========================================================

df = pd.read_csv(EXISTING_FILE, dtype=str).dropna(how="all")

df["_street_clean"] = df["street"].apply(clean_street)


# =========================================================
# Build street -> foldername map
# using only rows where foldername is already assigned
# =========================================================

street_folder_map = (
    df[~df[FOLDER_COL].apply(is_blank)]
    .drop_duplicates("_street_clean")
    .set_index("_street_clean")[FOLDER_COL]
    .to_dict()
)


# =========================================================
# Fill blank foldername from same normalized street
# =========================================================

blank_mask = df[FOLDER_COL].apply(is_blank)

df.loc[blank_mask, FOLDER_COL] = (
    df.loc[blank_mask, "_street_clean"]
    .map(street_folder_map)
)


# =========================================================
# Remove helper column and save same format as existing file
# =========================================================

df = df.drop(columns=["_street_clean"])

df.to_csv(OUTPUT_FILE, index=False)

print(f"Created: {OUTPUT_FILE}")
print(f"Updated blank foldername rows: {blank_mask.sum()}")