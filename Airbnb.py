import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import mysql.connector
import plotly.express as px

# Reading CSV File (Update the file path accordingly)
df = pd.read_csv('F:\Streamlit\Airbnb.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)

# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database='airbnb'
)
mycursor = mydb.cursor(buffered=True)

st.set_page_config(
    page_title="Airbnb Analysis - By Pranit Akhade",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Airbnb Analysis")

# Sidebar Filters
# User input
country = st.sidebar.selectbox("Select a Country", sorted(df['Country'].unique()))
room = st.sidebar.selectbox("Select a Room Type", sorted(df['Room_type'].unique()))
property_type = st.sidebar.selectbox("Select a Property Type", sorted(df['Property_type'].unique()))
price_range = st.sidebar.slider("Select a Price Range", df["Price"].min(), df["Price"].max(), (df["Price"].min(), df["Price"].max()))

# SQL query with parameterized input
query1 = f"SELECT * FROM Airbnb WHERE Country=%s AND Property_type=%s AND Room_type=%s AND Price BETWEEN %s AND %s"
query_params = (country, property_type, room, float(price_range[0]), float(price_range[1]))
mycursor.execute(query1, query_params)

# Fetch the result and create DataFrame
filtered_data = pd.DataFrame(mycursor.fetchall(), columns=[desc[0] for desc in mycursor.description])

# Filter out rows with missing location information
filtered_data = filtered_data.dropna(subset=['Latitude', 'Longitude'])

# Check if there are rows available for mapping
if not filtered_data.empty:
    # Display map
    st.header("Airbnb Geospatial Analysis")

    # Create a folium map centered around the mean latitude and longitude of filtered data
    m = folium.Map(location=[filtered_data['Latitude'].mean(), filtered_data['Longitude'].mean()], zoom_start=10, control_scale=True)

    # Plot markers on the map
    for index, row in filtered_data.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']], popup=f"Price: ${row['Price']}, Rating: {row['Review_scores']}, Host Name : {row['Host_name']}").add_to(m)

    # Display the map using streamlit
    folium_static(m)

    # Display a table of filtered data
    st.subheader("Filtered Airbnb Listings")
    st.write(filtered_data)
else:
    pass
    #st.warning("No data available for the selected filters. Try adjusting your criteria.")


query2 = f"SELECT AVG(Price) as Average_Price, AVG(Security_deposit) as Average_Security_Deposit, AVG(Cleaning_fee) as Average_Cleaning_Fee FROM Airbnb WHERE Country='{country}' AND Room_type='{room}' AND Property_type='{property_type}'"

mycursor.execute(query2)
result_averages = mycursor.fetchone()

# Display the results
if result_averages and any(value is not None for value in result_averages):
    st.sidebar.write(f"Average Price : ${result_averages[0]:,.2f}")
    st.sidebar.write(f"Average Security Deposit: ${result_averages[1]:,.2f}")
    st.sidebar.write(f"Average Cleaning Fee: ${result_averages[2]:,.2f}")
else:
    pass
    #st.sidebar.warning("No data available for the selected filters.")


query3 = f"SELECT SUM(AvgValues) as Total FROM (SELECT AVG(Price) + AVG(Security_deposit) + AVG(Cleaning_fee) as AvgValues FROM Airbnb WHERE Country='{country}' AND Room_type='{room}' AND Property_type='{property_type}') as subquery"

mycursor.execute(query3)
total_sum = mycursor.fetchone()

# Display the result
if total_sum and total_sum[0] is not None:
    st.sidebar.write(f"Total : ${total_sum[0]:,.2f}")
else:
    pass
    #st.sidebar.warning("No data available for the selected filters.")

# Dynamic SQL Query based on selected filters
#query = "SELECT Property_type, COUNT(*) as Count FROM Airbnb GROUP BY Property_type ORDER BY Count DESC LIMIT 10"
col1, col2 = st.columns(2)

with col1:
    query5 = f"SELECT Property_type, Price FROM airbnb WHERE Country = '{country}' GROUP BY Property_type ORDER BY Price DESC LIMIT 10 ;"
    mycursor.execute(query5)
    result_df = pd.DataFrame(mycursor.fetchall(), columns=['Property_type', 'Price'])

    fig = px.bar(result_df, x='Property_type', y='Price', title='Top 10 Property Types by Price')
    st.plotly_chart(fig, use_container_width=True)

    
with col2:
    query4 = f"SELECT Property_type, COUNT(*) as Count FROM Airbnb WHERE Country='{country}' GROUP BY Property_type ORDER BY Count DESC LIMIT 10"

    mycursor.execute(query4)
    result_df = pd.DataFrame(mycursor.fetchall(), columns=['Property_type', 'Count'])

    fig = px.pie(result_df,
                title='Property Type by Count',
                names='Property_type',
                values='Count',
                color_discrete_sequence=px.colors.sequential.Rainbow
            )
    #fig.update_traces(textposition='inside', textinfo='value+label')
    st.plotly_chart(fig,use_container_width=True)


col3, col4 = st.columns(2)

with col3:
    query5 = f"SELECT Room_type, Price FROM airbnb WHERE Country = '{country}' GROUP BY Room_type ORDER BY Price DESC LIMIT 10 ;"
    mycursor.execute(query5)
    result_df = pd.DataFrame(mycursor.fetchall(), columns=['Room_type', 'Price'])

    fig = px.bar(result_df, x='Room_type', y='Price', title='Room Types by Price')
    st.plotly_chart(fig, use_container_width=True)

    
with col4:
    query5 = f"SELECT Room_type, COUNT(*) as Count FROM Airbnb WHERE Country='{country}' GROUP BY Room_type ORDER BY Count DESC"

    mycursor.execute(query5)
    result_df = pd.DataFrame(mycursor.fetchall(), columns=['Room_type', 'Count'])

    fig = px.pie(result_df,
                title='Room Type by Count',
                names='Room_type',
                values='Count',
                color_discrete_sequence=px.colors.sequential.Rainbow
            )
    #fig.update_traces(textposition='inside', textinfo='value+label')
    st.plotly_chart(fig,use_container_width=True)

col5, col6 = st.columns(2)

with col5:
    query5 = f"SELECT Bed_type, Price FROM Airbnb WHERE Country='{country}' AND Room_type = '{room}' AND Property_type = '{property_type}' GROUP BY Bed_type ORDER BY Price DESC;"

    mycursor.execute(query5)
    result_df = pd.DataFrame(mycursor.fetchall(), columns=['Bed_type', 'Price'])

    fig = px.bar(result_df, x='Bed_type', y='Price', title='Bed Types by Price')
    st.plotly_chart(fig, use_container_width=True)

    
with col6:
    query6 = f"SELECT Bed_type, COUNT(*) as Count FROM Airbnb WHERE Country='{country}' AND Room_type = '{room}' AND Property_type = '{property_type}' GROUP BY Bed_type ORDER BY Count DESC;"

    mycursor.execute(query6)
    result_df = pd.DataFrame(mycursor.fetchall(), columns=['Bed_type', 'Count'])

    if not result_df.empty:
        fig = px.pie(result_df,
                    title='Bed Type by Count',
                    names='Bed_type',
                    values='Count',
                    color_discrete_sequence=px.colors.sequential.Rainbow
                )
        #fig.update_traces(textposition='inside', textinfo='value+label')
        st.plotly_chart(fig,use_container_width=True)

query6 = f"SELECT Bed_type, COUNT(*) as Count FROM Airbnb WHERE Country='{country}' AND Room_type = '{room}' AND Property_type = '{property_type}' GROUP BY Bed_type ORDER BY Count DESC;"

mycursor.execute(query6)
result_df = pd.DataFrame(mycursor.fetchall(), columns=['Bed_type', 'Count'])

if not result_df.empty:
# Plot using Plotly Express
    st.table(result_df)
    fig = px.bar(result_df, x='Bed_type', y='Count', title='Bed Types by Count')
    st.plotly_chart(fig, use_container_width=True)



query7 = f"SELECT Host_name, COUNT(*) as Count FROM Airbnb WHERE Country='{country}' GROUP BY Host_name ORDER BY Count DESC LIMIT 10;"

mycursor.execute(query7)
result_df = pd.DataFrame(mycursor.fetchall(), columns=['Host_name', 'Count'])

# Plot using Plotly Express
fig = px.bar(result_df, x='Host_name', y='Count', title='Top 10 Hosts by Country')
st.plotly_chart(fig, use_container_width=True)

