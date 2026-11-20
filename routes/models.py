from django.db import models


class Route(models.Model):
    class Difficulty(models.TextChoices):
        """SAC hiking scale."""

        T1 = "T1", "Hiking"
        T2 = "T2", "Mountain hiking"
        T3 = "T3", "Demanding mountain hiking"
        T4 = "T4", "Alpine hiking"
        T5 = "T5", "Demanding alpine hiking"
        T6 = "T6", "Difficult alpine hiking"

    name = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    distance_km = models.FloatField()
    elevation_gain_m = models.PositiveIntegerField()
    difficulty = models.CharField(max_length=2, choices=Difficulty.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "region": self.region,
            "distance_km": self.distance_km,
            "elevation_gain_m": self.elevation_gain_m,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat(),
        }
