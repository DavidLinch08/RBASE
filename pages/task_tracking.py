import streamlit as st
import streamlit.components.v1 as components
from utils import Auth, Theme,  case_tracking, case_statuses
from streamlit_datalist import stDatalist
import time

auth = Auth()
supabase = auth.init_supabase()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'dialog_eddited' not in st.session_state:
    st.session_state.dialog_eddited = False
if 'edit_address1' not in st.session_state:
    st.session_state.edit_address1 = ""
if 'edit_address2' not in st.session_state:
    st.session_state.edit_address2 = ""
if 'edit_person_name' not in st.session_state:
    st.session_state.edit_person_name = ""
if 'data' not in st.session_state:
    st.session_state.data = []
if f'new_case' not in st.session_state:
    st.session_state.new_case = False
if f'open_archive' not in st.session_state:
    st.session_state.open_archive = False


def fetch_data(supabase, user, table):
    # Извлечение всех данных за один запрос
    # query = supabase.table("case_list").select("id", "vendor", "sn" , "case_status", "description", "track_number", "person_name", "address_line1", "address_line2")
    query = supabase.table(table).select("*")
    query = query.filter("user_name", "eq", user)
    return query.execute()


def fetch_address_lines(supabase, user):
    # Извлечение всех address_line1 и address_line2 за один запрос
    query = supabase.table("case_list").select("address_line1", "address_line2").filter("user_name", "eq", user)
    response = query.execute()
    return response.data


def fetch_vendor_list(supabase):
    response = supabase.table("vendor_list").select("vendor").execute()
    return list({row['vendor'] for row in response.data})


def save_data_to_db(supabase, data):
    try:
        # Вставляем данные и ждем результат
        response = supabase.table("case_list").insert(data).execute()

        # Проверяем, есть ли данные в ответе
        if not response.data:
            st.error("Ошибка при сохранении данных: изменения не сохранены.")
            return f"Ошибка при сохранении данных: изменения не сохранены."  # Возвращаем False в случае ошибки
        else:
            return "OK"
    except Exception as e:
        return f"Exception occurred: {e}"  # В случае исключения также возвращаем False
    # return True  # Если все успешно, возвращаем True


def update_case_in_db(supabase, id, status, description, track_number, user):
    try:
        # Вставляем данные и ждем результат
        response = supabase.table("case_list").update({
            'case_status': status,
            'description': description,
            'track_number': track_number   
            }).eq("id", id).eq("user_name", user).execute()
        if not response.data:
            return f"Ошибка при сохранении данных: изменения не сохранены."
        else:
            return "OK"
    except Exception as e:
        return f"Exception occurred: {e}"  # В случае исключения также возвращаем False


def delete_case_from_table(supabase, case_id, user, from_table):
    try:
        # Выполняем удаление
        response = supabase.table(from_table).delete().match({"id": case_id, "user_name": user}).execute()

        # Проверяем, были ли данные удалены
        if not response.data:
            st.error("Ошибка при удалении данных: данные не были удалены.")
            return False  # Возвращаем False в случае ошибки
        else:
            st.success("Кейс успешно удален!")
    except Exception as e:
        st.error(f"Exception occurred: {e}")
        return False  # В случае исключения также возвращаем False
    return True  # Если все успешно, возвращаем True


def move_case(supabase, case_id, user, from_table, to_table):
    try:
        fetch_response = supabase.table(from_table).select("*").filter("user_name", "eq", user).filter("id", "eq", case_id).execute()
        # Проверяем, что запрос прошёл успешно
        if fetch_response.data:
            # Удаляем поле 'id' из каждого элемента (если fetch_response.data — список)
            for record in fetch_response.data:
                record.pop('id', None)  # Удаляем 'id', если оно существует
            result_data = fetch_response.data
        insert_response = supabase.table(to_table).insert(result_data).execute()
        if not insert_response.data:
            st.error("Ошибка при сохранении данных: изменения не сохранены.")
            return f"Ошибка при сохранении данных: изменения не сохранены."  # Возвращаем False в случае ошибки
        else:
            return "OK"
    except Exception as e:
        return f"Exception occurred: {e}"  # В случае исключения также возвращаем False


