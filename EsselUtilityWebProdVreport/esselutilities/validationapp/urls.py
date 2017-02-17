from validationapp import views
from django.conf.urls import include,url

urlpatterns =[

url(r'^validate-jobcard-list/$',views.validate_jobcard_list, name='validate_jobcard_list'),
url(r'^validate-jobcard-list/(?P<month>\d+)/$',views.validate_jobcard_list, name='validate_jobcard_list'),

url(r'^validate-consumer-search/$',views.validate_consumer_search, name='validate_consumer_search'),

url(r'^validator-summery/(?P<month>\d+)/$',views.validator_summery, name='validator_summery'),
url(r'^validator-summery/(?P<month>\d+)/(?P<billcycle_id>\d+)/$',views.validator_summery, name='validator_summery'),
url(r'^validator-summery/(?P<month>\d+)/(?P<billcycle_id>\d+)/(?P<role>\d+)/$',views.validator_summery, name='validator_summery'),

url(r'^validator-summery-export/(?P<month>\d+)/(?P<billcycle_id>\d+)/(?P<role>\d+)/$',views.validator_summery_export, name='validator_summery_export'),


url(r'^validation-level-one/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.validation_level_one, name='validation_level_one'),
url(r'^validation-level-one/(?P<billcycle_id>\d+)/(?P<month>\d+)/(?P<validatorassigned_id>\d+)/$',views.validation_level_one, name='validation_level_one'),


url(r'^validation-level-two/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.validation_level_two, name='validation_level_two'),
url(r'^validation-level-two/(?P<billcycle_id>\d+)/(?P<month>\d+)/(?P<validatorassigned_id>\d+)/$',views.validation_level_two, name='validation_level_two'),


url(r'^validation-level-one-validate/',views.validation_level_one_validate, name='validation_level_one_validate'),
url(r'^validation-level-one-validate-complete/',views.validation_level_one_validate_complete, name='validation_level_one_validate_complete'),


url(r'^validation-level-two-validate/',views.validation_level_two_validate, name='validation_level_two_validate'),

url(r'^validation-level-one-revisit/',views.validation_level_one_revisit, name='validation_level_one_revisit'),
url(r'^validation-level-two-revisit/',views.validation_level_two_revisit, name='validation_level_two_revisit'),

url(r'^validation-level-one-listview/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.validation_level_one_listview,name='validation_level_one_listview'),
url(r'^validation-level-two-listview/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.validation_level_two_listview,name='validation_level_two_listview'),

url(r'^validation-level-one-list-export/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.validation_level_one_list_export,name='validation_level_one_list_export'),
url(r'^validation-level-two-list-export/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.validation_level_two_list_export,name='validation_level_two_list_export'),

url(r'^unbillconsumer/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.unbillconsumer, name='unbillconsumer'),
url(r'^unbillconsumer-export/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.unbillconsumer_export, name='unbillconsumer_export'),

url(r'^unbillconsumerreview/(?P<billcycle_id>\d+)/(?P<month>\d+)/(?P<cons_id>\d+)/$',views.unbillconsumerreview, name='unbillconsumerreview'),

url(r'^duplicate/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.dupicatelist, name='dupicatelist'),
url(r'^dupicatelist-export/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.dupicatelist_export, name='dupicatelist_export'),

url(r'^addduplicate/$',views.addduplicate, name='addduplicate'),
url(r'^rejectduplicate/$',views.rejectduplicate, name='rejectduplicate'),
url(r'^viewduplicate/(?P<billcycle_id>\d+)/(?P<month>\d+)/(?P<duplicate_id>\d+)/$',views.viewduplicate, name='viewduplicate'),


url(r'^verifyconsumer/$',views.verifyconsumer, name='verifyconsumer'),
url(r'^discardconsumer/$',views.discard_consumer, name='discard_consumer'),
url(r'^addconsumer/$',views.add_unbilled_consumer, name='add_unbilled_consumer'),
url(r'^check-duplicate-existence/$',views.check_duplicate_existence, name='check_duplicate_existence'),



]
