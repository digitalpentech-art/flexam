from app.models.grading import GradingRule

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
