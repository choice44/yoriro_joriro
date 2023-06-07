from django.contrib import admin
from recruitments.models import Recruitments, Applicant, Participant


admin.site.register(Recruitments)
admin.site.register(Applicant)
admin.site.register(Participant)