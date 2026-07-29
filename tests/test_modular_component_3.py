import pytest
from flask import render_template_string
from app.models.metadata import ComponentDefinition

def test_render_table_macro(app):
    with app.app_context():
        # Setup component data
        config = {
            "columns": [{"key": "name", "label": "Name"}],
            "data": [{"id": "1", "name": "Test Row"}]
        }
        component = ComponentDefinition(name="Test Table", component_type="table", configuration=config)
        
        # Test macro rendering
        template = "{% from 'macros/render.html' import render_table %}{{ render_table(component) }}"
        rendered = render_template_string(template, component=component)
        
        assert "Test Table" in rendered
        assert "Name" in rendered
        assert "Test Row" in rendered
        assert "table" in rendered

def test_render_form_macro(app):
    with app.app_context():
        # Setup component data
        config = {
            "submit_url": "/submit",
            "fields": [{"name": "test_input", "label": "Test Input", "field_type": "text"}]
        }
        component = ComponentDefinition(name="Test Form", component_type="form", configuration=config)
        
        # Test macro rendering
        template = "{% from 'macros/render.html' import render_form %}{{ render_form(component) }}"
        rendered = render_template_string(template, component=component)
        
        assert "Test Form" in rendered
        assert "test_input" in rendered
        assert "/submit" in rendered
        assert "input" in rendered
