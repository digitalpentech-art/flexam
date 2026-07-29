from app import db
from app.models.metadata import EntityDefinition, Record
from app.models.security import SecurityPolicy
from app.core.tenancy import get_current_tenant_id
from app.core.query_engine import apply_dynamic_filters
from sqlalchemy.orm.attributes import flag_modified
from flask_login import current_user

class CrudService:
    @staticmethod
    def get_entity_by_slug(slug):
        tenant_id = get_current_tenant_id()
        return EntityDefinition.query.filter_by(tenant_id=tenant_id, name=slug).first_or_404()

    @staticmethod
    def create_record(entity_id, data):
        tenant_id = get_current_tenant_id()
        record = Record(tenant_id=tenant_id, entity_definition_id=entity_id, data=data)
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def read_records(entity_id, filters=None):
        query = Record.query.filter_by(entity_definition_id=entity_id)
        
        # 1. Apply Dynamic Component Filters
        if filters:
            query = apply_dynamic_filters(query, filters, model=Record)
            
        # 2. Enforce Security Policies
        tenant_id = get_current_tenant_id()
        policies = SecurityPolicy.query.filter_by(
            tenant_id=tenant_id,
            entity_definition_id=entity_id,
            role_id=current_user.role_id,
            action='READ'
        ).all()
        print(f"DEBUG: Found {len(policies)} policies for role {current_user.role_id}")
        
        for policy in policies:
            print(f"DEBUG: Applying policy rules: {policy.filter_rules}")
            if policy.filter_rules:
                query = apply_dynamic_filters(query, policy.filter_rules, model=Record)
                
        return query.all()

    @staticmethod
    def update_record(record_id, data):
        record = Record.query.get(record_id)
        if record:
            # Create a new dict to ensure detection
            new_data = record.data.copy()
            new_data.update(data)
            record.data = new_data
            flag_modified(record, 'data') # Mark as dirty
            db.session.commit()
        return record

    @staticmethod
    def delete_record(record_id):
        record = Record.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return True
