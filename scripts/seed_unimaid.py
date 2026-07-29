import os
from app import create_app, db
from app.models.core import Tenant, User, Role
from app.models.metadata import EntityDefinition, FieldDefinition
from app.core.types import FieldType

def seed_unimaid():
    app = create_app('development')
    with app.app_context():
        # Create Tenant
        tenant = Tenant.query.filter_by(slug='unimaid').first()
        if not tenant:
            tenant = Tenant(name='Federal University of Maiduguri', slug='unimaid')
            db.session.add(tenant)
            db.session.flush()

        # Ensure Roles
        roles = ['Admin', 'Examiner', 'Student']
        for role_name in roles:
            role = Role.query.filter_by(tenant_id=tenant.id, name=role_name).first()
            if not role:
                role = Role(name=role_name, tenant_id=tenant.id, permissions={})
                db.session.add(role)
        db.session.flush()

        # Create Admin
        admin = User.query.filter_by(email='admin@unimaid.edu.ng').first()
        if not admin:
            admin = User(email='admin@unimaid.edu.ng', tenant_id=tenant.id, password='Password123!', role=Role.query.filter_by(tenant_id=tenant.id, name='Admin').first())
            db.session.add(admin)

        # Create Core Entities
        entities = [
            {'name': 'Department', 'fields': [{'name': 'name', 'label': 'Department Name', 'field_type': 'string'}, {'name': 'code', 'label': 'Code', 'field_type': 'string'}]},
            {'name': 'Course', 'fields': [{'name': 'title', 'label': 'Course Title', 'field_type': 'string'}, {'name': 'code', 'label': 'Course Code', 'field_type': 'string'}]},
            {'name': 'Student', 'fields': [{'name': 'name', 'label': 'Full Name', 'field_type': 'string'}, {'name': 'mat_no', 'label': 'Matric Number', 'field_type': 'string'}]}
        ]

        for ent_data in entities:
            entity = EntityDefinition.query.filter_by(tenant_id=tenant.id, name=ent_data['name']).first()
            if not entity:
                entity = EntityDefinition(tenant_id=tenant.id, name=ent_data['name'])
                db.session.add(entity)
                db.session.flush()
                for f_data in ent_data['fields']:
                    field = FieldDefinition(entity_id=entity.id, **f_data)
                    db.session.add(field)

        db.session.commit()
        print('UNIMAID seeded successfully.')

if __name__ == '__main__':
    seed_unimaid()
