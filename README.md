<img width="1024" height="1024" alt="Logo" src="https://github.com/user-attachments/assets/f7b0a356-5fb7-4432-b27f-3791eae45998" />

<img width="1916" height="1080" alt="page" src="https://github.com/user-attachments/assets/1eaca249-c79e-4698-9de0-7b03df5b3e49" />

OUR WEB APP:-- https://ai-real-estate-agent.streamlit.app/



---

# 🏠 AI Real Estate Agent

AI Real Estate Agent is a powerful, user-friendly, AI-powered property search and analysis platform built with **Streamlit**. Whether you're an investor or a home seeker, this smart assistant makes discovering, comparing, and analyzing real estate properties easier than ever.

🔗 **Live App**: [ai-real-estate-agent.streamlit.app](https://ai-real-estate-agent.streamlit.app/)

---

## 🚀 App Introduction

**AI Real Estate Agent** is your smart property hunting companion powered by AI-driven insights, real-time trends, and rich visualizations.
This intelligent app transforms the real estate experience with automation, advanced filters, and personalized features—
designed with sleek modern UI, optimized performance, and intuitive flow for seamless exploration.
It’s more than just a listing tool — it’s your AI partner for smarter investment decisions.
Built for modern users, by a developer passionate about data-driven real estate.
Now live and ready to assist your next property decision.

---

## ✨ Core Features

### 🎨 Modern UI/UX

* Dark theme for an immersive experience
* Custom CSS-styled sidebar with logo, dev info, and animated buttons
* Clean, responsive design for better usability

### 🔌 Smart API Integration

* Integrates **Firecrawl API** for real-time property data
* Uses **OpenAI API** for AI-powered analysis and summaries
* All API keys securely managed via **Streamlit Secrets**

### 🔍 Property Search Engine

* Filter properties by:

  * City
  * Price range
  * Category (Residential / Commercial)
  * Type (Flat / Individual House)

### 🧠 Advanced Sidebar Filters

* Min/Max price
* Property age
* Available amenities
* Builder reputation score
* Sorting options (price, location, etc.)

### 📩 Personalized Alerts (Demo Logic)

* Save search criteria
* Get notified when matching properties are found *(demo feature)*

### 📊 Property Comparison Dashboard

* Select multiple properties
* Side-by-side comparison with detailed metrics

### ❤️ Favorites / Shortlist

* Add/remove properties to your favorite list
* View saved properties and export them as a **CSV file**

### 🗺️ Interactive Map View

* Visualize properties on a **dark-themed map** using **folium**
* Custom markers show price, type, and location details

### 📉 Location Trend Analysis

* AI-generated investment tips per city/locality
* Real-time price trend summaries

### 🔥 Heatmap Visualizations

* **Price per sqft**
* **Rental yield**
* Color-coded maps for quick investment decisions

### 🛠️ Error Handling

* Elegant, user-friendly alerts for:

  * Empty results
  * API timeouts
  * Invalid queries

### 🧩 Asset & Branding Support

* Displays developer image, brand logo, and app identity in the sidebar

---

## 🧑‍💻 Tech Stack

| Tech             | Purpose                               |
| ---------------- | ------------------------------------- |
| Streamlit        | UI and front-end app framework        |
| Firecrawl        | Property data scraping/API            |
| OpenAI           | AI-powered insights and summaries     |
| Pydantic         | Data validation and structuring       |
| Agno             | API utilities and simplified back-end |
| Folium           | Interactive map visualizations        |
| Pandas           | Data transformation and analytics     |
| streamlit-folium | Embedding folium into Streamlit UI    |

---

## ☁️ Deployment Ready

* Deployed on **Streamlit Cloud**
* Secure API management via **Streamlit Secrets**
* Optimized for scalability and low-latency performance

---

## 📸 Screenshots

*(Add screenshots here if you'd like — UI, map view, comparison, etc.)*

---

## 🙌 Contribution

If you'd like to contribute or suggest improvements, feel free to open issues or pull requests. This is an open project built to learn and help others explore real estate using smart AI.


Here is a complete **LangGraph-style Decision Tree Flow** of your 🏠 **AI Real Estate Agent** app, followed by a **GitHub README with LangGraph structure** for easy documentation and clarity.

---

## 🌐 LangGraph Decision Tree (AI Real Estate Agent App)

```mermaid
graph TD
  A[Start: App Launch] --> B[Sidebar UI Setup<br/>→ Custom CSS<br/>→ Dev Info<br/>→ Logo]
  B --> C[API Keys Load<br/>(Firecrawl & OpenAI via Streamlit Secrets)]

  C --> D[Main Screen: Search Page Loaded]

  D --> E[User Inputs City & Search Criteria]
  E --> F[Property API Call<br/>via Firecrawl]

  F --> G{Properties Found?}
  G -- Yes --> H[Display Property Cards<br/>→ Title, Price, Location, etc.]
  G -- No --> Z1[Error Handling: No Properties Found]

  H --> I[Sidebar Filters Applied<br/>→ Price Range<br/>→ Property Age<br/>→ Amenities<br/>→ Builder Reputation]
  I --> J[Properties Filtered & Refreshed]

  J --> K[User Action Options]
  
  K --> L1[Compare Properties<br/>→ Show Dashboard with Side-by-side Metrics]
  K --> L2[Shortlist Property<br/>→ Add to Favorites CSV]
  K --> L3[View on Map<br/>→ Folium Dark Map with Markers]
  K --> L4[Location Trend Analysis<br/>→ OpenAI Summary + Price Trend]
  K --> L5[Heatmap View<br/>→ Price/Sqft & Rental Yield]
  K --> L6[Save Criteria for Alerts<br/>(Demo Logic)]

  L1 --> M[Continue Exploring]
  L2 --> M
  L3 --> M
  L4 --> M
  L5 --> M
  L6 --> M

  M --> N[End or New Search]
```

---


# 🏠 AI Real Estate Agent

AI-powered app to help users find the best properties with smart filters, trends, analysis, and visual insights.

🔗 **Live App**: [ai-real-estate-agent.streamlit.app](https://ai-real-estate-agent.streamlit.app/)

---

## 🔁 LangGraph Decision Flow

This project follows a step-by-step decision graph (like LangGraph) to guide users from entry to intelligent insights.

### 🪜 Step-by-Step Flow

1. **Start**
   - Load Sidebar
   - Apply custom UI (CSS, logos, developer info)

2. **API Integration**
   - Load API keys securely via `streamlit.secrets`
   - Connect to:
     - Firecrawl (property listings)
     - OpenAI (trend analysis)

3. **User Search Input**
   - City
   - Category (Residential/Commercial)
   - Property Type (Flat/House)
   - Price Range

4. **Property Results**
   - Display results with title, price, city, and filters
   - If not found, show user-friendly error message

5. **Advanced Filters**
   - Property age
   - Amenities
   - Builder reputation
   - Price range adjustments
   - Sorting (High to Low, etc.)

6. **Interactive Options**
   - 🟢 **Compare Properties** → Detailed dashboard view
   - ❤️ **Favorites** → Save and export as CSV
   - 🗺️ **Map View** → Visualize locations using Folium
   - 📊 **Trends** → Location-wise insights using OpenAI
   - 🔥 **Heatmaps** → Price/sqft & rental yield
   - 📩 **Alert Demo** → Simulated user notification setup

7. **Navigation**
   - Reset search
   - Modify filters
   - Repeat

---

## 💡 Features

- 🖤 Modern UI/UX (Dark theme)
- 🔌 Firecrawl + OpenAI API Integration
- 🏘️ City-wise Search & Filters
- 📊 Comparison, Favorites, and Smart Filters
- 🗺️ Interactive Mapping
- 📈 Trend Analysis & Heatmaps
- 🛠️ Error Handling + UX Enhancements
- ✅ Deployment-ready with Streamlit Cloud

---

## 🔧 Tech Stack

| Tool            | Use                              |
|-----------------|----------------------------------|
| Streamlit       | Frontend/App Framework           |
| Firecrawl API   | Real estate listings             |
| OpenAI API      | Location insights/summaries      |
| Pydantic        | Data structure/validation        |
| Agno            | Backend utils                    |
| Folium          | Map + heatmap visualizations     |
| Pandas          | Data cleaning, CSV export        |
| streamlit-folium| Folium integration in UI         |

---

## 🚀 Deployment

- ✅ Streamlit Cloud Compatible
- 🔐 Streamlit Secrets for secure API keys

---

## 🧑‍💻 Author

Developed by **Abhishek Kr Yadav**  
_"Smart Search. Smarter Investment."_

---

## 📎 License

MIT License (or your preferred)

---

## 📌 Note

This app is a working prototype for real estate exploration and is intended for demo/educational purposes. Data accuracy depends on APIs.

---

---

## 👨‍💻 Developer

Made with 💡 and ☕ by **[Abhishek Kr Yadav](https://github.com/abhishekyadav001)**
*"Smart Search. Smarter Investment."*

---
