import requests

# -------- Add Volunteer --------
url = "http://127.0.0.1:5000/add_volunteer"
data = {"name": "Ramu", "latitude": 12.9716, "longitude": 77.5946}
response = requests.post(url, json=data)
print("Add Volunteer:", response.json())

# -------- Add Patient --------
url = "http://127.0.0.1:5000/add_patient"
data = {"name": "Mrs. Meena", "latitude": 12.9700, "longitude": 77.5940}
response = requests.post(url, json=data)
print("Add Patient:", response.json())

# -------- Add Pharmacy --------
url = "http://127.0.0.1:5000/add_pharmacy"
data = {"name": "Green Pharmacy","latitude": 12.9720,"longitude": 77.5950,"medicine_name": "Paracetamol","quantity": 50}
response = requests.post(url, json=data)
print("Add Pharmacy:", response.json())

# -------- Request Nearest Volunteer --------
url = "http://127.0.0.1:5000/request_volunteer"
data = {"latitude": 12.9700, "longitude": 77.5940}
response = requests.post(url, json=data)
print("Nearest Volunteer:", response.json())

# -------- Request Medicine --------
url = "http://127.0.0.1:5000/request_medicine"
data = {"medicine_name": "Paracetamol","latitude": 12.9700,"longitude": 77.5940,"quantity": 5}
response = requests.post(url, json=data)
print("Request Medicine:", response.json())