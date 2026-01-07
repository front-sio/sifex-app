from django.contrib import admin
from sifex_system.models import *

admin.site.site_header = "Sifex Admin"
admin.site.site_title = "Sifex Admin"
admin.site.index_title = "Operations Overview"


@admin.register(Masterawb)
class MasterAwbAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "awb",
        "order_number",
        "receiver_name",
        "awb_type",
        "date_received",
        "current_status",
        "deleted",
    )
    list_filter = (
        "awb_type",
        "accepted",
        "loaded",
        "manifested",
        "departed",
        "arrived",
        "under_clearance",
        "released",
        "bill",
        "invoice_generated",
        "billed",
        "delivered",
        "POD",
        "deleted",
    )
    search_fields = (
        "awb",
        "order_number",
        "sender_name",
        "receiver_name",
        "sender_tel",
        "receiver_tel",
    )
    ordering = ("-date_received",)
    date_hierarchy = "date_received"
    list_per_page = 50

    @admin.display(description="Status")
    def current_status(self, obj):
        return obj.get_current_status()


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "awb",
        "status",
        "invoice_detail",
        "date",
        "date_of_payment",
        "total_amount_usd",
        "deleted",
    )
    list_filter = ("status", "invoice_detail", "date", "deleted")
    search_fields = (
        "id",
        "customer",
        "customer_email",
        "customer_phone",
        "awb__awb",
        "awb__order_number",
    )
    ordering = ("-date",)
    date_hierarchy = "date"
    list_select_related = ("awb",)
    list_per_page = 50


@admin.register(InvoiceHistory)
class InvoiceHistoryAdmin(admin.ModelAdmin):
    list_display = ("invoice_id", "customer", "awb", "status", "action", "performed_at")
    list_filter = ("status", "action", "performed_at")
    search_fields = ("invoice_id", "customer", "awb", "note")
    ordering = ("-performed_at",)
    list_per_page = 50


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "description", "timestamp")
    list_filter = ("activity_type", "timestamp")
    search_fields = ("user__username", "description")
    ordering = ("-timestamp",)
    list_per_page = 50


@admin.register(Slaveawb)
class SlaveAwbAdmin(admin.ModelAdmin):
    list_display = ("id", "awb", "master", "awb_type")
    list_filter = ("awb_type",)
    search_fields = ("awb", "master_awb", "master__awb")
    list_select_related = ("master",)
    list_per_page = 50


@admin.register(MasterStatus)
class MasterStatusAdmin(admin.ModelAdmin):
    list_display = ("master", "status", "date", "time", "terminal", "user")
    list_filter = ("status", "terminal", "date")
    search_fields = ("master__awb", "master__order_number", "user__username")
    list_select_related = ("master", "user")
    list_per_page = 50


@admin.register(SlaveStatus)
class SlaveStatusAdmin(admin.ModelAdmin):
    list_display = ("sub_awb", "status", "date", "time", "terminal", "user")
    list_filter = ("status", "terminal", "date")
    search_fields = ("sub_awb__awb", "user__username")
    list_select_related = ("sub_awb", "user")
    list_per_page = 50


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "service")
    search_fields = ("name", "email", "phone", "service")
    list_per_page = 50


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "tracking_key", "amount_usd", "amount_tz")
    search_fields = ("customer__customer", "tracking_key")
    list_select_related = ("customer",)
    list_per_page = 50


@admin.register(SystemPreference)
class SystemPreferenceAdmin(admin.ModelAdmin):
    list_display = ("exchange_rate", "rate", "currency", "deleted")
    list_filter = ("deleted", "currency")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "designation", "department", "phone")
    search_fields = ("name", "designation", "department", "phone")
    list_per_page = 50


@admin.register(AwbLocation)
class AwbLocationAdmin(admin.ModelAdmin):
    list_display = ("awb", "rack", "bay", "pcs")
    search_fields = ("awb__awb", "rack", "bay")
    list_select_related = ("awb",)
    list_per_page = 50


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("staff", "present", "date", "in_time", "out_time")
    list_filter = ("present", "date")
    search_fields = ("staff__name",)
    list_select_related = ("staff",)
    list_per_page = 50


@admin.register(AwbHistory)
class AwbHistoryAdmin(admin.ModelAdmin):
    list_display = ("master_awb", "changed_by", "changed_at")
    list_filter = ("changed_at",)
    search_fields = ("master_awb__awb", "master_awb__order_number", "changed_by__username")
    list_select_related = ("master_awb", "changed_by")
    ordering = ("-changed_at",)
    list_per_page = 50


@admin.register(Freight)
class FreightAdmin(admin.ModelAdmin):
    list_display = ("id", "awb_type", "freight_rete", "created_at")
    list_filter = ("awb_type", "created_at")
    search_fields = ("awb_type",)
    ordering = ("-created_at",)
    list_per_page = 50


@admin.register(FreightHistory)
class FreightHistoryAdmin(admin.ModelAdmin):
    list_display = ("freight", "action", "performed_by", "performed_at")
    list_filter = ("action", "performed_at")
    search_fields = ("freight__awb_type", "freight__freight_rete", "performed_by__username")
    list_select_related = ("performed_by",)
    ordering = ("-performed_at",)
    list_per_page = 50
