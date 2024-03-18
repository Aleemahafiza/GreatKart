from django.urls import path
from custom_admin import views

urlpatterns = [
    # USER MANAGEMENT PATHS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    path(
        "userprofile/",
        views.UserProfileList.as_view(),
        name="userprofile",
    ),
    path(
        "userdetail/<int:pk>/",
        views.UserDetail.as_view(),
        name="userdetail",
    ),
    # ADMIN AUTHENTICATION PATH>>>>>>>>>>>>>>>>>>>>>>>>>>
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    path("adminhome/", views.adminhome, name="adminhome"),
    path("adminlogout/", views.adminlogout, name="adminlogout"),
    path(
        "admin_dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),
    # CATEGORY MANAGEMENT PATH>>>>>>>>>>>>>>>>>>>>>>>>>>
    path(
        "category_list/",
        views.CategoriesListView.as_view(),
        name="category_list",
    ),
    path(
        "best_selling_category/",
        views.BestSellingCategories.as_view(),
        name="best_selling_category",
    ),
    path(
        "category_create/",
        views.CategoriesCreate.as_view(),
        name="category_create",
    ),
    path(
        "category_update/<slug:pk>",
        views.CategoriesUpdate.as_view(),
        name="category_update",
    ),
    path(
        "deletecategory/<pk>",
        views.deletecategory,
        name="deletecategory",
    ),
    # PRODUCTD MANAGEMENT PATH>>>>>>>>>>>>>>>>>>>>>>>>>>
    path(
        "product_list/",
        views.ProductsListView.as_view(),
        name="product_list",
    ),
    path(
        "product_create/",
        views.ProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "best_selling_product/",
        views.BestSellingProduct.as_view(),
        name="best_selling_product",
    ),
    path(
        "product_update/<slug:pk>",
        views.ProductUpdate.as_view(),
        name="product_update",
    ),
    path(
        "deleteproduct/<pk>", views.deleteproduct, name="deleteproduct"
    ),
    # VARIATIONS PATH>>>>>>>>>>>>>>>>>>>>>>>>>>
    path("variation/", views.VariationList.as_view(), name="variation"),
    path(
        "variation_create/",
        views.VariationCreate.as_view(),
        name="variation_create",
    ),
    # ORDERS PATH>>>>>>>>>>>>>>>>>>>>>>>>>>
    path(
        "order_management",
        views.order_management,
        name="order_management",
    ),
    path(
        "view_returt_list",
        views.view_returt_list,
        name="view_returt_list",
    ),
    path(
        "view_order_detail/<int:order_id>/",
        views.view_order_detail,
        name="view_order_detail",
    ),
    path(
        "admin_cancel_order/<int:order_id>/",
        views.admin_cancel_order,
        name="admin_cancel_order",
    ),
    path(
        "change_order_status/<int:order_id>/",
        views.change_order_status,
        name="change_order_status",
    ),
    path(
        "view_return_order/<int:order_id>/",
        views.view_return_order,
        name="view_return_order",
    ),
    path(
        "admin_grant_return_request/<int:order_id>/",
        views.admin_grant_return_request,
        name="admin_grant_return_request",
    ),
    # Coupon PATH>>>>>>>>>>>>>>>>>>>>>>>>>>
    path("coupon/", views.coupon, name="coupon"),
    path("add_coupon/", views.add_coupon, name="add_coupon"),
    path(
        "edit_coupon/<uuid:pk>/", views.edit_coupon, name="edit_coupon"
    ),
    path(
        "delete_coupon/<uuid:pk>/",
        views.delete_coupon,
        name="delete_coupon",
    ),
    path(
        "undelete_coupon/<uuid:pk>/",
        views.undelete_coupon,
        name="undelete_coupon",
    ),
]
