# Design: Dynamic Entity Autoincrement (Sequence) Fields

## Goal
Support user-friendly, sequential identifiers (e.g., "Student #1001") for dynamically defined entities in a multi-tenant system, without compromising the security of using UUIDs as primary keys.

## Proposed Architecture

### 1. New Model: `SequenceState`
A dedicated table to maintain the current counter value per tenant and per entity definition.

```python
class SequenceState(db.Model):
    __tablename__ = 'sequence_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    entity_definition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    
    # The next available value to assign
    next_value = db.Column(db.Integer, default=1)
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'entity_definition_id', name='_tenant_entity_sequence_uc'),
    )
```

### 2. Workflow for `Record` Creation
When `records_bp.create_record` is called:
1.  Identify the `EntityDefinition`.
2.  Inspect `FieldDefinition` associated with this `EntityDefinition` to find any fields with `field_type='autoincrement'`.
3.  For each `autoincrement` field:
    *   Find or create the `SequenceState` for this `(tenant_id, entity_definition_id)`.
    *   Atomically increment `next_value` (using `SELECT ... FOR UPDATE` or `db.session` transaction handling).
    *   Insert the current `next_value` into the `Record.data` JSON blob.

## Impact Analysis
- **Schema:** Requires a new table `sequence_states`.
- **API:** No breaking changes to existing endpoints.
- **Concurrency:** Requires careful transaction management to ensure sequence values are unique and non-overlapping.
