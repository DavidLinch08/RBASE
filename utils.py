import streamlit as st
from supabase import create_client # Client

class Theme:
    main_color = "#b58763"
    second_color = "#d0c1b7"

class Auth:
    def __init__(self):
        # Инициализация состояния
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
        if 'user' not in st.session_state:
            st.session_state.user = None

    def authentication(self):
        """Проверка аутентификации пользователя."""
        if not st.session_state['logged_in']:
            self.login()  # Вызов метода входа
            return False
        return True
    
    def init_supabase(self):
        url = st.secrets.database_url
        key = st.secrets.database_key
        return create_client(url, key)

    def login(self):
        """Форма входа в систему."""
        loginform = st.container()
        with loginform:
            l, c, r = st.columns([2, 1, 2])
            with c:
                cloginform = st.container(border=True)
                with cloginform:
                    st.header('Sign in')
                    login = st.text_input('Login')
                    password = st.text_input('Password', type='password')
                    if st.button('Sign in'):
                        supabase = self.init_supabase()
                        response = supabase.table("users").select("username").filter("username", "eq", login).filter("password", "eq", password).execute()
                        if response.data and len(response.data) > 0:
                            st.session_state['logged_in'] = True
                            st.session_state.user = login
                            st.rerun()
                        else:
                            st.error('Invalid login or password')

    def logout(self):
        """Выход из системы."""
        st.session_state['logged_in'] = False
        st.session_state.user = None
        st.rerun()

    def sidebar_logged_in(self):
        """Отображение боковой панели для залогиненного пользователя."""
        st.markdown("""
            <style>
            [data-testid="stSidebarContent"] div {
                color: #d0c1b7;
                
            }
            [data-testid="stPageLink-NavLink"] span {
                font-size: 1.6rem;
                
            }
            [data-testid="stPageLink-NavLink"] p {
                font-size: 1.2rem;
                margin-left: 0.5rem;
            }        
                    
            [data-testid="stVerticalBlockBorderWrapper"] div {
                gap: 0.25rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
        with st.sidebar:
            us_l,us_r = st.columns([3, 1])
            if st.session_state.user == "Purple":
                user_index = 0
            if st.session_state.user == "Kitkat":
                user_index = 1
            user =  st.selectbox("user", ("Purple", "Kitkat"),index=user_index, label_visibility="collapsed",key="selected_user")
            if user:
                st.session_state.user = user
            st.subheader("")
            st.page_link("Rbase.py", label="HOME", icon=":material/home:", use_container_width=True)
            # st.page_link("pages/dashboard.py", label="DASHBOARD", icon=":material/event_note:", use_container_width=True)
            st.page_link("pages/task_tracking.py", label="TASKS", icon=":material/task:", use_container_width=True)
            st.subheader("SN", divider="gray")
            st.page_link("pages/check_sn.py", label="CHECK SN", icon=":material/visibility:", use_container_width=True)
            st.page_link("pages/new_sn.py", label="NEW SNs", icon=":material/list_alt_add:", use_container_width=True)
            st.page_link("pages/used_sn.py", label="USED SNs", icon=":material/delete_sweep:", use_container_width=True)
            st.subheader("Receipt", divider="gray")
            st.page_link("pages/amazon_receipt_gen.py", label="AMAZON", icon=":material/receipt:", use_container_width=True)
            st.subheader("")
            st.subheader("")
            st.subheader("")
            if st.button("EXIT"):
                Auth.logout(self)
                




def case_statuses():
   return [
                "⚪️Не начато",
                "🟠Начато. Жду Лейбл",
                "🟣Есть лейбл. Нужен FTID",
                "🕑Едет на ремонт",
                "🟡Приехал на ремонт.",
                "🔵В работе",
                "🟢Выполнен",
                "⚫️Отказ"
            ]

def vendor_color_mapping():
    return {
        "DELL": "#0179b7", "Acer": "#7dbc42", "Dyson": "#ba2b79",
        "Yamaha": "#462076", "Corsair": "#f4921e", "Nuwave": "#b11d23"
    }
    
def case_tracking(response):
    # Сортировка данных по имени вендора
    sorted_data = sorted(response, key=lambda row: row.get("vendor", "Unknown Vendor").lower())

    tags_with_links = []
    for row in sorted_data:
        track_number = row.get("track_number")
        vendor = row.get("vendor", "Unknown Vendor")
        case_status = row.get("case_status")
        color = vendor_color_mapping().get(vendor, "gray")

        if track_number:
            if track_number.startswith("1Z"):  # UPS трек-номер
                tracking_link = f"https://www.ups.com/track?loc=en_US&tracknum={track_number}"
            elif track_number.isdigit() and len(track_number) in [12, 15]:  # FedEx трек-номер
                tracking_link = f"https://www.fedex.com/fedextrack/?tracknumbers={track_number}"
            else:
                tracking_link = None
        else:
            tracking_link = None

        # Определение стиля и содержания для тегов
        if case_status in ["⚫️Отказ", "🟢Выполнен"]:
            opacity = 0.9
            color = "black"
            text_color = "grey"
            if case_status == "⚫️Отказ":
                tag = (
                    f'<span style="display:inline-block; background-color: {color}; color: {text_color}; '
                    f'opacity: {opacity}; text-decoration: none; border-radius: 0.5rem; padding: 0 10px; '
                    f'margin-block: 1px; margin-right: 4px;">✖️{vendor}</span>'
                )
            else:
                tag = (
                    f'<span style="display:inline-block; background-color: {color}; color: #16c60c; '
                    f'opacity: {opacity}; text-decoration: none; border-radius: 0.5rem; padding: 0 10px; '
                    f'margin-block: 1px; margin-right: 4px;">✔️{vendor}</span>'
                )
        else:
            if tracking_link:
                tag = (
                    f'<a href="{tracking_link}" target="_blank" style="display:inline-block; background-color: {color}; '
                    f'color: #ffffff; border-radius: 0.5rem; padding: 0 10px; text-decoration: none; '
                    f'margin-block: 1px; margin-right: 4px;">{vendor}</a>'
                )
            else:
                tag = (
                    f'<span style="display:inline-block; background-color: {color}; '
                    f'color: #ffffff; opacity: .7; border-radius: 0.5rem; padding: 0 10px; margin-block: '
                    f'1px; margin-right: 4px;">{vendor}</span> '
                )
        tags_with_links.append(tag)

    tags_container = " ".join(tags_with_links)
    return tags_container


