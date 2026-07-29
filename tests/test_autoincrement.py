import pytest
import uuid
from app import create_app, db
from app.models.metadata import EntityDefinition, FieldDefinition
from app.models.core import Tenant

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Setup two tenants for isolation testing
            unique_id1 = str(uuid.uuid4())[:8]
            unique_id2 = str(uuid.uuid4())[:8]
            t1 = Tenant(name="Tenant 1", slug=f"t1-{unique_id1}")
            t2 = Tenant(name="Tenant 2", slug=f"t2-{unique_id2}")
            db.session.add_all([t1, t2])
            db.session.commit()
            
            # Create an entity for both tenants
            e1 = EntityDefinition(tenant_id=t1.id, name="Student")
            e2 = EntityDefinition(tenant_id=t2.id, name="Student")
            db.session.add_all([e1, e2])
            db.session.commit()
            
            # Add an autoincrement field
            f1 = FieldDefinition(entity_id=e1.id, name="roll_no", label="Roll No", field_type="autoincrement")
            f2 = FieldDefinition(entity_id=e2.id, name="roll_no", label="Roll No", field_type="autoincrement")
            db.session.add_all([f1, f2])
            db.session.commit()
            
            yield client, t1, t2, e1, e2
            db.drop_all()

def test_autoincrement_isolation(client):
    client, t1, t2, e1, e2 = client
    
    # Create records for Tenant 1
    for _ in range(3):
        client.post(f'/api/records/{e1.id}/', 
                    headers={'X-Tenant-ID': str(t1.id)},
                    json={})
    
    # Create records for Tenant 2
    for _ in range(2):
        client.post(f'/api/records/{e2.id}/', 
                    headers={'X-Tenant-ID': str(t2.id)},
                    json={})
    
    # Check T1 records
    resp1 = client.get(f'/api/records/{e1.id}/', headers={'X-Tenant-ID': str(t1.id)})
    records1 = resp1.get_json()
    assert len(records1) == 3
    assert records1[0]['data']['roll_no'] == 1
    assert records1[2]['data']['roll_no'] == 3
    
    # Check T2 records
    resp2 = client.get(f'/api/records/{e2.id}/', headers={'X-Tenant-ID': str(t2.id)})
    records2 = resp2.get_json()
    assert len(records2) == 2
    assert records2[0]['data']['roll_no'] == 1
    assert records2[1]['data']['roll_no'] == 2
