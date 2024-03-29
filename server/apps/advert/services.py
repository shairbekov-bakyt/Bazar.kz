import json

from rest_framework import serializers
from phonenumber_field.validators import validate_international_phonenumber
from user.utils import Util
from datetime import datetime

from advert.utils import connect_to_redis
from advert.models import Advert, AdvertImage, AdvertContact


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


def set_views(ad_id: int, user, ip, view_type):
    view = connect_to_redis()
    date_format = "%Y-%m-%d, %H:%M"
    date = str(datetime.now().strftime(date_format))
    key = ad_id
    if view_type == "contacts":
        key = f"{ad_id}-contacts"

    view_info = {"ip": [], "user": [], "views_counter": 0, "last_view": {}}
    if not view.exists(key):
        view.set(key, json.dumps(view_info))

    object_views = json.loads(view.get(key).decode("utf-8"))

    if user == "AnonymousUser":
        if ip not in object_views["ip"]:
            object_views["views_counter"] += 1
            object_views["ip"] += [ip]
            object_views["last_view"][f"{user}-{ip}"] = date

        else:
            user_last_view = object_views["last_view"][f"{user}-{ip}"]
            if dates_difference(user_last_view, date_format) > 1:
                object_views["views_counter"] += 1
                object_views["last_view"][f"{user}-{ip}"] = datetime.now()

    elif user not in object_views["user"]:
        object_views["views_counter"] += 1
        object_views["user"] += [user]
        object_views["last_view"][f"{user}"] = date

    else:
        user_last_view = object_views["last_view"][f"{user}"]
        if dates_difference(user_last_view, date_format) > 1:
            object_views["views_counter"] += 1
            object_views["last_view"][f"{user}"] = datetime.now()
    if view_type == "adverts":
        ad = Advert.objects.get(id=ad_id)
        ad.views = object_views["views_counter"]
        ad.save()

    view.set(key, json.dumps(object_views))


def dates_difference(date, date_format):
    now = datetime.now()
    dt_object = datetime.strptime(str(date).replace("b", "").replace("'", ""), date_format)
    diff = now - dt_object

    return diff.days


def create_ad_imgs(advert, imgs):
    if len(imgs) > 8:
        raise serializers.ValidationError("Максимальное кол-во изображений: 8")

    img_objects = []
    for img in imgs:
        img_objects.append(AdvertImage(advert=advert, image=img))
    AdvertImage.objects.bulk_create(img_objects)


def create_ad_contacts(advert, contacts):
    if len(contacts) > 8:
        raise serializers.ValidationError("Максимальное кол-во контактов: 8")

    ad_contacts = []
    for contact in contacts[0].split(','):
        validate_international_phonenumber(contact)
        ad_contacts.append(AdvertContact(advert=advert, phone_number=contact))

    AdvertContact.objects.bulk_create(ad_contacts)


def delete_ad_imgs(advert):
    images = AdvertImage.objects.filter(advert=advert)
    for image in images:
        image.delete()


def delete_ad_contacts(advert):
    contacts = AdvertContact.objects.filter(advert=advert)
    for contact in contacts:
        contact.delete()