vendor_list = fetch_vendor_list(supabase)
vendor_list_orig = fetch_vendor_list(supabase)
statuses = case_statuses()


def open_dialog(user, edit_address1, edit_address2, edit_person_name, data):
    # Сохраняем аргументы в session_state
    st.session_state.edit_address1 = edit_address1
    st.session_state.edit_address2 = edit_address2
    st.session_state.edit_person_name = edit_person_name
    st.session_state.data = data  # Сохраняем данные

    dialog_title = f"{edit_person_name or 'Новый'}"

    @st.dialog(dialog_title, width="large")
    def dialog():
        st.markdown("""
            <style>
            [aria-label="dialog"] {
                width: 75% !important;
                max-width: 75% !important; /* Ограничение максимальной ширины */
                margin-top: 6%;
            }
            [viewBox="0 0 24 24"] {
                display: none !important;

            }
            </style>
        """, unsafe_allow_html=True)

        st.session_state.dialog_eddited = False
        st.subheader(f"{edit_address1} , {edit_address2}")
        st.html(f'<div style="border: 1px solid {Theme.main_color};"></div>')

        st.subheader("")
        st.subheader("")

        c_vendor, c_tag, c_status, c_description, c_track_num, c_track_button, c_remind, c_action = st.columns([1,0.2,1.2,2,1,0.2,1,0.2], vertical_alignment="top", gap="small")
        c_vendor.write("Вендор")
        c_tag.write("ㅤ")
        c_status.write("Статус")
        c_description.write("Описание")
        c_track_num.write("Трек номер")
        c_track_button.write("ㅤ")
        c_remind.write("Напомнить")
        c_action.write(f"ㅤ")

        edited_cases = []
        for i, row in enumerate(data):
            vendor = data[i]['vendor']
            vendor_list.insert(0, vendor)
            sn = data[i]['sn']
            case_status = data[i]['case_status']

            # Добавляем статус только если его еще нет в списке
            if case_status not in statuses:
                statuses.append(case_status)

            description = data[i]['description']
            id = data[i]['id']
            track = data[i]['track_number']
            if track:
                with c_track_button.popover(":material/visibility:"):
                    

                    if track.startswith("1Z"):  # UPS трек-номер
                        tracking_link = f"https://www.ups.com/track?loc=en_US&tracknum={track}"
                        carrier = "UPS"
                    elif track.isdigit() and len(track) in [12, 15]:  # FedEx трек-номер
                        tracking_link = f"https://www.fedex.com/fedextrack/?tracknumbers={track}"
                        carrier = "FedEx"
                    else:
                        tracking_link = None
                        carrier = "0"
                    st.write(carrier)
                    components.html(f"""
                    <div id="YQContainer"></div>
                    
                    <script type="text/javascript" src="//www.17track.net/externalcall.js"></script>
                    <script type="text/javascript">
                    function doTrack() {{
                        var num = "{track}";
                        YQV5.trackSingle({{
                            YQ_ContainerId:"YQContainer",
                            YQ_Height:100,
                            YQ_Fc:"UPS",
                            YQ_Lang:"en",
                            YQ_Num:num
                        }});
                    }}

                    doTrack();
                    </script>
                """, height=400, width=300)
                    if tracking_link:
                        st.link_button(f"перейти на сайт {carrier}",tracking_link)
            else:
                with c_track_button.popover(":material/visibility:"):
                    st.header("Трека нет")

            editted_vendor = c_vendor.selectbox("Vendor", vendor_list, label_visibility="collapsed", disabled=True, key=f"vendor_{id}")
            with c_tag.popover(":material/tag:", use_container_width=False):
                st.write(sn)
            # Получаем индекс case_status в списке statuses
            case_status_index = statuses.index(case_status)

            editted_status = c_status.selectbox("Status", statuses, label_visibility="collapsed", index=case_status_index, key=f"status_{id}",help="asd123asd")
            editted_description = c_description.text_input("Description", value=description, label_visibility="collapsed", key=f"description_{id}")
            editted_track = c_track_num.text_input("Track", value=track, label_visibility="collapsed", key=f"track_{id}")
            editted_shedule = c_remind.date_input("Schedule", key=f"schedule_{id}", label_visibility="collapsed")
            placeholder = st.empty() #TODO Нужно ли?

            # Добавляем измененные данные в список
            edited_cases.append({
                'id': id,
                'vendor': editted_vendor,
                'status': editted_status,
                'description': editted_description,
                'track': editted_track
            })

            with c_action.popover(":material/delete:", use_container_width=False):

                # Проверяем, существует ли флаг подтверждения в session_state
                if f'delete_case_{id}' not in st.session_state:
                    st.session_state[f'delete_case_{id}'] = False
                if f'archive_case_{id}' not in st.session_state:
                    st.session_state[f'archive_case_{id}'] = False

                # Логика кнопки удаления
                if not st.session_state[f'delete_case_{id}']:
                    # c_arh,c_del = st.columns([1, 1])
                    if st.button(":material/archive: В ахрив", key=f"archive_{id}", use_container_width=True, type="secondary"):
                        st.session_state[f'archive_case_{id}'] = True
                    if st.button(":material/delete_forever: Удалить", key=f"delete_{id}", use_container_width=True, type="primary"):
                        st.session_state[f'delete_case_{id}'] = True

                    

                # Если удаление было подтверждено, показываем чекбокс для окончательного подтверждения
                if st.session_state[f'delete_case_{id}']:
                    st.subheader("")
                    st.write(f'Удалить {editted_vendor}?')
                    del_case_yes, del_case_no = st.columns([1, 1], vertical_alignment="center", gap="small")
                    confirm_delete = del_case_yes.button("ДА", key=f'confirm_delete_{id}' ,use_container_width=True)
                    decline_delete = del_case_no.button("Нет", key=f'decline_delete_{id}' ,use_container_width=True)


                    if decline_delete:
                        st.session_state[f'delete_case_{id}'] = False
                        st.session_state.dialog_eddited = True
                        st.rerun(scope="fragment")

                    # Если пользователь подтвердил, выполняем удаление
                    if confirm_delete:
                        with placeholder:
                            # Выполняем удаление
                            delete_case_from_table(supabase, id, st.session_state.user, from_table="case_list")

                            # Обновляем данные после удаления
                            st.session_state.data = fetch_data(supabase, st.session_state.user, table="case_list").data
                            filtered_data = [row for row in st.session_state.data if row['address_line1'] == edit_address1 and row['address_line2'] == edit_address2]
                            st.session_state.data = filtered_data

                            # Сбрасываем флаг подтверждения
                            st.session_state[f'delete_case_{id}'] = False

                            # Обновляем интерфейс без перезагрузки
                            st.session_state.dialog_eddited = True
                            st.rerun()

                # Если перемещение в архив было подтверждено, показываем чекбокс для окончательного подтверждения
                if st.session_state[f'archive_case_{id}']:
                    st.subheader("")
                    st.write(f'Переместить {editted_vendor} в архив?')
                    del_case_yes, del_case_no = st.columns([1, 1], vertical_alignment="center", gap="small")
                    confirm_archive = del_case_yes.button("ДА", key=f'confirm_archive_{id}' ,use_container_width=True)
                    decline_archive = del_case_no.button("Нет", key=f'decline_archive_{id}' ,use_container_width=True)


                    if decline_archive:
                        st.session_state[f'archive_case_{id}'] = False
                        st.session_state.dialog_eddited = True
                        st.rerun(scope="fragment")

                    # Если пользователь подтвердил, выполняем удаление
                    if confirm_archive:
                        with placeholder:
                            archive_case = move_case(supabase, id, st.session_state.user, from_table="case_list", to_table="case_list_archive")
                            if "Ошибка" not in archive_case and "Exception" not in archive_case:
                                # Выполняем удаление
                                delete_case_from_table(supabase, id, st.session_state.user, from_table="case_list")

                                # Обновляем данные после удаления
                                st.session_state.data = fetch_data(supabase, st.session_state.user, table="case_list").data
                                filtered_data = [row for row in st.session_state.data if row['address_line1'] == edit_address1 and row['address_line2'] == edit_address2]
                                st.session_state.data = filtered_data

                                # Сбрасываем флаг подтверждения
                                st.session_state[f'archive_case_{id}'] = False

                                # Обновляем интерфейс без перезагрузки
                                st.session_state.dialog_eddited = True
                                st.rerun()
                            else:
                                st.error(archive_case)

        st.title("")
        st.title("")
        st.title("")
        st.title("")
        st.title("")
        st.title("")

        sc1, sc2, sc3, sc_space = st.columns([4, 1, 1, 4], vertical_alignment="bottom", gap="small")
        c_vendor.subheader("")
        with c_vendor.popover(":material/add: Добавить кейс",use_container_width=True):
            add_new_case = st.selectbox("Добавить",vendor_list_orig,index=None, label_visibility="collapsed", placeholder="Вендор")
            if add_new_case:
                new_case_sn = st.text_input(label="SN", placeholder="SN", label_visibility="collapsed")
                if st.button(f"Добавить {add_new_case}"):
                    st.session_state.new_case = add_new_case
                    with st.spinner('Ждем...'):
                        new_case_data = {
                            "user_name": st.session_state.user,
                            "address_line1": edit_address1,
                            "address_line2": edit_address2,
                            "person_name": edit_person_name,
                            "vendor": st.session_state.new_case,
                            "sn": new_case_sn,
                            "case_status": "⚪️Не начато",
                            "description": None,
                            "track_number": None,
                        }
                        save_result = save_data_to_db(supabase, data = new_case_data)
                        if "Ошибка" not in save_result and "Exception" not in save_result:
                            # Обновляем данные в session_state только для текущего адреса
                            st.session_state.data = fetch_data(supabase, user, table="case_list").data
                            # Фильтруем только для конкретного адреса и отображаем только обновленные данные
                            filtered_data = [row for row in st.session_state.data if row['address_line1'] == edit_address1 and row['address_line2'] == edit_address2]
                            st.session_state.data = filtered_data  # Обновляем данные для диалога
                            st.success("Кейс успешно добавлен!")
                            st.session_state.new_case = False
                            st.session_state.dialog_eddited = True
                            st.rerun()
                        elif "already exists" in save_result:
                            st.error("Такой кейс уже существует")
                        else:
                            st.error(save_result)

        if sc2.button("Сохранить", key=edit_address1+edit_address2, type="primary", use_container_width=True):
            with st.spinner('Сохранение изменений...'):
                all_saved = True  # Флаг для отслеживания успеха всех операций

                for case in edited_cases:
                    save_result = update_case_in_db(
                        supabase,
                        id=case['id'],
                        status=case['status'],
                        description=case['description'],
                        track_number=case['track'],
                        user=st.session_state.user
                    )


                    if "Ошибка" not in save_result and "Exception" not in save_result:
                        st.success(f"{case['vendor']} - Изменения сохранены")
                    else:
                        all_saved = False  # Если одна из операций не удалась, меняем флаг
                        st.error(f"Ошибка при сохранении кейса {case['vendor']}---{save_result}")

            if all_saved:
                time.sleep(1)
                st.success("Все изменения сохранены!")
                st.session_state.dialog_eddited = True
                st.rerun()
            else:
                st.error("Некоторые изменения не были сохранены.")
                if st.button("Ок"):
                    st.session_state.dialog_eddited = True
                    st.rerun()


        if sc3.button("Отмена", key="rerun_case_list", help= "Отменятся только еще не сохраненные изменения"):
            with st.spinner('Ждем...'):
                st.session_state.dialog_eddited = False
                st.rerun()

    dialog()


