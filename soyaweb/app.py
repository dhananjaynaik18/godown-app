import streamlit as st
import pandas as pd
import requests
from datetime import date

st.set_page_config(
    page_title="DB Naik Soybean Godown Ledger",
    layout="wide"
)

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyy4UODezcMR7Yk4qLQuS7h5VuUY9fxQ7uQympKTEGCx59tFQHbZMmcL6efl_v8Zm8lJA/exec"


# =========================================================
# TEXT
# =========================================================

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
        "farmer_details": "Farmer Details",
        "farmer_name": "Farmer Name",
        "phone": "Phone Number",
        "sacks": "Number of Sacks",
        "weigh_details": "Weighbridge Details",
        "gross": "Gross Weight (Qtl)",
        "tare": "Tare Weight (Qtl)",
        "rate": "Rate (per Qtl) ₹",
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
        "username": "वापरकर्तानाव",
        "password": "पासवर्ड",
        "login_btn": "लॉग-इन करा",
        "logout_btn": "बाहेर पडा",
        "nav": "मेनू",
        "menu_dash": "डॅशबोर्ड",
        "menu_in": "नवीन खरेदी (आवक)",
        "menu_out": "नवीन विक्री (जावक)",
        "dash_header": "📊 आजचा गोदामाचा अहवाल",
        "total_sacks": "गोदामातील एकूण पोती",
        "total_wt": "एकूण वजन (क्विंटल)",
        "unpaid": "देय रक्कम",
        "farmer_details": "शेतकऱ्याचा तपशील",
        "farmer_name": "शेतकऱ्याचे नाव",
        "phone": "मोबाईल क्रमांक",
        "sacks": "पोत्यांची संख्या",
        "weigh_details": "वजन काट्याचा तपशील",
        "gross": "एकूण वजन (क्विंटल)",
        "tare": "रिकाम्या वाहनाचे वजन (क्विंटल)",
        "rate": "आजचा दर (प्रती क्विंटल) ₹",
        "status": "पैसे दिले/बाकी?",
        "save_btn": "माहिती जतन करा",
        "buyer_details": "व्यापारी / मिलचा तपशील",
        "buyer_name": "व्यापाऱ्याचे नाव",
        "truck": "ट्रक नंबर",
        "save_out": "विक्री जतन करा",
        "success": "माहिती यशस्वीरित्या नोंदवली गेली!"
    }
}


# =========================================================
# SESSION
# =========================================================

if "role" not in st.session_state:
    st.session_state["role"] = None

if "lang" not in st.session_state:
    st.session_state["lang"] = "English"


# =========================================================
# GOOGLE SHEET GET
# =========================================================

