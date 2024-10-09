import streamlit as st
import pandas as pd
import numpy as np
from utils import Auth, Theme


# Initialize Supabase client
supabase = Auth.init_supabase(self=True)


def fetch_vendor_list(supabase):
    response = supabase.table("vendor_list").select("vendor").execute()
    return [row['vendor'] for row in response.data]


def add_new_vendor(supabase, vendor):
    response = supabase.table("vendor_list").select("vendor").filter("vendor", "eq", vendor).execute()
    if response.data and len(response.data) > 0:
        st.error(f"{vendor} already exists.")
        return False
    else:
        insert_data = {"vendor": vendor}
        response = supabase.table("vendor_list").insert(insert_data).execute()
        if 'error' in response and response['error']:
            st.error("Failed to add new vendor: " + response['error']['message'])
            return False
        else:
            st.success(f"**{vendor}** added successfully.")
            return True


def add_sn(supabase, vendor, sn):
    response = supabase.table("used_sn").select("sn").filter("vendor", "eq", vendor).filter("sn", "eq", sn).execute()
    if response.data and len(response.data) > 0:
        st.error(f"SN already exists for **{vendor}**")
    else:
        insert_data = {
            "vendor": vendor,
            "sn": sn
        }
        response = supabase.table("used_sn").insert(insert_data).execute()
        if 'error' in response and response['error']:
            st.error("Failed to add SN: " + response['error']['message'])
        else:
            st.success(f"**{sn}** added successfully to **{vendor}**.")


def delete_from_new_sn(supabase, vendor, sn):
    response = supabase.table("new_sn").select("sn").filter("vendor", "eq", vendor).filter("sn", "eq", sn).execute()
    if response.data and len(response.data) > 0:
        subresponse = supabase.table("new_sn").delete().filter("vendor", "eq", vendor).filter("sn", "eq", sn).execute()
        if 'error' in subresponse and subresponse['error']:
            st.error("Failed to delete SN from NEW SN list: " + response['error']['message'])
        else:
            st.success(f"**{sn}** successfully deleted from **{vendor}** NEW SN list .")


def display_sn_list(supabase, vendor):
    response = supabase.table("used_sn").select("sn").filter("vendor", "eq", vendor).execute()
    df = pd.DataFrame(response.data, index=np.arange(1, len(response.data) + 1))
    st.dataframe(df,use_container_width=True)


def main():
    st.set_page_config(page_title="Used SN", layout="wide")
    vendor_list = fetch_vendor_list(supabase)
    vendor_list.insert(0,'➕➕➕ADD NEW VENDOR➕➕➕')

# # # # # # Check Auth # # # # # #
    auth = Auth()
    if not auth.authentication():
        return
# # # # # # ------------ # # # # # 
    auth.sidebar_logged_in()
    st.html(f"<span style='color: {Theme.main_color}; font-size: 2rem; font-weight: 600;'>Used SN</span>")
    st.html(f'<div style="border: 2px solid {Theme.main_color};"></div>')
    
    left, right,space = st.columns([1.5, 2, 1.5])

    with left:
        with st.container(border=True):
            vendor = st.selectbox("Vendor", vendor_list, placeholder="select vendor", index=None, label_visibility='collapsed')
            existing_vendor = True
            if vendor:
                if vendor == "➕➕➕ADD NEW VENDOR➕➕➕":
                    newvendor = st.text_input("New vendor name", placeholder="Name") 
                    existing_vendor = False           
                subleft, subright = st.columns([5, 1.5])
                with subleft:
                    sn = st.text_input("SN", placeholder="SN", label_visibility='collapsed')
                with subright:
                    submitted = st.button(f"➕SN")
                if submitted:
                    if sn == "" or sn == None:
                        st.error("Fill SN.")
                        return
                    if not existing_vendor:
                        if newvendor  == "" or newvendor == None:
                            st.error("Fill vendor name.")
                            return
                        else:  
                            vendor = newvendor
                            add_new_vendor(supabase, vendor)
                            add_sn(supabase, vendor, sn)
                            st.experimental_rerun()
                    else:
                        add_sn(supabase, vendor, sn)
                        delete_from_new_sn(supabase, vendor, sn)
    with right:        
        if existing_vendor and vendor is not None:
            display_sn_list(supabase, vendor)
            

if __name__ == "__main__":
    main()