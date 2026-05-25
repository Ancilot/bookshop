from .forms import PriceForm, AuthorForm, TagForm
from django.contrib.auth.decorators import (
    login_required
)
from django.http import JsonResponse
from django.template.loader import render_to_string
from shop.models import Category, Price
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.http import HttpResponse

from openpyxl import Workbook
from reportlab.pdfgen import canvas
from django.shortcuts import render, get_object_or_404, redirect

from orders.models import (
    Order,
    OrderItem
)

from shop.models import (
    Product,
    ProductImage,
    Book,
    BoardGame,
    Stationery,
    Author,
    Genre,
    Tag
)

from .decorators import admin_required

from .forms import (
    ProductForm,
    BookForm,
    BoardGameForm,
    StationeryForm
)

from admin_panel.constant import (
    CATEGORY_MAP,
    RELATED_MAP
)
from shop.models import Genre
from .forms import GenreForm
from django.contrib import messages

from shop.models import Supplier
from .forms import SupplierForm

def supplier_list(request):
    suppliers = Supplier.objects.filter(is_active=True)
    archived_suppliers = Supplier.objects.filter(is_active=False)
    return render(request, 'admin_panel/dictionaries/suppliers/suppliers.html', {
        'suppliers': suppliers,
        'archived_suppliers': archived_suppliers,
    })

def supplier_create(request):
    form = SupplierForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('admin_panel:supplier_list')

    return render(request, 'admin_panel/dictionaries/suppliers/supplier_form.html', {'form': form})

def supplier_delete(request, id):
    supplier = get_object_or_404(Supplier, id=id)

    used = (
        Book.objects.filter(publisher=supplier).exists() or
        BoardGame.objects.filter(publisher=supplier).exists() or
        Stationery.objects.filter(supplier=supplier).exists()
    )

    if used:
        supplier.is_active = False
        supplier.save()

        messages.warning(
            request,
            "Поставщик используется в товарах → отправлен в архив"
        )
    else:
        supplier.delete()
        messages.success(
            request,
            "Поставщик удалён"
        )

    return redirect('admin_panel:supplier_list')

def supplier_restore(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    supplier.is_active = True
    supplier.save()

    return redirect('admin_panel:supplier_list')

def genre_list(request):
    genres = Genre.objects.all()
    return render(request, 'admin_panel/dictionaries/genres/genres.html', {'genres': genres})

def genre_create(request):
    form = GenreForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('admin_panel:genre_list')

    return render(request, 'admin_panel/dictionaries/genres/genre_form.html', {'form': form})

def genre_delete(request, id):
    genre = get_object_or_404(Genre, id=id)

    if genre.book_set.exists():
        messages.error(request, "Нельзя удалить — используется в книгах")
        return redirect('admin_panel:genre_list')

    genre.delete()
    return redirect('admin_panel:genre_list')

def author_list(request):
    authors = Author.objects.all()
    return render(request, 'admin_panel/dictionaries/authors/authors.html', {'authors': authors})

def author_create(request):
    form = AuthorForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('admin_panel:author_list')

    return render(request, 'admin_panel/dictionaries/authors/author_form.html', {'form': form})

def author_delete(request, id):
    author = get_object_or_404(Author, id=id)

    if author.book_set.exists():
        messages.error(request, "Нельзя удалить — автор используется в книгах")
        return redirect('admin_panel:author_list')

    author.delete()
    return redirect('admin_panel:author_list')

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'admin_panel/dictionaries/tags/tags.html', {'tags': tags})

def tag_create(request):
    form = TagForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('admin_panel:tag_list')

    return render(request, 'admin_panel/dictionaries/tags/tag_form.html', {'form': form})

def tag_delete(request, id):
    tag = get_object_or_404(Tag, id=id)

    if Book.objects.filter(tags=tag).exists():
        messages.error(request, "Нельзя удалить — тег используется в книгах")
        return redirect('admin_panel:tag_list')

    tag.delete()
    return redirect('admin_panel:tag_list')

def dictionaries(request):
    return render(request, 'admin_panel/dictionaries/index.html')