def get_google_data():

    response = requests.get(
        GOOGLE_SHEET_URL,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    inward = data.get("inward", [])
    outward = data.get("outward", [])

    return (
        pd.DataFrame(inward),
        pd.DataFrame(outward)
    )


# =========================================================
# GOOGLE SHEET POST
# =========================================================

def send_to_google(data):

    response = requests.post(
        GOOGLE_SHEET_URL,
        json=data,
        headers={
            "Content-Type": "application/json"
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# NUMBER HELPER
# =========================================================

def number_column(df, names):

    if df.empty:
        return 0.0

    for column in df.columns:

        clean_column = str(column).strip().lower()

        for name in names:

            if clean_column == name.lower():

                values = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

                return float(values.sum())

    return 0.0


# =========================================================
# LOGIN
# =========================================================

def login():

    st.session_state["lang"] = st.selectbox(
        "Language / भाषा",
        ["English", "Marathi"]
    )

    t = TEXT[st.session_state["lang"]]

    st.title(t["login_title"])

    with st.form("login_form"):

        username = st.text_input(t["username"])

        password = st.text_input(
            t["password"],
            type="password"
        )

        submit = st.form_submit_button(
            t["login_btn"]
        )

        if submit:

            if username == "dbnaik" and password == "797979":

                st.session_state["role"] = "admin"

                st.rerun()

            elif username == "staff" and password == "12345678":

                st.session_state["role"] = "worker"

                st.rerun()

            else:

                st.error("❌ Incorrect username or password")


# =========================================================
# LOGOUT
# =========================================================

def logout():

    st.session_state["role"] = None

    st.rerun()


# =========================================================
# MAIN APP
# =========================================================

def main_app():

    st.sidebar.selectbox(
        "Language / भाषा",
        ["English", "Marathi"],
        key="lang"
    )

    t = TEXT[st.session_state["lang"]]

    st.title(t["title"])

    st.sidebar.title(t["nav"])

    if st.session_state["role"] == "admin":

        menu_options = [
            t["menu_dash"],
            t["menu_in"],
            t["menu_out"]
        ]

    else:

        menu_options = [
            t["menu_in"]
        ]

    menu = st.sidebar.radio(
        "Go to:",
        menu_options
    )

    st.sidebar.markdown("---")

    if st.sidebar.button(t["logout_btn"]):

        logout()


# =====================================================
# DASHBOARD
# =====================================================

if menu == t["menu_dash"]:

    st.header(t["dash_header"])

    try:

        # Get latest data from Google Sheet
        inward_df, outward_df = get_google_data()

        # =================================================
        # CLEAN COLUMN NAMES
        # =================================================

        inward_df.columns = [
            str(c).strip()
            for c in inward_df.columns
        ]

        outward_df.columns = [
            str(c).strip()
            for c in outward_df.columns
        ]

        # =================================================
        # INWARD SACKS
        # =================================================

        inward_sacks = 0

        if not inward_df.empty:

            for column in inward_df.columns:

                if str(column).strip().lower() == "sacks":

                    inward_sacks = pd.to_numeric(
                        inward_df[column],
                        errors="coerce"
                    ).fillna(0).sum()

                    break

        # =================================================
        # OUTWARD SACKS
        # =================================================

        outward_sacks = 0

        if not outward_df.empty:

            for column in outward_df.columns:

                if str(column).strip().lower() == "sacks":

                    outward_sacks = pd.to_numeric(
                        outward_df[column],
                        errors="coerce"
                    ).fillna(0).sum()

                    break

        # =================================================
        # REMAINING SACKS
        # =================================================

        remaining_sacks = (
            inward_sacks - outward_sacks
        )

        # Prevent negative display
        if remaining_sacks < 0:
            remaining_sacks = 0


        # =================================================
        # INWARD WEIGHT
        # =================================================

        inward_weight = 0.0

        if not inward_df.empty:

            for column in inward_df.columns:

                column_name = (
                    str(column)
                    .strip()
                    .lower()
                    .replace("_", " ")
                )

                if column_name in [
                    "net",
                    "net weight"
                ]:

                    inward_weight = pd.to_numeric(
                        inward_df[column],
                        errors="coerce"
                    ).fillna(0).sum()

                    break


        # =================================================
        # OUTWARD WEIGHT
        # =================================================

        outward_weight = 0.0

        if not outward_df.empty:

            for column in outward_df.columns:

                column_name = (
                    str(column)
                    .strip()
                    .lower()
                    .replace("_", " ")
                )

                if column_name in [
                    "net",
                    "net weight"
                ]:

                    outward_weight = pd.to_numeric(
                        outward_df[column],
                        errors="coerce"
                    ).fillna(0).sum()

                    break


        # =================================================
        # REMAINING WEIGHT
        # =================================================

        remaining_weight = (
            inward_weight - outward_weight
        )

        if remaining_weight < 0:
            remaining_weight = 0


        # =================================================
        # CASH TO PAY
        # =================================================

        cash_to_pay = 0.0

        if not inward_df.empty:

            status_column = None
            total_column = None

            # Find Status column
            for column in inward_df.columns:

                column_name = (
                    str(column)
                    .strip()
                    .lower()
                )

                if column_name == "status":

                    status_column = column

                    break


            # Find Total column
            for column in inward_df.columns:

                column_name = (
                    str(column)
                    .strip()
                    .lower()
                    .replace("_", " ")
                )

                if column_name in [
                    "total",
                    "total amount"
                ]:

                    total_column = column

                    break


            # Calculate pending amount
            if (
                status_column is not None
                and total_column is not None
            ):

                status_values = (
                    inward_df[status_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                # Pending values
                pending_values = [
                    "pending",
                    "बाकी"
                ]

                pending_rows = (
                    status_values.isin(
                        pending_values
                    )
                )

                cash_to_pay = pd.to_numeric(
                    inward_df.loc[
                        pending_rows,
                        total_column
                    ],
                    errors="coerce"
                ).fillna(0).sum()


        # =================================================
        # DASHBOARD DISPLAY
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📦 Remaining Sacks",
                f"{int(remaining_sacks)}"
            )

        with col2:

            st.metric(
                "⚖️ Current Total Weight",
                f"{remaining_weight:.2f} Qtl"
            )

        with col3:

            st.metric(
                "💰 Cash to Pay",
                f"₹ {cash_to_pay:,.2f}"
            )


        # =================================================
        # DETAILS
        # =================================================

        st.markdown("---")

        with st.expander("🔎 Dashboard Calculation Details"):

            st.write(
                "Total Inward Sacks:",
                int(inward_sacks)
            )

            st.write(
                "Total Outward Sacks:",
                int(outward_sacks)
            )

            st.write(
                "Remaining Sacks:",
                int(remaining_sacks)
            )

            st.markdown("---")

            st.write(
                "Total Inward Weight:",
                f"{inward_weight:.2f} Qtl"
            )

            st.write(
                "Total Outward Weight:",
                f"{outward_weight:.2f} Qtl"
            )

            st.write(
                "Remaining Weight:",
                f"{remaining_weight:.2f} Qtl"
            )

            st.markdown("---")

            st.write(
                "Pending Cash:",
                f"₹ {cash_to_pay:,.2f}"
            )


    except Exception as e:

        st.error(
            "❌ Unable to calculate dashboard values."
        )

        st.code(str(e))


    # =====================================================
    # INWARD
    # =====================================================

    elif menu == t["menu_in"]:

        st.header(t["menu_in"])

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                t["farmer_details"]
            )

            entry_date = st.date_input(
                "Date",
                value=date.today()
            )

            farmer_name = st.text_input(
                t["farmer_name"]
            )

            phone = st.text_input(
                t["phone"]
            )

            sacks = st.number_input(
                t["sacks"],
                min_value=1,
                step=1
            )


        with col2:

            st.subheader(
                t["weigh_details"]
            )

            gross = st.number_input(
                t["gross"],
                min_value=0.0,
                step=0.1
            )

            tare = st.number_input(
                t["tare"],
                min_value=0.0,
                step=0.1
            )

            rate = st.number_input(
                t["rate"],
                min_value=0.0,
                step=50.0
            )

            status = st.selectbox(
                t["status"],
                [
                    "Paid",
                    "Pending",
                    "दिले",
                    "बाकी"
                ]
            )


        net_weight = gross - tare

        total_val = net_weight * rate

        st.success(
            f"⚖️ Net Weight: {net_weight:.2f} Qtl   |   "
            f"💰 Total: ₹ {total_val:,.2f}"
        )


        if st.button(t["save_btn"]):

            if (
                farmer_name
                and net_weight > 0
                and rate > 0
                and gross >= tare
            ):

                data = {

                    # VERY IMPORTANT
                    "type": "INWARD",

                    "date": str(entry_date),

                    "farmer_name": farmer_name,

                    "phone": phone,

                    "sacks": int(sacks),

                    "gross": float(gross),

                    "tare": float(tare),

                    "net": float(net_weight),

                    "rate": float(rate),

                    "total": float(total_val),

                    "status": status
                }

                try:

                    result = send_to_google(data)

                    if result.get("success"):

                        st.success(
                            "✅ Inward saved successfully!"
                        )

                        st.write(
                            "Google Sheet:",
                            result.get("sheet")
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Google Sheet Error"
                        )

                        st.code(
                            str(result)
                        )

                except Exception as e:

                    st.error(
                        "❌ Connection error"
                    )

                    st.code(str(e))

            else:

                st.warning(
                    "⚠️ Enter Farmer Name and valid weights/rate."
                )


    # =====================================================
    # OUTWARD
    # =====================================================

    elif menu == t["menu_out"]:

        st.header(t["menu_out"])

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                t["buyer_details"]
            )

            entry_date = st.date_input(
                "Date",
                value=date.today(),
                key="out_date"
            )

            buyer_name = st.text_input(
                t["buyer_name"]
            )

            truck_no = st.text_input(
                t["truck"]
            )

            sacks = st.number_input(
                t["sacks"],
                min_value=1,
                step=1,
                key="out_sacks"
            )


        with col2:

            st.subheader(
                "Loading Details"
            )

            gross = st.number_input(
                t["gross"],
                min_value=0.0,
                step=0.1,
                key="out_gross"
            )

            tare = st.number_input(
                t["tare"],
                min_value=0.0,
                step=0.1,
                key="out_tare"
            )

            rate = st.number_input(
                t["rate"],
                min_value=0.0,
                step=50.0,
                key="out_rate"
            )

            status = st.selectbox(
                t["status"],
                [
                    "Paid",
                    "Pending",
                    "दिले",
                    "बाकी"
                ],
                key="out_status"
            )


        net_weight = gross - tare

        total_val = net_weight * rate

        st.success(
            f"⚖️ Net Weight: {net_weight:.2f} Qtl   |   "
            f"💰 Sale: ₹ {total_val:,.2f}"
        )


        if st.button(t["save_out"]):

            if (
                buyer_name
                and net_weight > 0
                and rate > 0
                and gross >= tare
            ):

                data = {

                    # VERY IMPORTANT
                    "type": "OUTWARD",

                    "date": str(entry_date),

                    "buyer_name": buyer_name,

                    "truck": truck_no,

                    "sacks": int(sacks),

                    "gross": float(gross),

                    "tare": float(tare),

                    "net": float(net_weight),

                    "rate": float(rate),

                    "total": float(total_val),

                    "status": status
                }

                try:

                    result = send_to_google(data)

                    if result.get("success"):

                        st.success(
                            "✅ Outward saved successfully!"
                        )

                        st.write(
                            "Google Sheet:",
                            result.get("sheet")
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Google Sheet Error"
                        )

                        st.code(
                            str(result)
                        )

                except Exception as e:

                    st.error(
                        "❌ Connection error"
                    )

                    st.code(str(e))

            else:

                st.warning(
                    "⚠️ Enter Buyer Name and valid weights/rate."
                )


# =========================================================
# START
# =========================================================

if st.session_state.get("role"):

    main_app()

else:

    login()
