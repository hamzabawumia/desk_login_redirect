# Desk Login Redirect

A Desk Login Redirect App for frappe 

#### License
MIT

---

# Problem Summary
### The Bug: Assigning a landing page route (e.g., /app/attendance) directly in the Role DocType via the UI does not consistently redirect users after login in v15.

### The Impact: Users are dumped onto a generic /users or user profile page, requiring manual navigation. 

# Solution Summary
We bypass the unreliable UI setting by implementing a custom Python hook that intercepts the login process at the server level.

Intercept Authentication: Use the on_session_creation for v15 hook in your custom app's hooks.py.

We use a Python function that:
    - Retrieves the user's roles.
    - Checks for a defined home_page for those roles in the database.
    - Force Redirect: Update frappe.local.flags.redirect_location and raise a frappe.Redirect exception to ensure the browser moves to the desired route immediately after the session is created. 

    
# 📘 Use Case Narrative: Desk Login Redirect

---

## 📌 Use Case: Role-Based Desk Landing Pages

### 🎯 Goal
Ensures that **System Users** (Desk Users) are automatically routed to a relevant Workspace, Report, or Dashboard upon login based on their assigned **Role**. This replaces the generic Frappe landing page with a department-specific interface, improving user efficiency across multiple apps.

---

### 👤 User Action
* User navigates to the login page.
* User enters their email/username and password.
* User clicks **Login**.

> **Note:** The redirect is transparent; the user does not perform any additional clicks to reach their specific dashboard.

---

### ⚙️ System Reaction

#### Step 1: Frontend / UI
* The standard Frappe Login Page handles credential collection.
* Because the redirect is triggered server-side during the authentication handshake, there is no "flicker" or secondary loading state on the frontend.

**Not trusted:**
* The browser's `localStorage` or session-cached URLs.
* Client-side route changes.

---

#### Step 2: Transport Layer
* The login request is processed via `/api/method/login`.
* Upon successful authentication, Frappe’s core triggers the **`on_session_creation`** hook (preferred in v15 for full session availability).
* The system passes the active `login_manager` instance to our custom app.

**Code location(s):**
* `apps/desk_login_redirect/desk_login_redirect/hooks.py`
* **Note:** Manually add `on_session_creation = "desk_login_redirect.utils.redirect_desk_user"` to the hooks file.

---

#### Step 3: Backend Logic
* The `redirect_desk_user` function executes the following logic:
    1. **Admin Bypass:** Checks if the user is `Administrator`. If so, it returns immediately to prevent locking the superuser out of the core desk.
    2. **Role Lookup:** Retrieves all roles assigned to the current user via `frappe.get_roles()`.
    3. **Database Query:** Searches the **Role** DocType for any assigned role that has a value in the `home_page` field.
    4. **Execution:** If a route is found, it sets the `frappe.local.flags.redirect_location` flag and raises **`frappe.Redirect`**.
    
    **Pathing:** When you enter the redirect in the Role DocType, use the full desk path (e.g., `/app/workspace/sales` or `/app/list/todo`).
    
    **Priority:** If a user has multiple roles with different home pages, `frappe.db.get_value` will return the first one it finds. If you want a specific role to "win," you can add `order_by="creation desc"` or a priority field to your query.

**Code location(s):**
* `apps/desk_login_redirect/desk_login_redirect/utils.py`

---

#### Step 4: Persistence
* The redirect destination is stored in the **Role** DocType database table (`tabRole`).
* Administrators can manage these routes via the [Frappe Desk UI](https://docs.api.frappe.io) by accessing the Role list and updating the `home_page` field.

---

### 🔒 Invariants
* **Non-Breaking:** If no `home_page` is defined for a user's roles, the system falls back to the default `/app` behavior.
* **Server-Side Authority:** The redirect logic is enforced before the Desk environment is initialized.
* **Centralization:** Even with 15+ apps installed, this single hook manages the entry point for the entire site.

---

### ❌ What This Use Case Does NOT Do
* **Website Portal Redirects:** Does not affect [Website Users](https://docs.frappe.io); it is strictly for internal System Users.
* **Conflict Resolution:** If a user has multiple roles with different home pages, the query picks the first match found in the database.

---

### ✅ Final Outcome
* Users land directly on their functional Workspace (e.g., `/app/accounting-workspace`).
* Improved security by directing users away from sensitive or irrelevant modules.
* Zero-code maintenance for adding new role-based redirects.

---

### 🧠 Key Takeaway
> By decoupling the redirect logic from the core apps and storing routes in the **Role** DocType, we provide a scalable "Traffic Control" system that is easy to audit and modify.
