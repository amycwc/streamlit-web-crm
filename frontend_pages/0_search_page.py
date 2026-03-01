
import streamlit as st
import pandas as pd
import logging


def search_customers():
    # Import only when function is called
    from crm_model.models import CustomerProfile, CustomerManager
    return CustomerProfile.objects.all()

col1, col2 = st.columns(2)
with col1:
  
  with st.form("my_form"):
     input_customer_id = st.text_input("Customer ID", "")
     input_phone = st.text_input("Phone", "")
     submit = st.form_submit_button('Search')

  if 'selected_filter' not in st.session_state:
         st.session_state['selected_filter'] = ''
  selected_filter = st.multiselect(
          'Filter',
          ['first_name', 'last_name','email'], 
          max_selections=5,
          accept_new_options=True)
with col2:
   if selected_filter:
    for filter_name in selected_filter:
        st.session_state['selected_filter'] = filter_name
        value = st.session_state.get(f"input_{filter_name}")
        input = st.text_input(
            f"Enter value for {filter_name}",
            key=f"input_{filter_name}")     

if submit:
    st.session_state['customer_id'] = input_customer_id
    st.session_state['phone'] = input_phone
    
    try:
        customer_query = search_customers()
        if input_customer_id:
            exact_query = customer_query.filter(customer_id=input_customer_id)
            fuzzy_query = customer_query.filter(customer_id__icontains=input_customer_id)
        if input_phone:
            exact_query = customer_query.filter(phone_number=input_phone)
            fuzzy_query = customer_query.filter(phone_number__icontains=input_phone)
        for filter_name in selected_filter:
            filter_value = st.session_state.get(f"input_{filter_name}")
            if filter_value:
                exact_kwargs = {f"{filter_name}": filter_value}
                exact_query = customer_query.filter(**exact_kwargs)
                fuzzy_kwargs = {f"{filter_name}__icontains": filter_value}
                fuzzy_query = customer_query.filter(**fuzzy_kwargs)
        exact_query_results = list(exact_query.values())
        fuzzy_query_results = list(fuzzy_query.values())
        fuzzy_customer = pd.DataFrame(
            fuzzy_query_results,
            columns=[
                "customer_id",
                "phone_number",
                "email",
                "first_name",
                "last_name",
                "crm"
            ]
        )
   
        fuzzy_customer['crm'] = fuzzy_customer['customer_id'].apply(lambda x: f"/customer_dashboard?customer_id={x}").astype(str)
       
        st.data_editor(
            fuzzy_customer,
            column_config= {
                "customer_id": "customer_id",
                "phone_number": "Phone Number",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": "Email",
                "crm": st.column_config.LinkColumn(
                    "dashboard", display_text="dashboard📊"
                ),
            },
            hide_index=True,
            )
        
    except Exception as e:
        st.error(f"Error: {e}")
        logging.error(f"Failed to connect to the database: {e}")
