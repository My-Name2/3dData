# 3D / 4D Point Space Explorer

A simple Streamlit app for uploading or typing data and viewing it as a draggable 3D point-space chart.

## Required files

Upload these directly to the root of your GitHub repo:

```text
app.py
requirements.txt
```

This README is optional.

## Streamlit Cloud setup

Main file path:

```text
app.py
```

## CSV upload behavior

The app asks:

- First row contains column names
- First column is ticker / ID

If your CSV has no headers, the app creates names like:

```text
ticker, var1, var2, var3
```

## Suggested chart mapping

- X = averagepositive
- Y = averagepositivecfos
- Z = consistencyscoreadjusted
- Bubble size = log_mktcap
