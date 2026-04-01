# Account Manager / Payroll System

A comprehensive payroll management system featuring a Django backend and a React (Vite) frontend.

## Prerequisites

- **Python**: 3.12 or higher
- **Node.js**: 20.19+ or 22.12+
- **npm**: (comes with Node.js)

## Project Structure

- `accnt_bknd/payroll_system`: Django backend services.
- `salary-frontend`: React frontend application.

---

## Backend Setup (Django)

1.  **Navigate to the backend directory**:
    ```bash
    cd accnt_bknd/payroll_system
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the Virtual Environment**:
    - macOS/Linux: `source venv/bin/activate`
    - Windows: `venv\Scripts\activate`

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Configuration**:
    Create a `.env` file in `accnt_bknd/payroll_system/` if it doesn't exist:
    ```env
    SECRET_KEY='your-secret-key'
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    ESSL_DEVICE_IP=192.168.1.201
    ESSL_DEVICE_PORT=4370
    ```

6.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

7.  **Start the Server**:
    ```bash
    python manage.py runserver
    ```
    The backend will be available at `http://127.0.0.1:8000/`.

---

## Frontend Setup (Vite/React)

1.  **Navigate to the frontend directory**:
    ```bash
    cd salary-frontend
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Environment Configuration**:
    Create a `.env` file in `salary-frontend/` if you need to point to a different backend URL:
    ```env
    VITE_API_BASE_URL=http://127.0.0.1:8000
    ```

4.  **Start the Development Server**:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173/` (or the port specified by Vite).

---

## Actions Required (For New Users)

- [ ] **Virtual Environment**: Always ensure you are working within the activated `venv` for backend tasks.
- [ ] **Secret Key**: Update the `SECRET_KEY` in the `.env` file for production environments.
- [ ] **ESSI Device**: Update `ESSL_DEVICE_IP` and `ESSL_DEVICE_PORT` in `.env` if using hardware integration.
- [ ] **API Endpoint**: If the backend port changes, update `VITE_API_BASE_URL` in `salary-frontend/.env`.
- [ ] **Node Version**: If you encounter Vite errors, ensure your Node.js version meets the requirement (20.19+).
