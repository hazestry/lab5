import os
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.db.models import Q
from .forms import TourRouteForm
from .models import TourRoute
from xml.etree.ElementTree import Element, SubElement, tostring, parse, ParseError, ElementTree
from django.views.decorators.http import require_http_methods

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT)
ROUTES_XML = os.path.join(UPLOAD_DIR, 'routes.xml')

def index(request):
    return redirect('add_route')

def add_route(request):
    message = ''
    message_type = ''
    save_to = request.POST.get('save_to', 'file')  # По умолчанию в файл
    
    if request.method == 'POST':
        form = TourRouteForm(request.POST)
        if form.is_valid():
            route_data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'length_km': form.cleaned_data['length_km'],
                'difficulty': form.cleaned_data['difficulty']
            }
            
            if save_to == 'database':
                # Проверка на дубликаты в БД
                existing = TourRoute.objects.filter(
                    name=route_data['name'],
                    description=route_data['description'],
                    length_km=route_data['length_km'],
                    difficulty=route_data['difficulty']
                ).exists()
                
                if existing:
                    message = "⚠️ Такой маршрут уже существует в базе данных!"
                    message_type = 'warning'
                else:
                    form.save()
                    message = "✓ Маршрут успешно добавлен в базу данных"
                    message_type = 'success'
                    form = TourRouteForm()
            else:
                # Сохранение в XML файл
                if os.path.exists(ROUTES_XML):
                    tree = ElementTree()
                    tree.parse(ROUTES_XML)
                    root = tree.getroot()
                else:
                    root = Element('TourRoutes')
                
                route_elem = SubElement(root, 'TourRoute')
                for key, val in route_data.items():
                    child = SubElement(route_elem, key)
                    child.text = str(val)
                
                tree = ElementTree(root)
                tree.write(ROUTES_XML, encoding='utf-8', xml_declaration=True)
                
                message = "✓ Маршрут успешно добавлен в XML файл"
                message_type = 'success'
                form = TourRouteForm()
        else:
            message = "❌ Форма содержит ошибки: " + str(form.errors)
            message_type = 'error'
    else:
        form = TourRouteForm()
    
    return render(request, 'tour_routes/add_route.html', {
        'form': form, 
        'message': message,
        'message_type': message_type,
        'save_to': save_to
    })

def upload_file(request):
    message = ''
    message_type = ''
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if ext not in ['.xml']:
            message = "❌ Недопустимый формат файла. Принимаются только XML файлы."
            message_type = 'error'
        else:
            new_filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(UPLOAD_DIR, new_filename)
            
            with default_storage.open(filepath, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            is_valid = False
            if ext == '.xml':
                try:
                    tree = parse(filepath)
                    root = tree.getroot()
                    tags = [child.tag for child in root]
                    if all(tag in tags for tag in ['name', 'description', 'length_km', 'difficulty']):
                        is_valid = True
                except (ParseError, Exception):
                    is_valid = False
            
            if not is_valid:
                os.remove(filepath)
                message = "❌ Файл не прошел валидацию и был удален."
                message_type = 'error'
            else:
                message = f"✓ Файл {new_filename} успешно загружен."
                message_type = 'success'
    
    return render(request, 'tour_routes/upload_file.html', {
        'message': message,
        'message_type': message_type
    })

def list_files(request):
    source = request.GET.get('source', 'files')
    xml_files = []
    message = ''
    
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    files_data = []
    db_routes = []
    
    if source == 'files':
        for fname in os.listdir(UPLOAD_DIR):
            if fname.endswith('.xml'):
                xml_files.append(fname)
        
        if not xml_files:
            message = "📂 Файлы отсутствуют."
        
        for fname in xml_files:
            try:
                tree = parse(os.path.join(UPLOAD_DIR, fname))
                root = tree.getroot()
                content = parse_xml_element(root)
                files_data.append({'filename': fname, 'content': content, 'format': 'XML'})
            except Exception:
                continue
    else:
        db_routes = TourRoute.objects.all().order_by('-id')
        if not db_routes:
            message = "🗄️ База данных пуста."
    
    return render(request, 'tour_routes/list_files.html', {
        'files_data': files_data,
        'db_routes': db_routes,
        'message': message,
        'source': source
    })

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
        
        return result
    else:
        return element.text if element.text and element.text.strip() else None

def download_file(request, filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("Файл не найден")

# AJAX поиск
def search_routes(request):
    query = request.GET.get('q', '')
    
    if query:
        routes = TourRoute.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(difficulty__icontains=query)
        ).order_by('-id')
    else:
        routes = TourRoute.objects.all().order_by('-id')
    
    results = []
    for route in routes:
        results.append({
            'id': route.id,
            'name': route.name,
            'description': route.description,
            'length_km': route.length_km,
            'difficulty': route.difficulty
        })
    
    return JsonResponse({'routes': results})

# Редактирование маршрута
def edit_route(request, route_id):
    route = get_object_or_404(TourRoute, id=route_id)
    message = ''
    message_type = ''
    
    if request.method == 'POST':
        form = TourRouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            message = "✓ Маршрут успешно обновлен"
            message_type = 'success'
        else:
            message = "❌ Форма содержит ошибки: " + str(form.errors)
            message_type = 'error'
    else:
        form = TourRouteForm(instance=route)
    
    return render(request, 'tour_routes/edit_route.html', {
        'form': form,
        'route': route,
        'message': message,
        'message_type': message_type
    })

# Удаление маршрута (AJAX)
@require_http_methods(["DELETE", "POST"])
def delete_route(request, route_id):
    try:
        route = get_object_or_404(TourRoute, id=route_id)
        route_name = route.name
        route.delete()
        return JsonResponse({
            'success': True,
            'message': f'Маршрут "{route_name}" успешно удален'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при удалении: {str(e)}'
        }, status=400)