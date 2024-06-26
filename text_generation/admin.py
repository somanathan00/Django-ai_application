from django.contrib import admin
from .models import ImageInfo
from django.utils.html import mark_safe
class ImageInfoAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'color', 'what_the_image_is','quantity','dimensions')
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" />')
        return "No Image"

    image_tag.short_description = 'Image'

admin.site.register(ImageInfo, ImageInfoAdmin)
# Register your models here.
