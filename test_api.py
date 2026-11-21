import unittest
from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

class TestTaskFlowAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(seed_if_empty=True)
        db.seed_demo_data()

    def test_01_get_all_tasks(self):
        """Test retrieving the list of tasks."""
        response = client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)

    def test_02_create_task(self):
        """Test creating a new task via POST."""
        payload = {
            "title": "Unit Test Task",
            "description": "Automated test description.",
            "category": "Development",
            "priority": "High",
            "status": "To Do",
            "due_date": "2026-12-31"
        }
        response = client.post("/api/tasks", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], payload["title"])
        self.assertEqual(data["category"], payload["category"])
        self.assertEqual(data["priority"], payload["priority"])
        self.assertIn("id", data)

        TestTaskFlowAPI.created_id = data["id"]

    def test_03_get_task_by_id(self):
        """Test retrieving task by ID."""
        task_id = getattr(TestTaskFlowAPI, "created_id", 1)
        response = client.get(f"/api/tasks/{task_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], task_id)

    def test_04_update_task(self):
        """Test updating a task via PUT."""
        task_id = getattr(TestTaskFlowAPI, "created_id", 1)
        update_payload = {
            "title": "Updated Task Title",
            "status": "Completed"
        }
        response = client.put(f"/api/tasks/{task_id}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Updated Task Title")
        self.assertEqual(data["status"], "Completed")

    def test_05_get_stats(self):
        """Test global stats calculation."""
        response = client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        self.assertIn("total", stats)
        self.assertIn("completed", stats)
        self.assertIn("completion_rate", stats)
        self.assertIsInstance(stats["completion_rate"], float)

    def test_06_filter_search(self):
        """Test filtering and search."""
        response = client.get("/api/tasks?search=Updated")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertGreaterEqual(len(results), 1)

    def test_07_delete_task(self):
        """Test deleting a task via DELETE."""
        task_id = getattr(TestTaskFlowAPI, "created_id", 1)
        response = client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(response.status_code, 200)

        get_res = client.get(f"/api/tasks/{task_id}")
        self.assertEqual(get_res.status_code, 404)

    def test_08_ai_breakdown(self):
        """Test AI project breakdown endpoint."""
        payload = {
            "project_title": "Build a React Portfolio Website",
            "horizon": "month",
            "intensity": "standard"
        }
        response = client.post("/api/ai/breakdown", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tasks", data)
        self.assertGreaterEqual(len(data["tasks"]), 3)

    def test_09_deliberate_failure(self):
        """Deliberate failing test to demonstrate CI failure / Red pipeline for teacher evaluation."""
        self.assertEqual(1, 2, "Assertion failed: 1 != 2 (Demonstration of pipeline failure on broken test)")

if __name__ == "__main__":
    unittest.main()
