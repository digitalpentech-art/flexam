import pytest
import uuid
from app import create_app, db
from app.models.metadata import EntityDefinition, Record
from app.models.core import Tenant

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Setup tenant and entity
            t1 = Tenant(name="Tenant 1", slug="t1-unique")
            db.session.add(t1)
            db.session.commit()
            
            e1 = EntityDefinition(tenant_id=t1.id, name="Student")
            db.session.add(e1)
            db.session.commit()
            
            yield client, t1, e1
            db.drop_all()

def test_record_crud(client):
    client, t1, e1 = client
    headers = {'X-Tenant-ID': str(t1.id)}
    
    # Create
    resp = client.post(f'/api/records/{e1.id}/', headers=headers, json={"name": "Alice"})
    assert resp.status_code == 201
    record_id = resp.get_json()['id']
    
    # Get
    resp = client.get(f'/api/records/{e1.id}/{record_id}/', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['data']['name'] == "Alice"
    
    # Update
    resp = client.put(f'/api/records/{e1.id}/{record_id}/', headers=headers, json={"name": "Alice Smith", "age": 20})
    assert resp.status_code == 200
    
    # Verify Update
    resp = client.get(f'/api/records/{e1.id}/{record_id}/', headers=headers)
    data = resp.get_json()['data']
    assert data['name'] == "Alice Smith"
    assert data['age'] == 20
    
    # Delete
    resp = client.delete(f'/api/records/{e1.id}/{record_id}/', headers=headers)
    assert resp.status_code == 200
    
    # Verify Delete
    resp = client.get(f'/api/records/{e1.id}/{record_id}/', headers=headers)
    assert resp.status_code == 404
