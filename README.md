# Property Price Predictor (Frontend) 🏠

Real Estate Predictions Accessible Through Smart UI Design

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Geopy](https://img.shields.io/badge/Geopy-Geocoding-green?style=for-the-badge)](https://geopy.readthedocs.io)
[![Requests](https://img.shields.io/badge/Requests-2CA5E0?style=for-the-badge&logo=python&logoColor=white)](https://requests.readthedocs.io)

## The Story Behind This Project

### Making Real Estate Predictions Accessible Through Smart UI Design

Property price estimation shouldn't require technical expertise. This Streamlit-based frontend transforms complex machine learning predictions into an intuitive web interface where users simply input property details and receive instant price estimates backed by trained ML models.

---

## Table of Contents

- [Property Price Predictor (Frontend) 🏠](#property-price-predictor-frontend-)
  - [The Story Behind This Project](#the-story-behind-this-project)
    - [Making Real Estate Predictions Accessible Through Smart UI Design](#making-real-estate-predictions-accessible-through-smart-ui-design)
  - [Table of Contents](#table-of-contents)
  - [What Makes This Special](#what-makes-this-special)
  - [Technical Architecture](#technical-architecture)
  - [Features That Matter](#features-that-matter)
    - [User Experience](#user-experience)
    - [Property Input Capabilities](#property-input-capabilities)
    - [Technical Features](#technical-features)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Installation \& Setup](#installation--setup)
    - [1. Environment Setup](#1-environment-setup)
    - [2. Dependency Installation](#2-dependency-installation)
    - [3. Configuration Setup](#3-configuration-setup)
    - [4. Launch Application](#4-launch-application)
  - [Backend Integration](#backend-integration)
    - [Required API Endpoints](#required-api-endpoints)
    - [API Integration Features](#api-integration-features)
  - [Usage Guide](#usage-guide)
    - [Property Input Flow](#property-input-flow)
    - [Interactive Elements](#interactive-elements)
  - [Technology Stack](#technology-stack)
  - [Future Roadmap](#future-roadmap)
    - [User Experience Enhancements](#user-experience-enhancements)
    - [Data Integration](#data-integration)

## What Makes This Special

**Intuitive ML Interface**: Transforms complex property valuation models into a user-friendly web application that anyone can use without technical knowledge.

**Geographic Intelligence**: Integrates postcode-to-coordinates mapping with interactive visualizations to provide spatial context for property predictions.

**Production Architecture**: Demonstrates proper client-server separation with health checks, error handling, and configurable API endpoints.

**Real-Time Predictions**: Seamless integration with ML backend services for instant price estimates based on comprehensive property features.

## Technical Architecture

```
User Input Forms (Streamlit)
    ↓ Property Details
Input Validation & Processing
    ↓ Structured Data
API Client (Requests)
    ↓ HTTP POST
ML Prediction Backend
    ↓ Price Prediction
Results Visualization (Streamlit)
    ↓ Interactive UI
Geographic Mapping (Geopy)
```

**Key Components:**

- **Frontend**: Streamlit web application with custom styling
- **Data Layer**: Pandas for property data processing
- **Geocoding**: Geopy for location-based features
- **API Integration**: Requests library for backend communication
- **Visualization**: Interactive summary cards and map displays

## Features That Matter

### User Experience

- **Modern Interface**: Custom CSS styling with professional design aesthetics
- **Responsive Design**: Works across desktop and mobile devices
- **Interactive Elements**: Dynamic form updates and real-time feedback

### Property Input Capabilities

- **Comprehensive Forms**: Property type, subtype, location, and energy performance
- **Room Configuration**: Flexible bedroom, bathroom, and toilet count inputs
- **Surface Areas**: Separate inputs for habitable, terrace, and garden areas
- **Feature Toggles**: Binary options for amenities like lift, fireplace, pool, attic

### Technical Features

- **API Health Monitoring**: Real-time backend availability checking
- **Error Handling**: Graceful degradation when services are unavailable
- **Data Validation**: Input sanitization and type checking
- **Geographic Mapping**: Postal code visualization with coordinate lookup

## Project Structure

```
property-price-predictor-frontend/
├── app.py                                    # Main Streamlit application
├── data/                                     # Reference datasets
│   └── georef-belgium-postal-codes.csv     # Geographic reference data
├── .streamlit/                               # Streamlit configuration
│   └── secrets.toml                         # API endpoints (create this)
├── requirements.txt                          # Python dependencies
├── .gitignore                               # Version control exclusions
└── README.md                                # Project documentation
```

## Prerequisites

**Development Environment:**

- **Python 3.8+** with pip package manager
- **ML Prediction Backend** (separate service required)
- **Geographic Dataset** for postal code mapping

**API Requirements:**

- Backend service must expose health check and prediction endpoints
- Proper JSON response format for predictions
- CORS configuration for web client access

## Installation & Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/jgchoti/house-price-be.git
cd property-price-predictor-frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate     # Linux / macOS
venv\Scripts\activate        # Windows
```

### 2. Dependency Installation

```bash
# Install required packages
pip install -r requirements.txt

# Verify Streamlit installation
streamlit --version
```

### 3. Configuration Setup

Create `.streamlit/secrets.toml` for API configuration:

```toml
[predict_api]
base_url = "http://localhost:8000/"
predict_endpoint = "predict"

[app_settings]
theme = "light"
title = "Property Price Predictor"
```

### 4. Launch Application

```bash
# Start the Streamlit server
streamlit run app.py

# Application will be available at http://localhost:8501
```

## Backend Integration

### Required API Endpoints

**Health Check Endpoint:**

```
GET /
Response: {"status": "healthy", "timestamp": "..."}
```

**Prediction Endpoint:**

```
POST /predict
Content-Type: application/json

Request Body:
{
  "data": {
    "type": "APARTMENT",
    "subtype": "FLAT_STUDIO",
    "province": "Antwerp",
    "postCode": 2000,
    "epcScore": "C",
    "habitableSurface": 75.0,
    "terraceSurface": 10.0,
    "gardenSurface": 0.0,
    "bedroomCount": 2,
    "bathroomCount": 1,
    "toiletCount": 1,
    "hasLift": true,
    "hasFireplace": false
  }
}

Response:
{
  "prediction": 285000,
  "confidence": 0.87,
  "model_version": "v2.1"
}
```

### API Integration Features

**Connection Management:**

- Automatic health checks on startup
- Retry logic for failed requests
- Timeout handling for slow responses

**Data Transformation:**

- Frontend form data → API payload mapping
- Response parsing and validation
- Error message standardization

## Usage Guide

### Property Input Flow

1. **Basic Information**: Select property type (Apartment/House) and subtype
2. **Location Details**: Choose province and enter postal code
3. **Property Specifications**: Input surface areas and room counts
4. **Energy Performance**: Select EPC rating from dropdown
5. **Additional Features**: Toggle amenities like lift, fireplace, pool
6. **Price Prediction**: Click predict button for ML-generated estimate

### Interactive Elements

**Summary Cards**: Real-time display of entered property details
**Map Visualization**: Geographic context based on postal code
**Prediction Display**: Formatted price estimate with confidence metrics
**Error Handling**: User-friendly messages for invalid inputs or API issues

## Technology Stack

**Frontend Framework:**

- **Streamlit**: Modern web app framework for data science
- **Custom CSS**: Professional styling and responsive design

**Data Processing:**

- **Pandas**: Property data manipulation and validation
- **Geopy**: Geographic coordinate processing and mapping

**API Integration:**

- **Requests**: HTTP client for backend communication
- **JSON**: Data serialization for API payloads

**Deployment Ready:**

- **Requirements.txt**: Dependency management
- **Configuration Files**: Environment-based settings

## Future Roadmap

### User Experience Enhancements

- **Authentication System**: User accounts and saved property searches
- **Search History**: Previously entered properties and predictions
- **Comparison Tools**: Side-by-side property analysis features

### Data Integration

- **Additional Datasets**: Integration with more comprehensive property databases
- **Real-Time Market Data**: Current market trends and pricing indices
- **Historical Analysis**: Price trend visualization over time

Demo: [https://house-price-be.streamlit.app](https://house-price-be.streamlit.app/)