def display_cases(data, user, address1, address2):
    row_key = f"{address1}_{address2}"

    person_name = list(set(row["person_name"] for row in data if row.get("person_name")))
    vendor = list(set(row["vendor"] for row in data if row.get("vendor")))
    case_status = list(set(row["case_status"] for row in data if row.get("case_status")))

    tags_container = case_tracking(data)

    c1, c2, c3, c4 = st.columns([0.1, 0.1, 0.3, 0.1], vertical_alignment="center", gap="small")
    st.html(f'<div style="border: 1px solid {Theme.second_color + "1a"};"></div>')

    with c1:
        st.html(f"<span style='color: {Theme.second_color}; font-size: 1.4rem; font-weight: 400;'>{address2}</span>")
    
    with c2:
        person_name_str = ", ".join(person_name)
        st.html(f"<span style='color: {Theme.second_color}; font-size: 1.2rem; font-weight: 300;'>{person_name_str}</span>")
        
    with c3:
        st.markdown(tags_container, unsafe_allow_html=True)
        
    with c4:
        edit_case = st.button("Редактировать", key=row_key, use_container_width=True)

    # Логика открытия и закрытия контейнеров
    if edit_case:
        open_dialog(user, address1, address2, person_name_str, data)

    
def display_archive_cases(data, user, address1, address2):
    archive_row_key = f"archive_{address1}_{address2}"

    arhive_person_name = list(set(row["person_name"] for row in data if row.get("person_name")))
    arhive_vendor = list(set(row["vendor"] for row in data if row.get("vendor")))
    arhive_case_status = list(set(row["case_status"] for row in data if row.get("case_status")))

    tags_container = case_tracking(data)

    c1, c2, c3, c4 = st.columns([0.1, 0.2, 0.2, 0.2], vertical_alignment="center", gap="small")
    st.html(f'<div style="border: 1px solid {Theme.second_color + "1a"};"></div>')

    with c1:
        st.html(f"<span style='color: {Theme.second_color}; font-size: 1.4rem; font-weight: 400;'>{address2}</span>")
    
    with c2:
        person_name_str = ", ".join(arhive_person_name)
        st.html(f"<span style='color: {Theme.second_color}; font-size: 1.2rem; font-weight: 300;'>{person_name_str}</span>")
        
    with c3:
        st.markdown(tags_container, unsafe_allow_html=True)
        
    with c4:
        with st.popover("Восстановить", use_container_width=True):
            for i, row in enumerate(data):
                id = data[i]['id']
                vendor = data[i]['vendor']
                restoring_case = st.button(f"{vendor}",key=f"restore{archive_row_key}_{vendor}",use_container_width=True)
                if restoring_case:                    
                    restore_case = move_case(supabase, id, user, from_table="case_list_archive", to_table="case_list")
                    if "Ошибка" not in restore_case and "Exception" not in restore_case:
                            # Выполняем удаление
                            delete_case_from_table(supabase, id, st.session_state.user, from_table="case_list_archive")
                            st.rerun(scope="fragment")
                    else:
                        st.error(restore_case)


