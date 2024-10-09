import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils import Auth, Theme

supabase = Auth.init_supabase(self=True)

def main():
    response = supabase.table("new_sn").select("vendor").execute()
    vendor_list = list(set(row['vendor'] for row in response.data))

    st.set_page_config(page_title="New SN", layout="wide")

# # # # # # Check Auth # # # # # #
    auth = Auth()
    if not auth.authentication():
        return
# # # # # # ------------ # # # # # 
    auth.sidebar_logged_in()
# PAGE CONTENT GOES HERE #################################################################
    st.html(f"<span style='color: {Theme.main_color}; font-size: 2rem; font-weight: 600;'>New SN</span>")
    st.html(f'<div style="border: 2px solid {Theme.main_color};"></div>')
    maincontainer = st.container(border=False)
    with maincontainer:
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
            firstcontainer = st.container(border=True)
            with firstcontainer:
                vendor = st.selectbox("Vendor", (vendor_list), placeholder="select vendor", index=None)
                if vendor:
                    response = supabase.table("new_sn").select("vendor", "sn", "model","expiredate").filter("vendor", "eq", vendor).execute()
                    model_list = list(set(row['model'] for row in response.data))
                    model_list.append("All models")
                    model = st.selectbox("Model", (model_list), placeholder="select model", index=len(model_list) - 1)
                    if st.button("🔍 Search"):
                        if model == "All models":
                            response = supabase.table("new_sn").select("vendor", "sn", "model", "expiredate").filter("vendor", "eq", vendor).execute()
                        else:
                            response = supabase.table("new_sn").select("vendor", "sn", "model", "expiredate").filter("vendor", "eq", vendor).filter("model", "eq", model).execute()
                        df = pd.DataFrame(response.data, index=np.arange(1, len(response.data) + 1))
                        df['expiredate'] = pd.to_datetime(df['expiredate']).dt.date

                        current_date = datetime.now().date()
                        future_date = current_date + timedelta(days=14)

                        def color_cells(val):
                            val_date = val
                            days_diff = (val_date - current_date).days
                            if val_date < future_date:
                                red_intensity = min(255, int(255 * (14 - days_diff) / 14))
                                alpha = min(0.8, red_intensity / 255)
                                color = f'rgba(255, 0, 0, {alpha})'
                            else:
                                green_intensity = min(255, int(255 * days_diff / 365))
                                alpha = max(0.2, min(0.3, green_intensity / 255))
                                color = f'rgba(60, 255, 60, {alpha})' 
                            return f'background-color: {color}'
                        
                        styled_df = df.style.applymap(color_cells, subset=['expiredate'])
                        
                        with col2:
                                st.dataframe(styled_df, height=600, use_container_width=True, selection_mode="single-row")

if __name__ == "__main__":
    main()
