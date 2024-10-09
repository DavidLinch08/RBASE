import streamlit as st
from utils import Auth


def main():
    st.set_page_config(page_title="REDBASE", layout="wide")
    # # # # # # Check Auth # # # # # #
    auth = Auth()
    if not auth.authentication():
        return
    # # # # # # ------------ # # # # #
    auth.sidebar_logged_in()
    st.header(f'Hi {st.session_state["user"]}!')


if __name__ == "__main__":
    main()