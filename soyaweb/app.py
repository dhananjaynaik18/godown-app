import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ==========================================
# 1. APP CONFIGURATION & DICTIONARY
# ==========================================
st.set_page_config(page_title="DB Naik Godown Ledger", layout="wide")
GOOGLE_SHEET_URL="https://script.google.com/macros/s/AKfycbz8T2n36X9K2oQ3DtaxyJcNg0ZY_n5ISZhQrmJ0Dm4c2eGbGw-TxD8CFgixyg8GGh8ORA/exec"

# Language Dictionary for Translation
TEXT = {
    "English": {
        "title": "📦 DB Naik Soybean Godown Ledger",
        "login_title": "🔒 DB Naik Godown Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "nav": "Navigation",
        "menu_dash": "Dashboard (Admin Only)",
        "menu_in": "New Purchase (Inward)",
        "menu_out": "New Dispatch (Outward)",
        "dash_header": "📊 Today's Snapshot",
        "total_sacks": "Total Sacks in Godown",
        "total_wt": "Current Total Weight (Qtl)",
        "unpaid": "Cash to Pay (Pending)",
        "recent_in": "🕒 Recent Purchases",
        "download_csv": "📥 Download Ledger (CSV)",
        "farmer_details": "Farmer Details",
        "farmer_name": "Farmer Name",
        "phone": "Phone Number",
        "sacks": "Number of Sacks",
        "weigh_details": "Weighbridge Details",
        "gross": "Gross Weight (Tractor + Soybean) in Qtl",
        "tare": "Tare Weight (Empty Tractor) in Qtl",
        "rate": "Today's Rate (per Qtl) in ₹",
        "status": "Payment Status",
        "save_btn": "SAVE ENTRY TO LEDGER",
        "buyer_details": "Buyer / Mill Details",
        "buyer_name": "Buyer Name",
        "truck": "Truck Number",
        "save_out": "SAVE DISPATCH",
        "success": "Entry saved successfully!"
    },
    "Marathi": {
        "title": "📦 डी.बी. नाईक सोयाबीन गोदाम खातेवही",
        "login_title": "🔒 गोदाम लॉग-इन",
        "username": "वापरकर्तानाव (Username)",
        "password": "पासवर्ड (Password)",
        "login_btn": "लॉग-इन करा",
        "logout_btn": "बाहेर पडा (Logout)",
        "nav": "मेनू",
        "menu_dash": "डॅशबोर्ड (फक्त मालकांसाठी)",
        "menu_in": "नवीन खरेदी (आवक)",
        "menu_out": "नवीन विक्री (जावक)",
        "dash_header": "📊 आजचा गोदामाचा अहवाल",
        "total_sacks": "गोदामातील एकूण पोती",
        "total_wt": "एकूण वजन (क्विंटल)",
        "unpaid": "देय रक्कम (बाकी)",
        "recent_in": "🕒 अलीकडील खरेदी",
        "download_csv": "📥 खातेवही डाउनलोड करा (CSV)",
        "farmer_details": "शेतकऱ्याचा तपशील",
        "farmer_name": "शेतकऱ्याचे नाव",
        "phone": "मोबाईल क्रमांक",
        "sacks": "पोत्यांची संख्या",
        "weigh_details": "वजन काट्याचा तपशील",
        "gross": "एकूण वजन (क्विंटलमध्ये)",
        "tare": "रिकाम्या वाहनाचे वजन (क्विंटल)",
        "rate": "आजचा दर (प्रती क्विंटल) ₹",
        "status": "पैसे दिले/बाकी?",
        "save_btn": "माहिती जतन करा (Save)",
        "buyer_details": "व्यापारी / मिलचा तपशील",
        "buyer_name": "व्यापाऱ्याचे नाव",
        "truck": "ट्रक नंबर",
        "save_out": "विक्री जतन करा",
        "success": "माहिती यशस्वीरित्या नोंदवली गेली!"
    }
}

