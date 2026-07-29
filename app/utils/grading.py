from app.models.grading import GradingRule
from app.models.examination import ExamAttempt
from app.models.response import Response
from app.models.question import Question, QuestionOption
from app.models.results import Result, ResultComponent
from app.simulations.engine import evaluate_simulation
from app.extensions import db

def compute_grade(tenant_id, score):
    rule = GradingRule.query.filter_by(tenant_id=tenant_id).first()
    if not rule:
        return "N/A"
    
    # Sort rules by min score descending
    sorted_rules = sorted(rule.rules.items(), key=lambda x: x[1]['min'], reverse=True)
    
    for grade, criteria in sorted_rules:
        if score >= criteria['min']:
            return grade
            
    return "F"

def calculate_score(attempt_id):
    attempt = ExamAttempt.query.get(attempt_id)
    if not attempt:
        return None

    # Clear existing results
    Result.query.filter_by(exam_attempt_id=attempt_id).delete()
    
    new_result = Result(tenant_id=attempt.examination.tenant_id, exam_attempt_id=attempt_id, total_score=0.0)
    db.session.add(new_result)
    
    total_score = 0.0
    responses = Response.query.filter_by(attempt_id=attempt_id).all()
    
    for resp in responses:
        if resp.response_mode == 'mcq':
            option_id = resp.content.get('option_id')
            option = QuestionOption.query.get(option_id)
            if option and option.is_correct:
                question = Question.query.get(resp.question_id)
                total_score += question.marks if question else 0
        elif resp.response_mode == 'simulation':
            # Use simulation engine to evaluate practical score
            total_score += evaluate_simulation(resp.content.get('sim_type'), resp.content.get('data'))
        
        # Essay/File/Handwriting remain 0 for automated grading
        
    new_result.total_score = total_score
    new_result.final_grade = compute_grade(new_result.tenant_id, total_score)
    db.session.commit()
    return new_result
