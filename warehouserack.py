import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection
from io import BytesIO
from datetime import datetime, timedelta
import re
#from zoneinfo import ZoneInfo

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

#url = "https://docs.google.com/spreadsheets/d/1dK2tKeeRGAiVc6p0guapTITane-NckvuAFB3rrHu3k8/edit?usp=sharing"
url = "WarehouseAlldata"
urlp = "percobaan"

@st.cache_data(ttl=30)
def load_sheet():
    """Read Google Sheet (cached for 60 seconds)."""
    return conn.read(worksheet=url)
#urll = "https://docs.google.com/spreadsheets/d/1dK2tKeeRGAiVc6p0guapTITane-NckvuAFB3rrHu3k8/edit?usp=sharing"
# sheet_id = "1dK2tKeeRGAiVc6p0guapTITane-NckvuAFB3rrHu3k8"
# excel_link = f"https://docs.google.com/spreadsheets/d/1dK2tKeeRGAiVc6p0guapTITane-NckvuAFB3rrHu3k8/export?format=xlsx"

conn = st.connection("gsheets", type=GSheetsConnection)

# percobaan= conn.read(worksheet=urlp)
# value_b7 = url.iat[6, 1] 
# urlp.iat[6, 9] = f"Komentar otomatis: {value_b7}"
# conn.update(worksheet=urlp, data=urlp)

#data = conn.read(spreadsheet=url, worksheet="1750077145")
#data = conn.read(worksheet=url)

name= load_sheet()

#selected_date = st.8number_input("Tanggal:", min_value=1, max_value=30, step=1)


dff = pd.DataFrame(name)
# st.dataframe(data)

# File to store submissions
CSV_FILE = "submissions.csv"
# Set your admin password here
ADMIN_PASSWORD = "mumi99"

st.set_page_config(page_title="Warehouse",
                   page_icon="✨",
                   layout="wide")

st.markdown(
        """
        <div class="transparent-container">
            <h1>✨ Rack Tracking System</h1>
            <h4>
            Warehouse<br>💡 QTM 2025 💡
    </h4>
    
        """,
        unsafe_allow_html=True
    )
now = datetime.now() - timedelta(hours=-7)

# Format nicely: day name, day-month-year, hour:minute:second
formatted_now = now.strftime("%A, %d %B %Y - %H:%M:%S")

st.markdown(f"### 🗺️ {formatted_now}")

# Use day of month for attendance
selected_date = now.day

# now_jakarta = datetime.now(tz=ZoneInfo("Asia/Jakarta"))
# formatted_now = now_jakarta.strftime("%A, %d %B %Y - %H:%M:%S")
# selected_date = now_jakarta.day

# Safely slice rows B6:B27 (column index 1 since A=0, B=1)

sheet_warehouse = "WarehouseAlldata"
sheet_layout = "layoutwarehouse2"

# rack_ranges = {
#     "U37": "U2:U4",         # vertical 3 cells
#     "T36": "W2:Y4",         # 3x3
#     "T35": "W6:Y8",
#     "S34": "W10:Y12",
#     "S33": "W14:Y16",
#     "R32": "W18:Y20",       # 3x5
#     "R31": "W22:Y24"
# }
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.session_state.clear()  # clear all session_state variables
    st.rerun()

st.header("✏️ Edit Berdasarkan PO, Kode, dan Material")

# --- Dropdown 1: PO ---
name_list = name.iloc[:, 7].dropna().astype(str).unique().tolist()
name_list.insert(0, "-")
selected_name = st.selectbox("Pilih PO:", name_list)

