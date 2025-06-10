from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from PIL import Image
import os
from .models import Photo, Album, Person, Keyword, Label


class PhotoListView(ListView):
    model = Photo
    template_name = 'photos/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Photo.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(filename__icontains=search_query) |
                Q(keywords__name__icontains=search_query) |
                Q(labels__name__icontains=search_query) |
                Q(persons__name__icontains=search_query) |
                Q(albums__name__icontains=search_query)
            ).distinct()
        
        # Filter by various criteria
        filters = {}
        
        # Photo type filters
        if self.request.GET.get('favorites'):
            queryset = queryset.filter(favorite=True)
        
        if self.request.GET.get('videos'):
            queryset = queryset.filter(is_movie=True)
        elif self.request.GET.get('photos'):
            queryset = queryset.filter(is_photo=True)
        
        if self.request.GET.get('screenshots'):
            queryset = queryset.filter(is_screenshot=True)
        
        if self.request.GET.get('selfies'):
            queryset = queryset.filter(is_selfie=True)
        
        if self.request.GET.get('portraits'):
            queryset = queryset.filter(is_portrait=True)
        
        if self.request.GET.get('panoramas'):
            queryset = queryset.filter(is_panorama=True)
        
        if self.request.GET.get('live_photos'):
            queryset = queryset.filter(live_photo=True)
        
        if self.request.GET.get('bursts'):
            queryset = queryset.filter(is_burst=True)
        
        if self.request.GET.get('hdr'):
            queryset = queryset.filter(is_hdr=True)
        
        # Filter by album
        album_id = self.request.GET.get('album')
        if album_id:
            queryset = queryset.filter(albums__id=album_id)
        
        # Filter by person
        person_id = self.request.GET.get('person')
        if person_id:
            queryset = queryset.filter(persons__id=person_id)
        
        # Filter by keyword
        keyword_id = self.request.GET.get('keyword')
        if keyword_id:
            queryset = queryset.filter(keywords__id=keyword_id)
        
        # Filter by label
        label_id = self.request.GET.get('label')
        if label_id:
            queryset = queryset.filter(labels__id=label_id)
        
        # Filter by camera
        camera_make = self.request.GET.get('camera_make')
        if camera_make:
            queryset = queryset.filter(camera_make=camera_make)
        
        camera_model = self.request.GET.get('camera_model')
        if camera_model:
            queryset = queryset.filter(camera_model=camera_model)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Filter by location
        has_location = self.request.GET.get('has_location')
        if has_location:
            queryset = queryset.exclude(latitude__isnull=True, longitude__isnull=True)
        
        # Sort options
        sort = self.request.GET.get('sort', '-date')
        valid_sorts = ['date', '-date', 'title', '-title', 'filename', '-filename', 
                      '-score__overall', 'created_at', '-created_at']
        if sort in valid_sorts:
            if 'score__' in sort:
                queryset = queryset.select_related('score')
            queryset = queryset.order_by(sort)
        
        return queryset.prefetch_related('albums', 'persons', 'keywords', 'labels')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['albums'] = Album.objects.annotate(photo_count=Count('photos')).order_by('name')
        context['persons'] = Person.objects.annotate(photo_count=Count('photos')).order_by('name')
        context['keywords'] = Keyword.objects.annotate(photo_count=Count('photos')).order_by('name')
        context['labels'] = Label.objects.annotate(photo_count=Count('photos')).order_by('name')
        
        # Get unique camera makes and models
        context['camera_makes'] = Photo.objects.exclude(
            camera_make=''
        ).values_list('camera_make', flat=True).distinct().order_by('camera_make')
        
        context['camera_models'] = Photo.objects.exclude(
            camera_model=''
        ).values_list('camera_model', flat=True).distinct().order_by('camera_model')
        
        # Pass current filters
        context['current_filters'] = self.request.GET.dict()
        
        return context


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'photos/photo_detail.html'
    context_object_name = 'photo'
    
    def get_object(self):
        return get_object_or_404(
            Photo.objects.prefetch_related(
                'albums', 'persons', 'keywords', 'labels', 'faces__person'
            ).select_related('score'),
            pk=self.kwargs['pk']
        )


@require_http_methods(["GET"])
def photo_thumbnail(request, pk):
    """Serve photo thumbnail"""
    photo = get_object_or_404(Photo, pk=pk)
    
    # Check if photo file exists
    if not photo.path or not os.path.exists(photo.path):
        return HttpResponse("Photo not found", status=404)
    
    # Generate thumbnail
    size = int(request.GET.get('size', 300))
    
    try:
        img = Image.open(photo.path)
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Save to response
        response = HttpResponse(content_type='image/jpeg')
        img.save(response, 'JPEG', quality=85)
        return response
    except Exception as e:
        return HttpResponse(f"Error generating thumbnail: {str(e)}", status=500)


@require_http_methods(["GET"])
def photo_full(request, pk):
    """Serve full photo"""
    photo = get_object_or_404(Photo, pk=pk)
    
    # Use edited version if available and requested
    use_edited = request.GET.get('edited', False)
    photo_path = photo.path_edited if use_edited and photo.path_edited else photo.path
    
    if not photo_path or not os.path.exists(photo_path):
        return HttpResponse("Photo not found", status=404)
    
    try:
        with open(photo_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/jpeg')
            response['Content-Disposition'] = f'inline; filename="{photo.filename}"'
            return response
    except Exception as e:
        return HttpResponse(f"Error serving photo: {str(e)}", status=500)


def stats_view(request):
    """Display library statistics"""
    stats = {
        'total_photos': Photo.objects.filter(is_photo=True).count(),
        'total_videos': Photo.objects.filter(is_movie=True).count(),
        'total_favorites': Photo.objects.filter(favorite=True).count(),
        'total_persons': Person.objects.count(),
        'total_albums': Album.objects.count(),
        'total_keywords': Keyword.objects.count(),
        'total_labels': Label.objects.count(),
        'photos_with_location': Photo.objects.exclude(
            latitude__isnull=True, longitude__isnull=True
        ).count(),
        'photos_with_faces': Photo.objects.filter(faces__isnull=False).distinct().count(),
        'top_cameras': Photo.objects.exclude(
            camera_model=''
        ).values('camera_make', 'camera_model').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        'top_persons': Person.objects.annotate(
            photo_count=Count('photos')
        ).order_by('-photo_count')[:10],
        'top_keywords': Keyword.objects.annotate(
            photo_count=Count('photos')
        ).order_by('-photo_count')[:10],
    }
    
    return render(request, 'photos/stats.html', {'stats': stats})


def search_autocomplete(request):
    """Provide autocomplete suggestions for search"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Search in keywords
    keywords = Keyword.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:5]
    suggestions.extend([{'type': 'keyword', 'value': k} for k in keywords])
    
    # Search in persons
    persons = Person.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:5]
    suggestions.extend([{'type': 'person', 'value': p} for p in persons])
    
    # Search in albums
    albums = Album.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:5]
    suggestions.extend([{'type': 'album', 'value': a} for a in albums])
    
    # Search in labels
    labels = Label.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:5]
    suggestions.extend([{'type': 'label', 'value': l} for l in labels])
    
    return JsonResponse({'suggestions': suggestions})