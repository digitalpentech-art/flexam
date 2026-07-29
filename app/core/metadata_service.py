from app import db
from app.models.metadata import RelationshipDefinition, RecordLink, Record
from app.core.tenancy import get_current_tenant_id

class MetadataService:
    @staticmethod
    def create_relationship(name, source_entity_id, target_entity_id, rel_type):
        tenant_id = get_current_tenant_id()
        rel = RelationshipDefinition(
            tenant_id=tenant_id,
            name=name,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=rel_type
        )
        db.session.add(rel)
        db.session.commit()
        return rel

    @staticmethod
    def link_records(relationship_id, source_record_id, target_record_id):
        tenant_id = get_current_tenant_id()
        link = RecordLink(
            tenant_id=tenant_id,
            relationship_id=relationship_id,
            source_record_id=source_record_id,
            target_record_id=target_record_id
        )
        db.session.add(link)
        db.session.commit()
        return link

    @staticmethod
    def get_related_records(source_record_id, relationship_id):
        links = RecordLink.query.filter_by(
            relationship_id=relationship_id,
            source_record_id=source_record_id
        ).all()
        
        target_ids = [link.target_record_id for link in links]
        return Record.query.filter(Record.id.in_(target_ids)).all()
