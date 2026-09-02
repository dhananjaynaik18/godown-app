import streamlit as st
import pandas as pd
import requests
from datetime import date


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="DB Naik Soybean Godown Ledger",
    layout="wide"
)


# =========================================================
# GOOGLE APPS SCRIPT URL
# =========================================================

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbz8T2n36X9K2oQ3DtaxyJcNg0ZY_n5ISZhQrmJ0Dm4c2eGbGw-TxD8CFgixyg8GGh8ORA/exec"


# =========================================================
# TEXT / LANGUAGE
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

        "total_sacks": "Remaining Sacks in Godown",

        "total_wt": "Current Total Weight (Qtl)",

        "unpaid": "Cash to Pay (Pending)",

        "farmer_details": "Farmer Details",

        "farmer_name": "Farmer Name",

        "phone": "Phone Number",

        "sacks": "Number of Sacks",

        "weigh_details": "Weighbridge Details",

        "gross": "Gross Weight (Qtl)",

        "tare": "Tare Weight (Qtl)",

        "rate": "Rate (per Qtl) in ₹",

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

        "total_sacks": "गोदामातील शिल्लक पोती",

        "total_wt": "एकूण शिल्लक वजन (क्विंटल)",

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
# SESSION STATE
# =========================================================

if "role" not in st.session_state:

    st.session_state["role"] = None


if "lang" not in st.session_state:

    st.session_state["lang"] = "English"


# =========================================================
# GET DATA FROM GOOGLE SHEETS
# =========================================================

def get_google_data():

    response = requests.get(
        GOOGLE_SHEET_URL,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    inward_data = data.get("inward", [])

    outward_data = data.get("outward", [])

    inward_df = pd.DataFrame(inward_data)

    outward_df = pd.DataFrame(outward_data)

    return inward_df, outward_df


# =========================================================
# SEND DATA TO GOOGLE SHEETS
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
# FIND COLUMN
# =========================================================

def find_column(df, possible_names):

    if df.empty:

        return None

    for column in df.columns:

        clean_column = (
            str(column)
            .strip()
            .lower()
            .replace("_", " ")
        )

        for name in possible_names:

            clean_name = (
                str(name)
                .strip()
                .lower()
                .replace("_", " ")
            )

            if clean_column == clean_name:

                return column

    return None


# =========================================================
# GET NUMERIC TOTAL
# =========================================================

def get_numeric_total(df, possible_names):

    if df.empty:

        return 0.0

    column = find_column(
        df,
        possible_names
    )

    if column is None:

        return 0.0

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0)

    return float(values.sum())


# =========================================================
# LOGIN
# =========================================================

def login():

    st.session_state["lang"] = st.selectbox(
        "Language / भाषा",
        [
            "English",
            "Marathi"
        ]
    )

    t = TEXT[
        st.session_state["lang"]
    ]

    st.title(
        t["login_title"]
    )

    with st.form("login_form"):

        username = st.text_input(
            t["username"]
        )

        password = st.text_input(
            t["password"],
            type="password"
        )

        submit = st.form_submit_button(
            t["login_btn"]
        )

        if submit:

            if (
                username == "dbnaik"
                and password == "797979"
            ):

                st.session_state["role"] = "admin"

                st.rerun()


            elif (
                username == "staff"
                and password == "12345678"
            ):

                st.session_state["role"] = "worker"

                st.rerun()


            else:

                st.error(
                    "❌ Incorrect username or password"
                )


# =========================================================
# LOGOUT
# =========================================================

def logout():

    st.session_state["role"] = None

    st.rerun()


# =========================================================
# MAIN APPLICATION
# =========================================================

