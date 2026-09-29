from django.db import models

class Crop(models.Model):

    name=models.CharField(max_length=100)

    scientific_name=models.CharField(max_length=150)

    description=models.TextField()

    image=models.ImageField(upload_to="crops/")

    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name