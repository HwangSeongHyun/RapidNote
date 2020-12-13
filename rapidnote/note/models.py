# Create your models here.
from django.db import models


# Create your models here.
class Member(models.Model):
    member_id = models.CharField(max_length=20, null=False, primary_key=True)
    pw = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=12, null=False)
    email = models.CharField(max_length=30, null=False)

    def __str__(self):
        return self.member_id


class FileSystem(models.Model):
    member_id = models.CharField(max_length=20, null=False)
    fileName = models.CharField(max_length=100, null=False)
    filePath = models.CharField(max_length=300, null=False)
    lastModifiedDate = models.DateTimeField('date published', null=False)

    def __str__(self):
        return str(self.member_id)


class FileList(models.Model):
    member_id = models.CharField(max_length=20, null=False)
    fileName = models.CharField(max_length=500, null=False)
    fileContent = models.CharField(max_length=4000, null=False)

    def __str__(self):
        return str(self.member_id+"/"+self.fileName)


class HashList(models.Model):
    member_id = models.CharField(max_length=20, null=False)
    filePath = models.CharField(max_length=300, null=False)
    fileName = models.CharField(max_length=100, null=False)
    hash = models.CharField(max_length=100, null=False)

    def __str__(self):
        return str(self.hash + ":" + self.member_id + "/" + self.fileName + "/" + self.fileName)