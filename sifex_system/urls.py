from django.urls import path
from .views import *
from accounts.views import *


urlpatterns = [
    path('', console, name="console"),
    path('location/search/', location_view, name="location_search"),
    path('location/save/', save_location_info, name="save_location_info"),
    path('location/search/process/', location_search_result, name='location_search_process'),
    path('location/<int:pk>/', location_search_result_found, name='location_search_result_found'),
    path('location_search_process/', location_search_process, name='location_search_process'),


    path('awb-details/<int:awb_id>/', awb_details, name='awb_details'),

  

    # search
    path('search/', search_parcel, name='search_parcel'),
    path('search/<int:pk>/', search_found, name='search_found'),
    path('awb-history/', awb_history, name='awb_history'),

    path('accept_console/', accept_console, name="accept_console"),
    path('get-freight-by-awb-type/', get_freight_by_awb, name='get_freight_by_awb_type'),
    path('accept_loaded_console/', accept_loaded_console, name="accept_loaded_console"),
    path('accept_manifested_console/', accept_manifested_console, name="accept_manifested_console"),
    path('parcel_import/', parcel_import, name="parcel_import"),
    path('accept_arrived_console/', accept_arrived_console, name="accept_arrived_console"),
    path('accept_release_console/', accept_release_console, name="accept_release_console"),
    path('accept_pod_console/', accept_pod_console, name="accept_pod_console"),
    path('accept_underclearance_console/', accept_underclearance_console, name="accept_underclearance_console"),
    path('accept_delivered_console/', accept_delivered_console, name="accept_delivered_console"),
    path('accept/', accept_parcel, name="accept_parcel"),
    path('accept/<str:pk>/', parcel_view, name="parcel_view"),
    path('save_parcel/', add_parcel, name="save_parcel"),
    path('accept_form/', accept_form_view, name="accept_form_view"),
    path('new_staff/', new_staff, name="new_staff"),
    path('password_success/', password_success, name="password_success"),
    path('password_change/', PasswordChange.as_view(), name="password_change"),
    path('loaded/', add_master_status, name="load_master_status"),
    path('manifested/', manifested_master_status, name="manifested_master_status"),
    path('departed/', departed_master_status, name="departed_master_status"),
    path('arrived/', arrived_master_status, name="arrived_master_status"),
    path('underclearance/', underclearance_master_status, name="underclearance_master_status"),
    path('delivered/', delivered_master_status, name="delivered_master_status"),
    path('released/', released_master_status, name="released_master_status"),
    path('pod/', pod_master_status, name="pod_master_status"),
    path('payment/', payment_master_status, name="payment_master_status"),
    path('loaded/sub/', add_sub_status, name="load_sub_status"),
    path('manifested/sub/', add_sub_status, name="load_sub_status"),

    path('total_master_awb_kg/', total_master_awb_kg, name="total_master_awb_kg"),
    path('total_month_master_awb_kg/', total_month_master_awb_kg, name="total_month_master_awb_kg"),

    path('update_master_arr/<int:id>/', update_master_arr, name="update_slave_arr"),
    path('update_master_dlv/<int:id>/', update_master_dlv, name="update_master_dlv"),

    path('blog_create/', blog_create_view, name="blog_create"),
    path('blogs/', blog_view, name="blogs"),
    path('quotes/', quotes_view, name="quotes"),
    path('users/', users, name="users"),
    path('delete_user/<int:id>/', delete_user, name="delete-user"),

    path('awb_edit/<int:pk>/', awb_edit, name="awb-edit"),


    path('add_awb/<int:pk>/', on_edit_add_parcel_view, name="on_edit_add_awb_view"),
    path('save_awb/', on_edit_add_parcel, name="on_edit_save_awb"),
    path('export/pdf/<int:pk>/', export_masterawb_pdf_label, name="export-master-awb-pdf-label"),
    path('delete_awb/<int:id>/', delete_awb, name="delete-awb"),
    path('delete_invoice/<int:id>/', DeleteInvoiceView.as_view(), name="delete-invoice"),

    # sales report


    path('generate_sales_report/', generate_sales_report, name='generate_sales_report'),
    path('cash_sales_report/<str:date_from>/<str:date_to>/', cash_sales_report, name='cash_sales_report'),
    path('bank_sales_report/<str:date_from>/<str:date_to>/', bank_sales_report, name='bank_sales_report'),
    path('mobile_sales_report/<str:date_from>/<str:date_to>/', mobile_sales_report, name='mobile_sales_report'),


    # INVOICE APP

    path('activity-logs/', activity_log_list, name='activity_log_list'),

    path('invoices/', InvoiceListView.as_view(), name="invoice-list"),
    path('create/<int:pk>/', createInvoice, name="invoice-create"),
    path('generate-invoice/', invoice_generation, name="generate-invoice"),

      # printing
    path('print_label/<int:pk>/', print_label, name='print_label'),
    path('invoice/pdf/<int:invoice_id>/', generate_invoice_pdf, name='invoice_pdf'),
    path('invoice_detail/<int:invoice_id>/', invoice_detail, name='invoice-detail'),

    path('generate_pdf/', generate_pdf, name='generate_pdf'),
    path('generate_spreadsheet/', generate_spreadsheet, name='generate_spreadsheet'),

    #CUSTOMER APP
    path('add-customer/', add_customer, name="add-customer"),
    path('customers', customer_list, name="customers-list"),

    # REPORT APP
    path('deliverd-goods/', list_of_delivered_awb, name="delivered-goods"),
    path('undeliverd-goods/', list_of_undelivered_awb, name="undelivered-goods"),
    path('paid-goods/', list_of_paid_awb, name="paid-goods"),
    path('unpaid-goods/', list_of_unpaid_awb, name="unpaid-goods"),
    path('credited-goods/', list_of_credited_awb, name="credited-goods"),

    path('delivered_report', delivered_report, name="delivered_report"),
    path('undelivered_report/', undelivered_report, name="undelivered_report"),
    path('paid_report', paid_report, name="paid_report"),
    path('unpaid_report', unpaid_report, name="unpaid_report"),
    path('credited_report', credited_report, name="credited_report"),
    path('freight_report', freight_report, name="freight_report"),


    # ATTENDANCE APP
    path('check-staff', check_staff, name="check-staff"),
    path('check-staff-by-code', check_staff_by_code, name="check-staff-by-code"),
    path('check-staff-id/', check_staff_id, name="check-staff-id"),
    path('mark-attendance-in/', mark_attendance_in, name="mark-attendance-in"),
    path('mark-attendance-out/', mark_attendance_out, name="mark-attendance-out"),
    path('filter-attendance', filter_attendance, name="filter-attendance"),
    path('attendance', list_attendance, name="attendance"),



    path('trash/', trash_view, name='trash'),
    path('restore-invoice/<int:id>/', restore_invoice, name='restore_invoice'),
    # path('delete-invoice/<int:id>/', permanently_delete_invoice, name='permanently_delete_invoice'),
    path('delete-invoice/permanently/<int:id>/', permanently_delete_invoice, name='delete-permanently-invoice'),
    path('restore-awb/<int:id>/', restore_awb, name='restore_awb'),
    path('delete-awb/<int:id>/', permanently_delete_awb, name='permanently_delete_awb'),




    path('users/view/<int:user_id>/', view_user, name='view_user'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/reset_password/<int:user_id>/', reset_password, name='reset_password'),
    path('users/activate/<int:user_id>/', activate_user, name='activate_user'),
    path('users/deactivate/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('users/reset_password/<int:user_id>/', reset_password, name='reset_password'),


    path('invoice-history/', InvoiceHistoryView.as_view(), name='invoice-history'),



    # freight zone
    path('freights/', freight_list, name='freight_list'),
    path('preferences/', rate_list, name='rate_list'),
    path('freights/new/', create_freight, name='create_freight'),
    path('freights/edit/<int:pk>/', update_freight, name='update_freight'),
    path('delete-freight/<int:freight_id>/', delete_freight, name='delete_freight'),



]
