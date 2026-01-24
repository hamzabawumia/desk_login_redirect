# apps/desk_login_redirect/desk_login_redirect/utils.py

import frappe
from frappe import Redirect
logger = frappe.logger("login_redirect")


def redirect_desk_user(login_manager):
    # login_manager is automatically provided by the on_session_creation hook
    user = login_manager.user
    logger.info(f"Login hook triggered for user: {user}")

    if user == "Administrator":
        return

    # Fetch roles for the user
    role_list = frappe.get_roles(user)

    # Query for a Role that has a defined home_page
    home_page = frappe.db.get_value("Role",
        {"name": ["in", role_list], "home_page": ["not in", ["", None]]},
        "home_page"
    )
    logger.info(f"Resolved home_page: {home_page}")

    if home_page:
        # Set the redirect location for the response
        frappe.local.flags.redirect_location = home_page

        logger.info(f"Redirecting {user} to {home_page}")
        # Force the redirect exception
        raise Redirect