def main_app():

    st.sidebar.selectbox(
        "Language / भाषा",
        [
            "English",
            "Marathi"
        ],
        key="lang"
    )

    t = TEXT[
        st.session_state["lang"]
    ]

    st.title(
        t["title"]
    )

    st.sidebar.title(
        t["nav"]
    )


    # =====================================================
    # MENU
    # =====================================================

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


    if st.sidebar.button(
        t["logout_btn"]
    ):

        logout()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == t["menu_dash"]:

        st.header(
            t["dash_header"]
        )


        try:

            # ---------------------------------------------
            # GET GOOGLE SHEET DATA
            # ---------------------------------------------

            inward_df, outward_df = get_google_data()


            # ---------------------------------------------
            # CLEAN COLUMN NAMES
            # ---------------------------------------------

            if not inward_df.empty:

                inward_df.columns = [

                    str(column).strip()

                    for column in inward_df.columns

                ]


            if not outward_df.empty:

                outward_df.columns = [

                    str(column).strip()

                    for column in outward_df.columns

                ]


            # ---------------------------------------------
            # TOTAL INWARD SACKS
            # ---------------------------------------------

            total_inward_sacks = get_numeric_total(
                inward_df,
                [
                    "Sacks",
                    "sacks"
                ]
            )


            # ---------------------------------------------
            # TOTAL OUTWARD SACKS
            # ---------------------------------------------

            total_outward_sacks = get_numeric_total(
                outward_df,
                [
                    "Sacks",
                    "sacks"
                ]
            )


            # ---------------------------------------------
            # REMAINING SACKS
            # ---------------------------------------------

            remaining_sacks = (
                total_inward_sacks
                - total_outward_sacks
            )


            # ---------------------------------------------
            # TOTAL INWARD NET WEIGHT
            # ---------------------------------------------

            total_inward_weight = get_numeric_total(
                inward_df,
                [
                    "Net",
                    "Net Weight",
                    "net",
                    "net weight"
                ]
            )


            # ---------------------------------------------
            # TOTAL OUTWARD NET WEIGHT
            # ---------------------------------------------

            total_outward_weight = get_numeric_total(
                outward_df,
                [
                    "Net",
                    "Net Weight",
                    "net",
                    "net weight"
                ]
            )


            # ---------------------------------------------
            # REMAINING WEIGHT
            # ---------------------------------------------

            remaining_weight = (
                total_inward_weight
                - total_outward_weight
            )


            # ---------------------------------------------
            # PENDING CASH
            # ---------------------------------------------

            cash_to_pay = 0.0


            if not inward_df.empty:

                status_column = find_column(
                    inward_df,
                    [
                        "Status",
                        "status"
                    ]
                )


                total_column = find_column(
                    inward_df,
                    [
                        "Total",
                        "Total Amount",
                        "total",
                        "total amount"
                    ]
                )


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


                    # -------------------------------------
                    # ACCEPT ONLY PENDING / BAAKI
                    # -------------------------------------

                    pending_rows = status_values.isin(
                        [
                            "pending",
                            "बाकी"
                        ]
                    )


                    pending_amounts = pd.to_numeric(
                        inward_df.loc[
                            pending_rows,
                            total_column
                        ],
                        errors="coerce"
                    ).fillna(0)


                    cash_to_pay = float(
                        pending_amounts.sum()
                    )


            # ---------------------------------------------
            # PREVENT NEGATIVE VALUES
            # ---------------------------------------------

            if remaining_sacks < 0:

                remaining_sacks = 0


            if remaining_weight < 0:

                remaining_weight = 0


            # =================================================
            # DISPLAY DASHBOARD
            # =================================================

            col1, col2, col3 = st.columns(3)


            # ---------------------------------------------
            # SACKS
            # ---------------------------------------------

            with col1:

                st.metric(
                    "📦 Remaining Sacks",
                    f"{int(remaining_sacks)}"
                )


            # ---------------------------------------------
            # WEIGHT
            # ---------------------------------------------

            with col2:

                st.metric(
                    "⚖️ Current Total Weight",
                    f"{remaining_weight:.2f} Qtl"
                )


            # ---------------------------------------------
            # CASH
            # ---------------------------------------------

            with col3:

                st.metric(
                    "💰 Cash to Pay",
                    f"₹ {cash_to_pay:,.2f}"
                )


            # =================================================
            # DASHBOARD DETAILS
            # =================================================

            st.markdown("---")


            with st.expander(
                "🔎 Dashboard Calculation Details"
            ):

                st.write(
                    "Total Inward Sacks:",
                    int(total_inward_sacks)
                )


                st.write(
                    "Total Outward Sacks:",
                    int(total_outward_sacks)
                )


                st.write(
                    "Remaining Sacks:",
                    int(remaining_sacks)
                )


                st.markdown("---")


                st.write(
                    "Total Inward Net Weight:",
                    f"{total_inward_weight:.2f} Qtl"
                )


                st.write(
                    "Total Outward Net Weight:",
                    f"{total_outward_weight:.2f} Qtl"
                )


                st.write(
                    "Remaining Weight:",
                    f"{remaining_weight:.2f} Qtl"
                )


                st.markdown("---")


                st.write(
                    "Cash to Pay:",
                    f"₹ {cash_to_pay:,.2f}"
                )


            # =================================================
            # RAW DATA CHECK
            # =================================================

            with st.expander(
                "📊 View Google Sheet Data"
            ):

                st.subheader(
                    "Inward"
                )

                st.dataframe(
                    inward_df,
                    use_container_width=True
                )


                st.subheader(
                    "Outward"
                )

                st.dataframe(
                    outward_df,
                    use_container_width=True
                )


        except Exception as e:

            st.error(
                "❌ Dashboard could not read Google Sheets."
            )

            st.code(
                str(e)
            )


    # =====================================================
    # INWARD
    # =====================================================

    elif menu == t["menu_in"]:

        st.header(
            t["menu_in"]
        )


        col1, col2 = st.columns(2)


        # -------------------------------------------------
        # FARMER DETAILS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # WEIGHT DETAILS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        net_weight = (
            gross - tare
        )


        total_val = (
            net_weight * rate
        )


        st.success(
            f"⚖️ Net Weight: "
            f"{net_weight:.2f} Qtl"
            f"   |   "
            f"💰 Total Amount: "
            f"₹ {total_val:,.2f}"
        )


        # -------------------------------------------------
        # SAVE INWARD
        # -------------------------------------------------

        if st.button(
            t["save_btn"]
        ):

            if not farmer_name:

                st.warning(
                    "⚠️ Please enter Farmer Name."
                )


            elif gross < tare:

                st.warning(
                    "⚠️ Gross weight cannot be less than tare weight."
                )


            elif net_weight <= 0:

                st.warning(
                    "⚠️ Net weight must be greater than 0."
                )


            elif rate <= 0:

                st.warning(
                    "⚠️ Rate must be greater than 0."
                )


            else:

                data = {

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

                    result = send_to_google(
                        data
                    )


                    if result.get("success"):

                        st.balloons()

                        st.success(
                            "✅ Inward saved successfully!"
                        )

                        st.info(
                            "📊 Dashboard will update automatically."
                        )


                    else:

                        st.error(
                            "❌ Google Sheet rejected the entry."
                        )

                        st.code(
                            str(result)
                        )


                except Exception as e:

                    st.error(
                        "❌ Connection error."
                    )

                    st.code(
                        str(e)
                    )


    # =====================================================
    # OUTWARD
    # =====================================================

    elif menu == t["menu_out"]:

        st.header(
            t["menu_out"]
        )


        col1, col2 = st.columns(2)


        # -------------------------------------------------
        # BUYER DETAILS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # LOADING DETAILS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        net_weight = (
            gross - tare
        )


        total_val = (
            net_weight * rate
        )


        st.success(
            f"⚖️ Net Weight: "
            f"{net_weight:.2f} Qtl"
            f"   |   "
            f"💰 Sale: "
            f"₹ {total_val:,.2f}"
        )


        # -------------------------------------------------
        # SAVE OUTWARD
        # -------------------------------------------------

        if st.button(
            t["save_out"]
        ):

            if not buyer_name:

                st.warning(
                    "⚠️ Please enter Buyer Name."
                )


            elif gross < tare:

                st.warning(
                    "⚠️ Gross weight cannot be less than tare weight."
                )


            elif net_weight <= 0:

                st.warning(
                    "⚠️ Net weight must be greater than 0."
                )


            elif rate <= 0:

                st.warning(
                    "⚠️ Rate must be greater than 0."
                )


            else:

                data = {

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

                    result = send_to_google(
                        data
                    )


                    if result.get("success"):

                        st.balloons()

                        st.success(
                            "✅ Outward saved successfully!"
                        )

                        st.info(
                            "📊 Dashboard will update automatically."
                        )


                    else:

                        st.error(
                            "❌ Google Sheet rejected the entry."
                        )

                        st.code(
                            str(result)
                        )


                except Exception as e:

                    st.error(
                        "❌ Connection error."
                    )

                    st.code(
                        str(e)
                    )


# =========================================================
# START APPLICATION
# =========================================================

if st.session_state.get("role"):

    main_app()

else:

    login()