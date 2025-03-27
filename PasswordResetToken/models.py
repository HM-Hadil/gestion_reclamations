from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid
class PasswordResetToken(models.Model):
    """
    Model to manage password reset tokens
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(
        max_length=255, 
        unique=True, 
        default=uuid.uuid4
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override save method to set expiration time
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        
        # Ensure only one active token per user
        if not self.pk:
            PasswordResetToken.objects.filter(
                user=self.user, 
                expires_at__gt=timezone.now()
            ).delete()
        
        super().save(*args, **kwargs)

    def is_valid(self):
        """
        Check if the token is still valid
        """
        return self.expires_at and timezone.now() <= self.expires_at

    def __str__(self):
        return f"Password Reset Token for {self.user.username}"

    class Meta:
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'token'], 
                name='unique_user_token'
            )
        ]
