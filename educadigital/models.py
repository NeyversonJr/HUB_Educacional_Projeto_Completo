import uuid
import random
from django.db import models


class BaseModel(models.Model):
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Question(BaseModel):
    category = models.ForeignKey(
        Category,
        related_name="questions",
        on_delete=models.CASCADE
    )
    question = models.CharField(max_length=600)
    marks = models.IntegerField(default=5)

    def __str__(self):
        return self.question

    def get_answers(self):
        answer_objs = list(Answer.objects.filter(question=self))
        random.shuffle(answer_objs)

        data = []
        for answer_obj in answer_objs:
            data.append({
                "answer": answer_obj.answer,
                "is_correct": answer_obj.is_correct
            })

        return data


class Answer(BaseModel):
    question = models.ForeignKey(
        Question,
        related_name="answers",
        on_delete=models.CASCADE
    )
    answer = models.CharField(max_length=600)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer
