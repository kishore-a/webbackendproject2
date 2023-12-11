# CPSC 449 Project 2

## Group Members
* Kishore Shankar Abimanyu
* Bill Kenneth Gatchalian
* Zhihuang Chen

## Description
This project involves developing a backend system for managing access to cloud
services based on user subscriptions. The primary users of the system are Customers
who access cloud services and Admins who manage subscription plans and
permissions. The system will regulate access to various cloud APIs based on the
subscription plan purchased by the customer. If a customer exceeds the maximum limit
of a service as defined in their plan, access to that specific service will be temporarily
restricted.


## Requirements
python.exe -m pip install --upgrade pip

pip install fastapi uvicorn

pip install pymongo


## How to use
1. uvicorn main:app --reload
2. Once the server is running, you can access your API at http://localhost:8000.
3. FastAPI generates automatic documentation for your API, which you can access at http://localhost:8000/docs or http://localhost:8000/redoc.
4. You can test the endpoints using the Swagger UI at http://localhost:8000/docs.
   * Alternatively, you can use tools like curl, Postman, or any HTTP client to make requests to your API.