@login_required
@admin_required
def product_create(request):

    product_form = ProductForm(request.POST or None)

    price_form = PriceForm(request.POST or None)
    category_slug = None
    category_form = None

    if request.method == 'POST':

        category_id = request.POST.get('category')
        category_obj = Category.objects.filter(id=category_id).first()

        category_slug = category_obj.slug if category_obj else None

        form_class = CATEGORY_MAP.get(category_slug)

        if form_class:
            category_form = form_class(request.POST)

        # validashion

        forms_valid = product_form.is_valid() and price_form.is_valid()

        if category_form:
            forms_valid = forms_valid and category_form.is_valid()

        if forms_valid:

            product = product_form.save()

            price = price_form.save(commit=False)
            price.product = product
            price.save()

            # category save
            if category_form:
                obj = category_form.save(commit=False)
                obj.product = product
                obj.save()

                if hasattr(category_form, "save_m2m"):
                    category_form.save_m2m()

            # изображения
            images = request.FILES.getlist('images')
            new_images = []

            for index, image in enumerate(images):
                img = ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_main=False
                )
                new_images.append(img)

            main_image_value = request.POST.get('main_image')

            if main_image_value:
                product.images.update(is_main=False)

                if main_image_value.startswith('new_'):
                    try:
                        idx = int(main_image_value.replace('new_', ''))
                        if idx < len(new_images):
                            new_images[idx].is_main = True
                            new_images[idx].save()
                    except ValueError:
                        pass

            return redirect('admin_panel:product_list')

        else:
            print("PRODUCT ERRORS:", product_form.errors)
            if category_form:
                print("CATEGORY ERRORS:", category_form.errors)

    return render(request, 'admin_panel/product_form.html', {
        'product_form': product_form,
        'category_form': category_form,
        'price_form': price_form,
    })

def load_category_form(request):

    category_id = request.GET.get('category_id')
    product_id = request.GET.get('product_id')

    category = Category.objects.filter(id=category_id).first()
    if not category:
        return JsonResponse({'html': ''})

    form_class = CATEGORY_MAP.get(category.slug)
    if not form_class:
        return JsonResponse({'html': ''})

    instance = None

    if product_id:
        product = Product.objects.filter(id=product_id).first()
        if product:
            related_name = RELATED_MAP.get(category.slug)
            instance = getattr(product, related_name, None)

    form = form_class(instance=instance)

    html = render_to_string(
        'admin_panel/partials/category_form.html',
        {'category_form': form}
    )

    return JsonResponse({'html': html})

def product_list(request):

    active_products = Product.objects.filter(available=True)
    inactive_products = Product.objects.filter(available=False)

    return render(request, 'admin_panel/product_list.html', {
        'active_products': active_products,
        'inactive_products': inactive_products,
    })

def product_restore(request, id):
    product = get_object_or_404(Product, id=id)
    product.available = True
    product.save()
    return redirect('admin_panel:product_list')

# print("BOOK DATA:", request.POST.get("publisher"), type(request.POST.get("publisher")))
       # print("YEAR DATA:", request.POST.get("year"), type(request.POST.get("year")))


#
# UPDATE PRODUCT
#
 #       print(BookForm(request.POST).errors)
  #      print("POST publisher:", request.POST.get("publisher"))


