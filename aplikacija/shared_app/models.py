from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MyUser(models.Model):
    """
    Model koji predstavlja korisnika aplikacije.

    Sadrži osnovne informacije o korisniku, uključujući korisničko ime, lozinku,
    email adresu i status naloga (aktivnost i zabranu).
    Model je povezan sa postojećom tabelom 'user' u bazi podataka.
    """
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
    """
    Model koji predstavlja studenta u aplikaciji.

    Povezan je jedan-prema-jedan sa modelom MyUser i sadrži osnovne
    informacije o studentu, uključujući ime, prezime i datum rođenja.
    Model koristi postojeću tabelu 'student' u bazi.
    """
    iduser = models.OneToOneField(MyUser, on_delete=models.CASCADE, db_column='idUser', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45)
    dateofbirth = models.DateField(db_column='dateOfBirth', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'student'

class Tutor(models.Model):
    """
    Model koji predstavlja tutora u aplikaciji.

    Povezan je jedan-prema-jedan sa modelom MyUser i sadrži osnovne
    informacije o tutoru, uključujući ime, prezime, datum rođenja i status verifikacije.
    Model koristi postojeću tabelu 'tutor' u bazi.
    """
    iduser = models.OneToOneField(MyUser, on_delete=models.CASCADE, db_column='idUser', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45)
    dateofbirth = models.DateField(db_column='dateOfBirth', blank=True, null=True)  # Field name made lowercase.
    isverified = models.IntegerField(db_column='isVerified')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tutor'


class Admin(models.Model):
    """
    Model koji predstavlja administratorski nalog u aplikaciji.

    Povezan je jedan-prema-jedan sa modelom MyUser i koristi postojeću
    tabelu 'admin' u bazi podataka.
    """
    iduser = models.OneToOneField(MyUser, models.CASCADE, db_column='idUser', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'admin'


class Applied(models.Model):
    """
    Model koji povezuje tag sa oglasom.

    Svaki zapis označava da određeni tag pripada određenom oglasu.
    Model koristi postojeću tabelu 'applied' u bazi.
    """
    idtag = models.ForeignKey('Tag', models.CASCADE, db_column='idTag')  # Field name made lowercase.
    idnotice = models.ForeignKey('Notice', models.CASCADE, db_column='idNotice')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'applied'


class Collaboration(models.Model):
    """
    Model koji predstavlja saradnju između studenta i tutora na određenom oglasu.

    Svaki zapis povezuje jednog studenta i jednog tutora sa određenim oglasom (Notice)
    i beleži period trajanja saradnje. Model koristi postojeću tabelu 'collaboration'
    u bazi.
    """
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
    """
    Model koji predstavlja CV (biografiju) tutora.

    Svaki tutor može imati jedan CV koji sadrži lične podatke, obrazovanje,
    projekte i iskustvo. Model koristi postojeću tabelu 'cv' u bazi.
    """
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
    """
    Model koji predstavlja oglas (Notice) unutar aplikacije.

    Svaki oglas objavljuje student i može biti povezan sa tutorom.
    Oglas sadrži osnovne informacije poput naslova, predmeta, tipa,
    opisa i eventualnog priloga. Model koristi postojeću tabelu 'notice'
    u bazi.
    """
    idnotice = models.AutoField(db_column='idNotice', primary_key=True)  # Field name made lowercase.
    idpublisher = models.ForeignKey('Student', models.DO_NOTHING, db_column='idPublisher')  # Field name made lowercase.
    title = models.CharField(max_length=45)
    subject = models.CharField(max_length=45)
    type = models.CharField(max_length=45)
    description = models.TextField(blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)
    idtutor = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='idTutor', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notice'


class Rating(models.Model):
    """
    Model koji predstavlja ocenu (rating) u aplikaciji.

    Svaki zapis povezuje korisnika koji ocenjuje sa korisnikom koji je ocenjen,
    zajedno sa vrednošću ocene, eventualnim komentarom i povezivanjem na saradnju
    (Collaboration) na kojoj se ocena zasniva. Model koristi postojeću tabelu
    'rating' u bazi.
    """
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
    """
    Model koji predstavlja zahtev tutora za određeni oglas (Notice).

    Svaki zapis povezuje tutora sa oglasom i prati status zahteva.
    Model koristi postojeću tabelu 'request' u bazi.
    """
    idrequest = models.AutoField(db_column='idRequest', primary_key=True)  # Field name made lowercase.
    idnotice = models.ForeignKey(Notice, models.CASCADE, db_column='idNotice')  # Field name made lowercase.
    idtutor = models.ForeignKey(Tutor, models.CASCADE, db_column='idTutor', db_comment="isAccepted possible values - 'P' as in 'Pending', 'A' as in 'Accepted', 'R' as in 'Rejected'")  # Field name made lowercase.
    isaccepted = models.CharField(db_column='isAccepted', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'request'


class Tag(models.Model):
    """
    Model koji predstavlja tag ili kategoriju koja se dodaje na oglas radi lakšeg pretraživanja.

    Svaki tag omogućava kategorizaciju i filtriranje oglasa u aplikaciji.
    Model koristi postojeću tabelu 'tag' u bazi.
    """
    idtag = models.AutoField(db_column='idTag', primary_key=True)  # Field name made lowercase.
    value = models.CharField(unique=True, max_length=45)

    class Meta:
        managed = False
        db_table = 'tag'

class Verification(models.Model):
    """
    Model koji predstavlja verifikaciju tutora u aplikaciji.

    Svaki tutor može imati jedan zapis u ovoj tabeli koji označava
    da je njegov nalog verifikovan. Model koristi postojeću tabelu
    'verification' u bazi.
    """
    idver = models.AutoField(db_column='idVer', primary_key=True)  # Field name made lowercase.
    iduser = models.OneToOneField(Tutor, models.CASCADE, db_column='idUser')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'verification'