if selected_name != "-":
    filtered_rows = name[name.iloc[:, 7] == selected_name]

    # --- Dropdown 2: Kode ---
    option_list = filtered_rows.iloc[:, 5].dropna().astype(str).unique().tolist()
    option_list.insert(0, "-")
    selected_option = st.selectbox("Pilih Kode:", option_list)

    if selected_option != "-":
        kode_filtered = filtered_rows[filtered_rows.iloc[:, 5] == selected_option]

        # --- Dropdown 3: Material ---
        material_list = kode_filtered.iloc[:, 6].dropna().astype(str).unique().tolist()
        material_list.insert(0, "-")
        selected_material = st.selectbox("Pilih Material:", material_list)

        if selected_material != "-":
            item_filtered = kode_filtered[kode_filtered.iloc[:, 6] == selected_material]

            # --- Dropdown 4: Item ---
            item_list = item_filtered.iloc[:, 4].dropna().astype(str).unique().tolist()
            item_list.insert(0, "-")
            selected_item = st.selectbox("Pilih Item:", item_list)

            if selected_item != "-":
                # --- Get the target row ---
                row_index = item_filtered.index[item_filtered.iloc[:, 4] == selected_item].tolist()

                if row_index:
                    idx = row_index[0]

                    # --- Get current Rak & Kolom values ---
                    current_k = str(name.iloc[idx, 16]) if len(name.columns) > 16 else ""
                    current_l = str(name.iloc[idx, 17]) if len(name.columns) > 17 else ""

                    st.write("### Edit Rak dan Kolom")

                    # --- Dropdown for existing Rak values ---
                    rak_list = name.iloc[:, 16].dropna().astype(str).unique().tolist()
                    rak_list.insert(0, "-")
                    selected_rak_dropdown = st.selectbox("Pilih Rak (opsional):", rak_list, index=rak_list.index(current_k) if current_k in rak_list else 0)

                    # --- Dropdown for existing Kolom values ---
                    kolom_list = name.iloc[:, 17].dropna().astype(str).unique().tolist()
                    kolom_list.insert(0, "-")
                    selected_kolom_dropdown = st.selectbox("Pilih Kolom (opsional):", kolom_list, index=kolom_list.index(current_l) if current_l in kolom_list else 0)

                    # --- Manual edit fields ---
                    new_k = st.text_input("Atau tulis Rak baru:", selected_rak_dropdown if selected_rak_dropdown != "-" else current_k)
                    new_l = st.text_input("Atau tulis Kolom baru:", selected_kolom_dropdown if selected_kolom_dropdown != "-" else current_l)

                    # --- Clean Kolom automatically ---
                    if new_l.strip():
                        cleaned = re.sub(r"[-\s;]+", ",", new_l)
                        cleaned = cleaned.replace(",,", ",").strip(",")
                        parts = [p.strip() for p in cleaned.split(",") if p.strip()]
                        new_l = ",".join([f'"{p}"' for p in parts])

                    # --- Save button ---
                    if st.button("💾 Simpan Perubahan"):
                        name.iat[idx, 16] = new_k
                        name.iat[idx, 17] = new_l
                        conn.update(worksheet=sheet_warehouse, data=name)
                        st.success("✅ Data di WarehouseAlldata berhasil diperbarui!")



st.markdown("---")
st.header("🔍 Cari Berdasarkan Rak & Kolom")

# --- Dropdown for Rak (Kolom K) ---
rak_list = name.iloc[:, 16].dropna().astype(str).unique().tolist()
rak_list.insert(0, "-")
selected_rak = st.selectbox("Pilih Rak (Kolom K):", rak_list, key="rak_select")

# --- Filter Kolom list based on selected Rak ---
if selected_rak != "-":
    filtered_for_rak = name[name.iloc[:, 16] == selected_rak]
    kolom_list = filtered_for_rak.iloc[:, 17].dropna().astype(str).unique().tolist()
    kolom_list.insert(0, "-")
else:
    kolom_list = ["-"]

selected_kolom = st.selectbox("Pilih Kolom (Kolom L):", kolom_list, key="kolom_select")

# --- Show result button ---
if st.button("🔎 Tampilkan Data"):
    # 🧹 Clear old editing state before showing new data
    for key in ["result", "chosen_idx", "edit_fields"]:
        if key in st.session_state:
            del st.session_state[key]

    if selected_rak != "-" and selected_kolom != "-":
        result = name[(name.iloc[:, 16] == selected_rak) & (name.iloc[:, 17] == selected_kolom)]

        if not result.empty:
            st.session_state["result"] = result
            st.session_state["selected_rak"] = selected_rak
            st.session_state["selected_kolom"] = selected_kolom
            st.success(f"📍 Ditemukan {len(result)} data di Rak {selected_rak}, Kolom {selected_kolom}")
        else:
            st.warning("⚠️ Tidak ada data untuk Rak & Kolom tersebut.")


