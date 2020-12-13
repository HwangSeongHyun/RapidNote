from django.urls import path, include
from . import views
from django.conf.urls import (handler404, handler500, handler400, handler403)

app_name='note'
urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name = 'logout'),
    path('index/', views.index, name = 'index'),
    path('plusmemo/', views.plusmemo, name = 'plusmemo'),
    path('plustask/', views.plustask, name = 'plustask'),
    path('idcheck/', views.idcheck, name='idcheck'),
    path('changetask/', views.changetask, name='changetask'),
    path('<str:task>/<str:memo>/', views.changememo, name='changememo'),
    path('renametask/', views.renametask, name='renametask'),
    path('renamememo/', views.renamememo, name='renamememo'),
    path('deletetask/', views.deletetask, name='deletetask'),
    path('deletememo/', views.deletememo, name='deletememo'),
    path('savehash/', views.savehash, name='savehash'),
    path('searchhash/', views.searchhash, name='searchhash'),
    path('applogin/', views.app_login, name='applogin'),
    path('appinsertdb/', views.app_insertDB, name='appinsertdb'),

    #임시 추가
    path('findIdPw/', views.findIdPw, name = 'findIdPw'),
    path('insertDB/', views.insertDB, name = 'insertDB'),
    path('viewer/<str:id>/<str:task>/<str:memo>/', views.viewer, name='viewer'),
    path('myPage/', views.myPage, name = 'myPage'),
    path('findId/', views.findId, name = 'findId'),
    path('findPw/', views.findPw, name = 'findPw'),
    path('download/', views.download, name = 'download'),
]

handler404 = 'note.views.error_page'
handler500 = 'note.views.error_page'
handler403 = 'note.views.error_page'
handler400 = 'note.views.error_page'
