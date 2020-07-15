from django.db import models


# Create your models here.
# PARAMETRES
class PARAMETERS(models.Model):
    id=models.UUIDField
    label= models.CharField(max_length=100)
    value= models.CharField(max_length=100)
    def __str__(self):
        return self.label

# LES DIFFERENTS COMPTES
class USER(models.Model):
    id= models.UUIDField
    firstname= models.CharField(max_length=100)
    lastname= models.CharField(max_length=50)
    username= models.CharField(max_length=20)
    password= models.CharField(max_length=20)
    email= models.CharField
    def __str__(self):
        return self.username

class ADMIN (models.Model):
    user_admin = models.ForeignKey(USER, on_delete=models.CASCADE)

class ACCOUNT(models.Model):
    user_account = models.ForeignKey(USER, on_delete=models.CASCADE)


# LES AUTRES TABLES
class SERVICE_CATEGORIE(models.Model):
    id = models.UUIDField
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    def __str__(self):
        return self.label

class SERVICE(models.Model):
    id = models.UUIDField
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=500)
    keywords = models.CharField(max_length=10)
    stars = models.IntegerField
    delay = models.IntegerField
    categorie = models.ForeignKey(SERVICE_CATEGORIE, on_delete=models.CASCADE)
    person = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class SERVICE_MEDIAS(models.Model):
    id = models.UUIDField
    url = models.URLField
    file = models.FileField
    service= models.ForeignKey(SERVICE, on_delete=models.CASCADE)

class COMMENTS(models.Model):
    id = models.UUIDField
    content = models.CharField(max_length=500)
    positive = models.BooleanField
    service = models.ForeignKey(SERVICE, on_delete=models.CASCADE)
    person = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)

class SERVICE_OPTIONS(models.Model):
    id = models.UUIDField
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    delay = models.IntegerField
    service = models.ForeignKey(SERVICE, on_delete=models.CASCADE)
    def __str__(self):
        return self.label

class SELLER_PURCHASE(models.Model):
    id= models.UUIDField
    delay= models.IntegerField
    accepted = models.BooleanField
    delivered = models.BooleanField
    approuved = models.BooleanField
    seller=models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)
    service = models.ForeignKey(SERVICE, on_delete=models.CASCADE)


class SELLER_PURCHASE_SERVICE_OPTIONS(models.Model):
    id= models.UUIDField
    service = models.ForeignKey(SERVICE_OPTIONS, on_delete=models.CASCADE)
    purchase = models.ForeignKey(SELLER_PURCHASE, on_delete=models.CASCADE)

class CHATS(models.Model):
    id = models.UUIDField
    content= models.CharField
    purchase = models.ForeignKey(SELLER_PURCHASE, on_delete=models.CASCADE)
    person = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)

class LITIGATION(models.Model):
    id = models.UUIDField
    title= models.CharField(max_length=100)
    description= models.CharField(max_length=500)
    handled= models.BooleanField
    admin=models.ForeignKey(ADMIN, on_delete=models.CASCADE)
    person = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)
    purchase = models.ForeignKey(SELLER_PURCHASE, on_delete=models.CASCADE)
    def __str__(self):
        return self.title