if "result" in st.session_state:
    result = st.session_state["result"]

    # Show table
    st.dataframe(result.iloc[:, [7, 5, 4, 6, 16, 17]].rename(
        columns={
            name.columns[7]: "PO",
            name.columns[5]: "Kode",
            name.columns[4]: "Item",
            name.columns[6]: "Material",
            name.columns[16]: "Rak",
            name.columns[17]: "Kolom",
        }
    ))

    # Choose which row to edit if multiple
    if len(result) > 1:
        idx_list = result.index.tolist()
        chosen_idx = st.selectbox("Pilih baris untuk diedit:", idx_list, key="edit_idx")
    else:
        chosen_idx = result.index.tolist()[0]

    st.session_state["chosen_idx"] = chosen_idx

    # Load current values once
    if "edit_fields" not in st.session_state:
        idx = chosen_idx
        st.session_state["edit_fields"] = {
            "po": str(name.iloc[idx, 7]),
            "kode": str(name.iloc[idx, 5]),
            "item": str(name.iloc[idx, 4]),
            "material": str(name.iloc[idx, 6]),
            "rak": str(name.iloc[idx, 16]),
            "kolom": str(name.iloc[idx, 17]),
        }

    edit = st.session_state["edit_fields"]

    # ✅ Dynamic unique key based on chosen index
    suffix = f"_{chosen_idx}"

    st.write("### ✏️ Edit Data di Rak & Kolom Ini")
    edit["po"] = st.text_input("PO:", edit["po"], key=f"po_edit{suffix}")
    edit["kode"] = st.text_input("Kode:", edit["kode"], key=f"kode_edit{suffix}")
    edit["item"] = st.text_input("Item:", edit["item"], key=f"item_edit{suffix}")
    edit["material"] = st.text_input("Material:", edit["material"], key=f"mat_edit{suffix}")
    edit["rak"] = st.text_input("Rak:", edit["rak"], key=f"rak_edit{suffix}")
    edit["kolom"] = st.text_input("Kolom:", edit["kolom"], key=f"kol_edit{suffix}")

    if st.button("💾 Simpan Perubahan (Rak & Kolom Ini)"):
        new_kolom = edit["kolom"].strip()
        if new_kolom:
            cleaned = re.sub(r"[-\s;]+", ",", new_kolom)
            cleaned = cleaned.replace(",,", ",").strip(",")
            parts = [p.strip() for p in cleaned.split(",") if p.strip()]
            new_kolom = ",".join([f'"{p}"' for p in parts])
            edit["kolom"] = new_kolom

        idx = st.session_state["chosen_idx"]
        name.iat[idx, 7] = edit["po"]
        name.iat[idx, 5] = edit["kode"]
        name.iat[idx, 4] = edit["item"]
        name.iat[idx, 6] = edit["material"]
        name.iat[idx, 16] = edit["rak"]
        name.iat[idx, 17] = edit["kolom"]

        conn.update(worksheet=sheet_warehouse, data=name)
        st.success("✅ Data berhasil diperbarui!")

        # Reset edit form after save
        st.session_state.pop("edit_fields", None)


        # refresh stored result to reflect saved changes (try to keep same filter if available)
        sel_rak = st.session_state.get("selected_rak")
        sel_kolom = st.session_state.get("selected_kolom")
        if sel_rak is not None and sel_kolom is not None:
            st.session_state["result"] = name[(name.iloc[:, 16] == sel_rak) & (name.iloc[:, 17] == sel_kolom)]
        else:
            # fallback: refresh result for current rak/kolom from the row we just saved
            st.session_state["result"] = name[(name.iloc[:, 16] == new_rak) & (name.iloc[:, 17] == nk)]

        # update the session widget values so UI shows saved values
        st.session_state["po_edit"] = str(name.iloc[idx, 7])
        st.session_state["kode_edit"] = str(name.iloc[idx, 5])
        st.session_state["item_edit"] = str(name.iloc[idx, 4])
        st.session_state["mat_edit"] = str(name.iloc[idx, 6])
        st.session_state["rak_edit"] = str(name.iloc[idx, 16])
        st.session_state["kol_edit"] = str(name.iloc[idx, 17])




