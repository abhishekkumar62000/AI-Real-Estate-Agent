import streamlit as st
# --- Set page config FIRST, before anything else ---
st.set_page_config(
    page_title="AI Real Estate Agent",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for dark colorful theme and button animation ---
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #232526 0%, #414345 100%);
        color: #f3f3f3;
    }
    .main {
        background: rgba(30,30,40,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 32px 0 rgba(0,0,0,0.25);
        padding: 16px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        box-shadow: 0 2px 8px 0 rgba(221,36,118,0.2);
        transition: transform 0.2s, box-shadow 0.2s;
        animation: pulse 1.5s infinite;
    }
    .stButton > button:hover {
        transform: scale(1.07);
        box-shadow: 0 4px 16px 0 rgba(255,81,47,0.3);
        background: linear-gradient(90deg, #dd2476 0%, #ff512f 100%);
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(221,36,118,0.4); }
        70% { box-shadow: 0 0 0 10px rgba(221,36,118,0); }
        100% { box-shadow: 0 0 0 0 rgba(221,36,118,0); }
    }
    .stSidebar .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: #fff;
        border-radius: 8px;
        font-weight: bold;
        animation: pulse 1.5s infinite;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
    }
    .stSidebar {
        background: #232526;
        color: #f3f3f3;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ff512f;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
    }
    .stMarkdown p, .stMarkdown ul, .stMarkdown li {
        color: #f3f3f3;
        font-size: 1.05rem;
    }
    .stDataFrame {
        background: #232526;
        color: #fff;
        border-radius: 10px;
    }
    .stCaption {
        color: #dd2476;
        font-size: 1.1rem;
        font-style: italic;
        font-family: 'Montserrat', sans-serif;
    }
    .stDivider {
        border-top: 2px solid #ff512f;
        margin-top: 18px;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
from typing import Dict, List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st
import os
from dotenv import load_dotenv
import base64

## Use Streamlit secrets for API keys (for Streamlit Cloud deployment)
# Remove dotenv loading

class PropertyData(BaseModel):
    """Schema for property data extraction"""
    building_name: str = Field(description="Name of the building/property", alias="Building_name")
    property_type: str = Field(description="Type of property (commercial, residential, etc)", alias="Property_type")
    location_address: str = Field(description="Complete address of the property")
    price: str = Field(description="Price of the property", alias="Price")
    description: str = Field(description="Detailed description of the property", alias="Description")

class PropertiesResponse(BaseModel):
    """Schema for multiple properties response"""
    properties: List[PropertyData] = Field(description="List of property details")

class LocationData(BaseModel):
    """Schema for location price trends"""
    location: str
    price_per_sqft: float
    percent_increase: float
    rental_yield: float

class LocationsResponse(BaseModel):
    """Schema for multiple locations response"""
    locations: List[LocationData] = Field(description="List of location data points")

class FirecrawlResponse(BaseModel):
    """Schema for Firecrawl API response"""
    success: bool
    data: Dict
    status: str
    expiresAt: str

class PropertyFindingAgent:
    """Agent responsible for finding properties and providing recommendations"""
    
    def __init__(self, firecrawl_api_key: str, openai_api_key: str, model_id: str = "gpt-3.5-turbo"):
        self.agent = Agent(
            model=OpenAIChat(id=model_id, api_key=openai_api_key),
            markdown=True,
            description="I am a real estate expert who helps find and analyze properties based on user preferences."
        )
        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

    def find_properties(
        self,
        city: str,
        max_price: float,
        property_category: str = "Residential",
        property_type: str = "Flat"
    ) -> str:
        """Find and analyze properties based on user preferences (optimized for low token usage)"""
        formatted_location = city.lower().strip()
        # Validate city input
        if not city or not formatted_location or len(formatted_location) < 2:
            return "No valid city name provided. Please enter a valid city name."
        urls = [
            f"https://www.squareyards.com/sale/property-for-sale-in-{formatted_location}/*",
            f"https://www.99acres.com/property-in-{formatted_location}-ffid/*",
            f"https://housing.com/in/buy/{formatted_location}/{formatted_location}",
        ]
        # Remove URLs if city is empty or contains invalid characters
        urls = [url for url in urls if city and formatted_location and '*' not in city and formatted_location.isalpha()]
        if not urls:
            return "No valid property listing URLs found for this city. Please check the city name or try a different one."
        property_type_prompt = "Flats" if property_type == "Flat" else "Individual Houses"
        try:
            raw_response = self.firecrawl.extract(
                urls=urls,
                prompt=f"Extract up to 5 {property_category} {property_type_prompt} in {city} under {max_price} crores. Return only essential details: name, location, price, key features. Format as a list.",
                schema=PropertiesResponse.model_json_schema()
            )
            print("Raw Firecrawl Response:", raw_response)
            if isinstance(raw_response, dict) and raw_response.get('success'):
                properties = raw_response['data'].get('properties', [])
            else:
                properties = []
            print("Properties:", properties)
            # Short, focused analysis prompt
            analysis = self.agent.run(
                f"""Analyze these properties for a buyer:
Properties: {properties}
1. List 3-5 best matches with name, location, price, and 1-2 key features each.
2. Which is best value and why?
3. Top 2 recommendations for investment.
4. One negotiation tip for each.
Keep response short and structured."""
            )
            print("AI Analysis:", analysis.content)
            return analysis.content
        except Exception as e:
            if "No valid URLs found to scrape" in str(e):
                return "No valid property listings found for this city. Please check the city name or try a different one."
            print("Error in find_properties:", e)
            return f"Error: {str(e)}"

    def get_location_trends(self, city: str) -> str:
        """Get price trends for different localities in the city (optimized for low token usage)"""
        try:
            raw_response = self.firecrawl.extract(
                urls=[f"https://www.99acres.com/property-rates-and-price-trends-in-{city.lower()}-prffid/*"],
                prompt="Extract price trends for up to 5 key localities in the city. Return only: name, price per sqft, percent increase, rental yield.",
                schema=LocationsResponse.model_json_schema()
            )
            print("Raw Firecrawl Location Response:", raw_response)
            if isinstance(raw_response, dict) and raw_response.get('success'):
                locations = raw_response['data'].get('locations', [])
            else:
                locations = []
            print("Locations:", locations)
            analysis = self.agent.run(
                f"""Summarize price trends for these locations in {city}:
Locations: {locations}
1. List 3-5 locations with price per sqft and percent increase.
2. Which is best for investment and why?
3. One tip for investors.
Keep response short."""
            )
            print("AI Location Analysis:", analysis.content)
            return analysis.content
        except Exception as e:
            print("Error in get_location_trends:", e)
            return f"Error: {str(e)}"

def create_property_agent():
    """Create PropertyFindingAgent with API keys from session state"""
    if 'property_agent' not in st.session_state:
        st.session_state.property_agent = PropertyFindingAgent(
            firecrawl_api_key=st.session_state.firecrawl_key,
            openai_api_key=st.session_state.openai_key,
            model_id=st.session_state.model_id
        )

def main():
    # --- Personalized Property Alerts (Sidebar) ---
    st.sidebar.markdown("<h2 style='color:#ff512f;'>🔔 Property Alerts</h2>", unsafe_allow_html=True)
    alert_email = st.sidebar.text_input("Email for Alerts", help="Enter your email to get property alerts")
    if st.sidebar.button("Save Search & Get Alerts"):
        with open("saved_searches.txt", "a") as f:
            f.write(f"{alert_email},{city},{property_category},{property_type},{max_price}\n")
        st.sidebar.success("Your search criteria has been saved! You'll get alerts when new properties match.")
    st.sidebar.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
    st.sidebar.markdown("<h3 style='color:#dd2476;'>🎛️ Advanced Filters</h3>", unsafe_allow_html=True)
    min_price = st.sidebar.number_input("Min Price (Crores)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    max_age = st.sidebar.slider("Max Property Age (years)", min_value=0, max_value=50, value=20)
    amenities = st.sidebar.multiselect("Amenities", ["Gym", "Pool", "Parking", "Security", "Garden", "Lift", "Clubhouse"])
    builder_reputation = st.sidebar.selectbox("Builder Reputation", ["Any", "Top Rated", "Established", "Newcomer"])
    sort_by = st.sidebar.selectbox("Sort By", ["Price: Low to High", "Price: High to Low", "Newest", "Best Amenities"])
    st.sidebar.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
    # --- Property Comparison Dashboard ---
    st.markdown("<h2 style='color:#ff512f;'>🏆 Property Comparison Dashboard</h2>", unsafe_allow_html=True)
    import re
    def extract_properties_for_comparison(text):
        pattern = r"-?\s*Name: ([^\n]+)\s*Location: ([^\n]+)\s*Price: ([^\n]+)"
        matches = re.findall(pattern, text)
        return matches
    properties_list = extract_properties_for_comparison(st.session_state.get('property_results', ''))
    if not properties_list:
        properties_list = extract_properties_for_comparison(''.join([str(x) for x in st.session_state.values() if isinstance(x, str)]))
    if properties_list:
        prop_names = [f"{name} ({location})" for name, location, price in properties_list]
        selected = st.multiselect("Select properties to compare", prop_names)
        compare_data = []
    # --- Saved Favorites & Shortlist ---
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    st.sidebar.markdown("<h3 style='color:#ff512f;'>⭐ Saved Favorites</h3>", unsafe_allow_html=True)
    if st.sidebar.button("View My Shortlist"):
        if st.session_state.favorites:
            st.sidebar.success(f"You have {len(st.session_state.favorites)} saved properties.")
            for idx, fav in enumerate(st.session_state.favorites):
                st.sidebar.markdown(f"<div style='background:#232526;border-radius:8px;padding:8px;margin-bottom:6px;'><b style='color:#ff512f;'>{fav['Name']}</b><br><span style='color:#f3f3f3;'>{fav['Location']}</span><br><span style='color:#dd2476;'>Price: {fav['Price']}</span></div>", unsafe_allow_html=True)
            st.sidebar.download_button("Export Shortlist (CSV)", data='\n'.join([f"{f['Name']},{f['Location']},{f['Price']}" for f in st.session_state.favorites]), file_name="shortlist.csv")
        else:
            st.sidebar.info("No favorites yet. Star properties to save them!")
        for idx, prop in enumerate(properties_list):
            name, location, price = prop
            if f"{name} ({location})" in selected:
                compare_data.append({"Name": name, "Location": location, "Price": price})
        if compare_data:
            st.dataframe(compare_data)
        else:
            st.info("Select properties above to compare.")
    else:
        st.info("No properties available for comparison yet.")
    # --- End Comparison Dashboard ---
    # ...existing code...

    # Get API keys from Streamlit secrets
    firecrawl_key = st.secrets.get("FIRECRAWL_API_KEY", "")
    openai_key = st.secrets.get("OPENAI_API_KEY", "")
    default_model = st.secrets.get("OPENAI_MODEL_ID", "gpt-3.5-turbo")

    # --- Sidebar Logo with Unique Style and Animation ---
    logo_path = os.path.join(os.path.dirname(__file__), "Logo.png")
    ai_logo_path = os.path.join(os.path.dirname(__file__), "AI.png")
    encoded_logo = None
    encoded_ai_logo = None
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
    if os.path.exists(ai_logo_path):
        with open(ai_logo_path, "rb") as image_file:
            encoded_ai_logo = base64.b64encode(image_file.read()).decode()

    with st.sidebar:
        if encoded_logo:
            st.markdown(
                f"""
                <style>
                @keyframes colorfulGlow {{
                    0% {{ box-shadow: 0 0 24px #ffd200, 0 0 0px #00c6ff; filter: hue-rotate(0deg); }}
                    25% {{ box-shadow: 0 0 32px #00c6ff, 0 0 12px #f7971e; filter: hue-rotate(90deg); }}
                    50% {{ box-shadow: 0 0 40px #f7971e, 0 0 24px #ffd200; filter: hue-rotate(180deg); }}
                    75% {{ box-shadow: 0 0 32px #00c6ff, 0 0 12px #ffd200; filter: hue-rotate(270deg); }}
                    100% {{ box-shadow: 0 0 24px #ffd200, 0 0 0px #00c6ff; filter: hue-rotate(360deg); }}
                }}
                .colorful-animated-logo {{
                    animation: colorfulGlow 2.5s linear infinite;
                    transition: box-shadow 0.3s, filter 0.3s;
                    border-radius: 30%;
                    box-shadow: 0 2px 12px #00c6ff;
                    border: 2px solid #ffd200;
                    background: #232526;
                    object-fit: cover;
                }}
                .sidebar-logo {{
                    text-align: center;
                    margin-bottom: 12px;
                }}
                </style>
                <div class='sidebar-logo'>
                    <img class='colorful-animated-logo' src='data:image/png;base64,{encoded_logo}' alt='Logo' style='width:150px;height:150px;'>
                    <div style='color:#00c6ff;font-size:1.1em;font-family:sans-serif;font-weight:bold;text-shadow:0 1px 6px #ffd200;margin-top:8px;'>Visualization Saathi</div>
                </div>
                <!-- Second logo below the first -->
                <div class='sidebar-AI' style='margin-top:0;'>
                    {f"<img src='data:image/png;base64,{encoded_ai_logo}' alt='AI' style='width:210px;height:220px;border-radius:30%;box-shadow:0 2px 12px #00c6ff;border:2px solid #ffd200;margin-bottom:8px;background:#232526;object-fit:cover;'>" if encoded_ai_logo else "<div style='color:#ff4b4b;'>AI.png not found</div>"}
                    <div style='color:#00c6ff;font-size:1.1em;font-family:sans-serif;font-weight:bold;text-shadow:0 1px 6px #ffd200;margin-top:8px;'></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Developer info and image below the logos
            st.markdown("<div style='text-align:center;font-size:1.1em;margin-top:10px;'>👨👨‍💻<b>Developer:</b> Abhishek💖Yadav</div>", unsafe_allow_html=True)
            developer_path = os.path.join(os.path.dirname(__file__), "pic.jpg")
            if os.path.exists(developer_path):
                st.image(developer_path, caption="Abhishek Yadav", use_container_width=True)
            else:
                st.warning("pic.jpg file not found. Please check the file path.")
        else:
            st.markdown(
                "<div style='text-align:center;font-size:2em;margin:16px 0;'>🚀</div><div style='text-align:center;color:#00c6ff;font-weight:bold;'>NewsCraft.AI</div>",
                unsafe_allow_html=True
            )
        # ...existing sidebar code...

    st.markdown("""
        <div style='text-align:center;padding:18px 0 8px 0;'>
            <h1 style='color:#ff512f;font-family:Montserrat,sans-serif;font-size:2.7rem;margin-bottom:0;'>🏠 AI Real Estate Agent</h1>
            <span class='stCaption'>Find your dream property with AI-powered insights, trends, and recommendations.<br> <span style='color:#dd2476;font-weight:bold;'>"Smart Search. Smarter Investment."</span></span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
    st.info(
        """
        Welcome to the AI Real Estate Agent! 
        Enter your search criteria below to get property recommendations 
        and location insights.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input(
            "🏙️ City",
            placeholder="Enter city name (e.g., Bangalore)",
            help="Enter the city where you want to search for properties"
        )
        property_category = st.selectbox(
            "🏢 Property Category",
            options=["Residential", "Commercial"],
            help="Select the type of property you're interested in"
        )
    with col2:
        max_price = st.number_input(
            "💰 Maximum Price (in Crores)",
            min_value=0.1,
            max_value=100.0,
            value=5.0,
            step=0.1,
            help="Enter your maximum budget in Crores"
        )
        property_type = st.selectbox(
            "🏠 Property Type",
            options=["Flat", "Individual House"],
            help="Select the specific type of property"
        )
    st.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
    if st.button("🔍 Start Search", use_container_width=True):
        if 'property_agent' not in st.session_state:
            st.error("⚠️ Please enter your API keys in the sidebar first!")
            return
        if not city:
            st.error("⚠️ Please enter a city name!")
            return
        try:
            with st.spinner("🔍 Searching for properties..."):
                property_results = st.session_state.property_agent.find_properties(
                    city=city,
                    max_price=max_price,
                    property_category=property_category,
                    property_type=property_type
                )
                st.session_state.property_results = property_results
                st.success("✅ Property search completed!")
                st.markdown("<h2 style='color:#dd2476;'>🏘️ Property Recommendations</h2>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:rgba(30,30,40,0.85);border-radius:12px;padding:18px;margin-bottom:12px;'>{property_results}</div>", unsafe_allow_html=True)
                # --- Interactive Map Visualization ---
                import folium
                from streamlit_folium import st_folium
                import re
                st.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#ff512f;'>🗺️ Interactive Property Map</h3>", unsafe_allow_html=True)
                def extract_properties(text):
                    pattern = r"-?\s*Name: ([^\n]+)\s*Location: ([^\n]+)\s*Price: ([^\n]+)"
                    matches = re.findall(pattern, text)
                    return matches
                properties = extract_properties(property_results)
                import requests
                def geocode(address):
                    try:
                        url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
                        resp = requests.get(url)
                        data = resp.json()
                        if data:
                            return float(data[0]['lat']), float(data[0]['lon'])
                    except:
                        return None, None
                    return None, None
                city_lat, city_lon = geocode(city)
                m = folium.Map(location=[city_lat or 20.5937, city_lon or 78.9629], zoom_start=12, tiles="CartoDB dark_matter")
                for name, location, price in properties:
                    lat, lon = geocode(location)
                    if lat and lon:
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"<b>{name}</b><br>{location}<br>Price: {price}",
                            tooltip=name,
                            icon=folium.Icon(color="pink", icon="home", prefix="fa")
                        ).add_to(m)
                st_folium(m, width=700, height=500)
                # --- End Map Visualization ---
                st.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
                with st.spinner("📊 Analyzing location trends..."):
                    location_trends = st.session_state.property_agent.get_location_trends(city)
                    st.success("✅ Location analysis completed!")
                    with st.expander("📈 Location Trends Analysis of the city"):
                        st.markdown(location_trends)

                # --- Interactive Location Heatmap ---
                st.markdown("<hr class='stDivider'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#dd2476;'>🔥 Location Price & Yield Heatmap</h3>", unsafe_allow_html=True)
                import re
                import folium
                from streamlit_folium import st_folium
                import pandas as pd
                pattern = r"-?\s*Location: ([^\n]+)\s*Price per sqft: ([\d.]+)\s*Percent increase: ([\d.]+)%\s*Rental yield: ([\d.]+)%"
                matches = re.findall(pattern, location_trends)
                heat_data = []
                for loc, price, inc, yield_ in matches:
                    import requests
                    try:
                        url = f"https://nominatim.openstreetmap.org/search?format=json&q={loc} {city}"
                        resp = requests.get(url)
                        data = resp.json()
                        if data:
                            lat, lon = float(data[0]['lat']), float(data[0]['lon'])
                            heat_data.append({"Location": loc, "lat": lat, "lon": lon, "Price": float(price), "Increase": float(inc), "Yield": float(yield_)})
                    except:
                        continue
                if heat_data:
                    m_heat = folium.Map(location=[city_lat or 20.5937, city_lon or 78.9629], zoom_start=12, tiles="CartoDB dark_matter")
                    from folium.plugins import HeatMap
                    heat_points = [[d["lat"], d["lon"], d["Price"]] for d in heat_data]
                    HeatMap(heat_points, radius=18, blur=12, min_opacity=0.5, max_zoom=1).add_to(m_heat)
                    for d in heat_data:
                        folium.CircleMarker(
                            location=[d["lat"], d["lon"]],
                            radius=8,
                            color="#dd2476",
                            fill=True,
                            fill_color="#ff512f",
                            popup=f"{d['Location']}<br>Price/sqft: ₹{d['Price']}<br>Yield: {d['Yield']}%",
                        ).add_to(m_heat)
                    st_folium(m_heat, width=700, height=500)
                    st.caption("Color intensity shows price per sqft. Pink circles show rental yield.")
                else:
                    st.info("No location trend data available for heatmap.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
