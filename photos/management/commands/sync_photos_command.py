import osxphotos
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import pytz
from photos.models import (
    Photo, Album, Person, Keyword, Label, PhotoScore, Face
)


class Command(BaseCommand):
    help = 'Syncs photos from macOS Photos app to Django database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Force update all photos, even if they already exist',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of photos to process in each batch',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of photos to process',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting Photos sync...')
        
        # Initialize osxphotos
        photosdb = osxphotos.PhotosDB()
        
        # Get all photos
        photos = photosdb.photos()
        
        if options['limit']:
            photos = photos[:options['limit']]
        
        total_photos = len(photos)
        self.stdout.write(f'Found {total_photos} photos in Photos library')
        
        processed = 0
        created = 0
        updated = 0
        skipped = 0
        errors = 0
        
        batch_size = options['batch_size']
        force_update = options['force_update']
        
        # Process photos in batches
        for i in range(0, total_photos, batch_size):
            batch = photos[i:i + batch_size]
            
            with transaction.atomic():
                for photo_info in batch:
                    try:
                        processed += 1
                        
                        # Check if photo already exists
                        try:
                            photo = Photo.objects.get(uuid=photo_info.uuid)
                            
                            # Check if photo has been modified
                            if not force_update and photo.date_modified:
                                photo_modified = self._make_aware(photo_info.date_modified)
                                if photo_modified and photo.date_modified >= photo_modified:
                                    skipped += 1
                                    continue
                            
                            # Update existing photo
                            self._update_photo(photo, photo_info)
                            updated += 1
                            
                        except Photo.DoesNotExist:
                            # Create new photo
                            photo = self._create_photo(photo_info)
                            created += 1
                        
                        # Update relationships
                        self._update_relationships(photo, photo_info)
                        
                        if processed % 10 == 0:
                            self.stdout.write(
                                f'Progress: {processed}/{total_photos} '
                                f'(Created: {created}, Updated: {updated}, '
                                f'Skipped: {skipped}, Errors: {errors})'
                            )
                    
                    except Exception as e:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error processing photo {photo_info.uuid}: {str(e)}'
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSync completed!\n'
                f'Total processed: {processed}\n'
                f'Created: {created}\n'
                f'Updated: {updated}\n'
                f'Skipped: {skipped}\n'
                f'Errors: {errors}'
            )
        )
    
    def _make_aware(self, dt):
        """Convert naive datetime to aware datetime"""
        if dt is None:
            return None
        if timezone.is_aware(dt):
            return dt
        return timezone.make_aware(dt)
    
    def _create_photo(self, photo_info):
        """Create a new Photo object from PhotoInfo"""
        photo = Photo(
            uuid=photo_info.uuid,
            original_filename=photo_info.original_filename or '',
            filename=photo_info.filename or '',
            path=photo_info.path or '',
            path_edited=photo_info.path_edited or '',
            
            # Photo type flags
            is_photo=photo_info.isphoto,
            is_movie=photo_info.ismovie,
            is_cloud_photo=photo_info.iscloudphoto,
            has_adjustments=photo_info.hasadjustments,
            is_missing=photo_info.ismissing,
            
            # Dates
            date=self._make_aware(photo_info.date),
            date_modified=self._make_aware(photo_info.date_modified),
            date_added=self._make_aware(photo_info.date_added),
            exif_datetime=self._make_aware(photo_info.exif_datetime),
            
            # Metadata
            title=photo_info.title or '',
            description=photo_info.description or '',
            
            # Location
            latitude=photo_info.latitude,
            longitude=photo_info.longitude,
            
            # Camera & Technical
            uti=photo_info.uti or '',
            live_photo=photo_info.live_photo,
            is_burst=photo_info.isburst,
            is_hdr=getattr(photo_info, 'ishdr', False),
            is_portrait=photo_info.isportrait,
            is_screenshot=photo_info.isscreenshot,
            is_slow_mo=photo_info.isslow_mo,
            is_selfie=photo_info.isselfie,
            is_panorama=photo_info.ispanorama,
            has_raw=photo_info.has_raw,
            
            # Image properties
            orientation=photo_info.orientation,
            height=photo_info.height,
            width=photo_info.width,
            duration=photo_info.duration,
            
            # EXIF
            camera_make=photo_info.camera_make or '',
            camera_model=photo_info.camera_model or '',
            fstop=photo_info.fstop,
            aperture=photo_info.aperture,
            iso=photo_info.iso,
            focal_length=photo_info.focal_length,
            exposure_time=photo_info.exposure_time,
            
            # Timezone
            timezone_name=photo_info.timezone_name or '',
            timezone_offset=photo_info.timezone_offset,
            
            # Apple Photos categorization
            favorite=photo_info.favorite,
            hidden=photo_info.hidden,
            in_trash=photo_info.in_trash,
            shared=photo_info.shared,
            
            # File size
            original_file_size=photo_info.original_file_size,
        )
        
        # Handle optional fields that might not exist
        if hasattr(photo_info, 'live_photo_video_uuid'):
            photo.live_photo_video_uuid = photo_info.live_photo_video_uuid or ''
        if hasattr(photo_info, 'live_photo_video_path'):
            photo.live_photo_video_path = photo_info.live_photo_video_path or ''
        if hasattr(photo_info, 'burst_uuid'):
            photo.burst_uuid = photo_info.burst_uuid or ''
        if hasattr(photo_info, 'raw_path'):
            photo.raw_path = photo_info.raw_path or ''
        
        # Handle place information
        if photo_info.place:
            photo.place_name = photo_info.place.name or ''
            photo.place_country_code = photo_info.place.country_code or ''
            photo.place_address = photo_info.place.address_str or ''
            photo.place_is_home = photo_info.place.ishome
        
        photo.save()
        return photo
    
    def _update_photo(self, photo, photo_info):
        """Update an existing Photo object"""
        # Update all fields
        photo.original_filename = photo_info.original_filename or ''
        photo.filename = photo_info.filename or ''
        photo.path = photo_info.path or ''
        photo.path_edited = photo_info.path_edited or ''
        
        # Update flags
        photo.is_photo = photo_info.isphoto
        photo.is_movie = photo_info.ismovie
        photo.is_cloud_photo = photo_info.iscloudphoto
        photo.has_adjustments = photo_info.hasadjustments
        photo.is_missing = photo_info.ismissing
        
        # Update dates
        photo.date = self._make_aware(photo_info.date)
        photo.date_modified = self._make_aware(photo_info.date_modified)
        photo.date_added = self._make_aware(photo_info.date_added)
        photo.exif_datetime = self._make_aware(photo_info.exif_datetime)
        
        # Update metadata
        photo.title = photo_info.title or ''
        photo.description = photo_info.description or ''
        
        # Update other fields...
        # (Similar to _create_photo but updating existing object)
        
        photo.save()
    
    def _update_relationships(self, photo, photo_info):
        """Update many-to-many relationships"""
        
        # Update albums
        if photo_info.albums:
            photo.albums.clear()
            for album_name in photo_info.albums:
                album, _ = Album.objects.get_or_create(
                    name=album_name,
                    is_shared=False
                )
                album.photos.add(photo)
        
        # Update shared albums
        if hasattr(photo_info, 'albums_shared') and photo_info.albums_shared:
            for album_name in photo_info.albums_shared:
                album, _ = Album.objects.get_or_create(
                    name=album_name,
                    is_shared=True
                )
                album.photos.add(photo)
        
        # Update persons
        if photo_info.persons:
            photo.persons.clear()
            for person_name in photo_info.persons:
                person, _ = Person.objects.get_or_create(name=person_name)
                person.photos.add(photo)
        
        # Update keywords
        if photo_info.keywords:
            photo.keywords.clear()
            for keyword_name in photo_info.keywords:
                keyword, _ = Keyword.objects.get_or_create(name=keyword_name)
                keyword.photos.add(photo)
        
        # Update labels
        if hasattr(photo_info, 'labels') and photo_info.labels:
            photo.labels.clear()
            for label_name in photo_info.labels:
                label, _ = Label.objects.get_or_create(name=label_name)
                label.photos.add(photo)
        
        # Update scores
        if hasattr(photo_info, 'score') and photo_info.score:
            self._update_scores(photo, photo_info.score)
        
        # Update faces
        if hasattr(photo_info, 'faces') and photo_info.faces:
            self._update_faces(photo, photo_info.faces)
    
    def _update_scores(self, photo, score_info):
        """Update or create PhotoScore"""
        score_data = {
            'overall': getattr(score_info, 'overall', None),
            'aesthetics': getattr(score_info, 'aesthetics', None),
            'curation': getattr(score_info, 'curation', None),
            'noise': getattr(score_info, 'noise', None),
            'pleasant_camera_tilt': getattr(score_info, 'pleasant_camera_tilt', None),
            'pleasant_composition': getattr(score_info, 'pleasant_composition', None),
            'pleasant_lighting': getattr(score_info, 'pleasant_lighting', None),
            'pleasant_pattern': getattr(score_info, 'pleasant_pattern', None),
            'pleasant_subject_movement': getattr(score_info, 'pleasant_subject_movement', None),
            'pleasant_symmetry': getattr(score_info, 'pleasant_symmetry', None),
            'pleasant_texture': getattr(score_info, 'pleasant_texture', None),
            'pleasant_tone': getattr(score_info, 'pleasant_tone', None),
            'utility_activity': getattr(score_info, 'utility_activity', None),
            'utility_blurry': getattr(score_info, 'utility_blurry', None),
            'utility_colorful': getattr(score_info, 'utility_colorful', None),
            'utility_interesting_subject': getattr(score_info, 'utility_interesting_subject', None),
            'utility_low_light': getattr(score_info, 'utility_low_light', None),
            'utility_not_on_tripod': getattr(score_info, 'utility_not_on_tripod', None),
            'utility_people': getattr(score_info, 'utility_people', None),
            'utility_pet': getattr(score_info, 'utility_pet', None),
            'utility_poor_contrast': getattr(score_info, 'utility_poor_contrast', None),
            'utility_quality': getattr(score_info, 'utility_quality', None),
            'utility_sharply_focused': getattr(score_info, 'utility_sharply_focused', None),
            'utility_still_action': getattr(score_info, 'utility_still_action', None),
            'utility_uninteresting_subject': getattr(score_info, 'utility_uninteresting_subject', None),
            'utility_vibrance': getattr(score_info, 'utility_vibrance', None),
            'curation_blurry': getattr(score_info, 'curation_blurry', None),
            'curation_noise': getattr(score_info, 'curation_noise', None),
            'curation_interesting_subject': getattr(score_info, 'curation_interesting_subject', None),
            'curation_scene': getattr(score_info, 'curation_scene', None),
            'curation_light': getattr(score_info, 'curation_light', None),
            'curation_activity': getattr(score_info, 'curation_activity', None),
            'curation_animated': getattr(score_info, 'curation_animated', None),
            'curation_face': getattr(score_info, 'curation_face', None),
            'curation_landscape': getattr(score_info, 'curation_landscape', None),
            'curation_time': getattr(score_info, 'curation_time', None),
            'curation_version': getattr(score_info, 'curation_version', None),
        }
        
        PhotoScore.objects.update_or_create(
            photo=photo,
            defaults=score_data
        )
    
    def _update_faces(self, photo, faces_info):
        """Update face information"""
        # Clear existing faces
        photo.faces.all().delete()
        
        for face_info in faces_info:
            face_data = {
                'center_x': face_info.center_x,
                'center_y': face_info.center_y,
                'width': face_info.width,
                'height': face_info.height,
                'age': getattr(face_info, 'age', None),
                'gender': getattr(face_info, 'gender', '') or '',
                'ethnicity': getattr(face_info, 'ethnicity', '') or '',
                'quality': getattr(face_info, 'quality', None),
                'is_hidden': getattr(face_info, 'is_hidden', False),
            }
            
            face = Face(photo=photo, **face_data)
            
            # Link to person if identified
            if hasattr(face_info, 'person_info') and face_info.person_info and face_info.person_info.name:
                person, _ = Person.objects.get_or_create(
                    name=face_info.person_info.name,
                    defaults={'uuid': getattr(face_info.person_info, 'uuid', None)}
                )
                face.person = person
            
            face.save()