# status_map = {"Hadir": "H", "Ijin": "I", "Sakit": "S"}
# status_list = ["-", "Hadir", "Ijin", "Sakit"]
# selected_status = st.selectbox("Pilih Status:", status_list)
#selected_status = st.selectbox("Status Kehadiran:", list(status_map.keys()))
# Text input

    
# if selected_status == "Ijin" and selected_name != "-":
#         user_input = st.text_input("Ketik alasan: (contoh: ijin kerja)")
#         if user_input.strip() == "":
#             st.warning("Tidak boleh kosong ok!")
#         else:
#             if os.path.exists(CSV_FILE):
#                 df = pd.read_csv(CSV_FILE)
#             else:
#                 df = pd.DataFrame(columns=["Text"])
        
#                 # Add new submission
#             #new_row = pd.DataFrame({"Text":  f"{selected_name}" [user_input]})
#             new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
#             df = pd.concat([df, new_row], ignore_index=True)
        
#                 # Save to CSV
#             df.to_csv(CSV_FILE, index=False)
# elif selected_status == "Sakit" and selected_name != "-":
#         user_input = st.text_input("Ketik alasan: (contoh: sakit demam)")
#         if user_input.strip() == "":
#             st.warning("Tidak boleh kosong ok!")
#         else:
#             # Load or create dataframe
#             if os.path.exists(CSV_FILE):
#                 df = pd.read_csv(CSV_FILE)
#             else:
#                 df = pd.DataFrame(columns=["Text"])
    
#             # Add new submission
#             new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
#             df = pd.concat([df, new_row], ignore_index=True)
    
#             # Save to CSV
#             df.to_csv(CSV_FILE, index=False)
# elif selected_status == "Hadir" and selected_name != "-":
#         user_input = "Hadir"
#         if user_input.strip() == "":
#             st.warning("Tidak boleh kosong ok!")
#         else:
#             # Load or create dataframe
#             if os.path.exists(CSV_FILE):
#                 df = pd.read_csv(CSV_FILE)
#             else:
#                 df = pd.DataFrame(columns=["Text"])
    
#             # Add new submission
#             new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
#             df = pd.concat([df, new_row], ignore_index=True)
    
#             # Save to CSV
#             df.to_csv(CSV_FILE, index=False)

# if st.button("Submit Kehadiran"):
#     # st.session_state["selected_name"] = "-"
#     # st.session_state["selected_status"] = "-"
#     # Find row for the selected name
#     name_row = name.index[name.iloc[:, 1] == selected_name].tolist()
#     # if user_input.strip() == "":
#     #     st.warning("Tidak boleh kosong ok!")
#     #else:
#     if selected_name == "-":
#         st.warning("⚠️ Silakan pilih nama terlebih dahulu.")
#     else:
#         if name_row:
#             row_idx = name_row[0]
#              # Column D=3 (0-based index), so date 1 = col 3
#             col_idx = 3 + (selected_date - 1)
    
#             if selected_status == "-":
#                 st.warning("Isi hadir/ijin/sakit ok")
#                 if selected_status == "Ijin":
#                     if user_input == "" and selected_name == "-":
#                         st.warning("Tidak boleh kosong ok!")
#                     else:
#                         pass
#                 if selected_status == "Sakit" :
#                     if user_input == "" and selected_name == "-":
#                         st.warning("Tidak boleh kosong ok!")
#                     else:
#                         pass
#             else:
#                 name.iat[row_idx, col_idx] = status_map[selected_status]
            
#                  # Update Google Sheet
                
