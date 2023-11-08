from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("blog/", views.index, name="main"),
    path("blog/post-<str:title>/", views.post, name="post"),
    path("about", views.about, name="about"),
    path('blog/category/<str:name>', views.category, name='category'),
    path("blog/search/", views.search, name='search'),
    path("blog/create/", views.create, name="create"),
path('create_category/', views.create_category, name='create_category'),
    path("blog/login", LoginView.as_view(), name="blog_login"),
    path("blog/logout/", LogoutView.as_view(), name="blog_logout"),
    path("blog/registration/", views.registration_user, name="registration"),
    path("blog/profile/", views.profile, name="profile"),
    path("edit_profile/", views.edit_profile, name="editProfile"),
    path('edit_avatar/', views.edit_avatar, name='edit_avatar'),
path('blog/add_to_cart/<int:post_id>/', views.add_to_cart, name='add_to_cart'),
    path('blog/view_cart/', views.view_cart, name='view_cart'),
    path('blog/checkout/', views.checkout, name='checkout'),
path('blog/add_credit_card/', views.add_credit_card, name='add_credit_card'),
path('blog/buy_completed/', views.buy_completed, name='buy_completed'),
path('blog/edit_credit_card/', views.edit_credit_card, name='edit_credit_card'),
]
