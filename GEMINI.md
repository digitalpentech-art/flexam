# FLEXAM Project Documentation

## UI/UX Design System
The `flexam` application follows a modern corporate aesthetic, achieved through **Tailwind CSS** and **Jinja2 Macros**.

### Design Principles
- **Corporate Cleanliness:** Light backgrounds (`gray-50`), crisp borders (`gray-200`), and rounded components (`rounded-lg`).
- **Standardized Interactivity:** Utilize Alpine.js for client-side behaviors.
- **Maintainability:** All repetitive UI elements (buttons, inputs, tables) MUST be implemented using Jinja2 macros.

### Design Tokens
- **Primary Color:** `#337ab7` (Tailwind `primary`)
- **Containers:** `bg-white shadow-sm border border-gray-200 rounded-lg`
- **Buttons:**
    - Primary: `bg-primary text-white hover:bg-blue-800 transition`
    - Secondary: `bg-gray-200 text-gray-800 hover:bg-gray-300 transition`

### Macro Usage
When adding new UI elements, follow these mandatory conventions:
- **Buttons:** `{% from 'macros/ui.html' import button %}`
- **Inputs:** `{% from 'macros/ui.html' import input %}`
- **Form Fields:** `{% from 'macros/forms.html' import render_field %}`

NEVER mix custom raw CSS classes with these macros unless authorized by the team lead.
