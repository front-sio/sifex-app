from django.contrib import admin
from sifex_system.models import *

admin.site.register(Masterawb)
admin.site.register(Slaveawb)
admin.site.register(MasterStatus)
admin.site.register(SlaveStatus)
admin.site.register(Quote)
admin.site.register(Invoice)
admin.site.register(LineItem)
admin.site.register(SystemPreference)
admin.site.register(Staff)
admin.site.register(AwbLocation)
admin.site.register(Attendance)
admin.site.register(ActivityLog)
admin.site.register(AwbHistory)
admin.site.register(InvoiceHistory)
admin.site.register(Freight)
admin.site.register(FreightHistory)

