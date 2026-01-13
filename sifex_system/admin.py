from django.contrib import admin
from sifex_system.models import *


@admin.register(Masterawb)
class MasterawbAdmin(admin.ModelAdmin):
    search_fields = (
        "awb",
        "order_number",
        "sender_name",
        "sender_address",
        "sender_tel",
        "sender_city",
        "sender_country",
        "receiver_name",
        "receiver_address",
        "receiver_tel",
        "receiver_city",
        "receiver_country",
        "awb_type",
        "payment_mode",
    )
    list_display = (
        "awb",
        "order_number",
        "receiver_name",
        "sender_name",
        "awb_pcs",
        "awb_kg",
        "awb_type",
        "payment_mode",
        "date_received",
        "deleted",
    )
    list_filter = (
        "awb_type",
        "payment_mode",
        "currency",
        "deleted",
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
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "customer",
        "customer_email",
        "customer_phone",
        "awb__awb",
        "awb__order_number",
        "invoces_line__tracking_key",
        "status",
        "invoice_detail",
    )
    list_select_related = ("awb",)
    list_display = (
        "id",
        "awb_number",
        "tracking_keys",
        "customer",
        "status",
        "total_amount_usd",
        "total_amount_tzs",
        "date",
        "due_date",
        "deleted",
    )
    list_filter = (
        "status",
        "invoice_detail",
        "date",
        "deleted",
    )
    list_select_related = ("awb",)
    actions = ("link_awb_by_tracking_key",)

    def awb_number(self, obj):
        return obj.awb.awb if obj.awb else "-"

    awb_number.short_description = "AWB"

    def tracking_keys(self, obj):
        return ", ".join(
            obj.invoces_line.values_list("tracking_key", flat=True)
        )

    tracking_keys.short_description = "Tracking Keys"

    def link_awb_by_tracking_key(self, request, queryset):
        linked = 0
        skipped = 0
        for invoice in queryset:
            if invoice.awb_id:
                skipped += 1
                continue
            tracking_keys = list(
                invoice.invoces_line.values_list("tracking_key", flat=True)
            )
            if not tracking_keys:
                skipped += 1
                continue
            matches = Masterawb.objects.filter(awb__in=tracking_keys).distinct()
            if matches.count() == 1:
                invoice.awb = matches.first()
                invoice.save(update_fields=["awb"])
                linked += 1
            else:
                skipped += 1
        self.message_user(
            request,
            f"Linked {linked} invoice(s). Skipped {skipped} invoice(s) with no "
            "tracking key, existing AWB, or ambiguous matches."
        )

    link_awb_by_tracking_key.short_description = "Link AWB from tracking key"


@admin.register(MasterStatus)
class MasterStatusAdmin(admin.ModelAdmin):
    search_fields = (
        "master__awb",
        "master__order_number",
        "status",
        "terminal",
        "delivered_to",
    )
    list_display = (
        "master",
        "status",
        "terminal",
        "delivered_to",
        "date",
        "time",
        "user",
    )
    list_filter = ("status", "terminal", "date")


@admin.register(AwbHistory)
class AwbHistoryAdmin(admin.ModelAdmin):
    search_fields = (
        "master_awb__awb",
        "master_awb__order_number",
        "change_summary",
        "remark",
        "changed_by__username",
    )
    list_display = (
        "master_awb",
        "changed_by",
        "changed_at",
        "change_summary",
    )
    list_filter = ("changed_at", "changed_by")


@admin.register(InvoiceHistory)
class InvoiceHistoryAdmin(admin.ModelAdmin):
    search_fields = (
        "invoice_id",
        "awb",
        "customer",
        "status",
    )
    list_display = (
        "invoice_id",
        "awb",
        "customer",
        "status",
        "total_amount_tzs",
    )
    list_filter = ("status",)


admin.site.register(Slaveawb)
admin.site.register(SlaveStatus)
admin.site.register(Quote)
admin.site.register(LineItem)
admin.site.register(SystemPreference)
admin.site.register(Staff)
admin.site.register(AwbLocation)
admin.site.register(Attendance)
admin.site.register(ActivityLog)
admin.site.register(Freight)
admin.site.register(FreightHistory)
