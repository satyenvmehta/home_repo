import time
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from sklearn.cluster import AgglomerativeClustering

# --- STEP 1: LOAD & PREPARE DATA ---
# Let's say your starting DataFrame is 'df'
data = {
    'street_num': [100, 150, 4500, 4550, 9000],
    'street_name': ['Main St', 'Main St', 'Broad St', 'Broad St', 'Oak Rd'],
    'city': ['Anytown', 'Anytown', 'Anytown', 'Anytown', 'Anytown'],
    'state': ['NJ', 'NJ', 'NJ', 'NJ', 'NJ'],
    'zip_code': ['08824', '08824', '08824', '08824', '08852']
}

data = {
    'street_num': [100, 340, 15, 5, 25],
    'street_name': ['Municipal Blvd', 'Wood Ave', 'Green St', 'Middlesex Blvd', 'Green St'],
    'city': ['Edison', 'Edison', 'Woodbridge', 'Plainsboro', 'Woodbridge'],
    'state': ['NJ', 'NJ', 'NJ', 'NJ', 'NJ'],
    'zip_code': ['08817', '08820', '07095', '08536', '07095']
}
df = pd.DataFrame(data)

# Combine fields into a clean, single-line address string for the geocoder
df['full_address'] = (
    df['street_num'].astype(str) + " " +
    df['street_name'] + ", " +
    df['city'] + ", " +
    df['state'] + " " +
    df['zip_code'].astype(str)
)

# --- STEP 2: GEOCODING ---
# Initialize the geocoder. Be sure to name your user_agent something unique.
geolocator = Nominatim(user_agent="my_town_courier_router")

# Limit requests to 1 per second to strictly follow OpenStreetMap's usage policy
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

print("Starting geocoding (this may take a moment due to rate limits)...")
df['location'] = df['full_address'].apply(geocode)

# Extract lat/lon floats from the location objects
df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

# Clean up: Drop rows that failed to geocode so they don't break the clustering step
df_clean = df.dropna(subset=['latitude', 'longitude']).copy()


# --- STEP 3: STRICT 2-MILE CLUSTERING ---
# 1. Convert coordinates to radians
coords = np.radians(df_clean[['latitude', 'longitude']].values)

# 2. Convert 2 miles to radians (using Earth's radius of ~3956 miles)
two_miles_in_radians = 2 / 3956.0

# 3. Fit Agglomerative Clustering (Complete Linkage)
from sklearn.metrics.pairwise import haversine_distances
distance_matrix = haversine_distances(coords)
# Linkage='complete' forces the *maximum* distance between any two cluster members to remain
# strictly below the 2-mile threshold.
cluster_model = AgglomerativeClustering(
    metric='precomputed',
    linkage='complete',
    distance_threshold=two_miles_in_radians,
    n_clusters=None # Required when setting a distance threshold instead of a fixed k
)
df_clean['Area_Group_ID'] = cluster_model.fit_predict(distance_matrix)

# df_clean['Area_Group_ID'] = cluster_model.fit_predict(coords)

# Clean up helper columns before saving
final_df = df_clean.drop(columns=['location'])
print("\nClustering complete! Here is your grouped data:")
print(final_df[['full_address', 'Area_Group_ID']])