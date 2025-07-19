from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'registration_number',
        'engine_number',
        'chassis_number',
        'insurance_expiry_date',
        'tax_expiry_date',
        'permit_expiry_date',
        'fitness_expiry_date',
        'puc_expiry_date'
    )
    search_fields = ('registration_number', 'engine_number', 'chassis_number')
