from django.db import models
import uuid
from product.models import TimeStampedModel

"""Start of Creating Models for SiteSettings Section"""
class contantInfo(TimeStampedModel):
    """Model for Contact Information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    business_hours = models.TextField()
    facebook = models.URLField()
    twitter = models.URLField()
    instagram = models.URLField()
    youtube = models.URLField()
    linkedin = models.URLField()
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
    
class RequestQuote(TimeStampedModel):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    companyName = models.CharField(max_length=255)
    interest = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.firstName

    class Meta:
        verbose_name = "Request Quote"
        verbose_name_plural = "Request Quotes"
    
    