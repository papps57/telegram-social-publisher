import json
import requests
from config import FB_BASE_URL


def _catbox_upload(filepath):
    with open(filepath, "rb") as f:
        resp = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
        )
    url = resp.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Upload image hosting fallito: {url}")
    return url


def _upload_photo(page_id, token, image_path):
    url = f"{FB_BASE_URL}/{page_id}/photos"
    with open(image_path, "rb") as f:
        resp = requests.post(
            url,
            params={"access_token": token, "published": "false"},
            files={"source": f},
        )
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Upload foto FB fallito: {data}")
    return data["id"]


def post_to_facebook(page_id, token, message, image_paths):
    photo_ids = [_upload_photo(page_id, token, p) for p in image_paths]
    attached_media = json.dumps([{"media_fbid": fid} for fid in photo_ids])

    url = f"{FB_BASE_URL}/{page_id}/feed"
    params = {
        "access_token": token,
        "message": message,
        "attached_media": attached_media,
    }
    resp = requests.post(url, params=params)
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Post FB fallito: {data}")
    post_id = data["id"]
    permalink = f"https://facebook.com/{post_id.replace('_', '/posts/')}"
    return {"id": post_id, "url": permalink}


def _ig_create_media(ig_id, token, image_url, caption, is_carousel=False):
    params = {"access_token": token, "image_url": image_url}
    if is_carousel:
        params["is_carousel_item"] = "true"
    else:
        params["caption"] = caption
    url = f"{FB_BASE_URL}/{ig_id}/media"
    resp = requests.post(url, params=params)
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Creazione media IG fallita: {data}")
    return data["id"]


def _ig_create_carousel(ig_id, token, caption, children_ids):
    url = f"{FB_BASE_URL}/{ig_id}/media"
    params = {
        "access_token": token,
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
    }
    resp = requests.post(url, params=params)
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Creazione carosello IG fallita: {data}")
    return data["id"]


def _ig_publish(ig_id, token, creation_id):
    url = f"{FB_BASE_URL}/{ig_id}/media_publish"
    params = {"access_token": token, "creation_id": creation_id}
    resp = requests.post(url, params=params)
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Pubblicazione IG fallita: {data}")
    return data["id"]


def post_to_instagram(ig_id, token, message, image_paths):
    if not image_paths:
        raise ValueError("Instagram richiede almeno un'immagine")

    public_urls = [_catbox_upload(p) for p in image_paths]

    if len(public_urls) == 1:
        creation_id = _ig_create_media(ig_id, token, public_urls[0], message)
    else:
        children = [
            _ig_create_media(ig_id, token, url, "", is_carousel=True)
            for url in public_urls
        ]
        creation_id = _ig_create_carousel(ig_id, token, message, children)

    media_id = _ig_publish(ig_id, token, creation_id)
    permalink = f"https://instagram.com/p/{media_id}"
    return {"id": media_id, "url": permalink}


def publish_all(page_config, message, image_paths):
    fb_result = post_to_facebook(
        page_config["id"], page_config["token"], message, image_paths
    )
    ig_result = post_to_instagram(
        page_config["ig_id"], page_config["token"], message, image_paths
    )
    return {"facebook": fb_result, "instagram": ig_result}
