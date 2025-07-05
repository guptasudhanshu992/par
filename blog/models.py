from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from bs4 import BeautifulSoup
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
import math
from django_ckeditor_5.fields import CKEditor5Field
import uuid
import re
from django.utils.html import strip_tags
import os

User = get_user_model()

class BlogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    ext = filename.split('.')[-1].lower()
    folder = 'images' if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp'] else 'videos' if ext in ['mp4', 'mov', 'avi', 'webm'] else 'files'
    return os.path.join(f'media/{folder}', filename)

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
    ]

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to=upload_to)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, editable=False)
    title = models.CharField(max_length=255, blank=True, help_text="Optional title or alt text.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            self.media_type = 'image'
        elif ext in ['.mp4', '.mov', '.avi', '.webm']:
            self.media_type = 'video'
        else:
            self.media_type = 'file'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or os.path.basename(self.file.name)

    class Meta:
        ordering = ['-uploaded_at']


class Blog(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    cover_image = models.ForeignKey('Media', on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs_using_media')
    snippet = CKEditor5Field('Snippet', config_name='extends', null=True, blank=True)
    content = CKEditor5Field('Content', config_name='extends', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(BlogCategory, blank=True)
    tags = models.ManyToManyField(BlogTag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)
    published_at = models.DateTimeField(default=timezone.now, blank=True)
    reading_time = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Blog)
def update_blogpost_word_count(sender, instance, **kwargs):
    combined_text = strip_tags(instance.content or "") + " " + strip_tags(instance.snippet or "")
    words = re.findall(r'\b\w+\b', combined_text)
    instance.reading_time = max(1, math.ceil(len(words) / 200))
    Blog.objects.filter(pk=instance.pk).update(reading_time=instance.reading_time)
