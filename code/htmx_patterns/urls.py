from django.contrib import admin
from django.urls import path

from . import views
from .views import headers, partials, posts

urlpatterns = [
    path("", views.home),
    path("headers/", headers.headers_demo, name="headers_demo"),
    path("simple-post-form/", posts.simple_post_form, name="simple_post_form"),
    path("post-without-form/", posts.post_without_form, name="post_without_form"),
    path("post-form-endpoint/", posts.post_form_endpoint, name="post_form_endpoint"),
    path(
        "toggle-with-separate-partials/", partials.toggle_with_separate_partials, name="toggle_with_separate_partials"
    ),
    path("toggle-item/<int:monster_id>/", partials.toggle_item, name="toggle_item"),
    path(
        "paging-with-separate-partials/", partials.paging_with_separate_partials, name="paging_with_separate_partials"
    ),
    path(
        "paging-with-separate-partials-improved/",
        partials.paging_with_separate_partials_improved,
        name="paging_with_separate_partials_improved",
    ),
    path(
        "paging-with-inline-partials/",
        partials.paging_with_inline_partials,
        name="paging_with_inline_partials",
    ),
    path(
        "paging-with-inline-partials-improved/",
        partials.paging_with_inline_partials_improved,
        name="paging_with_inline_partials_improved",
    ),
    path("admin/", admin.site.urls),
]
