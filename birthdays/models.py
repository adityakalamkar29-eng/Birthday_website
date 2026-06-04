from django.db import models

def photo_upload_path(instance, filename):
    dob_str = instance.person.dob.strftime('%Y-%m-%d')
    ext = filename.rsplit('.', 1)[-1].lower()
    import uuid
    return f'photos/{dob_str}/{uuid.uuid4().hex[:8]}.{ext}'

class BirthdayPerson(models.Model):
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, blank=True, help_text="Optional nickname/pet name")
    dob = models.DateField(unique=True, help_text="Date of Birth (used in URL)")
    message = models.TextField(blank=True, help_text="Personal birthday message")
    song_url = models.CharField(max_length=500, blank=True,
        help_text="Direct MP3 audio URL (e.g. from Google Drive, Dropbox, etc.)")
    song_file = models.FileField(upload_to='songs/', blank=True, null=True,
        help_text="Or upload an MP3 file directly")
    song_name = models.CharField(max_length=200, blank=True, help_text="Song name to display")
    theme_color = models.CharField(max_length=7, default='#e91e8c',
        help_text="Hex color code e.g. #ff69b4")
    admin_password = models.CharField(max_length=100, help_text="Password to manage this page")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.dob}"

    @property
    def display_name(self):
        return self.nickname if self.nickname else self.name

    @property
    def has_music(self):
        return bool(self.song_file or self.song_url)

    @property
    def music_source(self):
        if self.song_file:
            return self.song_file.url
        return self.song_url


class BirthdayPhoto(models.Model):
    person = models.ForeignKey(BirthdayPerson, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=photo_upload_path)
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Photo for {self.person.name}"