def add_new_address():
    all_address_data = fetch_address_lines(supabase, st.session_state.user)
    address_line1_options = list({row['address_line1'] for row in all_address_data})
    new_address_line1 = stDatalist("Address line 1", address_line1_options)
    c1, c2 = st.columns([1, 1])
    new_address_line2_prefix = c1.selectbox("Type", ["Apt", "Unit", "Suite", "Floor", "Building", "Room", "Wing", "Box", "Office", "Block", "Section", "Cell"])
    new_address_line2 = f"{new_address_line2_prefix} {c2.text_input('Address line 2', autocomplete='off')}"
    person_name = st.text_input("Name")
    
    if st.button("Сохранить"):
        address_exists = any(
            row['address_line1'] == new_address_line1 and row['address_line2'] == new_address_line2
            for row in all_address_data
        )
        if address_exists:
            st.error("Такой адрес уже используется")
        else:
            new_address_data = {
                "user_name": st.session_state.user,
                "address_line1": new_address_line1,
                "address_line2": new_address_line2,
                "person_name": person_name,
                "vendor": "⚪️Не назначен", #TODO Добавить функционал указания вендора перед внесением в бд###################
                "case_status": "⚪️Не начато",
                "description": None,
                "track_number": None,
            }
            save_result = save_data_to_db(supabase, data = new_address_data)
            if "Ошибка" not in save_result and "Exception" not in save_result:
                st.success("Кейс успешно добавлен!")
                st.rerun()
            elif "already exists" in save_result:
                st.error("Такой кейс уже существует")
            else:
                st.error(save_result)


