from django.db import models
from django.db.models import Avg, Count, Q

from routes.hiking_time import estimated_duration_min


class RouteQuerySet(models.QuerySet):
    def with_rating_stats(self):
        return self.annotate(rating_average=Avg("ratings__stars"), rating_count=Count("ratings"))


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

    objects = RouteQuerySet.as_manager()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def _rating_stats(self):
        if hasattr(self, "rating_count"):
            return self.rating_average, self.rating_count
        stats = self.ratings.aggregate(average=Avg("stars"), count=Count("id"))
        return stats["average"], stats["count"]

    def to_dict(self):
        average, count = self._rating_stats()
        return {
            "id": self.id,
            "name": self.name,
            "region": self.region,
            "distance_km": self.distance_km,
            "elevation_gain_m": self.elevation_gain_m,
            "difficulty": self.difficulty,
            "estimated_duration_min": estimated_duration_min(self.distance_km, self.elevation_gain_m),
            "rating_average": round(average, 1) if average is not None else None,
            "rating_count": count,
            "created_at": self.created_at.isoformat(),
        }


class Rating(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField()
    comment = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(stars__gte=1) & Q(stars__lte=5),
                name="rating_stars_between_1_and_5",
            )
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "stars": self.stars,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
