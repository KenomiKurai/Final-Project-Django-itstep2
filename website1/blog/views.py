import random
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.db.models import Q
from .forms import PostForm, UserEditForm, RegistrationForm, AvatarUploadForm, CategoryForm
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .models import Post, Category, UserProfile, Cart
from django.contrib.auth import login, update_session_auth_hash


def dummy():
    return str(random.randint(1, 10))


def get_categories():
    all = Category.objects.all()
    count = all.count()
    half = count // 2 + 1
    return {"cat1": all[:half], "cat2": all[half:]}


# Create your views here.
def index(request):
    # posts = Post.objects.all()
    # posts = Post.objects.filter(title__contains='python')
    # posts = Post.objects.filter(published_date__year=2023)
    # posts = Post.objects.filter(category__name__iexact='python')
    posts = Post.objects.order_by('-published_date')
    paginator = Paginator(posts, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # post = Post.objects.get(pk=2)
    context = {'posts': page_obj}
    context.update(get_categories())

    return render(request, "blog/index.html", context=context)


def post(request, title):
    post = get_object_or_404(Post, title=title)


    context = {"post": post}
    context.update(get_categories())

    return render(request, "blog/post.html", context=context)


def category(request, name=None):
    c = get_object_or_404(Category, name=name)
    posts = Post.objects.filter(category=c).order_by('-published_date')
    context = {"posts": posts}
    context.update(get_categories())

    return render(request, "blog/index.html", context=context)


def about(request):
    return render(request, "blog/about.html")





def search(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query))
    context = {"posts": posts}
    context.update(get_categories())

    return render(request, "blog/index.html", context=context)


def pro_url(request, dynamic_url):
    print(dynamic_url)
    return render(request, "blog/services.html", context={"url": dynamic_url})


# @login_required
# def create(request):
#     form = PostForm()
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.published_date = now()
#             post.user = request.user
#             post.save()
#             return index(request)
#     context = {'form': form}
#     return render(request, "blog/create.html", context=context)

from django.shortcuts import render, redirect
from .forms import CategoryForm




@login_required
def create(request):
    post_form = PostForm()
    categories = Category.objects.all()

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.published_date = now()
            post.user = request.user

            # Получите выбранную категорию
            category_id = request.POST.get('category', None)
            if category_id:
                post.category = Category.objects.get(pk=category_id)
            else:
                post.category = None  # Если категория не выбрана, установите ее как None

            post.save()
            return redirect('main')

    context = {'post_form': post_form, 'categories': categories}
    return render(request, "blog/create.html", context=context)


def create_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('create')  # Перенаправление на страницу создания поста после создания категории
    else:
        category_form = CategoryForm()
    return render(request, 'blog/create_category.html', {'category_form': category_form})



# views.py

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.user.first_name = user_form.cleaned_data['first_name']
            user.user.last_name = user_form.cleaned_data['last_name']
            user.user.save()

            user.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=user_profile)

    return render(request, 'blog/edit_profile.html', {'user_form': user_form})


def registration_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegistrationForm()

    return render(request, 'blog/registration.html', {'form': form})


@login_required
def profile(request):
    avatar_form = AvatarUploadForm()
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    context={'user': request.user, 'user_profile': user_profile,'avatar_form': avatar_form}
    return render(request, "blog/profile.html", context=context)


def edit_avatar(request):
    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AvatarUploadForm(instance=request.user.userprofile)
    return render(request, 'blog/edit_avatar.html', {'form': form})




@login_required
def add_to_cart(request, post_id):
    post = Post.objects.get(id=post_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.selected_post = post
    user_profile.save()
    return redirect('view_cart')
@login_required
def view_cart(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    selected_post = user_profile.selected_post
    total_price = selected_post.price if selected_post else 0
    context = {'selected_post': selected_post, 'total_price': total_price}
    return render(request, 'blog/view_cart.html', context)
def buy_completed(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    selected_post = user_profile.selected_post
    context = {'selected_post': selected_post}
    return render(request, 'blog/buy_completed.html', context)
from .models import CreditCard

from .forms import CreditCardForm

@login_required
def checkout(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    selected_post = user_profile.selected_post
    total_price = selected_post.price if selected_post else 0
    user_credit_card = CreditCard.objects.filter(user=request.user).first()
    context = {'selected_post': selected_post, 'total_price': total_price,'user_credit_card': user_credit_card}
    return render(request, 'blog/checkout.html', context)

@login_required
def edit_credit_card(request):
    user_credit_card = CreditCard.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = CreditCardForm(request.POST, instance=user_credit_card)
        if form.is_valid():
            form.save()
            return redirect('checkout')
    else:
        form = CreditCardForm(instance=user_credit_card)

    return render(request, 'blog/edit_credit_card.html', {'form': form})





@login_required
def add_credit_card(request):
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            credit_card = form.save(commit=False)
            credit_card.user = request.user
            credit_card.save()
            return redirect('checkout')
    else:
        form = CreditCardForm()

    return render(request, 'blog/add_credit_card.html', {'form': form})