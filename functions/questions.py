import uuid
from pydantic import BaseModel



class Question(BaseModel):
    question_statement : str
    options : list[str]


class QuestionList(BaseModel):
    questions : list[Question]


def to_dict(obj):
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        return {k: to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, list):
        return [to_dict(i) for i in obj]
    else:
        return obj


def questions_to_dict(questions):
    q_list = to_dict(questions)

    # add random q_id
    for q in q_list:
        q["q_id"] = str(uuid.uuid4())
    return q_list