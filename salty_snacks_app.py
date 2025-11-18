import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------
# Load & Clean Data
# -------------------------------------------
@st.cache_data
def load_data():
    # Use your working file path
    df = pd.read_excel("/Users/joseph/Downloads/Salty Snack Market Data Fall 2025.xlsx")

    # Filter to UPC level only
    df_upc = df[df["Product Level"] == "UPC"].copy()

    # Remove variety packs
    df_upc = df_upc[~df_upc["Subcategory"].str.contains("VARIETY PACKS", case=False, na=False)]

    # Remove non-product FRITO LAY items
    df_upc = df_upc[df_upc["Brand"].str.upper() != "FRITO LAY"]

    # Convert distribution to numeric
    df_upc["% of Stores Selling"] = pd.to_numeric(df_upc["% of Stores Selling"], errors="coerce")

    # Remove low-distribution items (<10%)
    df_upc = df_upc[df_upc["% of Stores Selling"] >= 10]

    # Clean numeric fields
    velocity = "Average Weekly Units Per Store Selling Per Item"
    dist = "% of Stores Selling"
    df_upc[velocity] = pd.to_numeric(df_upc[velocity], errors="coerce")
    df_upc[dist] = pd.to_numeric(df_upc[dist], errors="coerce")

    # Sales Strength Metric
    df_upc["Sales_Strength"] = df_upc[velocity] * (df_upc[dist] / 100)

    return df_upc, velocity

# Load data
df_upc, velocity_col = load_data()

# -------------------------------------------
# Sidebar Controls
# -------------------------------------------
st.sidebar.title("Salty Snack Analytics Dashboard")

st.sidebar.subheader("Top Categories (Quick Select)")

top_cat = st.sidebar.radio(
    "Choose a top category:",
    [
        "SS POTATO CHIPS",
        "SS TORTILLA & CORN CHIPS",
        "SS PUFFED SNACKS & STRAWS"
    ],
    index=0
)

st.sidebar.subheader("Or choose any subcategory:")
subcategory_list = sorted(df_upc["Subcategory"].unique())
selected_subcategory = st.sidebar.selectbox("All Subcategories:", subcategory_list)

# If user picks from the quick-select radio, it overrides the dropdown
final_subcategory = top_cat if top_cat in subcategory_list else selected_subcategory

# Metric selector
metric = st.sidebar.selectbox("Metric:", ["Velocity", "Sales Strength"])
metric_col = "Sales_Strength" if metric == "Sales Strength" else velocity_col

# -------------------------------------------
# Filter Data
# -------------------------------------------
subset = df_upc[df_upc["Subcategory"] == final_subcategory]
top10 = subset.sort_values(by=metric_col, ascending=False).head(10)

# -------------------------------------------
# Display UI
# -------------------------------------------
st.title("Salty Snack Analytics Dashboard")
st.subheader(f"Top 10 Products in {selected_subcategory} by {metric}")

# -------- CHART --------
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(top10["Description"].astype(str), top10[metric_col])
plt.xticks(rotation=70, ha="right")
ax.set_ylabel(metric)
ax.set_title(f"Top 10 {selected_subcategory} Products")
st.pyplot(fig)

# -------- TABLE --------
st.write("### Product Table")
st.dataframe(top10[["Brand", "Description", metric_col, "% of Stores Selling"]])

# -------- SUMMARY --------
st.write("---")
best = top10.iloc[0]
st.write(f"### ⭐ Best Performer in {selected_subcategory}")
st.write(f"**Product:** {best['Brand']} – {best['Description']}")
st.write(f"**{metric}:** {best[metric_col]:.2f}")
st.write(f"**Distribution:** {best['% of Stores Selling']}%")
