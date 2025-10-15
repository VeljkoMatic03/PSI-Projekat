from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MyUser(models.Model):
    iduser = models.AutoField(db_column='idUser', primary_key=True)  # Field name made lowercase.
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    isbanned = models.IntegerField(db_column='isBanned')  # Field name made lowercase.
    isactive = models.IntegerField(db_column='isActive')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'user'

class Student(models.Model):
    iduser = models.OneToOneField(MyUser, on_delete=models.CASCADE, db_column='idUser', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45)
    dateofbirth = models.DateField(db_column='dateOfBirth', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'student'

class Tutor(models.Model):
    iduser = models.OneToOneField(MyUser, on_delete=models.CASCADE, db_column='idUser', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45)
    dateofbirth = models.DateField(db_column='dateOfBirth', blank=True, null=True)  # Field name made lowercase.
    isverified = models.IntegerField(db_column='isVerified')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tutor'


class Admin(models.Model):
    iduser = models.OneToOneField(MyUser, models.CASCADE, db_column='idUser', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'admin'


class Applied(models.Model):
    pk = models.CompositePrimaryKey('idTag', 'idNotice')
    idtag = models.ForeignKey('Tag', models.CASCADE, db_column='idTag')  # Field name made lowercase.
    idnotice = models.ForeignKey('Notice', models.CASCADE, db_column='idNotice')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'applied'


class Collaboration(models.Model):
    idcollaboration = models.AutoField(db_column='idCollaboration', primary_key=True)  # Field name made lowercase.
    idnotice = models.ForeignKey('Notice', models.CASCADE, db_column='idNotice')  # Field name made lowercase.
    idstudent = models.ForeignKey(Student, models.CASCADE, db_column='idStudent')  # Field name made lowercase.
    idtutor = models.ForeignKey(Tutor, models.CASCADE, db_column='idTutor')  # Field name made lowercase.
    datebegin = models.DateField(db_column='dateBegin')  # Field name made lowercase.
    dateend = models.DateField(db_column='dateEnd', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'collaboration'


class Cv(models.Model):
    idcv = models.AutoField(db_column='idCV', primary_key=True)  # Field name made lowercase.
    idtutor = models.OneToOneField(Tutor, models.CASCADE, db_column='idTutor')  # Field name made lowercase.
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45)
    picture = models.TextField(blank=True, null=True)
    aboutme = models.TextField(db_column='aboutMe', blank=True, null=True)  # Field name made lowercase.
    education = models.TextField()
    projects = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cv'


class Notice(models.Model):
    idnotice = models.AutoField(db_column='idNotice', primary_key=True)  # Field name made lowercase.
    idpublisher = models.ForeignKey(Student, models.CASCADE, db_column='idPublisher')  # Field name made lowercase.
    type = models.CharField(max_length=45)
    description = models.TextField(blank=True, null=True)
    attachment = models.BinaryField(blank=True, null=True)
    idtutor = models.ForeignKey(Tutor, models.CASCADE, db_column='idTutor', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notice'


class Rating(models.Model):
    idrating = models.AutoField(db_column='idRating', primary_key=True)  # Field name made lowercase.
    value = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    idratinguser = models.ForeignKey(MyUser, models.CASCADE, db_column='idRatingUser')  # Field name made lowercase.
    idrateduser = models.ForeignKey(MyUser, models.CASCADE, db_column='idRatedUser', related_name='rating_idrateduser_set')  # Field name made lowercase.
    idcollaboration = models.ForeignKey(Collaboration, models.CASCADE, db_column='idCollaboration')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rating'


class Request(models.Model):
    idrequest = models.AutoField(db_column='idRequest', primary_key=True)  # Field name made lowercase.
    idnotice = models.ForeignKey(Notice, models.CASCADE, db_column='idNotice')  # Field name made lowercase.
    idtutor = models.ForeignKey(Tutor, models.CASCADE, db_column='idTutor', db_comment="isAccepted possible values - 'P' as in 'Pending', 'A' as in 'Accepted', 'R' as in 'Rejected'")  # Field name made lowercase.
    isaccepted = models.CharField(db_column='isAccepted', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'request'


class Tag(models.Model):
    idtag = models.AutoField(db_column='idTag', primary_key=True)  # Field name made lowercase.
    value = models.CharField(unique=True, max_length=45)

    class Meta:
        managed = False
        db_table = 'tag'

class Verification(models.Model):
    idver = models.AutoField(db_column='idVer', primary_key=True)  # Field name made lowercase.
    iduser = models.OneToOneField(Tutor, models.CASCADE, db_column='idUser')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'verification'
