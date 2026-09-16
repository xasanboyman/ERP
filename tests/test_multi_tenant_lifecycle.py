#!/usr/bin/env python3
"""
Multi-Tenant Lifecycle & Deployment Validation Test Suite
Tests against live API: https://localhost:4000/api

Lifecycle covered:
1. Super Admin login ('admin' / 'admin')
2. Super Admin creating new company with custom admin credentials ('Delta Logistics', 'delta_admin' / 'deltapass123')
3. Logging in as 'delta_admin' and asserting GET /api/role/list returns only /dashboard, /product, /sales, /hr and strictly excludes /company
4. Asserting non-superadmin access to /company or /company/list returns 403 or 404
5. Super Admin resetting 'delta_admin' password to 'new_deltapass_999', asserting old password fails, and new password succeeds
6. Testing company data isolation: creating a product under 'delta_admin' and asserting it is not visible to another company ('idk' or 'test')
7. Verifying existing accounts ('idk', 'test', 'admin') all authenticate and operate properly
"""

import unittest
import requests
import urllib3
import time
import uuid

# Suppress InsecureRequestWarning for self-signed development certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:4000/api"

class TestMultiTenantLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        cls.session.verify = False
        cls.test_run_id = uuid.uuid4().hex[:6]
        print(f"\n=======================================================")
        print(f"Starting Multi-Tenant End-to-End Test Suite [Run: {cls.test_run_id}]")
        print(f"Target API: {BASE_URL}")
        print(f"=======================================================\n")

    def api_post(self, path, json_data, token=None, expected_status=200):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = token
        url = f"{BASE_URL}{path}"
        res = self.session.post(url, json=json_data, headers=headers, timeout=10)
        if expected_status is not None:
            self.assertEqual(res.status_code, expected_status, f"POST {path} failed: {res.text}")
        try:
            return res.status_code, res.json()
        except Exception:
            return res.status_code, res.text

    def api_get(self, path, token=None, expected_status=200):
        headers = {}
        if token:
            headers["Authorization"] = token
        url = f"{BASE_URL}{path}"
        res = self.session.get(url, headers=headers, timeout=10)
        if expected_status is not None:
            self.assertEqual(res.status_code, expected_status, f"GET {path} failed: {res.text}")
        try:
            return res.status_code, res.json()
        except Exception:
            return res.status_code, res.text

    def test_01_superadmin_login(self):
        """Test Super Admin login with 'admin' / 'admin' and verify permissions."""
        print("[TEST 1] Authenticating Super Admin ('admin' / 'admin')...")
        status, body = self.api_post("/user/login", {"username": "admin", "password": "admin"})
        self.assertEqual(body.get("code"), 0, f"Login failed: {body}")
        
        data = body.get("data", {})
        self.assertTrue(data.get("is_super_admin"), "Admin user must have is_super_admin = True")
        self.assertIn("token", data, "Login must return an auth token")
        
        admin_token = data["token"]
        self.__class__.admin_token = admin_token

        # Verify Super Admin role menu contains /company
        status, role_body = self.api_get("/role/list", token=admin_token)
        self.assertEqual(role_body.get("code"), 0)
        routes = [r.get("path") for r in role_body.get("data", [])]
        print(f"  -> Super Admin route paths: {routes}")
        self.assertIn("/company", routes, "Super Admin MUST have access to /company")
        print("  ✓ Super Admin authenticated with full system permissions and /company access.")

    def test_02_superadmin_create_company(self):
        """Super Admin creates 'Delta Logistics' company with 'delta_admin' / 'deltapass123' credentials."""
        print("[TEST 2] Super Admin creating company 'Delta Logistics' with 'delta_admin'...")
        payload = {
            "name": "Delta Logistics",
            "code": "delta",
            "plan": "basic",
            "billing_cycle": "monthly",
            "admin_username": "delta_admin",
            "admin_password": "deltapass123",
            "admin_full_name": "Delta Logistics Administrator"
        }
        status, body = self.api_post("/company/save", payload, token=self.admin_token)
        self.assertEqual(body.get("code"), 0, f"Company creation failed: {body}")
        
        comp_data = body.get("data", {})
        self.assertEqual(comp_data.get("name"), "Delta Logistics")
        self.assertEqual(comp_data.get("code"), "delta")
        delta_id = comp_data.get("id")
        self.assertTrue(bool(delta_id), "Created company must return a valid ID")
        self.__class__.delta_company_id = delta_id
        print(f"  ✓ Company created: ID={delta_id}, Code=delta, Plan={comp_data.get('plan')}")

        # Verify company is returned in /company/list
        status, list_body = self.api_get("/company/list", token=self.admin_token)
        comps = list_body.get("data", {}).get("list", [])
        matched = [c for c in comps if c.get("id") == delta_id or c.get("code") == "delta"]
        self.assertTrue(len(matched) > 0, "Created company must appear in Super Admin company list")
        print("  ✓ Company confirmed in Super Admin company listing.")

    def test_03_delta_admin_login_and_role_permissions(self):
        """Log in as 'delta_admin' and assert GET /api/role/list contains only standard modules and NO /company."""
        print("[TEST 3] Logging in as 'delta_admin' and asserting strict menu isolation...")
        status, body = self.api_post("/user/login", {"username": "delta_admin", "password": "deltapass123"})
        self.assertEqual(body.get("code"), 0, f"delta_admin login failed: {body}")
        
        delta_data = body.get("data", {})
        self.assertFalse(delta_data.get("is_super_admin"), "delta_admin must NOT be super admin")
        self.assertEqual(delta_data.get("company_name"), "Delta Logistics")
        
        delta_token = delta_data.get("token")
        self.__class__.delta_token = delta_token

        # Assert GET /api/role/list
        status, role_body = self.api_get("/role/list", token=delta_token)
        self.assertEqual(role_body.get("code"), 0)
        route_paths = [r.get("path") for r in role_body.get("data", [])]
        print(f"  -> delta_admin menu routes: {route_paths}")

        # Asserting role/list returns /dashboard, /product, /sales, /hr, /authorization and DOES NOT include /company
        self.assertNotIn("/company", route_paths, "Security violation: /company found in delta_admin menu!")
        self.assertIn("/authorization", route_paths, "Company Admin MUST have /authorization (Roles & Branches)!")
        expected_modules = {"/dashboard", "/product", "/sales", "/hr", "/authorization"}
        self.assertEqual(set(route_paths), expected_modules, f"Expected strictly {expected_modules}, got {set(route_paths)}")
        print("  ✓ Strict menu isolation confirmed: /dashboard, /product, /sales, /hr, /authorization (no /company).")

        # Worker isolation verification: delta_admin should have 0 workers
        w_status, w_body = self.api_get("/worker/list", token=delta_token)
        self.assertEqual(w_body.get("code"), 0)
        self.assertEqual(w_body["data"]["total"], 0, f"delta_admin should have 0 workers, got {w_body['data']['total']}")
        print("  ✓ Worker tenant isolation confirmed: delta_admin has 0 workers.")

    def test_04_non_superadmin_access_restrictions(self):
        """Asserting non-superadmin access to /company or /company/list returns 403 or 404."""
        print("[TEST 4] Testing non-superadmin access rejection on company endpoints...")
        
        # 1. GET /company/list
        status, body = self.api_get("/company/list", token=self.delta_token, expected_status=None)
        self.assertIn(status, [403, 404], f"Expected 403 or 404 on /company/list, got HTTP {status}")
        print(f"  ✓ GET /api/company/list correctly blocked with HTTP {status}")

        # 2. GET /company
        status, body = self.api_get("/company", token=self.delta_token, expected_status=None)
        self.assertIn(status, [403, 404], f"Expected 403 or 404 on /company, got HTTP {status}")
        print(f"  ✓ GET /api/company correctly blocked with HTTP {status}")

        # 3. POST /company/save
        status, body = self.api_post("/company/save", {"name": "Hack Corp", "code": "hack"}, token=self.delta_token, expected_status=None)
        self.assertIn(status, [403, 404], f"Expected 403 or 404 on /company/save, got HTTP {status}")
        print(f"  ✓ POST /api/company/save correctly blocked with HTTP {status}")

    def test_05_superadmin_reset_company_admin_password(self):
        """Super Admin resets 'delta_admin' password to 'new_deltapass_999', old fails, new succeeds."""
        print("[TEST 5] Super Admin resetting 'delta_admin' password to 'new_deltapass_999'...")
        reset_payload = {
            "company_id": self.delta_company_id,
            "username": "delta_admin",
            "new_password": "new_deltapass_999"
        }
        status, body = self.api_post("/company/account/reset-password", reset_payload, token=self.admin_token)
        self.assertEqual(body.get("code"), 0, f"Password reset failed: {body}")
        print(f"  ✓ Reset API response: {body.get('message')}")

        # Verify old password fails
        print("  -> Testing old password ('deltapass123')...")
        status, old_body = self.api_post("/user/login", {"username": "delta_admin", "password": "deltapass123"}, expected_status=None)
        if isinstance(old_body, dict):
            self.assertNotEqual(old_body.get("code"), 0, "Old password MUST NOT succeed!")
        else:
            self.assertNotEqual(status, 200, "Old password MUST NOT return HTTP 200!")
        print(f"  ✓ Old password rejected as expected.")

        # Verify new password succeeds
        print("  -> Testing new password ('new_deltapass_999')...")
        status, new_body = self.api_post("/user/login", {"username": "delta_admin", "password": "new_deltapass_999"})
        self.assertEqual(new_body.get("code"), 0, f"New password login failed: {new_body}")
        new_token = new_body.get("data", {}).get("token")
        self.assertTrue(bool(new_token), "New password login must yield an auth token")
        self.__class__.delta_token = new_token
        print("  ✓ New password authenticated successfully.")

    def test_06_company_data_isolation(self):
        """Create a product under 'delta_admin' and assert it is isolated from other companies ('idk', 'test')."""
        print("[TEST 6] Testing company data isolation (product creation & multi-tenant visibility)...")
        
        # Log in reference companies
        status, idk_res = self.api_post("/user/login", {"username": "idk", "password": "idk"})
        self.assertEqual(idk_res.get("code"), 0, f"idk login failed: {idk_res}")
        idk_token = idk_res["data"]["token"]
        idk_company_id = idk_res["data"]["company_id"]

        status, test_res = self.api_post("/user/login", {"username": "test", "password": "test"})
        self.assertEqual(test_res.get("code"), 0, f"test login failed: {test_res}")
        test_token = test_res["data"]["token"]

        # Create unique product under delta_admin
        unique_sku = f"DELTA-{self.test_run_id.upper()}-{int(time.time())}"
        unique_barcode = f"998{int(time.time()) % 1000000000:09d}"
        product_name = f"Delta Cargo Container {self.test_run_id}"

        prod_payload = {
            "productName": product_name,
            "category": "Logistika",
            "price": 4500000,
            "cost": 3200000,
            "quantityInStock": 10,
            "unit": "dona",
            "SKU": unique_sku,
            "shtrix_code": unique_barcode
        }

        print(f"  -> Creating product '{product_name}' under delta_admin...")
        status, prod_res = self.api_post("/product/save", prod_payload, token=self.delta_token)
        self.assertEqual(prod_res.get("code"), 0, f"Product creation failed: {prod_res}")
        print(f"  ✓ Product created successfully: {prod_res.get('data')}")

        # 1. Verify visibility for delta_admin
        status, delta_list = self.api_get(f"/product/list?productName={product_name}", token=self.delta_token)
        delta_prods = delta_list.get("data", {}).get("list", [])
        self.assertTrue(
            any(p.get("productName") == product_name for p in delta_prods),
            f"Created product '{product_name}' must be visible to delta_admin"
        )
        print(f"  ✓ Product visible to Delta Logistics admin (found in search).")

        # 2. Assert isolation for 'idk' company
        status, idk_list = self.api_get(f"/product/list?productName={product_name}", token=idk_token)
        idk_prods = idk_list.get("data", {}).get("list", [])
        self.assertFalse(
            any(p.get("productName") == product_name for p in idk_prods),
            f"SECURITY LEAK: Product '{product_name}' of Delta Logistics leaked into company 'idk'!"
        )
        print(f"  ✓ Isolation verified: product is completely hidden from company 'idk'.")

        # 3. Assert isolation for 'test' user
        status, test_list = self.api_get(f"/product/list?productName={product_name}", token=test_token)
        test_prods = test_list.get("data", {}).get("list", [])
        self.assertFalse(
            any(p.get("productName") == product_name for p in test_prods),
            f"SECURITY LEAK: Product '{product_name}' of Delta Logistics leaked to 'test' user!"
        )
        print(f"  ✓ Isolation verified: product is completely hidden from user 'test'.")

    def test_07_existing_accounts_authentication_and_operation(self):
        """Verify existing accounts ('idk', 'test', 'admin') all authenticate and operate properly."""
        print("[TEST 7] Verifying standard operations across existing accounts ('admin', 'idk', 'test')...")

        # Account 1: 'admin' (Super Administrator)
        print("  -> Verifying 'admin' operational access...")
        status, res = self.api_post("/user/login", {"username": "admin", "password": "admin"})
        self.assertEqual(res.get("code"), 0)
        admin_tok = res["data"]["token"]
        
        # Verify admin can read main account details
        status, main_acc = self.api_get("/company/main-account", token=admin_tok)
        self.assertEqual(main_acc.get("code"), 0)
        self.assertEqual(main_acc["data"]["super_admin"]["username"], "admin")
        
        # Verify admin can list workers
        status, workers = self.api_get("/worker/list?pageIndex=1&pageSize=5", token=admin_tok)
        self.assertEqual(workers.get("code"), 0)
        print("  ✓ 'admin' operates properly (login, company/main-account, worker list).")

        # Account 2: 'idk' (Company Administrator)
        print("  -> Verifying 'idk' operational access...")
        status, res = self.api_post("/user/login", {"username": "idk", "password": "idk"})
        self.assertEqual(res.get("code"), 0)
        idk_tok = res["data"]["token"]
        self.assertFalse(res["data"]["is_super_admin"])
        
        # Verify idk current company endpoint
        status, comp_curr = self.api_get("/company/current", token=idk_tok)
        self.assertEqual(comp_curr.get("code"), 0)
        self.assertEqual(comp_curr["data"]["name"], "idk")
        
        # Verify idk role menu does not include company management
        status, idk_roles = self.api_get("/role/list", token=idk_tok)
        idk_paths = [r["path"] for r in idk_roles.get("data", [])]
        self.assertNotIn("/company", idk_paths)
        print("  ✓ 'idk' operates properly (login, company/current, role list isolated).")

        # Account 3: 'test' (Standard Tenant Worker)
        print("  -> Verifying 'test' operational access...")
        status, res = self.api_post("/user/login", {"username": "test", "password": "test"})
        self.assertEqual(res.get("code"), 0)
        test_tok = res["data"]["token"]
        self.assertFalse(res["data"]["is_super_admin"])
        
        # Verify test role menu
        status, test_roles = self.api_get("/role/list", token=test_tok)
        self.assertEqual(test_roles.get("code"), 0)
        test_paths = [r["path"] for r in test_roles.get("data", [])]
        self.assertNotIn("/company", test_paths)
        
        # Verify test can query products
        status, prods = self.api_get("/product/list?pageIndex=1&pageSize=5", token=test_tok)
        self.assertEqual(prods.get("code"), 0)
        print("  ✓ 'test' operates properly (login, role list, product catalog query).")

        print("\n=======================================================")
        print("All 7 Multi-Tenant End-to-End Test Phases Passed 100%!")
        print("=======================================================\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
