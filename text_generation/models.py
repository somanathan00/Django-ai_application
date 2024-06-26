from django.db import models
from PIL import Image
import imagehash
from django.contrib import admin

class ImageInfo(models.Model):
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    color = models.CharField(max_length=100, blank=True)
    what_the_image_is = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    dimensions= models.CharField(max_length=100, default="Null")
    image_hash = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.what_the_image_is} ({self.color}) - {self.quantity}"

    def calculate_image_hash(self):
        # Calculate dHash (difference hash) for the image
        hash_value = imagehash.dhash(Image.open(self.image))
        return str(hash_value)

    @classmethod
    def upload_or_update_image(cls, image, what_the_image_is, color, dimensions):
        # Calculate hash for the uploaded image
        uploaded_image_hash = cls.calculate_image_hash_from_image(image)

        try:
            # Look for existing ImageInfo based on image hash
            existing_image_info = cls.objects.get(image_hash=uploaded_image_hash)
            existing_image_info.quantity += 1
            existing_image_info.save()
            return existing_image_info
        except cls.DoesNotExist:
            try:
                # If no matching image hash, check for what_the_image_is and color
                matching_image_info = cls.objects.get(what_the_image_is=what_the_image_is, color=color)
                matching_image_info.quantity += 1
                matching_image_info.save()
                return matching_image_info
            except cls.DoesNotExist:
                # If no matching what_the_image_is and color, create a new entry
                new_image_info = cls(image=image, what_the_image_is=what_the_image_is, color=color, dimensions=dimensions)
                new_image_info.image_hash = uploaded_image_hash  # Assign the image hash
                new_image_info.save()
                return new_image_info

    @staticmethod
    def calculate_image_hash_from_image(image):
        # Calculate dHash (difference hash) for the image
        hash_value = imagehash.dhash(Image.open(image))
        return str(hash_value)

