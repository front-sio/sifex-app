from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

# Constants for choices
COURIER_STATUS_CHOICES = (
    ("ACCEPTED", "accepted"),
    ("LOADED", "loaded"),
    ("MANIFATED", "manifested"),
    ("RCS - recieved from shipper", "RCS recieved from shipper"),
    ("OFFLOADED", "offloaded"),
    ("DEPARTED", "departed"),
    ("ON TRANSIT", "on transit"),
    ("ARRIVED", "arrived"),
    ("UNDER CLEARANCE", "under clearance"),
    ("DELIVERED", "delivered"),
)

TYPE_CHOICES = (
    ("CAN - Guanzhou", "CAN - Guanzhou"),
    ("HKG - HongKong", "HKG - HongKong"),
    ("DXB - Dubai", "DXB - Dubai"),
    ("CAN - Express", "CAN - Express"),
    ("MCO - Express", "MCO - Express"),
)

STATION_CHOICES = (
    ('CAN - Guanzhou', 'CAN - Guanzhou'),
    ('HKG - HongKong', 'HKG - HongKong'),
    ('DAR - Dar es salaam', 'DAR - Dar es salaam'),
    ('DXB - Dubai', 'DXB - Dubai'),
    ('NBO - Nairobi', 'NBO - Nairobi'),
    ('SHJ - Sharjah', 'SHJ - Sharjah'),
    ('JNB - Johanesburg', 'JNB - Johanesburg'),
    ('MCT - Muscat', 'MCT - Muscat'),
    ('BOM - Mumbai', 'BOM - Mumbai'),
    ('ADD - Addis Ababa', 'ADD - Addis Ababa'),
    ('ZNZ - Zanzibar', 'ZNZ - Zanzibar'),
    
)



class ActivityLog(models.Model):
    # Constants for activity types
    ACTIVITY_TYPES = (
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} {self.description} at {self.timestamp}'

class Masterawb(models.Model):
    PAYMENT_MODE = (
        ('PP', 'pp'),
        ('CC', 'cc'),
    )
    awb = models.CharField(max_length=255, blank=True)
    order_number = models.CharField(max_length=255, null=True, blank=True)
    sender_name = models.CharField(max_length=255, blank=True)
    sender_address = models.CharField(max_length=255, blank=True)
    sender_company = models.CharField(max_length=255, blank=True)
    sender_tel = models.CharField(max_length=255, blank=True)
    sender_city = models.CharField(max_length=255, blank=True)
    sender_country = models.CharField(max_length=255, blank=True)
    receiver_name = models.CharField(max_length=255, blank=True)
    receiver_address = models.CharField(max_length=255, blank=True)
    receiver_company = models.CharField(max_length=255, blank=True)
    receiver_tel = models.CharField(max_length=255, blank=True)
    receiver_city = models.CharField(max_length=255, blank=True)
    receiver_country = models.CharField(max_length=255, blank=True)
    desc = models.CharField(max_length=255, blank=True)
    freight = models.CharField(max_length=255, blank=True)
    freight_rate = models.CharField(max_length=255, blank=True)
    insurance = models.CharField(max_length=255, blank=True)
    awb_pcs = models.CharField(max_length=255, blank=True)
    awb_kg = models.FloatField(blank=True)
    arr_pcs = models.CharField(max_length=255, null=True, blank=True)
    number_of_parcel = models.CharField(max_length=255, null=True, blank=True)
    parcel_kg = models.FloatField(null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    arr_kg = models.FloatField(null=True, blank=True)
    chargable_weight = models.CharField(max_length=255, null=True, blank=True)
    terms = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, blank=True)
    expected_arrival_date = models.DateTimeField(null=True, blank=True)
    date_received = models.DateTimeField(null=True, blank=True)
    custom_value = models.CharField(max_length=255, blank=True)
    payment_mode = models.CharField(max_length=255, null=True)
    awb_type = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True)
    dlv_pcs = models.CharField(max_length=255, null=True, blank=True)
    dlv_kg = models.FloatField(null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    width = models.CharField(max_length=255, null=True, blank=True)
    length = models.CharField(max_length=255, null=True, blank=True)
    accepted = models.BooleanField(default=True)
    loaded = models.BooleanField(default=False)
    manifested = models.BooleanField(default=False)
    departed = models.BooleanField(default=False)
    arrived = models.BooleanField(default=False)
    under_clearance = models.BooleanField(default=False)
    released = models.BooleanField(default=False)
    bill = models.BooleanField(default=False)
    invoice_generated = models.BooleanField(default=False)
    billed = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    POD = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuers')

    def __str__(self):
        return f'{self.receiver_name} {self.awb}'



class AwbLocation(models.Model):
    awb = models.ForeignKey(Masterawb, on_delete=models.CASCADE, null=True, blank=True, related_name="awb_locations")
    rack = models.CharField(max_length=255, null=True, blank=True)
    bay = models.CharField(max_length=255, null=True, blank=True)
    pcs = models.CharField(max_length=255, null=True, blank=True)



class Slaveawb(models.Model):
    PAYMENT_MODE = (
        ('PP', 'pp'),
        ('CC', 'cc'),
    )
    master = models.ForeignKey(Masterawb, on_delete=models.CASCADE, null=True, blank=True, related_name="slave_master")
    master_awb = models.CharField(max_length=255, null=True)
    awb = models.CharField(max_length=255, null=True)
    order_number = models.CharField(max_length=255, null=True)
    desc = models.CharField(max_length=255, null=True)
    freight = models.CharField(max_length=255, null=True)
    insurance = models.CharField(max_length=255, null=True)
    awb_pcs = models.CharField(max_length=255, null=True)
    awb_kg = models.FloatField(null=True)
    arr_pcs = models.CharField(max_length=255, null=True, blank=True)
    arr_kg = models.FloatField(null=True, blank=True)
    chargable_weight = models.CharField(max_length=255, null=True, blank=True)
    terms = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True)
    expected_arrival_date = models.DateField(null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    date_received = models.DateTimeField(null=True, blank=True)
    custom_value = models.CharField(max_length=255, null=True)
    payment_mode = models.CharField(max_length=255, null=True, choices=PAYMENT_MODE)
    awb_type = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True)
    dlv_pcs = models.CharField(max_length=255, null=True, blank=True)
    dlv_kg = models.FloatField(null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    width = models.CharField(max_length=255, null=True, blank=True)
    length = models.CharField(max_length=255, null=True, blank=True)
    accepted = models.BooleanField(default=True)
    loaded = models.BooleanField(default=False)
    manifested = models.BooleanField(default=False)
    departed = models.BooleanField(default=False)
    arrived = models.BooleanField(default=False)
    under_clearance = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    released = models.BooleanField(default=False)
    POD = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='slave_issuers')

    def __str__(self):
        return self.desc


