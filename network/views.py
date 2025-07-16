from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse


from .models import User, Newpost,Comment,Following,Notification





def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
# Function for creating a new post
@login_required
def create_post(request):
    if request.method == "POST":
         # Create the post with the current user and caption
        create_post= Newpost (
            user= request.user,
            caption= request.POST.get("caption")
        )
        create_post.save()
        return redirect("index") # Go back to the main page

      # Show the post creation form
    return render(request, "network/create.html")

  # The homepage showing all posts except the current user's  
@login_required
def index(request):
    all_post = Newpost.objects.exclude(user=request.user).order_by('-time')
    paginator = Paginator(all_post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    ## handles the process of allowing the user to comment
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = Newpost.objects.get(pk=post_id)
        Comment.objects.create(
            comment=request.POST.get("comment"),
            post=post,
            user=request.user
        )
        return redirect("index")  # prevent resubmission

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


@login_required
def profile(request,username):
    ##allows user A to view user B's profile
    profile_user = User.objects.get(username=username)
    user_related_post = Newpost.objects.filter(user=profile_user)

    follow_obj = Following.objects.filter(
        Sender=request.user,
        Reciever=profile_user
    ).first()

    follow_status = follow_obj.status if follow_obj else "follow"

    # Only count accepted followers
    followers_count = Following.objects.filter(
        Reciever=profile_user,
        status="accepted"
    ).count()

    following_count = Following.objects.filter(
        Sender=profile_user,
        status="accepted"
    ).count()

    # Get pending requests and unread notifications for own profile
    pending_requests = []
    notifications = []
    if request.user == profile_user:
        pending_requests = Following.objects.filter(Reciever=request.user, status="pending")
        notifications = Notification.objects.filter(user=request.user, read=False)

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "post": user_related_post,
        "follow_status": follow_status,
        "followers": followers_count,
        "following": following_count,
        "pending_requests": pending_requests,
        "notifications": notifications,
        "is_own_profile": request.user == profile_user })



## a function that handles following

@csrf_exempt
@login_required
def follow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")
    # These actions require a user_id
        if action in ["send", "accept", "reject"]:
            user_id = data.get("user_id")
            try:
                receiver = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return JsonResponse({ "error": "User not found." }, status=404)
              # Don't let users follow themselves
            if receiver == request.user:
                return JsonResponse({"error": "You cannot follow yourself"}, status=400)

             # Check if a follow relationship already exists
            follow_obj = Following.objects.filter(Sender=request.user, Reciever=receiver).first()

            if action == "send":
                if follow_obj:
                    follow_obj.delete()
                    return JsonResponse({"status": "follow"})
                else:
                    Following.objects.create(Sender=request.user, Reciever=receiver, status="pending")
                    Notification.objects.create(user=receiver, message=f"{request.user.username} sent you a follow request")
                    return JsonResponse({"status": "pending"})

            elif action == "accept":
                pending_request = Following.objects.filter(Sender=receiver, Reciever=request.user, status="pending").first()
                if pending_request:
                    pending_request.status = "accepted"
                    pending_request.save()
                    return JsonResponse({"status": "accepted"})

            elif action == "reject":
                pending_request = Following.objects.filter(Sender=receiver, Reciever=request.user, status="pending").first()
                if pending_request:
                    pending_request.status = "rejected"
                    pending_request.save()
                    return JsonResponse({"status": "rejected"})

        elif action == "clear_notification":
            notif_id = data.get("notif_id")
            notif = Notification.objects.filter(id=notif_id, user=request.user).first()
            if notif:
                notif.read = True
                notif.save()
                return JsonResponse({"status": "cleared"})
            else:
                return JsonResponse({"error": "Notification not found"}, status=404)

    return JsonResponse({"error": "POST required"}, status=400)