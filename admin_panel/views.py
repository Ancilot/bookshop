from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import (
    login_required
)

from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.http import HttpResponse

from openpyxl import Workbook
from reportlab.pdfgen import canvas

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
    Author
)

from .decorators import admin_required

from .forms import (
    ProductForm,
    BookForm,
    BoardGameForm,
    StationeryForm
)


#
# CREATE PRODUCT
#

@login_required
def product_create(request):

    if request.method == 'POST':

        # ===== PRODUCT =====
        product_form = ProductForm(request.POST)

        # категория берётся из POST (ВАЖНО)
        category = request.POST.get('category')

        # ===== дополнительные формы (только нужная) =====
        book_form = None
        game_form = None
        stationery_form = None

        if category == 'книги':
            book_form = BookForm(request.POST)

        elif category == 'настольные игры':
            game_form = BoardGameForm(request.POST)

        elif category == 'канцелярия':
            stationery_form = StationeryForm(request.POST)

        # ===== PRODUCT VALID =====
        if product_form.is_valid():

            product = product_form.save()

            # ===== IMAGES =====
            images = request.FILES.getlist('images')

            main_image_value = request.POST.get('main_image')

            new_images = []

            for index, image in enumerate(images):

                img = ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_main=False
                )

                new_images.append(img)

            # ===== MAIN IMAGE =====
            if main_image_value:

                product.images.update(is_main=False)

                if main_image_value.startswith('new_'):
                    idx = int(main_image_value.replace('new_', ''))
                    if idx < len(new_images):
                        new_images[idx].is_main = True
                        new_images[idx].save()

            # ===== CATEGORY LOGIC =====
            if category == 'книги' and book_form and book_form.is_valid():

                book = book_form.save(commit=False)
                book.product = product
                book.save()
                book_form.save_m2m()

            elif category == 'настольные игры' and game_form and game_form.is_valid():

                game = game_form.save(commit=False)
                game.product = product
                game.save()
                game_form.save_m2m()

            elif category == 'канцелярия' and stationery_form and stationery_form.is_valid():

                stationery = stationery_form.save(commit=False)
                stationery.product = product
                stationery.save()

            return redirect('admin_panel:product_list')

    else:

        product_form = ProductForm()

        book_form = BookForm()
        game_form = BoardGameForm()
        stationery_form = StationeryForm()

    return render(
        request,
        'admin_panel/product_form.html',
        {
            'product_form': product_form,
            'book_form': book_form,
            'game_form': game_form,
            'stationery_form': stationery_form,
        }
    )


#
# PRODUCT LIST
#

def product_list(request):

    products = Product.objects.all()

    return render(
        request,
        'admin_panel/product_list.html',
        {
            'products': products
        }
    )


#
# UPDATE PRODUCT
#

@login_required
def product_update(request, id):

    product = get_object_or_404(Product, id=id)
    images = product.images.all()

    book_instance = getattr(product, 'book', None)
    game_instance = getattr(product, 'board_game', None)
    stationery_instance = getattr(product, 'stationery', None)

    if request.method == 'POST':

        product_form = ProductForm(request.POST, instance=product)

        # ===== category берём из POST =====
        category = request.POST.get('category')

        # ===== формы создаём только нужные =====
        book_form = None
        game_form = None
        stationery_form = None

        if category == 'книги':
            book_form = BookForm(request.POST, instance=book_instance)

        elif category == 'настольные игры':
            game_form = BoardGameForm(request.POST, instance=game_instance)

        elif category == 'канцелярия':
            stationery_form = StationeryForm(
                request.POST,
                instance=stationery_instance
            )

        # ===== PRODUCT VALID =====
        if product_form.is_valid():

            product = product_form.save()

            # ===== CATEGORY SAVE =====
            if category == 'книги' and book_form and book_form.is_valid():

                obj = book_form.save(commit=False)
                obj.product = product
                obj.save()
                book_form.save_m2m()

            elif category == 'настольные игры' and game_form and game_form.is_valid():

                obj = game_form.save(commit=False)
                obj.product = product
                obj.save()
                game_form.save_m2m()

            elif category == 'канцелярия' and stationery_form and stationery_form.is_valid():

                obj = stationery_form.save(commit=False)
                obj.product = product
                obj.save()

            # ===== DELETE IMAGES =====
            delete_ids = request.POST.getlist('delete_image')

            if delete_ids:
                ProductImage.objects.filter(
                    id__in=delete_ids,
                    product=product
                ).delete()

            # ===== NEW IMAGES =====
            files = request.FILES.getlist('images')

            new_images = []

            for f in files:
                img = ProductImage.objects.create(
                    product=product,
                    image=f,
                    is_main=False
                )
                new_images.append(img)

            # ===== MAIN IMAGE =====
            main = request.POST.get('main_image')

            if main:
                product.images.update(is_main=False)

                if main.startswith('old_'):
                    img_id = int(main.replace('old_', ''))

                    ProductImage.objects.filter(
                        id=img_id,
                        product=product
                    ).update(is_main=True)

                elif main.startswith('new_'):
                    idx = int(main.replace('new_', ''))

                    if idx < len(new_images):
                        new_images[idx].is_main = True
                        new_images[idx].save()

            return redirect('admin_panel:product_list')

    else:

        product_form = ProductForm(instance=product)

        book_form = BookForm(instance=book_instance)
        game_form = BoardGameForm(instance=game_instance)
        stationery_form = StationeryForm(instance=stationery_instance)

    return render(
        request,
        'admin_panel/product_form.html',
        {
            'product_form': product_form,
            'book_form': book_form,
            'game_form': game_form,
            'stationery_form': stationery_form,
            'product': product,
            'images': images,
        }
    )


#
# DELETE PRODUCT
#

def product_delete(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    product.delete()

    return redirect(
        'admin_panel:product_list'
    )


#
# EXPORT PDF
#

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


#
# EXPORT EXCEL
#

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


#
# DASHBOARD
#

@admin_required
def dashboard(request):

    total_orders = Order.objects.count()

    total_products = Product.objects.count()

    total_sales = sum(
        order.total_price
        for order in Order.objects.all()
    )

    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_sales': total_sales,
    }

    return render(
        request,
        'admin_panel/dashboard.html',
        context
    )


#
# REPORTS
#

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