class Invoice(models.Model):
    customer = models.CharField(max_length=100)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=100, null=True)
    billing_address = models.TextField(null=True, blank=True)
    awb = models.ForeignKey(Masterawb, null=True, on_delete=models.CASCADE)
    origin = models.CharField(max_length=100, null=True)
    date = models.DateField()
    date_of_payment = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_amount_tzs = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    total_amount_usd = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, default='unpaid')
    invoice_detail = models.CharField(max_length=20, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuer_invoices')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.customer)
    
    def get_status(self):
        return self.status
    
    class Meta:
        ordering = ['-date']  # Order by date descending (latest first)


class LineItem(models.Model):
    customer = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoces_line")
    tracking_key = models.CharField(max_length=255, blank=True)
    service = models.TextField(null=True)
    description = models.TextField()
    quantity = models.IntegerField()
    chargable_weight = models.FloatField(null=True)
    awb_kg = models.FloatField(null=True)
    rate = models.DecimalField(max_digits=20, decimal_places=2)
    amount_tz = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    amount_usd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.customer)


class SlaveStatus(models.Model):
    sub_awb = models.ForeignKey(Slaveawb, on_delete=models.CASCADE, null=True, related_name="slave_status")
    status = models.CharField(verbose_name="status", null=True, max_length=50)
    date = models.DateField(_("Date"), auto_now_add=True, null=True, blank=True)
    time = models.TimeField(_("Time"), auto_now=True, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    terminal = models.CharField(max_length=100, null=True, choices=STATION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuer_slave_histories')


class MasterStatus(models.Model):
    master = models.ForeignKey(Masterawb, on_delete=models.CASCADE, null=True, related_name="master_status")
    status = models.CharField(verbose_name="status", null=True, max_length=50)
    delivered_to = models.CharField(verbose_name="delivered to", null=True, blank=True, max_length=50)
    date = models.DateField(_("Date"), auto_now_add=True, null=True, blank=True)
    time = models.TimeField(_("Time"), auto_now=True, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    terminal = models.CharField(max_length=100, null=True, choices=STATION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuer_parcel_histories')

    def __str__(self):
        return f'{self.master.sender_name} status: {self.status}'


class Quote(models.Model):
    SERVICE_CHOICES = (
        ("air transport", "air transport"),
        ("transport", "transport service"),
        ("warehouse", "Warehouse service"),
    )
    name = models.CharField(_("name"), max_length=50)
    email = models.EmailField(_("email"), max_length=254)
    phone = models.CharField(_("phone"), max_length=254)
    service = models.CharField(verbose_name="choose service", choices=SERVICE_CHOICES, max_length=50)
    massage = models.TextField(verbose_name="your quote massage", null=True)

    class Meta:
        verbose_name = _("Quote")
        verbose_name_plural = _("Quotes")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("quote_detail", kwargs={"pk": self.pk})


class SystemPreference(models.Model):
    rate = models.FloatField(null=True)
    currency = models.CharField(max_length=120, null=True)
    exchange_rate = models.FloatField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuer_preferences')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.rate}'


class Customer(models.Model):
    name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuer_customers')

    def __str__(self):
        return self.name


class Staff(models.Model):
    name = models.CharField(max_length=255, null=True)
    code_number = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    designation = models.CharField(max_length=255, null=True)
    department = models.CharField(max_length=255, null=True)
    company = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='issuer_stafs')

    def __str__(self):
        return self.name


class Attendance(models.Model):
    in_time = models.TimeField(auto_now=True)
    out_time = models.TimeField(null=True)
    date = models.DateField(auto_now=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)

    def __str__(self):
        return self.staff.name





class AwbHistory(models.Model):
    master_awb = models.ForeignKey(Masterawb, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    change_summary = models.TextField(null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Changed by {self.changed_by.username} at {self.changed_at}"





class InvoiceHistory(models.Model):
    invoice_id = models.IntegerField()  # Store the ID of the original invoice
    awb = models.CharField(max_length=255)
    customer = models.CharField(max_length=255)
    pcs = models.IntegerField()
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    origin = models.CharField(max_length=255)
    total_amount_tzs = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    action = models.CharField(max_length=50)  # "edited" or "deleted" or "status changed"
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_id} ({self.action})"






class Freight(models.Model):
    freight_rete = models.CharField(max_length=250, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    awb_type = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f"{self.awb_type} -> {self.freight_rete} by {self.performed_by.username} at {self.created_at}"




class FreightHistory(models.Model):
    freight = models.ForeignKey(Freight, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=[('deleted', 'Deleted')])
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.freight.freight_rete} - {self.action} by {self.performed_by.username} at {self.performed_at}"




