import streamlit as st
import pandas as pd
from utils import Auth, init_supabase, case_statuses

supabase = init_supabase()

def fetch_data_from_supabase(table_name, filters=None, select_fields=None):
    query = supabase.table(table_name).select(select_fields)
    if filters:
        for field, value in filters.items():
            query = query.filter(field, "eq", value)
    return query.execute()

def fetch_address_line1(supabase, user):
    response = fetch_data_from_supabase("case_list", {"user_name": user}, "address_line1")
    return list(set(row['address_line1'] for row in response.data))

def fetch_address_line2(supabase, user, address_line1):
    response = fetch_data_from_supabase(
        "case_list",
        {"user_name": user, "address_line1": address_line1},
        "address_line2"
    )
    return [row['address_line2'] for row in response.data]

def fetch_vendor_list(supabase):
    response = fetch_data_from_supabase("vendor_list", select_fields="vendor")
    return [row['vendor'] for row in response.data]

def build_query(supabase, user, address_line1, address_line2):
    filters = {"user_name": user}
    if address_line1:
        filters["address_line1"] = address_line1
    if address_line2:
        filters["address_line2"] = address_line2

    return fetch_data_from_supabase("case_list", filters, "id, vendor, case_status, description, track_number")

def case_column_config(vendor_list):
    return {
        "case_status": st.column_config.SelectboxColumn(
            "Case status",
            width="medium",
            default="Не начато",
            options=case_statuses(),
            required=True,
        ),
        "vendor": st.column_config.SelectboxColumn(
            "Vendor",
            width="small",
            options=vendor_list,
            required=True,
        ),
        "description": st.column_config.Column("Description", width="large"),
        "track_number": st.column_config.Column("Track number", width="medium"),
        "id": st.column_config.Column("id", width=None, disabled=True),
        "last_update": st.column_config.Column("Last Update", disabled=True),
    }

def preprocess_df(df):
    df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
    return df

def save_data_to_db(supabase, df, user, address_line1, address_line2):
    df = preprocess_df(df)
    for _, row in df.iterrows():
        data = {
            "user_name": user,
            "address_line1": address_line1,
            "address_line2": address_line2,
            "vendor": row["vendor"],
            "case_status": row["case_status"],
            "description": row["description"],
            "track_number": row["track_number"],
        }
        try:
            if row["id"] == 0:
                supabase.table("case_list").insert(data).execute()
            else:
                supabase.table("case_list").update(data).eq("id", row["id"]).execute()
        except Exception as e:
            st.error(f"Exception occurred: {e}")

def main():
    st.set_page_config(page_title="Dashboard", layout="wide")
# # # # # # Check Auth # # # # # #
    auth = Auth()
    if not auth.authentication():
        return
# # # # # # ------------ # # # # # 
    auth.sidebar_logged_in()

    st.header(':violet[DASHBOARD]', divider='violet')

    l1, l2, space = st.columns([0.2, 0.1, 0.7])
    # user = us.selectbox("User", ("Purple", "Kitkat"))
    user = st.session_state['user']
    address_line1 = st.session_state.get('address_line1', None)
    address_line2 = st.session_state.get('address_line2', None)

    address_line1_options = fetch_address_line1(supabase, user)
    select_address_line1 = l1.selectbox("Address line 1", address_line1_options, index=address_line1_options.index(address_line1) if address_line1 in address_line1_options else None)
    
    if select_address_line1:
        st.session_state.address_line1 = select_address_line1
        address_line1 = select_address_line1

    if address_line1:
        address_line2_options = fetch_address_line2(supabase, user, address_line1)
        select_address_line2 = l2.selectbox("Address line 2", address_line2_options, index=address_line2_options.index(address_line2) if address_line2 in address_line2_options else None)
        if select_address_line2:
            st.session_state.address_line2 = select_address_line2
            address_line2 = select_address_line2

    st.subheader(f"{user} | {address_line1} | {address_line2}")

    response = build_query(supabase, user, address_line1, address_line2)
    df = pd.DataFrame(response.data)
    vendor_list = fetch_vendor_list(supabase)

    with st.form(key='data_form', border=False):
        edited_df = st.data_editor(df, column_config=case_column_config(vendor_list), num_rows="dynamic", hide_index=True, key="editor")
        submit_button = st.form_submit_button("💾Save")

        if submit_button:
            with st.spinner("Saving data..."):
                save_data_to_db(supabase, edited_df, user, address_line1, address_line2)
                st.success("Data successfully saved!")
                st.experimental_rerun()

if __name__ == "__main__":
    main()
