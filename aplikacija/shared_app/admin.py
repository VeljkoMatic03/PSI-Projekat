#Veljko Matic, Andjela Dimitrijevic
from django.contrib import admin
from .models import (
    MyUser, Student, Tutor, Admin, Applied, Collaboration, Cv,
    Notice, Rating, Request, Tag, Verification
)


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    """Admin prikaz za MyUser model."""
    list_display = ("username", "email", "isactive", "isbanned")
    search_fields = ("username", "email")
    list_filter = ("isactive", "isbanned")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password", "email")}),
        ("Status", {"fields": ("isactive", "isbanned")}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin prikaz za Student model."""
    list_display = ("iduser", "name", "surname", "dateofbirth")
    search_fields = ("name", "surname")
    list_filter = ("dateofbirth",)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    """Admin prikaz za Tutor model."""
    list_display = ("iduser", "name", "surname", "dateofbirth", "isverified")
    search_fields = ("name", "surname")
    list_filter = ("isverified",)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    """Admin prikaz za administratorske naloge."""
    list_display = ("iduser",)
    search_fields = ("iduser__username",)


@admin.register(Applied)
class AppliedAdmin(admin.ModelAdmin):
    """Admin prikaz za Applied model (tagovi za oglase)."""
    list_display = ("idtag", "idnotice")
    search_fields = ("idtag__value", "idnotice__title")


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    """Admin prikaz za Collaboration model (saradnje)."""
    list_display = ("idcollaboration", "idnotice", "idstudent", "idtutor", "datebegin", "dateend")
    list_filter = ("datebegin", "dateend")
    search_fields = ("idstudent__name", "idtutor__name")


@admin.register(Cv)
class CvAdmin(admin.ModelAdmin):
    """Admin prikaz za Cv model."""
    list_display = ("idtutor", "name", "surname", "education")
    search_fields = ("name", "surname", "education", "projects")
    list_filter = ("education",)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """Admin prikaz za Notice model (oglase)."""
    list_display = ("idnotice", "title", "subject", "type", "idpublisher", "idtutor")
    search_fields = ("title", "subject", "description")
    list_filter = ("type",)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin prikaz za Rating model (ocene)."""
    list_display = ("idrating", "value", "idratinguser", "idrateduser", "idcollaboration")
    list_filter = ("value",)
    search_fields = ("comment", "idratinguser__username", "idrateduser__username")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    """Admin prikaz za Request model (zahtevi tutora za oglase)."""
    list_display = ("idrequest", "idnotice", "idtutor", "isaccepted")
    list_filter = ("isaccepted",)
    search_fields = ("idnotice__title", "idtutor__name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin prikaz za Tag model."""
    list_display = ("idtag", "value")
    search_fields = ("value",)


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    """Admin prikaz za Verification model (verifikacija tutora)."""
    list_display = ("idver", "iduser")
    search_fields = ("iduser__name",)

