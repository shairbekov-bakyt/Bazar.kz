import json

from user.utils import Util
from datetime import datetime

from advert.utils import connect_to_redis
from advert.models import Advert


def send_advert_to_email(emails):
    absurl = [
        "http://" + f"127.0.0.1:800/api/v1/advert/{i}"
        for i in Advert.objects.filter(status="act")
        .order_by("-created_date")
        .values_list("id", flat=True)[:11]
    ]
    urls = "\n".join(absurl)
    email_body = f"Hi username in Zeon Mall new advert link below\n{urls}"
    data = {
        "email_body": email_body,
        "email_subject": f"News Advert",
        "to_whom": emails,
    }
    Util.send_email(data)


def set_advert_count(id: int, user, ip):
    view = connect_to_redis()
    format = "%Y-%m-%d, %H:%M"
    date = str(datetime.now().strftime(format))

    view_info = {"ip": [], "user": [], "views_counter": 0, "last_view": {}}
    if not view.exists(id):
        view.set(id, json.dumps(view_info))

    advert_views = json.loads(view.get(id).decode("utf-8"))
    ad = Advert.objects.get(id=id)

    if user == "AnonymousUser":
        if ip not in advert_views["ip"]:
            advert_views["views_counter"] += 1
            advert_views["ip"] += [ip]
            advert_views["last_view"][f"{user}-{ip}"] = date

        else:
            user_last_view = advert_views["last_view"][f"{user}-{ip}"]
            if dates_difference(user_last_view, format) > 1:
                advert_views["views_counter"] += 1
                advert_views["last_view"][f"{user}-{ip}"] = datetime.now()

    elif user not in advert_views["user"]:
        advert_views["views_counter"] += 1
        advert_views["user"] += [user]
        advert_views["last_view"][f"{user}"] = date

    else:
        user_last_view = advert_views["last_view"][f"{user}"]
        if dates_difference(user_last_view, format) > 1:
            advert_views["views_counter"] += 1
            advert_views["last_view"][f"{user}"] = datetime.now()

    ad.views = advert_views["views_counter"]
    view.set(id, json.dumps(advert_views))


def set_advert_contacts_count(id: int, user, ip):
    view = connect_to_redis()
    format = "%Y-%m-%d, %H:%M"
    date = str(datetime.now().strftime(format))
    key = f"{id}-contacts"

    view_info = {"ip": [], "user": [], "views_counter": 0, "last_view": {}}
    if not view.exists(key):
        view.set(key, json.dumps(view_info))

    contacts_views = json.loads(view.get(key).decode("utf-8"))

    if user == "AnonymousUser":
        if ip not in contacts_views["ip"]:
            contacts_views["views_counter"] += 1
            contacts_views["ip"] += [ip]
            contacts_views["last_view"][f"{user}-{ip}"] = date

        else:
            user_last_view = contacts_views["last_view"][f"{user}-{ip}"]
            if dates_difference(user_last_view, format) > 1:
                contacts_views["views_counter"] += 1
                contacts_views["last_view"][f"{user}-{ip}"] = datetime.now()

    elif user not in contacts_views["user"]:
        contacts_views["views_counter"] += 1
        contacts_views["user"] += [user]
        contacts_views["last_view"][f"{user}"] = date

    else:
        user_last_view = contacts_views["last_view"][f"{user}"]
        if dates_difference(user_last_view, format) > 1:
            contacts_views["views_counter"] += 1
            contacts_views["last_view"][f"{user}"] = datetime.now()
    view.set(id, json.dumps(contacts_views))


def dates_difference(date, format):
    now = datetime.now()
    dt_object = datetime.strptime(str(date).replace("b", "").replace("'", ""), format)
    diff = now - dt_object

    return diff.days


def set_advert_views(id: int):
    view = connect_to_redis()

    if not view.exists(id):
        return 0

    advert_info = json.loads(view.get(id).decode("utf-8"))
    views_count = advert_info["views_counter"]

    return views_count
