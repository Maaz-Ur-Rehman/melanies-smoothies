# Import python packages
import streamlit as st
import pandas as pd   # ✅ NEW
import requests
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# ✅ Fetch FRUIT_NAME and SEARCH_ON from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# ✅ Convert Snowpark DataFrame to Pandas DataFrame
pd_df = fruit_df.to_pandas()

# ✅ Fruit list for multiselect comes from FRUIT_NAME column
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multi-select box for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Process if user selected ingredients
if ingredients_list and name_on_order.strip():
    st.write("You chose:", ingredients_list)
    ingredients_string = " ".join(ingredients_list)
    st.write(ingredients_string)

    if st.button('Submit Order'):
        # SAFE insert with parameters
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()
        st.success(f"Your Smoothie for **{name_on_order}** is ordered!")

elif st.button('Submit Order'):
    st.error("Please select at least one ingredient and enter a name for your smoothie.")

# ✅ Show nutrition info using SEARCH_ON values
if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")
        
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
