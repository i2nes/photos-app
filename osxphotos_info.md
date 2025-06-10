`osxphotos` provides a rich set of properties and methods to extract detailed information about your photos and videos from the macOS Photos app. The primary object you'll interact with is the `PhotoInfo` object, which represents a single photo or video in your library.

Here's a comprehensive list of properties you can typically extract from a `PhotoInfo` object, along with other related information you can get from the `PhotosDB` object:

**From a `PhotoInfo` object (representing a single photo/video):**

**Basic Information:**

* **`uuid`**: The universally unique identifier (UUID) for the photo/video. This is the primary key Photos uses to identify the asset.
* **`original_filename`**: The original filename of the photo.
* **`filename`**: The current filename of the photo (can be different from original if edited or exported).
* **`path`**: The path to the original photo file in the Photos library.
* **`path_edited`**: The path to the edited photo file (if edited) in the Photos library.
* **`isphoto`**: Boolean, `True` if it's an image.
* **`ismovie`**: Boolean, `True` if it's a video.
* **`iscloudphoto`**: Boolean, `True` if the photo is in iCloud Photos.
* **`hasadjustments`**: Boolean, `True` if the photo has been edited.
* **`ismissing`**: Boolean, `True` if the photo is optimized for storage and not currently on disk.

**Dates & Times:**

* **`date`**: The creation date and time of the photo (as a `datetime` object, often localized).
* **`date_modified`**: The last modification date and time of the photo.
* **`date_added`**: The date and time the photo was added to the library.
* **`start_date`**: For videos, the start time.
* **`end_date`**: For videos, the end time.
* **`added_date`**: The date the photo was added to the library.
* **`exif_datetime`**: The datetime from EXIF data.

**Metadata & Descriptions:**

* **`title`**: The title/name of the photo.
* **`description`**: The description/caption of the photo.
* **`keywords`**: A list of keywords (tags) associated with the photo.
* **`albums`**: A list of album names the photo belongs to.
* **`albums_shared`**: A list of shared album names the photo belongs to.
* **`persons`**: A list of names of persons identified in the photo.
* **`labels`**: A list of machine-learning labels (e.g., "tree", "dog", "food") detected by Photos (Photos 5+).
* **`uti`**: Uniform Type Identifier (e.g., 'public.jpeg', 'com.apple.live-photo.image').
* **`burst_uuid`**: The UUID of the burst if it's part of a photo burst.
* **`burst_photos`**: A list of `PhotoInfo` objects for other photos in the same burst.

**Location Information:**

* **`location`**: A tuple `(latitude, longitude)` if location data is present.
* **`latitude`**: The latitude.
* **`longitude`**: The longitude.
* **`place`**: A `PlaceInfo` object containing reverse geocoded location data (e.g., country, city, street).
    * **`place.name`**
    * **`place.names`** (list of all names, including country, city, etc.)
    * **`place.country_code`**
    * **`place.address_str`** (formatted address string)
    * **`place.address`** (dictionary of address components)
    * **`place.ishome`** (boolean, if location is marked as Home)

**Camera & Technical Data:**

* **`uti`**: Uniform Type Identifier.
* **`live_photo`**: Boolean, `True` if it's a Live Photo.
* **`live_photo_video_uuid`**: UUID of the associated video for Live Photos.
* **`live_photo_video_path`**: Path to the associated video file for Live Photos.
* **`isburst`**: Boolean, `True` if the photo is part of a burst.
* **`is hdr`**: Boolean, `True` if it's an HDR photo.
* **`isportrait`**: Boolean, `True` if it's a Portrait mode photo.
* **`isscreenshot`**: Boolean, `True` if it's a screenshot.
* **`isslow_mo`**: Boolean, `True` if it's a slow-motion video.
* **`is`selfie**: Boolean, `True` if it's a selfie.
* **`ispanorama`**: Boolean, `True` if it's a panorama.
* **`has_raw`**: Boolean, `True` if there's an associated RAW file.
* **`raw_original`**: `PhotoInfo` object for the RAW original (if it has one).
* **`raw_path`**: Path to the RAW file.
* **`orientation`**: Image orientation (e.g., 1, 3, 6, 8 for normal, 180-deg, 90-deg CW, 90-deg CCW).
* **`height`**: Image height in pixels.
* **`width`**: Image width in pixels.
* **`duration`**: Video duration in seconds.
* **`camera_make`**: Camera manufacturer (from EXIF).
* **`camera_model`**: Camera model (from EXIF).
* **`fstop`**: F-number (from EXIF).
* **`aperture`**: Aperture value (from EXIF).
* **`iso`**: ISO speed (from EXIF).
* **`focal_length`**: Focal length (from EXIF).
* **`exposure_time`**: Exposure time (from EXIF).
* **`timezone`**: Timezone information.
* **`timezone_offset`**: Timezone offset from UTC in seconds.
* **`timezone_name`**: Timezone name (e.g., "Europe/Lisbon").
* **`comments`**: A list of `CommentInfo` objects for shared photos.
* **`likes`**: A list of `LikeInfo` objects for shared photos.

**Apple Photos-Specific Categorization & Scores (Photos 5+):**