#                 #st.success(f"✅ Kehadiran {selected_name} untuk tanggal {selected_date} tersimpan sebagai '{status_map[selected_status]}'")
#                 if selected_status == "Hadir" and user_input and selected_name != "-":
#                     st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga kehadiran hari ini dapat memberikan kebarokahan dan ilmu yang bermanfaat")
#                     conn.update(worksheet=url, data=name)
#                 elif selected_status == "Ijin" and user_input and selected_name != "-":
#                     st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga allah paring banyak kelonggaran waktu sehingga dapat hadir dijadwal sambung selanjutnya")
#                     conn.update(worksheet=url, data=name)
#                 elif selected_status == "Sakit" and user_input and selected_name != "-":
#                     conn.update(worksheet=url, data=name)
#                     st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga allah paring kesembuhan dan kesehatan yang barokah sehingga dapat hadir dijadwal sambung selanjutnya")
#                 elif selected_status == "Ijin" and user_input == "" and selected_name == "-":
#                     st.warning("Tidak boleh kosong ok")
#                 elif selected_status == "Ijin" and user_input == "" and selected_name == "-":
#                     st.warning("Tidak boleh kosong ok")
#                 elif selected_status == "Sakit" and user_input == "" and selected_name == "-":
#                     st.warning("Tidak boleh kosong ok")
                
#         else:
#              st.error("Nama tidak ditemukan dalam daftar.")
            
if os.path.exists(CSV_FILE):
    st.subheader("Kehadiran hari ini:")
    df_display = pd.read_csv(CSV_FILE)
    # Function to censor from second word onward
    def censor_from_second_word(text):
        words = str(text).split()
        if len(words) > 1:
            censored = [words[0]] + ["*" * len(w) for w in words[1:]]
            return " ".join(censored)
        else:
            return text

    df_display["Absen"] = df_display["Text"].apply(censor_from_second_word)
    st.dataframe(df_display[["Absen"]])
    
# Submit button
# if st.button("Submit"):
#     if user_input.strip() == "":
#         st.warning("Tidak boleh kosong ok!")
#     else:
#         # Load or create dataframe
#         if os.path.exists(CSV_FILE):
#             df = pd.read_csv(CSV_FILE)
#         else:
#             df = pd.DataFrame(columns=["Text"])

#         # Add new submission
#         new_row = pd.DataFrame({"Text": [user_input]})
#         df = pd.concat([df, new_row], ignore_index=True)

#         # Save to CSV
#         df.to_csv(CSV_FILE, index=False)
#         st.success("✅ جَزَاكُمُ اللهُ خَيْرًا")

# Display current submissions
# if os.path.exists(CSV_FILE):
#     st.subheader("Kehadiran hari ini:")
#     df_display = pd.read_csv(CSV_FILE)

#     # Function to censor from second word onward
#     def censor_from_second_word(text):
#         words = str(text).split()
#         if len(words) > 1:
#             censored = [words[0]] + ["*" * len(w) for w in words[1:]]
#             return " ".join(censored)
#         else:
#             return text

#     df_display["Absen"] = df_display["Text"].apply(censor_from_second_word)
#     st.dataframe(df_display[["Absen"]])


# Divider
st.markdown("---")

# # Admin section
# st.subheader("Khusus Admin")

# # Ask for password first
# admin_password = st.text_input("Masukan password untuk menggunakan fitur:", type="password")

# # If password is correct, show expander
# if admin_password == ADMIN_PASSWORD:
#     with st.expander("🧹 Clear data alasan"):
#         if st.button("Clear Data"):
#             if os.path.exists(CSV_FILE):
#                 os.remove(CSV_FILE)
#                 st.success("✅ All data cleared successfully!")
#             else:
#                 st.info("No data file found to clear.")
#     with st.expander("🚀 Unduh Absen"):
#         col1, col2 = st.columns(2)
#         with col1:
#             csv = dff.to_csv(index=False).encode("utf-8")
#             st.download_button(
#                 label="⬇️ absen report",
#                 data=csv,
#                 file_name="absen report.csv",
#                 mime="text/csv")
                
#         with col2:
#             st.download_button(
#                 label="⬇️ alasan ijin/sakit",
#                 data=df_display.to_csv(index=False).encode('utf-8'),
#                 file_name="alasan ijin/sakit.csv",
#                 mime="text/csv")
    
# else:
#     if admin_password != "":
#         st.error("❌ Incorrect password.")






























































































































































































