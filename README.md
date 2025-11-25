# Weather-app

A simple, intuitive, and responsive weather application built with **Python**, **HTML**, and **CSS**. The app fetches real-time weather data and forecasts for any location, displaying the information in a user-friendly interface. With lightweight and clean code, the Weather-app is ideal for anyone looking to access weather updates effortlessly.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)

---

## Getting Started

This Python-based weather app retrieves weather data through external APIs and displays it in a web interface. Follow the steps below to set up the application on your local machine.

---

### Prerequisites

To run this project, make sure you have the following installed:

- **Python** (Version 3.8 or higher)
- **pip** (Python's package manager)
- (Optional) **virtualenv** (for creating an isolated Python environment)
- A valid weather API key (e.g., from [OpenWeatherMap](https://openweathermap.org/api) or another supported provider)

---

### Installation

#### For Linux:

1. **Clone the Repository**

   Download this repository to your local system:

   ```bash
   git clone https://github.com/HoomanMoradnia/Weather-app.git
   cd Weather-app
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**

   To create an isolated Python environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Required Dependencies**

   Use `pip` to install the necessary packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory of the project and add the following:

   ```bash
   WEATHER_API_KEY=your_api_key_here
   ```

   Replace `your_api_key_here` with your weather data API key.

5. **Run the Application**

   Start the application by running the main Python file (e.g., `app.py`):

   ```bash
   python app.py
   ```

6. **Access the Application**

   Open your browser and navigate to the provided address, such as `http://localhost:5000`.

---

#### For Windows:

1. **Clone the Repository**

   Download this repository to your local system:

   ```bash
   git clone https://github.com/HoomanMoradnia/Weather-app.git
   cd Weather-app
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**

   To create an isolated Python environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Required Dependencies**

   Use `pip` to install the necessary packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory of the project and add the following:

   ```bash
   WEATHER_API_KEY=your_api_key_here
   ```

   Replace `your_api_key_here` with your weather data API key. Alternatively, you can configure it in an `Environment Variables` GUI via system settings.

5. **Run the Application**

   Start the application by running the main Python file (e.g., `app.py`):

   ```bash
   python app.py
   ```

6. **Access the Application**

   Open your browser and navigate to the provided address, such as `http://localhost:5000`.

---

## About the Project

This project uses the following technologies:

- **Python**: Used for API requests and backend logic
- **HTML** & **CSS**: Used to create the user interface and styling

#### Key Features:

- Fetches real-time weather data for any city or geolocation
- Displays current weather conditions (e.g., temperature, humidity, wind speed)
- Forecast data for the upcoming days
- Clean and responsive design for web

Feel free to modify and extend the application for additional features or integrate it with other APIs.

---

If you encounter any issues during setup or run into bugs, please open an [issue](https://github.com/HoomanMoradnia/Weather-app/issues). Contributions and improvements are welcome!
