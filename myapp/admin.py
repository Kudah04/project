from django.contrib import admin
from .models import Driver_info
from .models import Images
from .models import UploadedImage

# Register your models here.


admin.site.register(Driver_info),
admin.site.register(Images),
admin.site.register(UploadedImage),