# ==========================================
# 2. DATABASE & AUTHENTICATION SETUP
# ==========================================
def init_db():
    conn = sqlite3.connect("godown_inventory.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inward_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, farmer_name TEXT, 
        phone TEXT, sacks INTEGER, gross_weight REAL, tare_weight REAL, 
        net_weight REAL, rate REAL, total_amount REAL, status TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outward_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, buyer_name TEXT, 
        truck_no TEXT, sacks INTEGER, net_weight REAL, rate REAL, total_amount REAL
    )""")
    conn.commit()
    return conn

if "role" not in st.session_state:
    st.session_state["role"] = None
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

def login():
    st.session_state["lang"] = st.selectbox("Language / भाषा", ["English", "Marathi"])
    t = TEXT[st.session_state["lang"]]
    
    st.title(t["login_title"])
    st.write("Admin (dbnaik/797979) | Worker (staff/12345678)")
    
    with st.form("login_form"):
        username = st.text_input(t["username"])
        password = st.text_input(t["password"], type="password")
        submit = st.form_submit_button(t["login_btn"])
        
        if submit:
            if username == "dbnaik" and password == "797979":
                st.session_state["role"] = "admin"
                st.rerun()
            elif username == "staff" and password == "12345678":
                st.session_state["role"] = "worker"
                st.rerun()
            else:
                st.error("❌ Incorrect Details")

def logout():
    st.session_state["role"] = None
    st.rerun()

# ==========================================
# 3. MAIN APP FUNCTION
# ==========================================
def main_app():
    conn = init_db()
    cursor = conn.cursor()
    
    # Language selector inside app
    st.sidebar.selectbox("Language / भाषा", ["English", "Marathi"], key="lang")
    t = TEXT[st.session_state["lang"]]
    
    st.title(t["title"])

    # Sidebar Navigation based on Role
    st.sidebar.title(t["nav"])
    
    if st.session_state["role"] == "admin":
        menu_options = [t["menu_dash"], t["menu_in"], t["menu_out"]]
    else:
        # Workers cannot see the dashboard or outward stock
        menu_options = [t["menu_in"]]
        
    menu = st.sidebar.radio("Go to:", menu_options)
    
    st.sidebar.markdown("---")
    if st.sidebar.button(t["logout_btn"]):
        logout()

    # --- DASHBOARD (ADMIN ONLY) ---
    if menu == t["menu_dash"]:
        st.header(t["dash_header"])
        
        in_df = pd.read_sql("SELECT * FROM inward_stock", conn)
        out_df = pd.read_sql("SELECT * FROM outward_stock", conn)

        # Math Calculations
        total_in_weight = in_df["net_weight"].sum() if not in_df.empty else 0.0
        total_out_weight = out_df["net_weight"].sum() if not out_df.empty else 0.0
        current_weight = total_in_weight - total_out_weight

        total_in_sacks = in_df["sacks"].sum() if not in_df.empty else 0
        total_out_sacks = out_df["sacks"].sum() if not out_df.empty else 0
        current_sacks = total_in_sacks - total_out_sacks
        
        unpaid_cash = in_df[in_df["status"].isin(["Pending", "बाकी"])]["total_amount"].sum() if not in_df.empty else 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric(t["total_sacks"], f"{current_sacks}")
        col2.metric(t["total_wt"], f"{current_weight:.2f}")
        col3.metric(t["unpaid"], f"₹ {unpaid_cash:,.2f}")

        st.markdown("---")
        
        # Admin Download Feature
        if not in_df.empty:
            csv = in_df.to_csv(index=False).encode('utf-8')
            st.download_button(label=t["download_csv"], data=csv, file_name='godown_ledger.csv', mime='text/csv')

        st.subheader(t["recent_in"])
        if not in_df.empty:
            st.dataframe(in_df.tail(10)[["date", "farmer_name", "sacks", "net_weight", "total_amount", "status"]], use_container_width=True)

    # --- NEW PURCHASE (INWARD) ---
    elif menu == t["menu_in"]:
        st.header(t["menu_in"])
        
        with st.form("purchase_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(t["farmer_details"])
                entry_date = st.date_input("Date", value=date.today())
                farmer_name = st.text_input(t["farmer_name"])
                phone = st.text_input(t["phone"])
                sacks = st.number_input(t["sacks"], min_value=1, step=1)
                
            with col2:
                st.subheader(t["weigh_details"])
                gross = st.number_input(t["gross"], min_value=0.0, step=0.1)
                tare = st.number_input(t["tare"], min_value=0.0, step=0.1)
                rate = st.number_input(t["rate"], min_value=0.0, step=50.0)
                status = st.selectbox(t["status"], ["Paid", "Pending", "दिले", "बाकी"])

            st.markdown("---")
            net_weight = gross - tare
            total_val = net_weight * rate
            st.info(f"Net Weight: {net_weight:.2f} Qtl | Amount: ₹{total_val:,.2f}")

            if st.form_submit_button(t["save_btn"]):
                if farmer_name and net_weight > 0 and rate > 0:
                    cursor.execute("""
                    INSERT INTO inward_stock (date, farmer_name, phone, sacks, gross_weight, tare_weight, net_weight, rate, total_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (str(entry_date), farmer_name, phone, sacks, gross, tare, net_weight, rate, total_val, status))
                    conn.commit()
                    st.success(t["success"])

    # --- NEW DISPATCH (OUTWARD - ADMIN ONLY) ---
    elif menu == t["menu_out"]:
        st.header(t["menu_out"])
        
        with st.form("dispatch_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(t["buyer_details"])
                entry_date = st.date_input("Date", value=date.today())
                buyer_name = st.text_input(t["buyer_name"])
                truck_no = st.text_input(t["truck"])
                
            with col2:
                st.subheader("Loading Details")
                sacks = st.number_input(t["sacks"], min_value=1, step=1)
                net_weight = st.number_input("Net Weight (Qtl)", min_value=0.0, step=0.1)
                rate = st.number_input(t["rate"], min_value=0.0, step=50.0)

            st.markdown("---")
            total_val = net_weight * rate
            
            if st.form_submit_button(t["save_out"]):
                if buyer_name and net_weight > 0:
                    cursor.execute("""
                    INSERT INTO outward_stock (date, buyer_name, truck_no, sacks, net_weight, rate, total_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (str(entry_date), buyer_name, truck_no, sacks, net_weight, rate, total_val))
                    conn.commit()
                    st.success(t["success"])

# ==========================================
# 4. ROUTING LOGIC
# ==========================================
if st.session_state.get("role"):
    main_app()
else:
    login()
