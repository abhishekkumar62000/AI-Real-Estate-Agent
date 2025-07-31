from typing import Dict, List
from pydantic import BaseModel, Field
from agno.agent import Agent 
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st
import os
from dotenv import load_dotenv 
 
# Load environment variables from .env file if it exists 
load_dotenv()

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
        formatted_location = city.lower()
        urls = [
            f"https://www.squareyards.com/sale/property-for-sale-in-{formatted_location}/*",
            f"https://www.99acres.com/property-in-{formatted_location}-ffid/*",
            f"https://housing.com/in/buy/{formatted_location}/{formatted_location}",
        ]
        property_type_prompt = "Flats" if property_type == "Flat" else "Individual Houses"
        raw_response = self.firecrawl.extract(
            urls=urls,
            prompt=f"Extract up to 5 {property_category} {property_type_prompt} in {city} under {max_price} crores. Return only essential details: name, location, price, key features. Format as a list.",
            schema=PropertiesResponse.model_json_schema()
        )
        if isinstance(raw_response, dict) and raw_response.get('success'):
            properties = raw_response['data'].get('properties', [])
        else:
            properties = []
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
        return analysis.content

    def get_location_trends(self, city: str) -> str:
        """Get price trends for different localities in the city (optimized for low token usage)"""
        raw_response = self.firecrawl.extract(
            urls=[f"https://www.99acres.com/property-rates-and-price-trends-in-{city.lower()}-prffid/*"],
            prompt="Extract price trends for up to 5 key localities in the city. Return only: name, price per sqft, percent increase, rental yield.",
            schema=LocationsResponse.model_json_schema()
        )
        if isinstance(raw_response, dict) and raw_response.get('success'):
            locations = raw_response['data'].get('locations', [])
            analysis = self.agent.run(
                f"""Summarize price trends for these locations in {city}:
Locations: {locations}
1. List 3-5 locations with price per sqft and percent increase.
2. Which is best for investment and why?
3. One tip for investors.
Keep response short."""
            )
            return analysis.content
        return "No price trends data available"

def create_property_agent():
    """Create PropertyFindingAgent with API keys from session state"""
    if 'property_agent' not in st.session_state:
        st.session_state.property_agent = PropertyFindingAgent(
            firecrawl_api_key=st.session_state.firecrawl_key,
            openai_api_key=st.session_state.openai_key,
            model_id=st.session_state.model_id
        )

def main():
    st.set_page_config(
        page_title="AI Real Estate Agent",
        page_icon="🏠",
        layout="wide"
    )

    # Get API keys from environment variables
    env_firecrawl_key = os.getenv("FIRECRAWL_API_KEY", "")
    env_openai_key = os.getenv("OPENAI_API_KEY", "")
    default_model = os.getenv("OPENAI_MODEL_ID", "gpt-3.5-turbo")

    with st.sidebar:
        st.title("🔑 API Configuration")
        st.subheader("🤖 Model Selection")
        model_id = st.selectbox(
            "Choose OpenAI Model",
            options=["gpt-3.5-turbo", "gpt-4-turbo"],
            index=0 if default_model == "gpt-3.5-turbo" else 1,
            help="Select a turbo model for best cost efficiency."
        )
        st.session_state.model_id = model_id
        st.divider()
        st.subheader("🔐 API Keys")
        if env_firecrawl_key:
            st.success("✅ Firecrawl API Key found in environment variables")
        if env_openai_key:
            st.success("✅ OpenAI API Key found in environment variables")
        firecrawl_key = st.text_input(
            "Firecrawl API Key (optional if set in environment)",
            type="password",
            help="Enter your Firecrawl API key or set FIRECRAWL_API_KEY in environment",
            value="" if env_firecrawl_key else ""
        )
        openai_key = st.text_input(
            "OpenAI API Key (optional if set in environment)",
            type="password",
            help="Enter your OpenAI API key or set OPENAI_API_KEY in environment",
            value="" if env_openai_key else ""
        )
        firecrawl_key = firecrawl_key or env_firecrawl_key
        openai_key = openai_key or env_openai_key
        if firecrawl_key and openai_key:
            st.session_state.firecrawl_key = firecrawl_key
            st.session_state.openai_key = openai_key
            create_property_agent()
        else:
            missing_keys = []
            if not firecrawl_key:
                missing_keys.append("Firecrawl API Key")
            if not openai_key:
                missing_keys.append("OpenAI API Key")
            if missing_keys:
                st.warning(f"⚠️ Missing required API keys: {', '.join(missing_keys)}")
                st.info("Please provide the missing keys in the fields above or set them as environment variables.")

    st.title("🏠 AI Real Estate Agent")
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
            "City",
            placeholder="Enter city name (e.g., Bangalore)",
            help="Enter the city where you want to search for properties"
        )
        
        property_category = st.selectbox(
            "Property Category",
            options=["Residential", "Commercial"],
            help="Select the type of property you're interested in"
        )

    with col2:
        max_price = st.number_input(
            "Maximum Price (in Crores)",
            min_value=0.1,
            max_value=100.0,
            value=5.0,
            step=0.1,
            help="Enter your maximum budget in Crores"
        )
        
        property_type = st.selectbox(
            "Property Type",
            options=["Flat", "Individual House"],
            help="Select the specific type of property"
        )

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
                
                st.success("✅ Property search completed!")
                
                st.subheader("🏘️ Property Recommendations")
                st.markdown(property_results)
                
                st.divider()
                
                with st.spinner("📊 Analyzing location trends..."):
                    location_trends = st.session_state.property_agent.get_location_trends(city)
                    
                    st.success("✅ Location analysis completed!")
                    
                    with st.expander("📈 Location Trends Analysis of the city"):
                        st.markdown(location_trends)
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
