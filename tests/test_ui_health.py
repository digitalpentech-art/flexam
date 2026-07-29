import pytest
import requests

# Assuming the app runs on port 5000
BASE_URL = "http://localhost:5000"

def test_ui_builder_renders():
    try:
        response = requests.get(f"{BASE_URL}/admin/ui-builder")
        assert response.status_code == 200, f"UI Builder page failed to render, status: {response.status_code}"
        
        # Simple string check instead of BeautifulSoup
        assert 'id="grid-canvas"' in response.text, "Grid canvas not rendered"
        print("UI Builder Template: Rendering OK")
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to the server. Is it running?")

def test_api_registry():
    try:
        response = requests.get(f"{BASE_URL}/api/components/registry")
        assert response.status_code == 200, f"Component Registry API failed, status: {response.status_code}"
        try:
            data = response.json()
            assert isinstance(data, list)
            print("API Registry: Connectivity OK")
        except ValueError:
            pytest.fail("API Registry returned invalid JSON")
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to the server. Is it running?")
