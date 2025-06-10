from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Photo(models.Model):
    """Model to store photo metadata from macOS Photos app"""
    
    # Basic Information
    uuid = models.CharField(max_length=100, unique=True, db_index=True)
    original_filename = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    path = models.TextField(blank=True)
    path_edited = models.TextField(blank=True, null=True)
    
    # Photo type flags
    is_photo = models.BooleanField(default=True)
    is_movie = models.BooleanField(default=False)
    is_cloud_photo = models.BooleanField(default=False)
    has_adjustments = models.BooleanField(default=False)
    is_missing = models.BooleanField(default=False)
    
    # Dates & Times
    date = models.DateTimeField(db_index=True, null=True)
    date_modified = models.DateTimeField(null=True)
    date_added = models.DateTimeField(db_index=True, null=True)
    exif_datetime = models.DateTimeField(null=True)
    
    # Metadata & Descriptions
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    # Location Information
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    place_name = models.CharField(max_length=255, blank=True)
    place_country_code = models.CharField(max_length=10, blank=True)
    place_address = models.TextField(blank=True)
    place_is_home = models.BooleanField(default=False)
    
    # Camera & Technical Data
    uti = models.CharField(max_length=100, blank=True)
    live_photo = models.BooleanField(default=False)
    live_photo_video_uuid = models.CharField(max_length=100, blank=True)
    live_photo_video_path = models.TextField(blank=True)
    is_burst = models.BooleanField(default=False)
    burst_uuid = models.CharField(max_length=100, blank=True)
    is_hdr = models.BooleanField(default=False)
    is_portrait = models.BooleanField(default=False)
    is_screenshot = models.BooleanField(default=False)
    is_slow_mo = models.BooleanField(default=False)
    is_selfie = models.BooleanField(default=False)
    is_panorama = models.BooleanField(default=False)
    has_raw = models.BooleanField(default=False)
    raw_path = models.TextField(blank=True)
    
    # Image properties
    orientation = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # For videos
    
    # EXIF data
    camera_make = models.CharField(max_length=100, blank=True)
    camera_model = models.CharField(max_length=100, blank=True)
    fstop = models.FloatField(null=True, blank=True)
    aperture = models.FloatField(null=True, blank=True)
    iso = models.IntegerField(null=True, blank=True)
    focal_length = models.FloatField(null=True, blank=True)
    exposure_time = models.FloatField(null=True, blank=True)
    
    # Timezone
    timezone_name = models.CharField(max_length=100, blank=True)
    timezone_offset = models.IntegerField(null=True, blank=True)
    
    # Apple Photos categorization
    favorite = models.BooleanField(default=False, db_index=True)
    hidden = models.BooleanField(default=False)
    in_trash = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    
    # File size
    original_file_size = models.BigIntegerField(null=True, blank=True)
    
    # Timestamps for our database
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'favorite']),
            models.Index(fields=['camera_make', 'camera_model']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.filename or self.original_filename} ({self.uuid})"


class Album(models.Model):
    """Model to store album information"""
    name = models.CharField(max_length=255, db_index=True)
    photos = models.ManyToManyField(Photo, related_name='albums')
    is_shared = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['name', 'is_shared']
    
    def __str__(self):
        return self.name


class Person(models.Model):
    """Model to store person information"""
    name = models.CharField(max_length=255, db_index=True)
    uuid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    photos = models.ManyToManyField(Photo, related_name='persons')
    
    def __str__(self):
        return self.name


class Keyword(models.Model):
    """Model to store keywords/tags"""
    name = models.CharField(max_length=255, unique=True, db_index=True)
    photos = models.ManyToManyField(Photo, related_name='keywords')
    
    def __str__(self):
        return self.name


class Label(models.Model):
    """Model to store machine-learning labels"""
    name = models.CharField(max_length=255, unique=True, db_index=True)
    photos = models.ManyToManyField(Photo, related_name='labels')
    
    def __str__(self):
        return self.name


class PhotoScore(models.Model):
    """Model to store Apple Photos ML scores"""
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE, related_name='score')
    
    # Overall scores
    overall = models.FloatField(null=True, blank=True)
    aesthetics = models.FloatField(null=True, blank=True)
    curation = models.FloatField(null=True, blank=True)
    noise = models.FloatField(null=True, blank=True)
    
    # Pleasant scores
    pleasant_camera_tilt = models.FloatField(null=True, blank=True)
    pleasant_composition = models.FloatField(null=True, blank=True)
    pleasant_lighting = models.FloatField(null=True, blank=True)
    pleasant_pattern = models.FloatField(null=True, blank=True)
    pleasant_subject_movement = models.FloatField(null=True, blank=True)
    pleasant_symmetry = models.FloatField(null=True, blank=True)
    pleasant_texture = models.FloatField(null=True, blank=True)
    pleasant_tone = models.FloatField(null=True, blank=True)
    
    # Utility scores
    utility_activity = models.FloatField(null=True, blank=True)
    utility_blurry = models.FloatField(null=True, blank=True)
    utility_colorful = models.FloatField(null=True, blank=True)
    utility_interesting_subject = models.FloatField(null=True, blank=True)
    utility_low_light = models.FloatField(null=True, blank=True)
    utility_not_on_tripod = models.FloatField(null=True, blank=True)
    utility_people = models.FloatField(null=True, blank=True)
    utility_pet = models.FloatField(null=True, blank=True)
    utility_poor_contrast = models.FloatField(null=True, blank=True)
    utility_quality = models.FloatField(null=True, blank=True)
    utility_sharply_focused = models.FloatField(null=True, blank=True)
    utility_still_action = models.FloatField(null=True, blank=True)
    utility_uninteresting_subject = models.FloatField(null=True, blank=True)
    utility_vibrance = models.FloatField(null=True, blank=True)
    
    # Curation scores
    curation_blurry = models.FloatField(null=True, blank=True)
    curation_noise = models.FloatField(null=True, blank=True)
    curation_interesting_subject = models.FloatField(null=True, blank=True)
    curation_scene = models.FloatField(null=True, blank=True)
    curation_light = models.FloatField(null=True, blank=True)
    curation_activity = models.FloatField(null=True, blank=True)
    curation_animated = models.FloatField(null=True, blank=True)
    curation_face = models.FloatField(null=True, blank=True)
    curation_landscape = models.FloatField(null=True, blank=True)
    curation_time = models.FloatField(null=True, blank=True)
    curation_version = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Scores for {self.photo.uuid}"


class Face(models.Model):
    """Model to store face detection information"""
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='faces')
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='faces')
    
    # Face coordinates (normalized 0-1)
    center_x = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    center_y = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    width = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    height = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Face attributes
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    ethnicity = models.CharField(max_length=50, blank=True)
    quality = models.FloatField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Face in {self.photo.uuid} - {self.person.name if self.person else 'Unknown'}"