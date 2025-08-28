from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    about = models.CharField(max_length=100)   # 총 지출, 총 수입 등
    type = models.CharField(max_length=50)     # 매주, 매월
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField()
    result_image = models.ImageField(upload_to="analysis/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.about} ({self.type})"
