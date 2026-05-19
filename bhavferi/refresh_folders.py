import pandas as pd


EXISTING_FILE = "existing_folder.csv"
NEWDATA_FILE = "newdata.csv"

DELTA_FILE = "delta.csv"
DIFFERENT_LASTNAME_FILE = "different_lastname.csv"

TMP = r"C:/tmp/"
EXISTING_FILE = TMP + EXISTING_FILE
NEWDATA_FILE = TMP + NEWDATA_FILE
DELTA_FILE = TMP + DELTA_FILE
DIFFERENT_LASTNAME_FILE = TMP + DIFFERENT_LASTNAME_FILE

import re
import pandas as pd


def clean_str(value):
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def clean_stnum(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    if value.endswith(".0"):
        value = value[:-2]

    return value


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
    "BLVD.": "BOULEVARD",
    "GRV" : "GROVE",
    "LN": "LANE",
    "LN.": "LANE",
    "CT": "COURT",
    "CT.": "COURT",
    "CIR": "CIRCLE",
    "CIR.": "CIRCLE",
    "PL": "PLACE",
    "PL.": "PLACE",
    "WAY": "WAY",
    "PKWY": "PARKWAY",
    "PKWY.": "PARKWAY",
    "TER": "TERRACE",
    "TER.": "TERRACE",
}


def clean_street(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    # remove extra spaces
    value = re.sub(r"\s+", " ", value)

    # remove commas
    value = value.replace(",", "")

    words = value.split()

    cleaned_words = []

    for word in words:
        cleaned_words.append(STREET_SUFFIX_MAP.get(word, word))

    return " ".join(cleaned_words)


def create_address_key(df):
    return (
        df["stnum"].apply(clean_stnum)
        + "|"
        + df["street"].apply(clean_street)
    )

existing_df = pd.read_csv(EXISTING_FILE).dropna(how="all")
new_df = pd.read_csv(NEWDATA_FILE).dropna(how="all")


# clean lastname for comparison
existing_df["lastname_clean"] = existing_df["lastname"].apply(clean_str)
new_df["lastname_clean"] = new_df["lastname"].apply(clean_str)

# create address key using ONLY stnum + street
existing_df["addr_key"] = create_address_key(existing_df)
new_df["addr_key"] = create_address_key(new_df)


# =========================================================
# Build address -> folder map
# Exact address key gives folder if address already exists
# Street map gives folder for new house number on known street
# =========================================================

addr_folder_map = (
    existing_df
    .drop_duplicates("addr_key")
    .set_index("addr_key")["foldername"]
    .to_dict()
)

# street_folder_map = (
#     existing_df
#     .dropna(subset=["street"])
#     .drop_duplicates("street")
#     .assign(street_clean=lambda x: x["street"].apply(clean_str))
#     .set_index("street_clean")["foldername"]
#     .to_dict()
# )

# ==========
existing_df["street_clean"] = existing_df["street"].apply(clean_street)
new_df["street_clean"] = new_df["street"].apply(clean_street)

street_folder_map = (
    existing_df
    .drop_duplicates("street_clean")
    .set_index("street_clean")["foldername"]
    .to_dict()
)



# =======


# =========================================================
# 1. delta.csv: address does NOT exist in existing file
# =========================================================

existing_addr_keys = set(existing_df["addr_key"])

delta_df = new_df[
    ~new_df["addr_key"].isin(existing_addr_keys)
].copy()

# assign folder based on street
delta_df["street_clean"] = delta_df["street"].apply(clean_str)
delta_df["foldername"] = delta_df["street_clean"].map(street_folder_map)



delta_df = delta_df[
    ["foldername", "firstname", "lastname", "stnum", "street", "city", "state", "zip"]
]

delta_df.to_csv(DELTA_FILE, index=False)


# =========================================================
# 2. different_lastname.csv:
# Same stnum + street exists, but lastname is different
# =========================================================

existing_lookup = existing_df[
    ["addr_key", "lastname", "lastname_clean", "foldername"]
].rename(columns={
    "lastname": "existing_lastname",
    "lastname_clean": "existing_lastname_clean",
    "foldername": "existing_folder"
})

matched_df = new_df.merge(
    existing_lookup,
    on="addr_key",
    how="inner"
)

different_lastname_df = matched_df[
    matched_df["lastname_clean"] != matched_df["existing_lastname_clean"]
].copy()

different_lastname_df["foldername"] = different_lastname_df["existing_folder"]

different_lastname_df = different_lastname_df[
    [
        "foldername",
        "firstname",
        "lastname",
        "existing_lastname",
        "stnum",
        "street",
        "city",
        "state",
        "zip",
    ]
]

different_lastname_df.to_csv(DIFFERENT_LASTNAME_FILE, index=False)


print(f"Created {DELTA_FILE}")
print(delta_df)

print(f"\nCreated {DIFFERENT_LASTNAME_FILE}")
print(different_lastname_df)