from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib import messages as django_messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import BirthdayPerson, BirthdayPhoto
from .forms import BirthdayPersonForm, PhotoUploadForm, AuthForm
import datetime

# ──────────────────────────────────────────────
# Home
# ──────────────────────────────────────────────
def home(request):
    if request.method == 'POST':
        dob_str = request.POST.get('dob', '').strip()
        try:
            datetime.datetime.strptime(dob_str, '%Y-%m-%d')
            return redirect('birthday_page', dob=dob_str)
        except ValueError:
            django_messages.error(request, 'Please enter a valid date.')
    return render(request, 'birthdays/home.html')


# ──────────────────────────────────────────────
# Birthday page (public)
# ──────────────────────────────────────────────
def birthday_page(request, dob):
    try:
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
    except ValueError:
        raise Http404

    try:
        person = BirthdayPerson.objects.get(dob=dob_date)
    except BirthdayPerson.DoesNotExist:
        return render(request, 'birthdays/not_found.html', {'dob': dob})

    if request.method == 'POST' and 'theme_color' in request.POST:
        color = request.POST.get('theme_color', '').strip()
        if color.startswith('#') and len(color) in [4, 7]:
            request.session[f'theme_{dob}'] = color
            return JsonResponse({'ok': True, 'color': color})

    theme_color = request.session.get(f'theme_{dob}', person.theme_color)
    photos = person.photos.all()
    today = datetime.date.today()
    is_birthday_today = (today.month == person.dob.month and today.day == person.dob.day)

    return render(request, 'birthdays/birthday.html', {
        'person': person,
        'photos': photos,
        'theme_color': theme_color,
        'is_birthday_today': is_birthday_today,
        'dob': dob,
    })


# ──────────────────────────────────────────────
# Create page — admin only (redirects to admin portal)
# ──────────────────────────────────────────────
def create_page(request):
    if not request.session.get('admin_master_auth'):
        return redirect('admin_portal')

    if request.method == 'POST':
        form = BirthdayPersonForm(request.POST, request.FILES)
        if form.is_valid():
            person = form.save()
            dob_str = person.dob.strftime('%Y-%m-%d')
            django_messages.success(request, f'🎉 Birthday page for {person.name} created!')
            return redirect('admin_portal')
    else:
        form = BirthdayPersonForm()
    return render(request, 'birthdays/create.html', {'form': form})


# ──────────────────────────────────────────────
# Per-page manage (password = each page's own admin_password)
# ──────────────────────────────────────────────
def manage_page(request, dob):
    try:
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
    except ValueError:
        raise Http404

    auth_key = f'manage_auth_{dob}'

    # Admin master auth counts as authenticated for any page
    if not request.session.get(auth_key) and not request.session.get('admin_master_auth'):
        form = AuthForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            password = form.cleaned_data['password']
            try:
                person = BirthdayPerson.objects.get(dob=dob_date)
                if person.admin_password == password:
                    request.session[auth_key] = True
                    return redirect('manage_page', dob=dob)
                else:
                    django_messages.error(request, '❌ Wrong password. Try again!')
            except BirthdayPerson.DoesNotExist:
                django_messages.error(request, 'No birthday page found for this date.')
        return render(request, 'birthdays/auth.html', {'form': form, 'dob': dob})

    try:
        person = BirthdayPerson.objects.get(dob=dob_date)
    except BirthdayPerson.DoesNotExist:
        return render(request, 'birthdays/not_found.html', {'dob': dob})

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload_photo':
            form = PhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                photo = form.save(commit=False)
                photo.person = person
                photo.save()
                django_messages.success(request, '📸 Photo uploaded!')
            else:
                django_messages.error(request, 'Upload failed. Make sure it\'s an image file.')
            return redirect('manage_page', dob=dob)

        elif action == 'delete_photo':
            photo_id = request.POST.get('photo_id')
            try:
                photo = BirthdayPhoto.objects.get(id=photo_id, person=person)
                photo.image.delete(save=False)
                photo.delete()
                django_messages.success(request, '🗑️ Photo deleted.')
            except BirthdayPhoto.DoesNotExist:
                django_messages.error(request, 'Photo not found.')
            return redirect('manage_page', dob=dob)

        elif action == 'update_settings':
            person.message = request.POST.get('message', person.message)
            color = request.POST.get('theme_color', person.theme_color).strip()
            if color.startswith('#'):
                person.theme_color = color
            person.song_url  = request.POST.get('song_url',  person.song_url).strip()
            person.song_name = request.POST.get('song_name', person.song_name).strip()
            if 'song_file' in request.FILES:
                if person.song_file:
                    person.song_file.delete(save=False)
                person.song_file = request.FILES['song_file']
            if request.POST.get('remove_song_file'):
                person.song_file.delete(save=False)
                person.song_file = None
            person.save()
            if f'theme_{dob}' in request.session:
                del request.session[f'theme_{dob}']
            django_messages.success(request, '✅ Settings saved!')
            return redirect('manage_page', dob=dob)

        elif action == 'logout':
            if auth_key in request.session:
                del request.session[auth_key]
            return redirect('birthday_page', dob=dob)

    photos = person.photos.all()
    upload_form = PhotoUploadForm()
    return render(request, 'birthdays/manage.html', {
        'person': person,
        'photos': photos,
        'upload_form': upload_form,
        'dob': dob,
    })


# ──────────────────────────────────────────────
# Admin Portal — master dashboard (you only)
# ──────────────────────────────────────────────
def admin_portal(request):
    # Handle logout
    if request.method == 'POST' and request.POST.get('action') == 'logout':
        if 'admin_master_auth' in request.session:
            del request.session['admin_master_auth']
        return redirect('home')

    # Login gate
    if not request.session.get('admin_master_auth'):
        error = None
        if request.method == 'POST':
            password = request.POST.get('password', '').strip()
            if password == settings.ADMIN_MASTER_PASSWORD:
                request.session['admin_master_auth'] = True
                return redirect('admin_portal')
            else:
                error = 'Wrong password. Try again!'
        return render(request, 'birthdays/admin_login.html', {'error': error})

    # Authenticated — handle actions
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_page':
            dob_str = request.POST.get('dob', '').strip()
            try:
                dob_date = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
                person = BirthdayPerson.objects.get(dob=dob_date)
                person_name = person.name
                # Delete all photos from Cloudinary / disk
                for photo in person.photos.all():
                    try:
                        photo.image.delete(save=False)
                    except Exception:
                        pass
                    photo.delete()
                # Delete song file
                if person.song_file:
                    try:
                        person.song_file.delete(save=False)
                    except Exception:
                        pass
                person.delete()
                django_messages.success(request, f'🗑️ {person_name}\'s page deleted successfully.')
            except (ValueError, BirthdayPerson.DoesNotExist):
                django_messages.error(request, 'Page not found.')
            return redirect('admin_portal')

    # Collect stats
    all_pages = BirthdayPerson.objects.prefetch_related('photos').order_by('name')
    total_photos = BirthdayPhoto.objects.count()
    today = datetime.date.today()

    pages_data = []
    for p in all_pages:
        is_today = (today.month == p.dob.month and today.day == p.dob.day)
        pages_data.append({
            'person': p,
            'photo_count': p.photos.count(),
            'is_birthday_today': is_today,
            'dob_str': p.dob.strftime('%Y-%m-%d'),
        })

    return render(request, 'birthdays/admin_panel.html', {
        'pages_data': pages_data,
        'total_pages': all_pages.count(),
        'total_photos': total_photos,
        'today': today,
    })
