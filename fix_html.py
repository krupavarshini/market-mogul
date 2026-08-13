# fix_html.py
import re

with open('app/templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 1: Fix broken nav
html = html.replace(
    """<button class="nav-item" onclick="nav('social')"><span class="nav-icon">💬</span>All</button> <button class="nav-item" onclick="nav('allcompanies')"><span class="nav-icon">🌐</span>All</button> <button class=""",
    """<button class="nav-item" onclick="nav('social')"><span class="nav-icon">💬</span>Chat</button>
<button class="nav-item" onclick="nav('allcompanies')"><span class="nav-icon">🌐</span>All</button>
<button class="""
)

# Fix 2: Fix renderPage
html = html.replace(
    "if(page==='companies' && token) loadMyCompanies(); if(page==='allcompanies' && token) loadAllCompanies();",
    "if(page==='companies' && token) loadMyCompanies();\nif(page==='allcompanies' && token) loadAllCompanies();"
)

with open('app/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("FIXED SUCCESSFULLY!")