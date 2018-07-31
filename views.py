from django.http import HttpResponse
from django.http import Http404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from datetime import timedelta

from .models import ServerEntry

# Hello, this is where all the fun stuff happens in the server list.
# I hope it's straightforward to understand



# This page lists all active Sanicball servers
# It is not meant to be viewed in a browser!
# The game will parse this list and display all servers in the pretty ingame UI instead.
def list(request):
    # Old servers are auto purged whenever anyone wants to list game servers
    cur_time = timezone.now()
    min_time = cur_time - timedelta(minutes=15)
    ServerEntry.objects.filter(last_ping__lt=min_time).delete()

    # Display 1 server per line in plain text, with IP and port seperated by a colon
    text = ""
    for server in ServerEntry.objects.all():
        text += server.ip + ":" + str(server.port) + "<br>"
    return HttpResponse(text)


# This page is used by the SanicballServer application
# to register a server and let any player join it
@csrf_exempt
def add(request):
    if (request.method == "POST"):
        ip = request.POST.get("ip", False)
        port = request.POST.get("port", False)

        if ip and port: 
            try:
                # If this exact server already exists, update its ping time instead to keep it from being purged
                existing_entry = ServerEntry.objects.get(ip=ip, port=port)
                existing_entry.last_ping=timezone.now()
                existing_entry.save()
            except ServerEntry.DoesNotExist:
                if (ServerEntry.objects.count() < 420):
                    # Still below max servers - add this server to the list
                    entry = ServerEntry(ip=ip, port=port, last_ping=timezone.now())
                    entry.save()
                else:
                    # Max servers is just a random number, and only serves to limit abuse of the list. Feel free to change or remove it
                    return HttpResponse("Too many servers.")
            return HttpResponse("Your server has been registered.")
        else:
            return HttpResponse("Invalid arguments.")

    # Display a 404 error if there is no POST data - makes it slightly less easy to add fake servers
    # Of course any competent hacker could still mess up the list
    # However, only servers that can be properly pinged show up in-game anyway, so fake servers will most likely not be an issue
    raise Http404()