# Отрисовка списка адресов с кейсами
@st.fragment
def render_adress_list():
    fc1, fc_sp, fc3, fc_sp2, fc4, fc_sp3 = st.columns([1.7, 3, 0.1, 0.2, 1, 4], vertical_alignment="center", gap="small")
    new_address = fc1.popover("Добавить адрес", use_container_width=True)
    with new_address:
        add_new_address()
    if fc3.button(":material/autorenew:",key="rerun_address_list"):
        st.rerun(scope="fragment")
    if fc4.button(label=":material/history: Архив ⟶", use_container_width=True, key="open_archive_button"):
        st.session_state.open_archive = not st.session_state.open_archive
    main1, space, main2 = st.columns([6, 0.3, 3.7], vertical_alignment="top", gap="small")

    with main1:
        case_data = fetch_data(supabase, st.session_state.user, table="case_list")
        for address1 in sorted({row['address_line1'] for row in case_data.data}):
            st.html(f"<span style='color: {Theme.main_color}; font-size: 2rem; font-weight: 600;'>{address1}</span>")
            st.html(f'<div style="border: 2px solid {Theme.main_color};"></div>')
            for address2 in sorted({row['address_line2'] for row in case_data.data if row['address_line1'] == address1}):
                filtered_cases = [row for row in case_data.data if row['address_line1'] == address1 and row['address_line2'] == address2]
                display_cases(filtered_cases, st.session_state.user, address1, address2)
            st.html("")
    if st.session_state.open_archive:
        with main2:
            st.subheader("")
            with st.container(border=True):
                st.subheader("Архив:")
                archive_case_data = fetch_data(supabase, st.session_state.user, table="case_list_archive")
                # st.header(archive_case_data.data)
                if archive_case_data.data == []:
                    st.html(f"<span style='color: #3c3c3c; font-size: 3rem; font-weight: 600; text-allign: center'>Пусто</span>")
                for arhive_address1 in sorted({row['address_line1'] for row in archive_case_data.data}):
                    st.html(f"<span style='color: {Theme.main_color}; font-size: 2rem; font-weight: 600;'>{arhive_address1}</span>")
                    st.html(f'<div style="border: 2px solid {Theme.main_color};"></div>')
                    for arhive_address2 in sorted({row['address_line2'] for row in archive_case_data.data if row['address_line1'] == arhive_address1}):
                        filtered_cases = [row for row in archive_case_data.data if row['address_line1'] == arhive_address1 and row['address_line2'] == arhive_address2]
                        display_archive_cases(filtered_cases, st.session_state.user, arhive_address1, arhive_address2)
                    st.html("")




def main():
    st.set_page_config(page_title="Method", layout="wide")
    
    # # # # # # Check Auth # # # # # #
    auth = Auth()
    if not auth.authentication():
        return
    auth.sidebar_logged_in()
    # # # # # ## # # # # ## # # # # #

    if st.session_state.dialog_eddited == True:
        open_dialog(st.session_state.user, st.session_state.edit_address1, st.session_state.edit_address2, st.session_state.edit_person_name, st.session_state.data)

    render_adress_list()

if __name__ == "__main__":
    main()
