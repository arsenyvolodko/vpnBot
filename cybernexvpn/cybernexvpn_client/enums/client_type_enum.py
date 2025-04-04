from django.db.models import TextChoices


class ClientTypeEnum(TextChoices):
    UNKNOWN = "unknown", "Неизвестен ❓"
    IPHONE = "iphone", "Iphone "
    ANDROID = "android", "Android 📱"
    MACOS = "macos", "MacOS ⌘"
    WINDOWS = "windows", "Windows 🖥️"
