import os
import re

files = [
    "app/templates/dashboard/manage_fields.html",
    "app/templates/dashboard/manage_roles.html",
    "app/templates/dashboard/results.html",
    "app/templates/dashboard/schema_builder.html",
    "app/templates/dashboard/student.html",
    "app/templates/dashboard/take.html",
    "app/templates/dashboard/test_form.html",
    "app/templates/dashboard/ui_builder_selector.html",
    "app/templates/superadmin/audit_logs.html",
    "app/templates/superadmin/base_superadmin.html",
    "app/templates/superadmin/create_tenant.html",
    "app/templates/superadmin/edit_tenant.html",
    "app/templates/superadmin/edit_user.html",
    "app/templates/superadmin/index.html",
    "app/templates/superadmin/tenants.html",
    "app/templates/superadmin/users.html"
]

replacements = [
    ("bg-white", "bg-white dark:bg-gray-800", "dark:bg-gray-800"),
    ("text-gray-800", "text-gray-800 dark:text-gray-100", "dark:text-gray-100"),
    ("text-gray-600", "text-gray-600 dark:text-gray-400", "dark:text-gray-400"),
    ("border-gray-200", "border-gray-200 dark:border-gray-700", "dark:border-gray-700"),
    ("hover:bg-gray-50", "hover:bg-gray-50 dark:hover:bg-gray-900", "dark:hover:bg-gray-900"),
    ("bg-gray-50", "bg-gray-50 dark:bg-gray-900", "dark:bg-gray-900"),
    ("bg-gray-100", "bg-gray-100 dark:bg-gray-700", "dark:bg-gray-700")
]

for file_path in files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    new_content = content
    for old, new, check in replacements:
        # Check if the dark variant already exists to avoid double replacement
        if check not in new_content:
            new_content = new_content.replace(old, new)
            
    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes for {file_path}")
