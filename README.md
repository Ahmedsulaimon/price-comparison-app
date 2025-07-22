# Grocery Price Comparison App

This application compares grocery prices from different UK retailers, recommends the best-value options, and provides predictive insights on what grocery prices might be for the following week.

## Tech Stack Used 

### Backend
- **Python**
  - Flask (API Gateway, microservices)
  - FastAPI (optional microservices or scraping endpoints)
- **Selenium + Headless Chrome** (for web scraping)
- **Docker** (for containerization of services)

### Frontend
- **Flutter** (cross-platform mobile app)

### Database
- **PostgreSQL**

### Testing
- **pytest** (unit testing for backend components)

---

## Application Architecture 

- **Microservice Architecture**
  - Separate services for product management, scraping, ML prediction, API Gateway, etc.
  - All services are containerized using **Docker** and orchestrated via **Docker Compose**

---

## How To Run Application

1.  **Clone the repository**
```bash
git clone https://github.com/Ahmedsulaimon/price-comparison-app
cd price-comparison-app
```
2. **Start backend services**
   ```bash
   docker-compose up --build
   ```
   - This will start all backend containers (API Gateway, microservices, database, etc.)
     
3. **Run the Flutter frontend**
   - Ensure you have Flutter installed and set up in your environment. 
   - Navigate to the frontend directory:
    ```bash
     cd frontend
   ```
    - run application
    ```bash
      flutter run
    ```
    - You can run this on an emulator or a connected device.
