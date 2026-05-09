import random
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from users.constants import (
    AVATAR_COLORS,
    AVATAR_DEFAULT_LETTER,
    AVATAR_FONT_NAME,
    AVATAR_FONT_SIZE,
    AVATAR_FORMAT,
    AVATAR_SIZE,
    AVATAR_TEXT_ANCHOR,
    AVATAR_TEXT_COLOR,
    AVATAR_UPLOAD_TO,
    PHONE_EIGHT_PREFIX,
    PHONE_REGEX,
    PHONE_RUSSIAN_PREFIX,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        validators=(RegexValidator(regex=PHONE_REGEX),),
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    avatar = models.ImageField(upload_to=AVATAR_UPLOAD_TO, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "surname")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("surname", "name", "email")

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            avatar_file = self.generate_avatar()
            self.avatar.save(f"avatar_{self.email}.png", avatar_file, save=False)

        if self.phone and self.phone.startswith(PHONE_EIGHT_PREFIX):
            self.phone = f"{PHONE_RUSSIAN_PREFIX}{self.phone[1:]}"

        super().save(*args, **kwargs)

    def generate_avatar(self):
        color = random.choice(AVATAR_COLORS)
        image = Image.new("RGB", AVATAR_SIZE, color)
        draw = ImageDraw.Draw(image)
        letter = self.name[0].upper() if self.name else AVATAR_DEFAULT_LETTER

        try:
            font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox(AVATAR_TEXT_ANCHOR, letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (
            (AVATAR_SIZE[0] - text_width) // 2,
            (AVATAR_SIZE[1] - text_height) // 2,
        )

        draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format=AVATAR_FORMAT)
        buffer.seek(0)

        return ContentFile(buffer.read(), f"avatar_{self.email}.png")
