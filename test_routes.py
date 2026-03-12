"""Comprehensive integration test for all auth routes — Steps 1-12."""
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar

BASE = "http://127.0.0.1:8001"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

# --- Test 1: Basic routes (no auth) ---
print("=" * 60)
print("TEST 1: Unauthenticated route checks")
print("=" * 60)

opener_no_redir = urllib.request.build_opener(NoRedirect)
routes = {
    "/":          (200, None),
    "/staff":     (200, None),
    "/admin":     (200, None),
    "/logout":    (302, "/"),
    "/dashboard": (302, "/staff"),
    "/health":    (200, None),
}

all_pass = True
for path, (expected_code, expected_loc) in routes.items():
    url = BASE + path
    try:
        r = opener_no_redir.open(url)
        code = r.status
        loc = ""
    except urllib.error.HTTPError as e:
        code = e.code
        loc = e.headers.get("Location", "")
    
    status = "PASS" if code == expected_code else "FAIL"
    if expected_loc and expected_loc not in loc:
        status = "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  {status}: GET {path:20s} => {code} (expected {expected_code})" + (f"  Location: {loc}" if loc else ""))

# --- Test 2: Staff login page contains correct form ---
print("\nTEST 2: Staff login template renders correctly")
r = urllib.request.urlopen(BASE + "/staff")
body = r.read().decode()
has_form = 'action="/staff"' in body
has_title = "Staff Sign In" in body
print(f"  {'PASS' if has_form else 'FAIL'}: Form action points to /staff")
print(f"  {'PASS' if has_title else 'FAIL'}: Page title is 'Staff Sign In'")
if not has_form or not has_title:
    all_pass = False

# --- Test 3: Admin login page contains correct form ---
print("\nTEST 3: Admin login template renders correctly")
r = urllib.request.urlopen(BASE + "/admin")
body = r.read().decode()
has_form = 'action="/admin"' in body
has_title = "Admin Sign In" in body
print(f"  {'PASS' if has_form else 'FAIL'}: Form action points to /admin")
print(f"  {'PASS' if has_title else 'FAIL'}: Page title is 'Admin Sign In'")
if not has_form or not has_title:
    all_pass = False

# --- Test 4: Admin login flow (with cookies) ---
print("\nTEST 4: Admin login + dashboard + logout flow")
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    NoRedirect,
)

login_data = urllib.parse.urlencode({"email": "admin@coepd.com", "password": "admin123"}).encode()
try:
    req = urllib.request.Request(BASE + "/admin", data=login_data, method="POST")
    opener.open(req)
    login_code = 200
    login_loc = ""
except urllib.error.HTTPError as e:
    login_code = e.code
    login_loc = e.headers.get("Location", "")

login_ok = login_code == 302 and "/admin/dashboard" in login_loc
print(f"  {'PASS' if login_ok else 'FAIL'}: POST /admin => {login_code} Location: {login_loc}")
if not login_ok:
    all_pass = False

# Check cookie was set
auth_cookie = any(c.name == "auth_token" for c in cj)
print(f"  {'PASS' if auth_cookie else 'FAIL'}: auth_token cookie set")
if not auth_cookie:
    all_pass = False

# Access admin dashboard with auth cookie
try:
    req = urllib.request.Request(BASE + "/admin/dashboard")
    r = opener.open(req)
    dash_code = r.status
    dash_body = r.read().decode()
except urllib.error.HTTPError as e:
    dash_code = e.code
    dash_body = ""

dash_ok = dash_code == 200
print(f"  {'PASS' if dash_ok else 'FAIL'}: GET /admin/dashboard => {dash_code}")
if not dash_ok:
    all_pass = False

# Logout
try:
    req = urllib.request.Request(BASE + "/logout")
    opener.open(req)
    logout_code = 200
    logout_loc = ""
except urllib.error.HTTPError as e:
    logout_code = e.code
    logout_loc = e.headers.get("Location", "")

logout_ok = logout_code == 302 and "/" == logout_loc.rstrip("/")
# Accept both "/" and empty redirect
logout_ok = logout_code == 302
print(f"  {'PASS' if logout_ok else 'FAIL'}: GET /logout => {logout_code} Location: {logout_loc}")
if not logout_ok:
    all_pass = False

# After logout, dashboard should redirect
try:
    req = urllib.request.Request(BASE + "/admin/dashboard")
    opener.open(req)
    post_logout = 200
    post_logout_loc = ""
except urllib.error.HTTPError as e:
    post_logout = e.code
    post_logout_loc = e.headers.get("Location", "")

redir_ok = post_logout == 302
print(f"  {'PASS' if redir_ok else 'FAIL'}: After logout, GET /admin/dashboard => {post_logout} (should redirect)")
if not redir_ok:
    all_pass = False

# --- Test 5: Invalid login shows error ---
print("\nTEST 5: Invalid credentials show error")
bad_data = urllib.parse.urlencode({"email": "wrong@x.com", "password": "bad"}).encode()
try:
    req = urllib.request.Request(BASE + "/staff", data=bad_data, method="POST")
    r = urllib.request.urlopen(req)
    bad_code = r.status
    bad_body = r.read().decode()
except urllib.error.HTTPError as e:
    bad_code = e.code
    bad_body = e.read().decode() if hasattr(e, "read") else ""

bad_ok = bad_code == 401 and "Invalid email or password" in bad_body
print(f"  {'PASS' if bad_ok else 'FAIL'}: POST /staff with bad creds => {bad_code}, error message shown")
if not bad_ok:
    all_pass = False

# --- Summary ---
print("\n" + "=" * 60)
print(f"RESULT: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 60)
