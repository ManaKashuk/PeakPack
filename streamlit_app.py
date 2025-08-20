import streamlit as st
import pandas as pd
import zipfile
import io
import os

st.title("XCMS Online Upload Packager")

st.markdown("""
This app helps you prepare **raw LC-MS data** and parameter metadata
for direct upload to [XCMS Online](https://xcmsonline.scripps.edu/).
""")

# --- File uploader
uploaded_files = st.file_uploader(
    "Upload LC-MS files (mzML / mzXML / NetCDF)",
    type=["mzML", "mzXML", "cdf", "CDF"],
    accept_multiple_files=True
)

# --- Presets
preset = st.selectbox(
    "Choose an instrument/chromatography preset",
    ["UHPLC-Orbitrap (default)", "HILIC-QTOF (default)", "Generic LC-MS"]
)

# --- Default parameters
params = {
    "UHPLC-Orbitrap (default)": {"ppm": 3, "peakwidth": "5,20", "snthresh": 10, "bw": 5, "mzwid": 0.015, "minfrac": 0.5},
    "HILIC-QTOF (default)": {"ppm": 15, "peakwidth": "10,60", "snthresh": 8, "bw": 10, "mzwid": 0.025, "minfrac": 0.5},
    "Generic LC-MS": {"ppm": 25, "peakwidth": "5,40", "snthresh": 6, "bw": 5, "mzwid": 0.02, "minfrac": 0.3},
}

selected_params = params[preset]

st.markdown("### Processing Parameters")
ppm = st.number_input("ppm", value=selected_params["ppm"])
peakwidth = st.text_input("Peak Width (min,max)", value=selected_params["peakwidth"])
snthresh = st.number_input("Signal-to-noise threshold", value=selected_params["snthresh"])
bw = st.number_input("Bandwidth (bw)", value=selected_params["bw"])
mzwid = st.number_input("mzwid", value=selected_params["mzwid"])
minfrac = st.number_input("minfrac", value=selected_params["minfrac"])

# --- Metadata form
st.markdown("### Sample Metadata")
metadata = []
if uploaded_files:
    for f in uploaded_files:
        sample_class = st.text_input(f"Class for {f.name}", value="Group1")
        batch = st.text_input(f"Batch for {f.name}", value="1")
        metadata.append({"filename": f.name, "class": sample_class, "batch": batch})

# --- ZIP export
if st.button("Create Upload Package"):
    if not uploaded_files:
        st.error("Please upload at least one file.")
    else:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            # Save metadata manifest
            manifest = pd.DataFrame(metadata)
            manifest_csv = manifest.to_csv(index=False)
            z.writestr("manifest.csv", manifest_csv)

            # Save params
            param_text = f"""XCMS Parameters:
Preset: {preset}
ppm: {ppm}
peakwidth: {peakwidth}
snthresh: {snthresh}
bw: {bw}
mzwid: {mzwid}
minfrac: {minfrac}
"""
            z.writestr("xcms_parameters.txt", param_text)

            # Add raw files
            for f in uploaded_files:
                z.writestr(f.name, f.getbuffer())

        st.download_button(
            label="Download Upload Package (ZIP)",
            data=buffer.getvalue(),
            file_name="xcms_upload_package.zip",
            mime="application/zip"
        )
