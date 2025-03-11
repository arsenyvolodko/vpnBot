from django.db.models import TextChoices


class ClientTypeEnum(TextChoices):
    UNKNOWN = "unknown", "Неизвестен ❓"
    ANDROID = "android", "Android 📱"
    Iphone = "iphone", "Iphone "
    PC = "pc", "PC 💻"
