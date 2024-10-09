import streamlit as st
from utils import Auth, Theme
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random
from jinja2 import Template

states_data = [
    {"name": "Alabama (AL)", "abbreviation": "AL", "sales_tax": 4.00},
    {"name": "Alaska (AK)", "abbreviation": "AK", "sales_tax": 0.00},
    {"name": "Arizona (AZ)", "abbreviation": "AZ", "sales_tax": 5.60},
    {"name": "Arkansas (AR)", "abbreviation": "AR", "sales_tax": 6.50},
    {"name": "California (CA)", "abbreviation": "CA", "sales_tax": 9.5},
    {"name": "Colorado (CO)", "abbreviation": "CO", "sales_tax": 2.90},
    {"name": "Connecticut (CT)", "abbreviation": "CT", "sales_tax": 6.35},
    {"name": "Delaware (DE)", "abbreviation": "DE", "sales_tax": 0.00},
    {"name": "Florida (FL)", "abbreviation": "FL", "sales_tax": 6.00},
    {"name": "Georgia (GA)", "abbreviation": "GA", "sales_tax": 4.00},
    {"name": "Hawaii (HI)", "abbreviation": "HI", "sales_tax": 4.00},
    {"name": "Idaho (ID)", "abbreviation": "ID", "sales_tax": 6.00},
    {"name": "Illinois (IL)", "abbreviation": "IL", "sales_tax": 6.25},
    {"name": "Indiana (IN)", "abbreviation": "IN", "sales_tax": 7.00},
    {"name": "Iowa (IA)", "abbreviation": "IA", "sales_tax": 6.00},
    {"name": "Kansas (KS)", "abbreviation": "KS", "sales_tax": 6.50},
    {"name": "Kentucky (KY)", "abbreviation": "KY", "sales_tax": 6.00},
    {"name": "Louisiana (LA)", "abbreviation": "LA", "sales_tax": 4.45},
    {"name": "Maine (ME)", "abbreviation": "ME", "sales_tax": 5.50},
    {"name": "Maryland (MD)", "abbreviation": "MD", "sales_tax": 6.00},
    {"name": "Massachusetts (MA)", "abbreviation": "MA", "sales_tax": 6.25},
    {"name": "Michigan (MI)", "abbreviation": "MI", "sales_tax": 6.00},
    {"name": "Minnesota (MN)", "abbreviation": "MN", "sales_tax": 6.875},
    {"name": "Mississippi (MS)", "abbreviation": "MS", "sales_tax": 7.00},
    {"name": "Missouri (MO)", "abbreviation": "MO", "sales_tax": 4.225},
    {"name": "Montana (MT)", "abbreviation": "MT", "sales_tax": 0.00},
    {"name": "Nebraska (NE)", "abbreviation": "NE", "sales_tax": 5.50},
    {"name": "Nevada (NV)", "abbreviation": "NV", "sales_tax": 6.85},
    {"name": "New Hampshire (NH)", "abbreviation": "NH", "sales_tax": 0.00},
    {"name": "New Jersey (NJ)", "abbreviation": "NJ", "sales_tax": 6.625},
    {"name": "New Mexico (NM)", "abbreviation": "NM", "sales_tax": 5.125},
    {"name": "New York (NY)", "abbreviation": "NY", "sales_tax": 4.00},
    {"name": "North Carolina (NC)", "abbreviation": "NC", "sales_tax": 4.75},
    {"name": "North Dakota (ND)", "abbreviation": "ND", "sales_tax": 5.00},
    {"name": "Ohio (OH)", "abbreviation": "OH", "sales_tax": 5.75},
    {"name": "Oklahoma (OK)", "abbreviation": "OK", "sales_tax": 4.50},
    {"name": "Oregon (OR)", "abbreviation": "OR", "sales_tax": 0.00},
    {"name": "Pennsylvania (PA)", "abbreviation": "PA", "sales_tax": 6.00},
    {"name": "Rhode Island (RI)", "abbreviation": "RI", "sales_tax": 7.00},
    {"name": "South Carolina (SC)", "abbreviation": "SC", "sales_tax": 6.00},
    {"name": "South Dakota (SD)", "abbreviation": "SD", "sales_tax": 4.50},
    {"name": "Tennessee (TN)", "abbreviation": "TN", "sales_tax": 7.00},
    {"name": "Texas (TX)", "abbreviation": "TX", "sales_tax": 6.25},
    {"name": "Utah (UT)", "abbreviation": "UT", "sales_tax": 4.85},
    {"name": "Vermont (VT)", "abbreviation": "VT", "sales_tax": 6.00},
    {"name": "Virginia (VA)", "abbreviation": "VA", "sales_tax": 5.30},
    {"name": "Washington (WA)", "abbreviation": "WA", "sales_tax": 6.50},
    {"name": "West Virginia (WV)", "abbreviation": "WV", "sales_tax": 6.00},
    {"name": "Wisconsin (WI)", "abbreviation": "WI", "sales_tax": 5.00},
    {"name": "Wyoming (WY)", "abbreviation": "WY", "sales_tax": 4.00}
]

