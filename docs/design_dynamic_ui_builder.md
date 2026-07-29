# Design & Implementation Plan: Dynamic Profile & Form Builder

This plan outlines the roadmap for turning the current dynamic metadata system into a **No-Code Visual Form Designer** (similar to Microsoft Visual Studio or Salesforce Page Layout Editor). This allows organizations to visually align, style, resize, and position fields based on their unique requirements.

---

## Technical Architecture Overview

To achieve a fully dynamic visual grid editor, we split the architecture into three parts:

```
+-----------------------------------+
|       Visual Editor UI            |  <-- Drag, resize, configure padding,
|  (app/templates/ui_builder.html)   |      typography, column-spans
+-----------------+-----------------+
                  |
         Saves Layout JSON
                  v
+-----------------+-----------------+
|      Metadata Schema Manager      |  <-- Persists grid coords, row-spans,
|   (app/core/schema_manager.py)    |      styles in JSONB layout_config
+-----------------+-----------------+
                  |
        Renders Dynamic HTML
                  v
+-----------------+-----------------+
|     Metadata-Driven Renderer      |  <-- Interprets layout JSON and outputs
|    (Jinja2 Macro / JS Engine)     |      pixel-perfect Tailwind grid forms
+-----------------------------------+
```

---

## Phase 1: Grid-Based Editor (The Studio Canvas)
**Goal:** Replace the current simple vertical sorting list with a responsive 12-column interactive canvas.

### 1.1 UI Library Choice
We will integrate **Gridstack.js** (or a lightweight equivalent if we prefer Vanilla JS) in `ui_builder.html`.
*   **Gridstack.js** allows visual blocks to be:
    *   Dragged to change position (`x`, `y` coordinates).
    *   Resized to change width (`width` = column span, from 1 to 12) and height (`height` = row height).

### 1.2 Layout Configuration Schema (JSON)
When the Admin clicks "Save Layout", the frontend will capture the coordinates of every field and compile them into a layout payload.

#### Target JSON format saved to `EntityDefinition.layout_config`:
```json
{
  "columns": 12,
  "sections": [
    {
      "id": "sec_basic",
      "title": "Profile Primary Details",
      "style": "bg-white p-6 shadow rounded-lg border border-gray-100",
      "fields": [
        {
          "field_name": "first_name",
          "x": 0, "y": 0, "width": 6, "height": 1,
          "styling": {
            "typography": "text-lg font-bold text-gray-800",
            "align": "left",
            "input_border": "border-blue-300"
          }
        },
        {
          "field_name": "last_name",
          "x": 6, "y": 0, "width": 6, "height": 1,
          "styling": {
            "typography": "text-lg font-bold text-gray-800",
            "align": "left",
            "input_border": "border-blue-300"
          }
        }
      ]
    }
  ]
}
```

---

## Phase 2: Metadata-Driven Page Renderer (The Interpreter)
**Goal:** Create a reusable component that parses the layout configuration and renders the actual user profile.

### 2.1 The Render Macro
We will implement a Jinja2 macro, `render_dynamic_layout(entity, record_data=None)`, inside `app/templates/macros/forms.html`.

### 2.2 Rendering Logic (Psuedocode)
```html
{# Loop through defined sections #}
{% for section in entity.layout_config.sections %}
    <div class="{{ section.style }} grid grid-cols-12 gap-4">
        <h3 class="col-span-12 text-xl font-bold">{{ section.title }}</h3>
        
        {# Loop through fields assigned to this section #}
        {% for grid_field in section.fields %}
            {% set field_meta = entity.fields.filter_by(name=grid_field.field_name).first() %}
            
            <div style="grid-column: span {{ grid_field.width }};" class="{{ grid_field.styling.typography }}">
                <label class="block text-sm font-semibold mb-1">{{ field_meta.label }}</label>
                
                {# Render input elements based on field types (text, autoincrement, date) #}
                {% if field_meta.field_type == 'text' %}
                    <input type="text" value="{{ record_data[field_meta.name] if record_data else '' }}" class="w-full p-2 border {{ grid_field.styling.input_border }}">
                {% elif field_meta.field_type == 'autoincrement' %}
                    <span class="p-2 bg-gray-100 border block rounded font-mono">
                        {{ record_data[field_meta.name] if record_data else '(Auto-assigned)' }}
                    </span>
                {% endif %}
            </div>
        {% endfor %}
    </div>
{% endfor %}
```

---

## Phase 3: Interactive Inspector Panel
**Goal:** Build the Microsoft Visual Studio-style configuration panel alongside the canvas.

When an Admin clicks on a field box within the visual editor:
1.  **Open Inspector:** A side panel slides out from the right.
2.  **Configurations Available:**
    *   **Text Size Dropdown:** (Small, Medium, Large, Heading) -> Maps to `text-sm`, `text-base`, `text-lg`, `text-2xl`.
    *   **Text Weight Toggle:** Bold / Normal.
    *   **Input Border Style:** (Soft, Solid, Outlined).
    *   **Alignment Buttons:** (Left, Center, Right).
3.  **Real-time Preview:** As the user changes these settings, Alpine.js instantly applies the CSS classes on the canvas so they see the result immediately.

---

## Milestones

1.  **Milestone 1:** Implement the side inspector panel layout in `ui_builder.html` using Tailwind and Alpine.js.
2.  **Milestone 2:** Integrate Gridstack.js on the canvas to support drag, position, and resize actions visually.
3.  **Milestone 3:** Connect the Inspector state to the grid items, ensuring style customizations are correctly bundled with coordinates inside the JSON payload when "Save Layout" is clicked.
4.  **Milestone 4:** Build the final `render_dynamic_layout` parser macro to render the exact pixel-perfect customized layout on the public/tenant profile pages.