* **`favorite`**: Boolean, `True` if marked as a favorite.
* **`hidden`**: Boolean, `True` if hidden.
* **`in_trash`**: Boolean, `True` if in "Recently Deleted".
* **`shared`**: Boolean, `True` if in a shared iCloud album.
* **`score`**: A `ScoreInfo` object containing various machine-learning scores computed by Photos:
    * **`score.overall`**: Overall aesthetic score.
    * **`score.aesthetics`**: Aesthetic score.
    * **`score.curation`**: Curation score.
    * **`score.noise`**: Noise score.
    * **`score.pleasant_camera_tilt`**: Pleasant camera tilt score.
    * **`score.pleasant_composition`**: Pleasant composition score.
    * **`score.pleasant_lighting`**: Pleasant lighting score.
    * **`score.pleasant_pattern`**: Pleasant pattern score.
    * **`score.pleasant_subject_movement`**: Pleasant subject movement score.
    * **`score.pleasant_symmetry`**: Pleasant symmetry score.
    * **`score.pleasant_texture`**: Pleasant texture score.
    * **`score.pleasant_tone`**: Pleasant tone score.
    * **`score.utility_activity`**: Utility activity score.
    * **`score.utility_blurry`**: Utility blurry score.
    * **`score.utility_colorful`**: Utility colorful score.
    * **`score.utility_interesting_subject`**: Utility interesting subject score.
    * **`score.utility_low_light`**: Utility low light score.
    * **`score.utility_not_on_tripod`**: Utility not on tripod score.
    * **`score.utility_people`**: Utility people score.
    * **`score.utility_pet`**: Utility pet score.
    * **`score.utility_poor_contrast`**: Utility poor contrast score.
    * **`score.utility_quality`**: Utility quality score.
    * **`score.utility_sharply_focused`**: Utility sharply focused score.
    * **`score.utility_still_action`**: Utility still action score.
    * **`score.utility_uninteresting_subject`**: Utility uninteresting subject score.
    * **`score.utility_vibrance`**: Utility vibrance score.
    * **`score.curation_blurry`**
    * **`score.curation_noise`**
    * **`score.curation_interesting_subject`**
    * **`score.curation_scene`**
    * **`score.curation_light`**
    * **`score.curation_activity`**
    * **`score.curation_animated`**
    * **`score.curation_face`**
    * **`score.curation_landscape`**
    * **`score.curation_time`**
    * **`score.curation_version`**

**Faces and Regions:**

* **`faces`**: A list of `FaceInfo` objects for detected faces. Each `FaceInfo` object contains:
    * **`face.uuid`**: UUID of the face.
    * **`face.person_info.name`**: Name of the person (if identified).
    * **`face.person_info.uuid`**: UUID of the person.
    * **`face.center_x`**: X coordinate of the face center (normalized).
    * **`face.center_y`**: Y coordinate of the face center (normalized).
    * **`face.width`**: Width of the face bounding box (normalized).
    * **`face.height`**: Height of the face bounding box (normalized).
    * **`face.age`**: Estimated age.
    * **`face.gender`**: Estimated gender.
    * **`face.ethnicity`**: Estimated ethnicity.
    * **`face.quality`**: Quality score of the face detection.
    * **`face.is_hidden`**: Boolean, `True` if face is hidden.

**Other Properties:**

* **`adjustments`**: A list of `AdjustmentsInfo` objects if the photo has edits.
* **`asdict()`**: Returns a dictionary of all properties.
* **`original_file_size`**: Size of the original file in bytes.
* **`has_raw`**: True if a RAW file is associated.
* **`has_extended_exif`**: True if extended EXIF information is available.

**From the `PhotosDB` object (representing the entire Photos library):**

* **`photos()`**: Returns a list of all `PhotoInfo` objects in the library. This method also supports various filters for querying specific photos (e.g., by keyword, person, album, date range, etc.).
* **`keywords`**: A list of all unique keywords in the library.
* **`persons`**: A list of all unique person names in the library.
* **`albums`**: A list of all unique album names in the library.
* **`album_names`**: Same as `albums`.
* **`keywords_as_dict`**: A dictionary where keys are keywords and values are lists of UUIDs of photos associated with that keyword.
* **`persons_as_dict`**: A dictionary where keys are person names and values are lists of UUIDs of photos associated with that person.
* **`albums_as_dict`**: A dictionary where keys are album names and values are lists of UUIDs of photos in that album.
* **`folders`**: A list of `FolderInfo` objects, allowing you to traverse the folder hierarchy in Photos.
* **`import_sessions`**: A list of `ImportInfo` objects, representing import sessions (e.g., when photos were imported from a camera).
* **`moments`**: A list of `MomentInfo` objects (groupings of photos by time and location, as seen in Photos).
* **`exiftool`**: An `ExifTool` object for interacting with ExifTool (if installed) for more advanced EXIF data extraction or writing.
* **`filepaths`**: A list of all file paths for original photos in the library.
* **`edited_filepaths`**: A list of all file paths for edited photos in the library.
* **`count`**: The total number of photos in the library.
* **`db_path`**: The path to the Photos library database file.
* **`library_path`**: The path to the Photos library bundle.

This extensive set of properties makes `osxphotos` incredibly powerful for querying, organizing, and analyzing your Photos library programmatically.