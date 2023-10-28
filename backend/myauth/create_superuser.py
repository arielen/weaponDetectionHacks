from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_superuser(sender, **kwargs) -> None:
    if not User.objects.filter(is_superuser=True).exists():
        username = 'user'
        email = 'user@example.com'
        password = 'user'
        User.objects.create_superuser(username, email, password)
        print(f"Created default superuser: {username} / {password}")
