from flask import g
from app.models.metadata import PageDefinition, MenuDefinition, FieldDefinition
from app.core.tenancy import get_current_tenant_id
from app import create_app

def get_page_by_slug(tenant_id, slug):
    return PageDefinition.query.filter_by(tenant_id=tenant_id, slug=slug).first_or_404()

def resolve_component_config(component):
    """
    If component has entity_id/field_ids, override/populate
    component.configuration with schema-driven data.
    """
    if not component.entity_id:
        return component.configuration

    # Fetch relevant fields
    fields = FieldDefinition.query.filter(
        FieldDefinition.entity_id == component.entity_id,
        FieldDefinition.id.in_(component.field_ids)
    ).all()
    
    # Sort fields based on field_ids order
    field_map = {f.id: f for f in fields}
    ordered_fields = [field_map[fid] for fid in component.field_ids if fid in field_map]
    
    config = component.configuration.copy()
    
    if component.component_type == 'table':
        config['columns'] = [{'key': f.name, 'label': f.label} for f in ordered_fields]
    elif component.component_type == 'form':
        config['fields'] = ordered_fields
        
    return config

def get_menu(slug):
    tenant_id = get_current_tenant_id()
    return MenuDefinition.query.filter_by(tenant_id=tenant_id, slug=slug).first()

# Context processor for templates
def register_ui_context_processors(app):
    @app.context_processor
    def inject_ui_helpers():
        return dict(get_menu=get_menu, resolve_component_config=resolve_component_config)