def generate_number():
    part1 = random.randint(100, 199)
    part2 = random.randint(1000000, 9999999)
    part3 = random.randint(1000000, 9999999)
    result = f"{part1}-{part2}-{part3}"
    return result

def generate_last_digits():
    return str(random.randint(1000, 9999))

def main():
    st.set_page_config(page_title="Amazon receipt", layout="wide")

# # # # # # Check Auth # # # # # #
    auth = Auth()
    if not auth.authentication():
        return
# # # # # # ------------ # # # # # 
    auth.sidebar_logged_in()

    if 'last_digits' not in st.session_state:
        st.session_state.last_digits = None
# PAGE CONTENT GOES HERE #################################################################
    st.html(f"<span style='color: {Theme.main_color}; font-size: 2rem; font-weight: 600;'>Amazon receipt</span>")
    st.html(f'<div style="border: 2px solid {Theme.main_color};"></div>')

    maincontainer = st.container(border=False)
    with maincontainer:
        col1, col2 = st.columns([1, 2])
        with col1:
            firstcontainer = st.container(border=True)
            with firstcontainer:
    # Order number ##########
                st.markdown("<span style='font-size:14px; margin-bottom: 4px;'>Order number</span>", unsafe_allow_html=True)     
                col_order_number, col_button = st.columns([3, 1])
                with col_button:
                    if st.button(":material/shuffle: Random", use_container_width=True):
                        order_value = generate_number()
                        st.session_state.order_number = order_value
                with col_order_number:
                    if 'order_number' not in st.session_state:
                        st.session_state.order_number = None
                    order_number = st.text_input("Order number",value=st.session_state.order_number, placeholder="Order number", label_visibility="collapsed")
                if st.session_state.order_number is not None:
                    if order_number == "":
                        st.error("Order number is required.")
    # Order date ##########
                order_date = st.date_input("Order date", value=None, max_value=datetime.now())
                if order_date:
                    order_date_obj = datetime.strptime(str(order_date), "%Y-%m-%d")
                    order_date = order_date_obj.strftime("%B %d, %Y").replace(" 0", " ")
                    order_date_year = order_date_obj.strftime("%Y")
                    default_dispatch_date = order_date_obj + timedelta(days=5)
                    current_date = datetime.now()
                    if default_dispatch_date > current_date:
                        default_dispatch_date = None
                else: 
                    default_dispatch_date = None
    # Dispatch date ##########
                dispatch_date = st.date_input("Dispatch date", value=default_dispatch_date, max_value=datetime.now())
                if dispatch_date:
                    dispatch_date_obj = datetime.strptime(str(dispatch_date), "%Y-%m-%d")
                    dispatch_date = dispatch_date_obj.strftime("%B %d, %Y").replace(" 0", " ")      
                if dispatch_date and order_date and dispatch_date_obj < order_date_obj:
                    st.error("Dispatch date cannot be earlier than order date.")
    # Sold by ##########
                by_amazon =st.toggle("Sold by Amazon")
                if by_amazon:
                    sold_by = "Amazon.com Services"
                    supplied_by = "Other"   
                else:
                    with st.container(border=True):
        # Supplied by ##########
                        sold_by = st.text_input("Sold by", placeholder="Seller name")
                        supplied_by = sold_by
        # Seller ID ##########
                        seller_id = st.text_input("Seller ID", placeholder="AQEJXZW1O9O7O", help=f"how to find it: https://www.sellersprite.com/en/blog/amazon-seller-ID-merchant-token-number")
                        if seller_id:
                            sold_by = sold_by + " " + f"(<a style=\"text-decoration: none;\" href=\"http://www.amazon.com/gp/help/seller/at-a-glance.html/ref=od_sold_by_link?ie=UTF8&isAmazonFulfilled=1&marketplaceSeller=1&orderID={order_number}&seller={seller_id}\">seller profile</a>)"
                            supplied_by = supplied_by + " " + f"(<a style=\"text-decoration: none;\" href=\"http://www.amazon.com/gp/help/seller/at-a-glance.html/ref=od_supplied_by_link?ie=UTF8&isAmazonFulfilled=1&marketplaceSeller=1&orderID={order_number}&seller={seller_id}\">seller profile</a>)"
                        else:
                            sold_by = sold_by + " " + f"(<a style=\"text-decoration: none;\" href=\"http://www.amazon.com/gp/help/seller/at-a-glance.html/ref=od_sold_by_link?ie=UTF8&isAmazonFulfilled=1&marketplaceSeller=1&orderID={order_number}&seller=AQEJXZW1O9O7O\">seller profile</a>)"
                            supplied_by = supplied_by + " " + f"(<a style=\"text-decoration: none;\" href=\"http://www.amazon.com/gp/help/seller/at-a-glance.html/ref=od_supplied_by_link?ie=UTF8&isAmazonFulfilled=1&marketplaceSeller=1&orderID={order_number}&seller=AQEJXZW1O9O7O\">seller profile</a>)"          
    # Shipping speed ##########
                shipping_speed = st.selectbox("Shipping speed", ["Standard", "FREE Prime Delivery"])
    # Shipping price ##########   
                if 'shipping_price' not in st.session_state:
                    st.session_state.shipping_price = 0.00
                shipping_price = st.text_input("Shipping price",value=st.session_state.shipping_price, placeholder="0.00")
                try:
                    shipping_price_value = float(shipping_price)
                    shipping_price = float(f"{shipping_price_value:.2f}")
                except ValueError:
                    shipping_price_value = 0.00
                    st.error("invalid value. Example: 12.50")
    # Item name ##########
                item_name = st.text_input("Item name", placeholder="Sony ZX Series Wired On-Ear Headphones")
    # Item cost ##########
                if 'item_cost' not in st.session_state:
                    st.session_state.item_cost = 0.00
                item_cost = st.text_input("Item cost", value=st.session_state.item_cost, placeholder="399.00")
                try:
                    item_cost_value = float(item_cost)
                    item_cost = float(f"{item_cost_value:.2f}")
                except ValueError:
                    item_cost_value = 0.00
                    st.error("invalid value. Example: 399.00")
    # Item quantity ##########       
                if 'item_quantity' not in st.session_state: 
                    st.session_state.item_quantity = 1
                item_quantity = st.text_input("Quantity", value=st.session_state.item_quantity, placeholder="1")
                try:
                    item_quantity_value = int(item_quantity)
                    item_quantity = int(f"{item_quantity_value}")
                except ValueError:
                    item_quantity_value = 1
                    st.error("invalid value. Example: 1")
    # Auto tax ##########
                st.markdown("<span style='font-size:14px; margin-bottom: 4px;'>Tax %</span>", unsafe_allow_html=True)
                left, right = st.columns([4, 2]) 
                with right:          
                    auto_tax = st.toggle("Auto tax", value=True)
                with left:
                    if not auto_tax:
                        if 'tax' not in st.session_state: 
                            st.session_state.tax = 0
                        tax = st.text_input("Tax %", value=st.session_state.item_cost, placeholder="7.25", label_visibility="collapsed")
                        try:
                            tax_value = float(tax)
                            tax = float(f"{tax_value:.2f}")
                        except ValueError:
                            tax_value = 0.00
                            st.error("invalid value. Example: 7.25")
                    else:
                        st.text_input("Tax %", placeholder="AUTO TAX",label_visibility="collapsed", disabled=True)
    # Customer name ##########
                full_name = st.text_input("Full name", placeholder="John Doe")
    # Customer address ##########          
                address_line1 = st.text_input("Address line 1", placeholder="1258 Main Street")
                address_line2 = st.text_input("Address line 2", placeholder="Apt. 21")
                address_city = st.text_input("City", placeholder="New York")
                address_state = st.selectbox("State", options=[state["name"] for state in states_data])
                address_zip = st.text_input("ZIP code", placeholder="10001")
    # Payment method ##########
                st.markdown("<span style='font-size:14px; margin-bottom: 4px;'>Payment method last 4 digits</span>", unsafe_allow_html=True) 
                ld1, ld2 = st.columns([4, 2])
                last_digits = None
                with ld1:
                    last_digits = st.text_input("Payment method last 4 digits", placeholder="1234", value=st.session_state.last_digits or "", label_visibility="collapsed")                             
                
                if auto_tax:
                    state_info = next((state for state in states_data if state["name"] == address_state), None)
                    if state_info:
                        tax = state_info['sales_tax']
                        if tax == 0.0:
                            tax = 0

                if shipping_price == 0.0:
                    shipping_price = float(f"{shipping_price:.2f}")
                if item_cost == 0.0:
                    item_cost = float(f"{item_cost:.2f}")
                if tax == 0.0:
                    tax = float(f"{tax:.2f}")
                
                if item_cost is not None and tax is not None and shipping_price is not None:
                
                    item_tax = item_cost * tax / 100
                    total_before_tax = item_cost + shipping_price
                    grand_total = item_cost + shipping_price + item_tax
                    shipping_tax = shipping_price * tax / 100
                    total_tax = item_tax + shipping_tax
                    shipping_price = f"{shipping_price:,.2f}"
                    total_tax = f"{total_tax:,.2f}"
                    grand_total = f"{grand_total:,.2f}"
                    total_before_tax = f"{total_before_tax:,.2f}"
                    item_cost = f"{item_cost:,.2f}"

                state_short = next((state for state in states_data if state["name"] == address_state), None)
                address_state = state_short['abbreviation']
                
                if st.button("Generate receipt", use_container_width=True):
                
                    with col2:
                        seccontainer = st.container(border=True)
                        with seccontainer:
                            with open("receipt.html", "r", encoding='utf-8') as html_file:
                                html_content = html_file.read()
                                template = Template(html_content)
                                rendered_html = template.render(
                                    order_number=order_number,
                                    order_date=order_date,
                                    dispatch_date=dispatch_date,
                                    sold_by=sold_by,
                                    supplied_by=supplied_by,
                                    shipping_speed=shipping_speed,
                                    grand_total=grand_total,
                                    shipping_price=shipping_price,
                                    total_before_tax=total_before_tax,
                                    total_tax=total_tax,
                                    item_name=item_name,
                                    item_cost=item_cost,
                                    last_digits=last_digits,
                                    item_quantity=item_quantity,
                                    full_name=full_name,
                                    address_line1=address_line1,
                                    address_line2=address_line2,
                                    address_city=address_city,
                                    address_state=address_state,
                                    address_zip=address_zip,
                                    order_date_year=order_date_year                    
                                    )
                                
                            components.html(rendered_html, height=1091, width=830)
                            st.download_button("Download .html file", rendered_html, mime="text/html",file_name = "Amazon.com - Order " + order_number + ".html")  
                            st.markdown("""
                                <style>
                                .custom-underline {
                                    text-decoration: underline;
                                    text-decoration-color: #E47911;
                                    color: #E47911;
                                }
                                </style>
                                Click <span class="custom-underline">Print this page for your records</span> on preview to download PDF.
                            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()