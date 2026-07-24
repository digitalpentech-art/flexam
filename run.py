import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app, db
from app.models.core import Tenant, User, Role, AuditLog
from app.models.metadata import EntityDefinition, FieldDefinition, RelationshipDefinition, Record, RecordLink
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentComponent
from app.models.examination import Examination, ExamAttempt
from app.models.results import Result, ResultComponent
from app.models.response import Response
from app.models.simulation import PracticalTask, SimulationState

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Tenant': Tenant,
        'User': User,
        'Role': Role,
        'AuditLog': AuditLog,
        'EntityDefinition': EntityDefinition,
        'FieldDefinition': FieldDefinition,
        'RelationshipDefinition': RelationshipDefinition,
        'Record': Record,
        'RecordLink': RecordLink,
        'Question': Question,
        'QuestionOption': QuestionOption,
        'Assessment': Assessment,
        'AssessmentComponent': AssessmentComponent,
        'Examination': Examination,
        'ExamAttempt': ExamAttempt,
        'Result': Result,
        'ResultComponent': ResultComponent,
        'Response': Response,
        'PracticalTask': PracticalTask,
        'SimulationState': SimulationState
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
