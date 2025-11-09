import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection
from io import BytesIO
from datetime import datetime, timedelta

#from zoneinfo import ZoneInfo

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

#url = "https://docs.google.com/spreadsheets/d/1dK2tKeeRGAiVc6p0guapTITane-NckvuAFB3rrHu3k8/edit?usp=sharing"
url = "WarehouseAlldata"
urlp = "percobaan"


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

name= conn.read(worksheet=url)

#selected_date = st.8number_input("Tanggal:", min_value=1, max_value=30, step=1)


dff = pd.DataFrame(name)
# st.dataframe(data)

# File to store submissions
CSV_FILE = "submissions.csv"
# Set your admin password here
ADMIN_PASSWORD = "mumi99"

st.set_page_config(page_title="Mumi Sukamulya 2",
                   page_icon="✨",
                   layout="wide")

st.markdown(
        """
        <div class="transparent-container">
            <h1>✨ Mumi SKM 2</h1>
            <h4>
            يٰٓاَيُّهَا الَّذِيْنَ اٰمَنُوْٓا اِنْ تَنْصُرُوا اللّٰهَ يَنْصُرْكُمْ وَيُثَبِّتْ اَقْدَامَكُمْ <br><br> 💡"Wahai orang-orang yang beriman, jika kamu menolong (agama) Allah, niscaya Dia akan menolongmu dan meneguhkan kedudukanmu" QS 47 ayat 7 <br><br>INFO:<br>Optimization Update! (9 November 2025)
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
sheet_layout = "layoutwarehouse"

# Read with header=None so A1 = [0,0]
warehouse_df = conn.read(worksheet=sheet_warehouse, ttl=0)
layout_df = conn.read(worksheet=sheet_layout, ttl=0, usecols=None, header=None)

# Choose a row to edit
selected_row = st.number_input("Masukkan nomor baris:", min_value=1, max_value=len(warehouse_df), step=1)
idx = selected_row - 1

current_k = warehouse_df.iloc[idx, 10] if len(warehouse_df.columns) > 10 else ""
current_l = warehouse_df.iloc[idx, 11] if len(warehouse_df.columns) > 11 else ""

new_k = st.text_input("Kolom K:", str(current_k))
new_l = st.text_input("Kolom L:", str(current_l))

if st.button("💾 Simpan Perubahan"):
    warehouse_df.iat[idx, 10] = new_k
    warehouse_df.iat[idx, 11] = new_l
    conn.update(worksheet=sheet_warehouse, data=warehouse_df)

    # --- Correctly edit A1 (top-left) ---
    if new_l.strip() == "" or new_l.strip() == "-":
        layout_df.iat[0, 0] = "x"     # truly A1
    else:
        layout_df.iat[0, 0] = ""      # clear A1

    conn.update(worksheet=sheet_layout, data=layout_df)
    st.success("✅ layoutwarehouse!A1 diperbarui sesuai isi kolom L.")

status_map = {"Hadir": "H", "Ijin": "I", "Sakit": "S"}
status_list = ["-", "Hadir", "Ijin", "Sakit"]
selected_status = st.selectbox("Pilih Status:", status_list)
#selected_status = st.selectbox("Status Kehadiran:", list(status_map.keys()))
# Text input

    
if selected_status == "Ijin" and selected_name != "-":
        user_input = st.text_input("Ketik alasan: (contoh: ijin kerja)")
        if user_input.strip() == "":
            st.warning("Tidak boleh kosong ok!")
        else:
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
            else:
                df = pd.DataFrame(columns=["Text"])
        
                # Add new submission
            #new_row = pd.DataFrame({"Text":  f"{selected_name}" [user_input]})
            new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
            df = pd.concat([df, new_row], ignore_index=True)
        
                # Save to CSV
            df.to_csv(CSV_FILE, index=False)
elif selected_status == "Sakit" and selected_name != "-":
        user_input = st.text_input("Ketik alasan: (contoh: sakit demam)")
        if user_input.strip() == "":
            st.warning("Tidak boleh kosong ok!")
        else:
            # Load or create dataframe
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
            else:
                df = pd.DataFrame(columns=["Text"])
    
            # Add new submission
            new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
            df = pd.concat([df, new_row], ignore_index=True)
    
            # Save to CSV
            df.to_csv(CSV_FILE, index=False)
elif selected_status == "Hadir" and selected_name != "-":
        user_input = "Hadir"
        if user_input.strip() == "":
            st.warning("Tidak boleh kosong ok!")
        else:
            # Load or create dataframe
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
            else:
                df = pd.DataFrame(columns=["Text"])
    
            # Add new submission
            new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
            df = pd.concat([df, new_row], ignore_index=True)
    
            # Save to CSV
            df.to_csv(CSV_FILE, index=False)

if st.button("Submit Kehadiran"):
    # st.session_state["selected_name"] = "-"
    # st.session_state["selected_status"] = "-"
    # Find row for the selected name
    name_row = name.index[name.iloc[:, 1] == selected_name].tolist()
    # if user_input.strip() == "":
    #     st.warning("Tidak boleh kosong ok!")
    #else:
    if selected_name == "-":
        st.warning("⚠️ Silakan pilih nama terlebih dahulu.")
    else:
        if name_row:
            row_idx = name_row[0]
             # Column D=3 (0-based index), so date 1 = col 3
            col_idx = 3 + (selected_date - 1)
    
            if selected_status == "-":
                st.warning("Isi hadir/ijin/sakit ok")
                if selected_status == "Ijin":
                    if user_input == "" and selected_name == "-":
                        st.warning("Tidak boleh kosong ok!")
                    else:
                        pass
                if selected_status == "Sakit" :
                    if user_input == "" and selected_name == "-":
                        st.warning("Tidak boleh kosong ok!")
                    else:
                        pass
            else:
                name.iat[row_idx, col_idx] = status_map[selected_status]
            
                 # Update Google Sheet
                
                #st.success(f"✅ Kehadiran {selected_name} untuk tanggal {selected_date} tersimpan sebagai '{status_map[selected_status]}'")
                if selected_status == "Hadir" and user_input and selected_name != "-":
                    st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga kehadiran hari ini dapat memberikan kebarokahan dan ilmu yang bermanfaat")
                    conn.update(worksheet=url, data=name)
                elif selected_status == "Ijin" and user_input and selected_name != "-":
                    st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga allah paring banyak kelonggaran waktu sehingga dapat hadir dijadwal sambung selanjutnya")
                    conn.update(worksheet=url, data=name)
                elif selected_status == "Sakit" and user_input and selected_name != "-":
                    conn.update(worksheet=url, data=name)
                    st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga allah paring kesembuhan dan kesehatan yang barokah sehingga dapat hadir dijadwal sambung selanjutnya")
                elif selected_status == "Ijin" and user_input == "" and selected_name == "-":
                    st.warning("Tidak boleh kosong ok")
                elif selected_status == "Ijin" and user_input == "" and selected_name == "-":
                    st.warning("Tidak boleh kosong ok")
                elif selected_status == "Sakit" and user_input == "" and selected_name == "-":
                    st.warning("Tidak boleh kosong ok")
                
        else:
             st.error("Nama tidak ditemukan dalam daftar.")
            
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

# Admin section
st.subheader("Khusus Admin")

# Ask for password first
admin_password = st.text_input("Masukan password untuk menggunakan fitur:", type="password")

# If password is correct, show expander
if admin_password == ADMIN_PASSWORD:
    with st.expander("🧹 Clear data alasan"):
        if st.button("Clear Data"):
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
                st.success("✅ All data cleared successfully!")
            else:
                st.info("No data file found to clear.")
    with st.expander("🚀 Unduh Absen"):
        col1, col2 = st.columns(2)
        with col1:
            csv = dff.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ absen report",
                data=csv,
                file_name="absen report.csv",
                mime="text/csv")
                
        with col2:
            st.download_button(
                label="⬇️ alasan ijin/sakit",
                data=df_display.to_csv(index=False).encode('utf-8'),
                file_name="alasan ijin/sakit.csv",
                mime="text/csv")
    
else:
    if admin_password != "":
        st.error("❌ Incorrect password.")









































































































































