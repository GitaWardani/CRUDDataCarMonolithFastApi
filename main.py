from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Database untuk menyimpan data mobil
cars_db = []

# Model Pydantic untuk Car
class Car(BaseModel):
    brand: str
    model: str
    year: int
    color: str

# Operasi CRUD

# Create Car
@app.post("/cars/", response_model=Car)
def create_car(car: Car):
    cars_db.append(car)
    return car

# Read All Cars
@app.get("/cars/", response_model=List[Car])
def read_cars():
    return cars_db

# Read Single Car
@app.get("/cars/{car_id}", response_model=Car)
def read_car(car_id: int):
    if car_id < 0 or car_id >= len(cars_db):
        raise HTTPException(status_code=404, detail="Car not found")
    return cars_db[car_id]

# Update Car
@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, updated_car: Car):
    if car_id < 0 or car_id >= len(cars_db):
        raise HTTPException(status_code=404, detail="Car not found")
    
    current_car = cars_db[car_id]
    current_car.brand = updated_car.brand
    current_car.model = updated_car.model
    current_car.year = updated_car.year
    current_car.color = updated_car.color
    
    return current_car

# Delete Car
@app.delete("/cars/{car_id}", response_model=Car)
def delete_car(car_id: int):
    if car_id < 0 or car_id >= len(cars_db):
        raise HTTPException(status_code=404, detail="Car not found")
    
    deleted_car = cars_db.pop(car_id)
    return deleted_car

# Serve files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML untuk antarmuka pengguna
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Car Inventory</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Car Inventory</h1>
    <div id="app">
        <ul>
            <li v-for="car in cars">
                {{ car.brand }} {{ car.model }} ({{ car.year }}, {{ car.color }})
                <button @click="deleteCar(car)">Delete</button>
            </li>
        </ul>
        <h2>Add New Car</h2>
        <form @submit.prevent="addCar">
            <label for="brand">Brand:</label>
            <input type="text" id="brand" v-model="newCar.brand" required>
            
            <label for="model">Model:</label>
            <input type="text" id="model" v-model="newCar.model" required>
            
            <label for="year">Year:</label>
            <input type="number" id="year" v-model="newCar.year" required>
            
            <label for="color">Color:</label>
            <input type="text" id="color" v-model="newCar.color" required>
            
            <button type="submit">Add Car</button>
        </form>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
    <script>
        new Vue({
            el: '#app',
            data: {
                cars: [],
                newCar: { brand: '', model: '', year: 0, color: '' }
            },
            mounted() {
                this.fetchCars();
            },
            methods: {
                fetchCars() {
                    fetch('/cars/')
                        .then(response => response.json())
                        .then(data => {
                            this.cars = data;
                        });
                },
                addCar() {
                    fetch('/cars/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(this.newCar)
                    })
                    .then(response => response.json())
                    .then(data => {
                        this.cars.push(data);
                        this.newCar = { brand: '', model: '', year: 0, color: '' };
                    });
                },
                deleteCar(car) {
                    const index = this.cars.indexOf(car);
                    if (index !== -1) {
                        fetch(`/cars/${index}`, {
                            method: 'DELETE'
                        })
                        .then(response => response.json())
                        .then(data => {
                            this.cars.splice(index, 1);
                        });
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

# Endpoint untuk halaman antarmuka pengguna
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=html_content, status_code=200)
