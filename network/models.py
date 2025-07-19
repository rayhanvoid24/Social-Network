from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Newpost(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    caption= models.TextField()
    time= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"post {self.id} by {self.user.username}"
    
class Comment(models.Model):
   user= models.ForeignKey(User, on_delete=models.CASCADE)
   post= models.ForeignKey(Newpost, on_delete=models.CASCADE)
   comment = models.CharField(max_length= 200)

   def __str__(self):
        return f" {self.comment} by {self.user.username}"


class Following(models.Model):
     Sender= models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'sent_request', blank= True, null= True)
     Reciever= models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'recieved_request', blank= True, null= True)
     status_choices = [
         ('pending', 'pending'),
         ('accepted', 'accepted'),
         ('rejected', 'rejected')

     ]
     status= models.CharField(max_length= 20, choices= status_choices, default= 'pending',blank= True, null= True)
     timestamp= models.DateField(auto_now_add=True,blank= True, null= True)
     
def __str__(self):
    return self.user.username




class Notification(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    message= models.TextField()
    read= models.BooleanField(default= False)
    timestamp= models.DateField(auto_now_add= True)