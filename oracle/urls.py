from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', 			views.index,	name='index'),
	url(r'^find$', 		views.find,		name = 'find'),
	url(r'^insert$',	views.insert,	name = 'insert'),
	url(r'^update$',	views.update,	name = 'update'),
	url(r'^delete$',	views.delete,	name = 'delete'),
	url(r'^viewstat$',	views.viewstat,	name = 'viewstat'), 
	url(r'^login$',	views.login,	name = 'login'), 
	url(r'^register$',	views.register,	name = 'register'), 
	url(r'^maps$',	views.maps,	name = 'maps'),
	url(r'^chat$',	views.chat,	name = 'chat'),
	url(r'^table$',	views.table,	name = 'table'),
	url(r'^user$',	views.user,	name = 'user'), 
	url(r'^updateProfile$',	views.updateProfile,	name = 'updateProfile'), 
	url(r'^addFlight$',	views.addFlight,	name = 'addFlight'), 
	url(r'^deleteFlight$',	views.deleteFlight,	name = 'deleteFlight'),
	url(r'^deleteAccount$',	views.deleteAccount,	name = 'deleteAccount'), 
	url(r'^logout$',	views.logout,	name = 'logout'), 
	url(r'^viewEstimate$',	views.viewEstimate,	name = 'viewEstimate')

]
