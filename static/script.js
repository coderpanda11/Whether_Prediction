document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('city-input');
    const searchBtn = document.getElementById('search-btn');
    const cityElement = document.getElementById('city');
    const dateElement = document.getElementById('date');
    const temperatureElement = document.getElementById('temperature');
    const humidityElement = document.getElementById('humidity');
    const windSpeedElement = document.getElementById('wind-speed');

    // Update date
    const updateDate = () => {
        const now = new Date();
        dateElement.textContent = now.toLocaleDateString('en-IN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };
    updateDate();

    // Fetch weather data
    const getWeatherData = async (city) => {
        try {
            const response = await fetch('http://localhost:5000/backend/get_weather', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ city: city })
            });
            
            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            // Update current weather
            cityElement.textContent = city;
            temperatureElement.textContent = `${data.current.temperature}°C`;
            humidityElement.textContent = `${data.current.humidity}%`;
            windSpeedElement.textContent = `${data.current.windSpeed} km/h`;

            // Create forecast cards
            const forecastContainer = document.getElementById('forecast-container');
            forecastContainer.innerHTML = ''; // Clear previous forecasts

            data.forecast.forEach((day, index) => {
                const date = new Date();
                date.setDate(date.getDate() + index + 1);

                const card = document.createElement('div');
                card.className = 'weather-info forecast-card';
                card.innerHTML = `
                    <div class="location">
                        <h2>${city}</h2>
                        <p>${date.toLocaleDateString('en-IN', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        })}</p>
                    </div>
                    <div class="weather-data">
                        <div class="info-card">
                            <h3>Temperature</h3>
                            <p>${day.temperature}°C</p>
                        </div>
                        <div class="info-card">
                            <h3>Humidity</h3>
                            <p>${day.humidity}%</p>
                        </div>
                        <div class="info-card">
                            <h3>Wind Speed</h3>
                            <p>${day.windSpeed} km/h</p>
                        </div>
                    </div>
                `;
                forecastContainer.appendChild(card);
            });
        } catch (error) {
            alert('Error fetching weather data. Please try again.');
            console.error(error);
        }
    };

    // Event listeners
    searchBtn.addEventListener('click', () => {
        const city = cityInput.value.trim();
        if (city) {
            getWeatherData(city);
        }
    });

    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const city = cityInput.value.trim();
            if (city) {
                getWeatherData(city);
            }
        }
    });
});