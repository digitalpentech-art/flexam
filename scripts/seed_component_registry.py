from app import db
from app.models.registry import ComponentRegistry

def seed_registry():
    # Define schemas for core components
    schemas = [
        {
            'component_type': 'text',
            'property_schema': {
                'placeholder': {'type': 'text', 'label': 'Placeholder', 'default': ''},
                'help_text': {'type': 'text', 'label': 'Help Text', 'default': ''}
            },
            'ui_metadata': {'icon': 'type', 'group': 'Fields'}
        },
        {
            'component_type': 'number',
            'property_schema': {
                'min': {'type': 'number', 'label': 'Min Value'},
                'max': {'type': 'number', 'label': 'Max Value'}
            },
            'ui_metadata': {'icon': 'hash', 'group': 'Fields'}
        },
        {
            'component_type': 'date',
            'property_schema': {},
            'ui_metadata': {'icon': 'calendar', 'group': 'Fields'}
        },
        {
            'component_type': 'boolean',
            'property_schema': {
                'label': {'type': 'text', 'label': 'Checkbox Label', 'default': 'Active?'}
            },
            'ui_metadata': {'icon': 'check-square', 'group': 'Fields'}
        },
        {
            'component_type': 'table',
            'property_schema': {
                'entity_id': {'type': 'reference', 'label': 'Source Entity', 'required': True},
                'show_search': {'type': 'boolean', 'label': 'Enable Search', 'default': True},
                'show_pagination': {'type': 'boolean', 'label': 'Enable Pagination', 'default': True}
            },
            'ui_metadata': {'icon': 'table', 'group': 'Data'}
        },
        {
            'component_type': 'form',
            'property_schema': {
                'entity_id': {'type': 'reference', 'label': 'Target Entity', 'required': True},
                'submit_url': {'type': 'text', 'label': 'Submission URL', 'required': True}
            },
            'ui_metadata': {'icon': 'form', 'group': 'Inputs'}
        }
    ]
    
    for s in schemas:
        reg = ComponentRegistry.query.filter_by(component_type=s['component_type']).first()
        if not reg:
            db.session.add(ComponentRegistry(**s))
    
    db.session.commit()
    print("Component Registry seeded successfully.")

if __name__ == '__main__':
    from app import create_app
    app = create_app('development')
    with app.app_context():
        seed_registry()
