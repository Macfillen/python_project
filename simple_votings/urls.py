"""simple_votings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from vote import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page),
    path('vote-create', views.vote_add_page),
    path('vote-process/<int:id>', views.vote_process, name = 'vote-process'),
    path('vote-process/<int:id>/revote', views.revote_process, name = 'revote-process'),
    path('profile/', include('django.contrib.auth.urls')),
    path('only-mine', views.only_mine_polls),
    path('vote/delete/<int:id>', views.poll_delete),
    path('profile/reg', views.reg_page),
    path('profile/history', views.profile_history_page),
    path('vote/edit/<int:id>', views.poll_edit),
    path('profile/', views.profile_edit_page),
    path('necessary/', views.necessary),
    path('add_claim/<int:id>', views.add_claim_page),
    path('claims/', views.claims_history),
    path('claim/status-rejection/<int:id>', views.claim_status_reject),
    path('claim/status-confirmation/<int:id>', views.claim_status_confirm)
]
