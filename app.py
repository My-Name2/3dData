import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
except ModuleNotFoundError:
    st.error("Plotly is not installed. Add plotly to requirements.txt, then reboot the app.")
    st.code("streamlit\npandas\nnumpy\nplotly", language="text")
    st.stop()

st.set_page_config(page_title="3D Point Space Explorer", layout="wide")

st.title("3D / 4D Point Space Explorer")
st.write(
    "Upload a CSV, choose whether the first row is headers, edit the data, "
    "then map numeric columns into 3D space. Text columns like ticker can be used as labels."
)

uploaded = st.file_uploader("Upload CSV", type=["csv"])

first_row_headers = st.checkbox("First row contains column names", value=True)
first_col_id = st.checkbox("First column is ticker / ID", value=True)

if uploaded is not None:
    if first_row_headers:
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_csv(uploaded, header=None)
        if first_col_id:
            df.columns = ["ticker"] + [f"var{i}" for i in range(1, df.shape[1])]
        else:
            df.columns = [f"var{i}" for i in range(1, df.shape[1] + 1)]
else:
    df = pd.DataFrame({
        "ticker": ["AAPL", "MSFT", "GOOG"],
        "sector": ["Technology", "Technology", "Communication Services"],
        "consistencyscoreadjusted": [0.82, 0.77, 0.70],
        "mktcap": [3000000000000, 2800000000000, 2200000000000],
        "averagepositive": [0.55, 0.50, 0.48],
        "averagepositivecfos": [0.61, 0.58, 0.54],
    })

st.subheader("Data")
df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Keep obvious ID/text columns as text. Convert the rest to numeric only when possible.
id_like_cols = ["ticker", "id", "name", "symbol", "sector", "industry", "subindustry"]

for col in df.columns:
    if col.lower() not in id_like_cols:
        converted = pd.to_numeric(df[col], errors="coerce")

        # Only replace the column if conversion produced at least one real number.
        # This prevents text/category columns from getting destroyed.
        if converted.notna().any():
            df[col] = converted

# Add log market cap if mktcap exists.
if "mktcap" in df.columns and pd.api.types.is_numeric_dtype(df["mktcap"]):
    df["log_mktcap"] = np.log1p(df["mktcap"].clip(lower=0))

numeric_cols = df.select_dtypes(include="number").columns.tolist()
all_cols = df.columns.tolist()
text_cols = [c for c in all_cols if c not in numeric_cols]

if len(numeric_cols) < 3:
    st.warning("You need at least 3 numeric columns for a 3D chart.")
    st.stop()

st.subheader("Chart controls")

c1, c2, c3 = st.columns(3)

with c1:
    x_col = st.selectbox("X axis", numeric_cols)
with c2:
    y_col = st.selectbox("Y axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
with c3:
    z_col = st.selectbox("Z axis", numeric_cols, index=2 if len(numeric_cols) > 2 else 0)

c4, c5, c6, c7 = st.columns(4)

with c4:
    color_col = st.selectbox(
        "Color / 4th dimension",
        ["None"] + all_cols,
        help="Can be numeric like market cap, or text like sector/cluster.",
    )

with c5:
    size_col = st.selectbox("Bubble size", ["None"] + numeric_cols)

with c6:
    default_label = "ticker" if "ticker" in text_cols else "None"
    label_col = st.selectbox(
        "Point label",
        ["None"] + text_cols,
        index=(["None"] + text_cols).index(default_label) if default_label in (["None"] + text_cols) else 0,
    )

with c7:
    show_text_labels = st.checkbox(
        "Show labels on chart",
        value=False,
        help="If off, labels still appear when you hover.",
    )

plot_df = df.dropna(subset=[x_col, y_col, z_col]).copy()

if plot_df.empty:
    st.warning("No usable rows after removing missing X/Y/Z values.")
    st.stop()

size_arg = None
if size_col != "None":
    plot_df["_size"] = pd.to_numeric(plot_df[size_col], errors="coerce").fillna(0).clip(lower=0)
    if plot_df["_size"].max() > 0:
        size_arg = "_size"

hover_name = None
if label_col != "None":
    hover_name = label_col
elif "ticker" in plot_df.columns:
    hover_name = "ticker"

fig = px.scatter_3d(
    plot_df,
    x=x_col,
    y=y_col,
    z=z_col,
    color=None if color_col == "None" else color_col,
    size=size_arg,
    hover_name=hover_name,
    hover_data=[c for c in plot_df.columns if not c.startswith("_")],
    title="3D Point Space",
)

if show_text_labels and label_col != "None":
    fig.update_traces(
        mode="markers+text",
        text=plot_df[label_col].astype(str),
        textposition="top center",
    )

fig.update_traces(marker=dict(opacity=0.85))
fig.update_layout(height=750)

st.plotly_chart(fig, use_container_width=True)

st.download_button(
    "Download edited CSV",
    df.to_csv(index=False),
    file_name="edited_point_space_data.csv",
    mime="text/csv",
)

st.download_button(
    "Download interactive HTML chart",
    fig.to_html(include_plotlyjs="cdn"),
    file_name="point_space_3d.html",
    mime="text/html",
)
