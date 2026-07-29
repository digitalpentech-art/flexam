from sqlalchemy.orm import Query
from app.models.metadata import Record
from flask_login import current_user

def apply_dynamic_filters(query: Query, filters: list, model=None):
    """
    Applies dynamic filters to a SQLAlchemy query.
    
    :param query: SQLAlchemy Query object
    :param filters: List of filter dictionaries from component configuration
    :param model: The SQLAlchemy model class (needed if filtering on Record.data)
    """
    for f in filters:
        column_name = f['db_column']
        operator = f['operator']
        value_source = f['value_source']
        
        # 1. Resolve the value dynamically
        if value_source == 'user_attribute':
            target_value = getattr(current_user, f['user_attribute_key'])
        else:
            target_value = f.get('value')
        
        # 2. Apply filter based on model type
        if model and model == Record:
            # Handle JSONB filtering for Records
            if operator == '==':
                query = query.filter(Record.data[column_name].astext == str(target_value))
            # Extend for other operators as needed
        else:
            # Handle standard model attribute filtering
            column = getattr(model, column_name)
            if operator == '==':
                query = query.filter(column == target_value)
            elif operator == 'in':
                query = query.filter(column.in_(target_value))
            # Extend for other operators as needed
            
    return query
