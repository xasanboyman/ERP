#!/usr/bin/env python3
"""
Branch Statistics & Multi-Tenant Cross-Company Isolation Test Suite
Verifies:
1. Branch-specific statistics calculations (employees, products, income) per branch.
2. Cross-company worker isolation (Company A workers never leak to Company B).
3. Cross-company product isolation (Company A products never leak to Company B).
4. Anti-tampering security: Company B cannot edit or delete Company A's products or workers.
5. Branch statistics strictly isolate data across company tenants and individual branches.
"""

import unittest
import requests
import urllib3
import uuid

import os

BASE_URL = os.environ.get("TEST_BASE_URL", "https://xn--dr8haa.uz/oracle/erp-api")

class TestBranchAndIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        cls.session.verify = False
        cls.run_id = uuid.uuid4().hex[:6]
        print(f"\n=================================================================")
        print(f"Running Branch Statistics & Multi-Tenant Isolation Test [Run: {cls.run_id}]")
        print(f"Target API: {BASE_URL}")
        print(f"=================================================================\n")

    def api_post(self, path, json_data, token=None, expected_status=200):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = token
        url = f"{BASE_URL}{path}"
        res = self.session.post(url, json=json_data, headers=headers, timeout=12)
        if expected_status is not None:
            self.assertEqual(res.status_code, expected_status, f"POST {path} failed: status {res.status_code}, text: {res.text}")
        try:
            return res.status_code, res.json()
        except Exception:
            return res.status_code, res.text

    def api_get(self, path, token=None, expected_status=200):
        headers = {}
        if token:
            headers["Authorization"] = token
        url = f"{BASE_URL}{path}"
        res = self.session.get(url, headers=headers, timeout=12)
        if expected_status is not None:
            self.assertEqual(res.status_code, expected_status, f"GET {path} failed: status {res.status_code}, text: {res.text}")
        try:
            return res.status_code, res.json()
        except Exception:
            return res.status_code, res.text

    def test_01_authenticate_principals(self):
        """Authenticate Superadmin and idk company admin."""
        print("[STEP 1] Authenticating 'admin' and 'idk' accounts...")
        _, admin_res = self.api_post("/user/login", {"username": "admin", "password": "admin"})
        self.assertEqual(admin_res.get("code"), 0, f"Superadmin login failed: {admin_res}")
        self.__class__.admin_token = admin_res["data"]["token"]

        _, idk_res = self.api_post("/user/login", {"username": "idk", "password": "idk"})
        self.assertEqual(idk_res.get("code"), 0, f"idk login failed: {idk_res}")
        self.__class__.idk_token = idk_res["data"]["token"]
        self.__class__.idk_company_id = idk_res["data"].get("company_id")
        print(f"  ✓ 'admin' and 'idk' authenticated successfully. idk company_id: {self.idk_company_id}")

    def test_02_create_second_company_tenant(self):
        """Create a separate isolated company 'Omega Corp' via Superadmin."""
        print("[STEP 2] Creating second tenant company 'Omega Corp'...")
        self.__class__.omega_code = f"omega_{self.run_id}"
        self.__class__.omega_username = f"omega_admin_{self.run_id}"
        self.__class__.omega_password = f"omega_pass_{self.run_id}"

        payload = {
            "name": f"Omega Corp {self.run_id}",
            "code": self.omega_code,
            "plan": "pro",
            "billing_cycle": "monthly",
            "admin_username": self.omega_username,
            "admin_password": self.omega_password,
            "admin_full_name": "Omega Lead Admin"
        }
        _, comp_res = self.api_post("/company/save", payload, token=self.admin_token)
        self.assertEqual(comp_res.get("code"), 0, f"Failed to create company: {comp_res}")
        self.__class__.omega_company_id = comp_res["data"]["id"]
        print(f"  ✓ Created Omega Corp: {self.omega_company_id}")

        # Login as omega admin
        _, omega_login = self.api_post("/user/login", {"username": self.omega_username, "password": self.omega_password})
        self.assertEqual(omega_login.get("code"), 0, f"Omega login failed: {omega_login}")
        self.__class__.omega_token = omega_login["data"]["token"]
        print(f"  ✓ Authenticated as Omega Admin with independent token.")

    def test_03_create_branch_and_records_for_both_tenants(self):
        """Seed branches, workers, products, and sales for both 'idk' and 'omega'."""
        print("[STEP 3] Seeding branches and items in both companies...")
        
        # 1. idk branch
        _, idk_branches = self.api_get("/branch/list", token=self.idk_token)
        self.assertEqual(idk_branches.get("code"), 0)
        self.assertGreater(len(idk_branches["data"]), 0, "idk must have at least 1 branch")
        self.__class__.idk_branch_id = idk_branches["data"][0]["id"]

        # Add worker to idk
        self.__class__.idk_worker_name = f"IDK Worker {self.run_id}"
        _, w_idk_res = self.api_post("/worker/save", {
            "name": self.idk_worker_name,
            "account": f"idk_acc_{self.run_id}",
            "role": "Sotuvchi",
            "phone": "+998901112233",
            "baseSalary": 4500000.0,
            "branch_id": self.idk_branch_id,
            "status": 1
        }, token=self.idk_token)
        self.assertEqual(w_idk_res.get("code"), 0)
        _, w_idk_list = self.api_get("/worker/list", token=self.idk_token)
        w_idk_match = next((w for w in w_idk_list["data"]["list"] if w["name"] == self.idk_worker_name), None)
        self.assertIsNotNone(w_idk_match)
        self.__class__.idk_worker_id = w_idk_match["id"]

        # Add product to idk
        self.__class__.idk_product_name = f"IDK Exclusive Product {self.run_id}"
        _, p_idk_res = self.api_post("/product/save", {
            "productName": self.idk_product_name,
            "category": "Elektronika",
            "price": 125000.0,
            "cost": 90000.0,
            "quantityInStock": 40,
            "branch_id": self.idk_branch_id,
            "status": 1
        }, token=self.idk_token)
        self.assertEqual(p_idk_res.get("code"), 0)
        _, p_idk_list = self.api_get("/product/list", token=self.idk_token)
        p_idk_match = next((p for p in p_idk_list["data"]["list"] if p["productName"] == self.idk_product_name), None)
        self.assertIsNotNone(p_idk_match)
        self.__class__.idk_product_id = p_idk_match["id"]

        # 2. omega branch
        _, omega_branch_res = self.api_post("/branch/save", {
            "name": f"Omega Chorsu Branch {self.run_id}",
            "code": f"OMG-{self.run_id[:4].upper()}",
            "address": "Chorsu, 14",
            "phone": "+998912345678"
        }, token=self.omega_token)
        self.assertEqual(omega_branch_res.get("code"), 0)
        self.__class__.omega_branch_id = omega_branch_res["data"]["id"]

        # Add worker to omega
        self.__class__.omega_worker_name = f"Omega Worker Alex {self.run_id}"
        _, w_omega_res = self.api_post("/worker/save", {
            "name": self.omega_worker_name,
            "account": f"omg_acc_{self.run_id}",
            "role": "Kassir",
            "phone": "+998998887766",
            "baseSalary": 3800000.0,
            "branch_id": self.omega_branch_id,
            "status": 1
        }, token=self.omega_token)
        self.assertEqual(w_omega_res.get("code"), 0)
        _, w_omg_list = self.api_get("/worker/list", token=self.omega_token)
        w_omg_match = next((w for w in w_omg_list["data"]["list"] if w["name"] == self.omega_worker_name), None)
        self.assertIsNotNone(w_omg_match)
        self.__class__.omega_worker_id = w_omg_match["id"]

        # Add product to omega
        self.__class__.omega_product_name = f"Omega Secret Formula {self.run_id}"
        _, p_omega_res = self.api_post("/product/save", {
            "productName": self.omega_product_name,
            "category": "Farmatsevtika",
            "price": 75000.0,
            "cost": 45000.0,
            "quantityInStock": 80,
            "branch_id": self.omega_branch_id,
            "status": 1
        }, token=self.omega_token)
        self.assertEqual(p_omega_res.get("code"), 0)
        _, p_omg_list = self.api_get("/product/list", token=self.omega_token)
        p_omg_match = next((p for p in p_omg_list["data"]["list"] if p["productName"] == self.omega_product_name), None)
        self.assertIsNotNone(p_omg_match)
        self.__class__.omega_product_id = p_omg_match["id"]

        # Record a sale in omega branch
        _, sale_res = self.api_post("/sales/checkout", {
            "receipt_number": f"REC-OMG-{self.run_id}",
            "payment_method": "naqd",
            "total_amount": 150000.0,
            "paid_amount": 150000.0,
            "debt_amount": 0.0,
            "branch_id": self.omega_branch_id,
            "items": [
                {
                    "product_id": self.omega_product_id,
                    "product_name": self.omega_product_name,
                    "price": 75000.0,
                    "quantity": 2,
                    "total": 150000.0
                }
            ]
        }, token=self.omega_token)
        self.assertEqual(sale_res.get("code"), 0)
        print("  ✓ Created isolated branches, workers, products, and sales for both companies.")

    def test_04_verify_cross_company_worker_isolation(self):
        """Assert Company A workers never appear in Company B, and vice-versa."""
        print("[TEST 4] Verifying cross-company worker isolation...")
        
        # idk worker list
        _, idk_workers_res = self.api_get("/worker/list", token=self.idk_token)
        idk_names = [w["name"] for w in idk_workers_res.get("data", {}).get("list", [])]
        self.assertIn(self.idk_worker_name, idk_names, "idk worker MUST be visible in idk")
        self.assertNotIn(self.omega_worker_name, idk_names, "CRITICAL: Omega worker MUST NOT appear in idk!")

        # omega worker list
        _, omega_workers_res = self.api_get("/worker/list", token=self.omega_token)
        omega_names = [w["name"] for w in omega_workers_res.get("data", {}).get("list", [])]
        self.assertIn(self.omega_worker_name, omega_names, "Omega worker MUST be visible in omega")
        self.assertNotIn(self.idk_worker_name, omega_names, "CRITICAL: idk worker MUST NOT appear in omega!")
        print("  ✓ Zero worker leakage between Company A and Company B.")

    def test_05_verify_cross_company_product_isolation(self):
        """Assert Company A products never appear in Company B, and vice-versa."""
        print("[TEST 5] Verifying cross-company product isolation...")
        
        # idk product list
        _, idk_prods_res = self.api_get("/product/list", token=self.idk_token)
        idk_pnames = [p["productName"] for p in idk_prods_res.get("data", {}).get("list", [])]
        self.assertIn(self.idk_product_name, idk_pnames, "idk product MUST be visible in idk")
        self.assertNotIn(self.omega_product_name, idk_pnames, "CRITICAL: Omega product MUST NOT appear in idk!")

        # omega product list
        _, omega_prods_res = self.api_get("/product/list", token=self.omega_token)
        omega_pnames = [p["productName"] for p in omega_prods_res.get("data", {}).get("list", [])]
        self.assertIn(self.omega_product_name, omega_pnames, "Omega product MUST be visible in omega")
        self.assertNotIn(self.idk_product_name, omega_pnames, "CRITICAL: idk product MUST NOT appear in omega!")
        print("  ✓ Zero product leakage between Company A and Company B.")

    def test_06_anti_tampering_cross_company_resistance(self):
        """Verify Company B CANNOT alter or delete Company A's product or worker."""
        print("[TEST 6] Verifying anti-tampering security boundaries...")
        
        # Omega tries to edit idk's product
        status_edit, body_edit = self.api_post("/product/save", {
            "id": self.idk_product_id,
            "productName": "HACKED BY OMEGA",
            "category": "Elektronika",
            "price": 1.0,
            "cost": 1.0,
            "quantityInStock": 1
        }, token=self.omega_token, expected_status=None)
        self.assertIn(status_edit, [403, 404], f"Omega must NOT be allowed to edit idk product: status {status_edit}, body {body_edit}")

        # Omega tries to delete idk's product
        status_del, body_del = self.api_post("/product/delete", {
            "ids": [self.idk_product_id]
        }, token=self.omega_token, expected_status=None)
        # Verify product is NOT deleted
        _, idk_check = self.api_get(f"/product/detail?id={self.idk_product_id}", token=self.idk_token)
        self.assertEqual(idk_check.get("code"), 0, "idk product MUST still exist untouched")
        self.assertEqual(idk_check["data"]["productName"], self.idk_product_name, "idk product name MUST NOT have changed")

        # Omega tries to edit idk's worker
        status_w_edit, body_w = self.api_post("/worker/save", {
            "id": self.idk_worker_id,
            "name": "TAMPERED WORKER",
            "account": "tamper_acc",
            "adminPassword": "some_password"
        }, token=self.omega_token, expected_status=None)
        # Should either be 403 HTTP status or JSON code 403
        is_blocked = (status_w_edit in [403, 404]) or (isinstance(body_w, dict) and body_w.get("code") in [403, 404, 400])
        self.assertTrue(is_blocked, f"Omega must NOT be allowed to edit idk worker: {status_w_edit}, {body_w}")

        print("  ✓ Cross-company anti-tampering verified. Product and worker cannot be hijacked or altered.")

    def test_07_branch_statistics_isolation_and_correctness(self):
        """Verify GET /api/branch/statistics gives exact stats for that branch and isolates companies."""
        print("[TEST 7] Verifying branch statistics endpoint and tenant isolation...")

        # 1. idk branch statistics
        _, idk_stats_res = self.api_get("/branch/statistics", token=self.idk_token)
        self.assertEqual(idk_stats_res.get("code"), 0)
        idk_branches = idk_stats_res.get("data", [])
        self.assertGreater(len(idk_branches), 0)
        
        for b in idk_branches:
            emp_names = [w["name"] for w in b["statistics"]["employees"]["list"]]
            prod_names = [p["productName"] for p in b["statistics"]["products"]["list"]]
            self.assertNotIn(self.omega_worker_name, emp_names, "Omega worker MUST NOT appear in idk branch statistics")
            self.assertNotIn(self.omega_product_name, prod_names, "Omega product MUST NOT appear in idk branch statistics")

        # 2. omega branch statistics
        _, omega_stats_res = self.api_get("/branch/statistics", token=self.omega_token)
        self.assertEqual(omega_stats_res.get("code"), 0)
        omega_branches = omega_stats_res.get("data", [])
        self.assertEqual(len(omega_branches), 1, "Omega has exactly 1 branch")

        target_b = omega_branches[0]
        stats = target_b["statistics"]

        # Employees check
        self.assertGreaterEqual(stats["employees"]["count"], 1)
        omega_emp_names = [w["name"] for w in stats["employees"]["list"]]
        self.assertIn(self.omega_worker_name, omega_emp_names)
        self.assertNotIn(self.idk_worker_name, omega_emp_names)

        # Products check
        self.assertGreaterEqual(stats["products"]["count"], 1)
        self.assertGreaterEqual(stats["products"]["total_quantity"], 78) # 80 minus 2 sold
        omega_prod_names = [p["productName"] for p in stats["products"]["list"]]
        self.assertIn(self.omega_product_name, omega_prod_names)
        self.assertNotIn(self.idk_product_name, omega_prod_names)

        # Income check
        self.assertEqual(stats["income"]["total_revenue"], 150000.0)
        self.assertEqual(stats["income"]["total_sales_count"], 1)
        self.assertEqual(stats["income"]["average_check"], 150000.0)

        print(f"  ✓ Branch statistics verified: {stats['employees']['count']} worker(s), {stats['products']['count']} product(s), {stats['income']['total_revenue']} so'm revenue.")
        print("  ✓ Zero cross-tenant data leakage in branch statistics.")

    def test_08_branch_filtered_dashboard_bundle(self):
        """Verify GET /api/analysis/bundle?branch_id=... returns branch-filtered analytics."""
        print("[TEST 8] Verifying branch-filtered analysis bundle...")
        _, bundle_res = self.api_get(f"/analysis/bundle?branch_id={self.omega_branch_id}", token=self.omega_token)
        self.assertEqual(bundle_res.get("code"), 0)
        ov = bundle_res["data"]["overview"]
        self.assertIsNotNone(ov)
        self.assertEqual(ov["grossRevenue"], 150000.0)
        self.assertEqual(ov["activeWorkersCount"], 1)
        print(f"  ✓ Analysis bundle filtered for branch {self.omega_branch_id} returned exact grossRevenue: {ov['grossRevenue']} and activeWorkersCount: {ov['activeWorkersCount']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
