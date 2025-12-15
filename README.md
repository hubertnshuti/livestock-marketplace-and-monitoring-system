# 🐄 ItungoHub: National Livestock Marketplace Management System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Digitizing the Livestock Trade in Rwanda** > A bridge connecting rural farmers to urban markets through a secure, inquiry-based digital platform.

---

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [Screenshots](#-screenshots)
- [Meet the Team](#-meet-the-team)
- [License](#-license)

---

## 📝 About the Project

**ItungoHub** is a web-based platform designed to modernize the traditional livestock market (*Amabagiro*) in Rwanda. Currently, farmers face significant challenges including lack of market access, high transport costs, and reliance on middlemen. 

This system solves these problems by providing a centralized digital marketplace where:
1.  **Farmers** can list their herd, manage inventory, and receive direct inquiries.
2.  **Buyers** can search for verified livestock by species, location, and price.
3.  **Transactions** are secured through an **"Inquiry & Approval" workflow**, replacing the risky instant-buy model with a trust-based negotiation system suitable for the agricultural sector.

---

## 🌟 Key Features

### 🚜 For Farmers
* **Digital Herd Management:** specific forms to list animals with details like Tag ID, Weight, Age, and Breed.
* **Sales Dashboard:** Real-time tracking of "Total Livestock" vs. "Sold Items".
* **Inquiry Management:** Receive purchase requests, view buyer contact details securely, and Approve/Reject sales.
* **Revenue Tracking:** Monitor completed sales and income.

### 🛒 For Buyers
* **Advanced Marketplace:** Filter livestock by **Species** (Cattle, Goats, Pigs), **Location** (District/Sector), and **Price Range**.
* **Smart Cart:** A "Self-Healing" cart system that ensures accurate pricing calculations.
* **Pay-on-Delivery Workflow:** Place inquiries without immediate payment; pay only after the farmer approves and delivery is arranged.
* **Order History:** Track the status of requests from "Pending" to "Approved" to "Delivered".

### 🛡️ System & Admin
* **Role-Based Access Control (RBAC):** Distinct dashboards for Administrators, Farmers, and Buyers.
* **Secure Authentication:** Custom profile management for farming cooperatives and individual traders.

---

## 🏗 System Architecture

The project follows the **Model-View-Template (MVT)** architectural pattern standard in Django.

1.  **The View Layer:** Handles complex logic like the *Marketplace Filter Algorithm* (case-insensitive search) and the *Cart Calculation Engine*.
2.  **The Model Layer:** Uses a robust relational database schema linking `Farmers`, `LivestockItems`, `Orders`, and `OrderItems`.
3.  **The Template Layer:** Utilizes **Bootstrap 5** for a mobile-responsive design, essential for farmers accessing the site via smartphones.

---

## 💻 Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Django (Python) | Handles auth, ORM, and business logic. |
| **Frontend** | HTML5, CSS3, Bootstrap 5 | Responsive UI design and styling. |
| **Database** | SQLite / PostgreSQL | Relational data management. |
| **Templating** | Jinja2 (Django Templates) | Dynamic data rendering. |
| **Icons** | FontAwesome 6 | UI iconography. |
| **Version Control** | Git & GitHub | Source code management. |

---

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites
* Python 3.8 or higher
* Git

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/hubertnshuti/livestock-marketplace-system.git
    cd itungohub
    ```

2.  **Create a Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Database Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a Superuser (Admin)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Server**
    ```bash
    python manage.py runserver
    ```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 📖 Usage Guide

To test the different user roles, you can use the following logic or create new accounts:

### 1. The Buyer Flow
* **Register** as a new user and select "Buyer".
* Go to **Marketplace**, filter for "Cattle", and click "View Details".
* Add to **Cart** and proceed to **Checkout**.
* Enter your phone/address and submit. *Status becomes: Inquiry Sent*.

### 2. The Farmer Flow
* **Register** as a new user and select "Farmer".
* Go to **Dashboard** -> **Add Livestock** to list a new animal.
* Go to **Incoming Inquiries** to see the order placed by the buyer.
* Click the **Eye Icon** to view buyer details, then click **Approve**.

### 3. The Payment Simulation
* Log back in as the **Buyer**.
* Go to **My Orders**. The status is now "Approved".
* Click **Pay Now** to run the mobile money simulation.

---

## 📸 Screenshots

| Landing Page | Farmer Dashboard |
|:---:|:---:|
| <img src="docs/screenshots/home.png" alt="Home" width="400"> | <img src="docs/screenshots/dashboard.png" alt="Dashboard" width="400"> |

| Marketplace | Cart & Checkout |
|:---:|:---:|
| <img src="docs/screenshots/marketplace.png" alt="Marketplace" width="400"> | <img src="docs/screenshots/cart.png" alt="Cart" width="400"> |

---

## 👥 Meet the Team

This project was designed, developed, and documented by:

| Name | Role | Student ID |
| :--- | :--- | :--- |
| **Hubert Nshuti Ngendahayo** | Full Stack Developer | [Insert ID] |
| **Gilbert Nsengimana** | Database Architect | [Insert ID] |
| **Jean Baptiste Niyonshuti** | System Analyst | [Insert ID] |

> **University of Rwanda** > College of Science and Technology (CST)  
> *Department of Computer and Software Engineering*

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ in Kigali, Rwanda 🇷🇼
</p>
