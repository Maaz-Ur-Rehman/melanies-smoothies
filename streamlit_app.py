# Import python packages
import streamlit as st
import pandas as pd
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

# Fetch fruit options from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = fruit_df.to_pandas()
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multi-select box
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Process if user selected ingredients
if ingredients_list and name_on_order.strip():
    st.write("You chose:", ingredients_list)

    # 🥋 Create the INGREDIENTS_STRING variable as an empty string
    ingredients_string = ""

    # 🥋 Add the FOR LOOP block (concatenate with no spaces or commas)
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen

    # 🥋 Output the string
    st.write(ingredients_string)

    # Submit order
    if st.button('Submit Order'):
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()
        st.success(f"Your Smoothie for **{name_on_order}** is ordered!")

elif st.button('Submit Order'):
    st.error("Please select at least one ingredient and enter a name for your smoothie.")

# Nutrition info section
if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
