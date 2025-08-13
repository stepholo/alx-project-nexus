# Shopvana E-Commerce Backend

Shopvana is a robust backend system for an e-commerce platform, built with Django and Django REST Framework. It supports product catalog management, user authentication, order processing, payments, reviews, wishlists, and more. This project is designed for real-world scalability and maintainability, and is a portfolio-ready showcase for backend engineering skills.

---

## 🚀 Features

- **User Authentication:** JWT-based registration, login, and account activation.
- **Product Catalog:** CRUD operations, filtering, sorting, and pagination.
- **Cart & Orders:** Add to cart, checkout, order creation, and order tracking.
- **Payments:** Integration with Chapa for secure online payments.
- **Reviews & Wishlists:** Users can review products and manage wishlists.
- **Admin Panel:** Manage users, products, orders, and payments.
- **Asynchronous Tasks:** Celery for background jobs (e.g., email notifications, payment status checks).
- **Caching:** Redis for performance optimization.
- **API Documentation:** Swagger/OpenAPI for easy API exploration.
- **Testing:** Unit and integration tests for reliability.

---

## 🛠️ Tech Stack

| Tool/Library         | Purpose                                   |
|----------------------|-------------------------------------------|
| Python, Django       | Core backend framework                    |
| Django REST Framework| API development                           |
| PostgreSQL           | Relational database                       |
| JWT (SimpleJWT)      | Secure authentication                     |
| Celery + Redis       | Asynchronous tasks & caching              |
| Chapa                | Payment gateway integration               |
| Swagger, Postman     | API documentation & testing               |
| Docker (optional)    | Containerization                          |

---

## 📦 Project Structure

```
shopvana/
├── cart/           # Cart management
├── orders/         # Order and order items
├── payments/       # Payment processing
├── products/       # Product catalog
├── reviews/        # Product reviews
├── users/          # User accounts
├── utils/          # Utilities (email, permissions, tasks, templates)
├── wishlists/      # User wishlists
├── shopvana/       # Project settings and configuration
├── templates/      # Email and other templates
├── manage.py       # Django management script
```

---

## ⚡ Installation & Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/stepholo/shopvana.git
    cd shopvana
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv E-comm
    source E-comm/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
    - Copy `.env.example` to `.env` and fill in your secrets (DB, email, Chapa keys, etc.).

5. **Apply migrations:**
    ```sh
    python manage.py migrate
    ```

6. **Create a superuser (admin):**
    ```sh
    python manage.py createsuperuser
    ```

7. **Run the development server:**
    ```sh
    python manage.py runserver
    ```

8. **Start Celery worker and beat (for async tasks):**
    ```sh
    celery -A shopvana worker -l info
    celery -A shopvana beat -l info
    ```

---

## 📚 API Documentation

- **Swagger UI:** Visit `/swagger/` on your running server for interactive API docs.
- **Postman Collection:** Import the provided collection for testing endpoints.

---

## 📝 Usage

- **Register/Login:** Use `/api/auth/register/` and `/api/auth/token/` for user authentication.
- **Browse Products:** `/api/products/`
- **Add to Cart:** `/api/cart/`
- **Checkout:** `/api/orders/checkout/`
- **Make Payment:** `/api/payments/`
- **Order Tracking:** `/api/orders/{order_id}/`
- **Review Products:** `/api/reviews/`
- **Manage Wishlists:** `/api/wishlists/`

---

## 🧑‍💻 Author

**Stephen Oloo**
- [GitHub](https://github.com/stepholo)
- [LinkedIn](https://www.linkedin.com/in/stepholo0/)
- [X (Twitter)](https://x.com/Stevenob12)

---

## 📄 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this software as per the terms of the MIT License.

---

## 🙏 Acknowledgements

- ALX ProDev Software Engineering Program
- Django, DRF, Celery, Chapa, and all open-source contributors

---

## 💡 Notes

- For production, configure proper email, payment, and security settings.
- See `requirements.txt` for all dependencies.
- For any issues or contributions, please open an issue or pull request on GitHub.