@login_required
@admin_required
def product_update(request, id):

    product = get_object_or_404(Product, id=id)
    images = product.images.all()

    product_form = ProductForm(
        request.POST or None,
        instance=product
    )
    price_instance = product.prices.first()

    price_form = PriceForm(
        request.POST or None,
        instance=price_instance
    )

    # slag
    category_id = request.POST.get('category') if request.method == 'POST' else product.category_id
    category_obj = Category.objects.filter(id=category_id).first()
    category_slug = category_obj.slug if category_obj else None

    form_class = CATEGORY_MAP.get(category_slug)

    category_instance = None
    category_form = None

    if form_class:

        related_name = RELATED_MAP.get(category_slug)

        category_instance = getattr(product, related_name, None)

        category_form = form_class(
            request.POST or None,
            instance=category_instance
        )

    if request.method == 'POST':

        if product_form.is_valid() and (
            category_form.is_valid() if category_form else True
        ):

            product = product_form.save()

            if price_form.is_valid():
                price_value = price_form.cleaned_data['value']

                last_price = product.prices.first()

                if not last_price or last_price.value != price_value:
                    Price.objects.create(product=product, value=price_value)
            else:
                price_value = None

            # save
            if category_form:
                obj = category_form.save(commit=False)
                obj.product = product
                obj.save()

                if hasattr(category_form, "save_m2m"):
                    category_form.save_m2m()

            # цдаление изображения
            delete_ids = request.POST.getlist('delete_image')

            if delete_ids:
                ProductImage.objects.filter(
                    id__in=delete_ids,
                    product=product
                ).delete()

            # обновление изображения
            uploaded_images = request.FILES.getlist('images')

            new_images = []

            for img in uploaded_images:
                new_images.append(
                    ProductImage.objects.create(
                        product=product,
                        image=img,
                        is_main=False
                    )
                )

            # основное изображение
            main_image = request.POST.get('main_image')

            if main_image:
                product.images.update(is_main=False)

                if main_image.startswith('new_'):
                    try:
                        i = int(main_image.replace('new_', ''))
                        if i < len(new_images):
                            new_images[i].is_main = True
                            new_images[i].save()
                    except ValueError:
                        pass

                elif main_image.startswith('old_'):
                    img_id = main_image.replace('old_', '')
                    ProductImage.objects.filter(
                        id=img_id,
                        product=product
                    ).update(is_main=True)

            return redirect('admin_panel:product_list')

        else:
            print("PRODUCT FORM ERRORS:", product_form.errors)
            if category_form:
                print("CATEGORY FORM ERRORS:", category_form.errors)

    return render(request, 'admin_panel/product_form.html', {
        'product_form': product_form,
        'category_form': category_form,
        'product': product,
        'images': images,
        'price_form': price_form,
    })

def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if product.orderitem_set.exists():
        product.available = False
        product.save()
    else:
        product.delete()

    return redirect('admin_panel:product_list')


@admin_required
def export_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=report.pdf'

    p = canvas.Canvas(response)

    y = 800

    p.drawString(
        100,
        y,
        'Отчет по продажам'
    )

    y -= 40

    products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')
    )

    for item in products:

        text = (
            f"{item['product__name']} - "
            f"{item['total']} шт"
        )

        p.drawString(100, y, text)

        y -= 25

    p.showPage()

    p.save()

    return response


@admin_required
def export_excel(request):

    wb = Workbook()

    ws = wb.active

    ws.title = 'Отчет'

    ws.append([
        'Товар',
        'Количество продаж'
    ])

    products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')
    )

    for item in products:

        ws.append([
            item['product__name'],
            item['total']
        ])

    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.sheet'
        )
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=report.xlsx'

    wb.save(response)

    return response


@admin_required
def dashboard(request):

    total_orders = Order.objects.count()

    total_products = Product.objects.count()

    total_sales = sum(
        order.total_price
        for order in Order.objects.all()
    )

    popular_products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_sales': total_sales,
        'popular_products': popular_products,
    }

    return render(
        request,
        'admin_panel/dashboard.html',
        context
    )

@admin_required
def reports(request):

    date_from = request.GET.get(
        'date_from'
    )

    date_to = request.GET.get(
        'date_to'
    )

    orders = Order.objects.all()

    if date_from:

        orders = orders.filter(
            created__date__gte=parse_date(
                date_from
            )
        )

    if date_to:

        orders = orders.filter(
            created__date__lte=parse_date(
                date_to
            )
        )

    popular_books = (
        OrderItem.objects
        .filter(
            product__book__isnull=False
        )
        .values('product__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')
    )

    popular_authors = (
        Author.objects
        .annotate(
            total_sold=Sum(
                'book__product__orderitem__quantity'
            )
        )
        .order_by('-total_sold')
    )

    unsold_books = (
        Book.objects
        .annotate(
            sold=Sum(
                'product__orderitem__quantity'
            )
        )
        .filter(sold__isnull=True)
    )

    context = {
        'popular_books': popular_books,
        'popular_authors': popular_authors,
        'unsold_books': unsold_books,
    }

    return render(
        request,
        'admin_panel/reports.html',
        context
    )

