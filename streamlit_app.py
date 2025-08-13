# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get Snowflake session
cnx=st.connection("snowflake")
session = cnx.session()
# Fetch fruit options from Snowflake and convert to Python list
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]

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


smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
