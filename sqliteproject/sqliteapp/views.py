import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.db.models import Q
from django.contrib import messages
from .forms import TourRouteForm, SearchForm
from .models import TourRoute
from xml.etree.ElementTree import Element, SubElement, tostring, parse, ParseError, ElementTree
import xml.etree.ElementTree as ET

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT)
ROUTES_XML = os.path.join(UPLOAD_DIR, 'routes.xml')

def index(request):
    return redirect('add_route')

def add_route(request):
    message = ''
    message_type = 'info'
    
    if request.method == 'POST':
        form = TourRouteForm(request.POST)
        if form.is_valid():
            save_location = form.cleaned_data.get('save_location')
            route = form.save(commit=False)
            
            if save_location == 'db':
                duplicate = TourRoute.objects.filter(
                    name=route.name,
                    length_km=route.length_km,
                    difficulty=route.difficulty
                ).exists()
                
                if duplicate:
                    message = "такой маршрут уже существует в базе данных!"
                    message_type = 'warning'
                else:
                    route.save()
                    message = "маршрут успешно добавлен в базу данных"
                    message_type = 'success'
                    form = TourRouteForm()
            else:
                # сохранение в XML файл
                new_data = {
                    'name': route.name,
                    'description': route.description,
                    'length_km': route.length_km,
                    'difficulty': route.difficulty,
                    'members_count': route.members_count
                }
                
                if os.path.exists(ROUTES_XML):
                    tree = ElementTree()
                    tree.parse(ROUTES_XML)
                    root = tree.getroot()
                else:
                    root = Element('TourRoutes')
                
                route_elem = SubElement(root, 'TourRoute')
                for key, val in new_data.items():
                    child = SubElement(route_elem, key)
                    child.text = str(val)
                
                tree = ElementTree(root)
                tree.write(ROUTES_XML, encoding='utf-8', xml_declaration=True)
                
                message = "маршрут успешно добавлен в XML файл"
                message_type = 'success'
                form = TourRouteForm()
        else:
            message = "форма невалидна: " + str(form.errors)
            message_type = 'danger'
    else:
        form = TourRouteForm()
    
    return render(request, 'tour_routes/add_route.html', {
        'form': form,
        'message': message,
        'message_type': message_type
    })

def upload_file(request):
    message = ''
    message_type = 'info'
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if ext not in ['.xml']:
            message = "недопустимый формат файла"
            message_type = 'danger'
        else:
            new_filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(UPLOAD_DIR, new_filename)
            
            with default_storage.open(filepath, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            is_valid = False
            if ext == '.xml':
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    is_valid = True
                except (ParseError, Exception):
                    is_valid = False
            
            if not is_valid:
                os.remove(filepath)
                message = "файл с данными невалиден и удалён"
                message_type = 'danger'
            else:
                message = f"файл {new_filename} успешно загружен"
                message_type = 'success'
    
    return render(request, 'tour_routes/upload_file.html', {
        'message': message,
        'message_type': message_type
    })

def list_files(request):
    xml_files = []
    message = ''
    
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    for fname in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, fname)
        if fname.endswith('.xml'):
            xml_files.append(fname)
    
    if not xml_files:
        message = "файлы отсутствуют"
    
    files_data = []
    for fname in xml_files:
        try:
            tree = parse(os.path.join(UPLOAD_DIR, fname))
            root = tree.getroot()
            content = parse_xml_element(root)
            files_data.append({'filename': fname, 'content': content, 'format': 'XML'})
        except Exception:
            continue
    
    return render(request, 'tour_routes/list_files.html', {
        'files_data': files_data,
        'message': message
    })

def list_database(request):
    search_form = SearchForm()
    routes = TourRoute.objects.all()
    
    return render(request, 'tour_routes/list_database.html', {
        'routes': routes,
        'search_form': search_form
    })

def search_routes(request):
    query = request.GET.get('query', '')
    
    if query:
        routes = TourRoute.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(difficulty__icontains=query)
        )
    else:
        routes = TourRoute.objects.all()
    
    results = []
    for route in routes:
        results.append({
            'id': route.id,
            'name': route.name,
            'description': route.description,
            'length_km': route.length_km,
            'difficulty': route.difficulty,
            'members_count': route.members_count,
        })
    
    return JsonResponse({'results': results})

def parse_xml_element(element):
    if len(element) > 0:
        result = {}
        for child in element:
            child_data = parse_xml_element(child)
            
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        if 'TourRoute' in result and not isinstance(result['TourRoute'], list):
            result['TourRoute'] = [result['TourRoute']]
        
        return result
    else:
        return element.text if element.text and element.text.strip() else None

def download_file(request, filename):
    safe_filename = filename
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("Файл не найден")