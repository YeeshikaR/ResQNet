from backend.services.priority_service import formula_priority


def test_formula_priority_caps_at_100():
    assert formula_priority('critical', 100) == 100


def test_formula_priority_adds_people_bonus():
    assert formula_priority('medium', 5) == 60
