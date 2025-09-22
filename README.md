CoffeeShop Admin Backend 🐍

Welcome to the **Coffee Admin Control Center** – your all-in-one backend for managing coffees, users, carts, and orders.  
Built with **FastAPI + MariaDB**, sprinkled with some extra beans for fun! 🚀

---

## ✨ Features

- 👤 **Admin Accounts** (Login/Signup with authentication)
- ☕ **Coffee Management**  
  - Add, update, remove products  
  - Auto-generate coffee IDs like `COF-2025-0001`
- 🛒 **User Carts**  
  - Firebase-linked users  
  - Add coffee products to cart  
- 📦 **Orders (soon)**  
  - Track order status, revenue, performance
- 🎨 **Dashboard Ready** – connect with your Flutter Admin UI

---

## ⚙️ Tech Stack
- 🐍 Python (FastAPI)
- 🐬 MariaDB / MySQL
- 📡 REST APIs
---

# run server
uvicorn main:app --reload --host 0.0.0.0 --port 8080
