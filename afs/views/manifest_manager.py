import json
import logging
import os
import requests
import shutil
import uuid
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.views.search import search_results

from afs.settings import CANTALOUPE_DIR, CANTALOUPE_HTTP_ENDPOINT, MEDIA_ROOT, MEDIA_URL, APP_ROOT

logger = logging.getLogger(__name__)

class ManifestManagerView(View):
    def post(self, request):
        def create_manifest(name, desc, file_url, canvases):
            attribution = "Provided by The J. Paul Getty Museum"
            logo = "http://www.getty.edu/museum/media/graphics/web/logos/getty.png"

            return  {
                        "@context": "http://iiif.io/api/presentation/2/context.json",
                        "@type": "sc:Manifest",
                        "description": desc,
                        "label": name,
                        "attribution": attribution,
                        "logo": logo,
                        "metadata": [{"label": "TBD", "value": ["Unknown"]}],
                        "thumbnail": {
                            "@id": file_url + "/full/!300,300/0/default.jpg",
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                            "label": "Main VIew (.45v)",
                        },
                        "sequences": [{
                                "@id": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/sequence/TBD.json",
                                "@type": "sc:Sequence",
                                "canvases": canvases,
                                "label": "Object",
                                "startCanvas": "",
                            }],
                    }

        def create_canvas(image_json, file_url, file_name):
            return  {
                        "@id": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/canvas/TBD.json",
                        "@type": "sc:Canvas",
                        "height": image_json["height"],
                        "width": image_json["width"],
                        "images": [
                            {
                                "@id": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/annotation/TBD.json",
                                "@type": "oa.Annotation",
                                "motivation": "unknown",
                                "on": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/canvas/TBD.json",
                                "resource": {
                                    "@id": file_url + "/full/full/0/default.jpg",
                                    "@type": "dctypes:Image",
                                    "format": "image/jpeg",
                                    "height": image_json["height"],
                                    "width": image_json["width"],
                                    "service": {
                                        "@context": "http://iiif.io/api/image/2/context.json",
                                        "@id": file_url,
                                        "profile": "http://iiif.io/api/image/2/level2.json",
                                    },
                                },
                            }
                        ],
                        "label": f"{file_name}",
                        "license": "TBD",
                        "thumbnail": {
                            "@id": file_url + "/full/!300,300/0/default.jpg",
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                            "service": {
                                "@context": "http://iiif.io/api/image/2/context.json",
                                "@id": file_url,
                                "profile": "http://iiif.io/api/image/2/level2.json",
                            },
                        },
                    }

        def delete_manifest(manifest):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            manifest.delete()
            return ""

        def add_canvases(manifest, canvases):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            manifest.manifest['sequences'][0]['canvases'] += canvases
            manifest.save()
            return manifest

        def delete_canvas(manifest, canvases_to_remove):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            canvas_ids_remove = [canvas['images'][0]['resource']['service']['@id'] for canvas in canvases_to_remove]
            canvases = manifest.manifest['sequences'][0]['canvases']
            manifest.manifest['sequences'][0]['canvases'] = [canvas for canvas in canvases if canvas['images'][0]['resource']['service']['@id'] not in canvas_ids_remove]
            manifest.save()
            return manifest

        def create_image(file):
            new_image_id = uuid.uuid4()
            new_image = models.ManifestImage.objects.create(imageid=new_image_id, image=file)
            new_image.save()

            file_name = os.path.basename(new_image.image.name)
            file_url = CANTALOUPE_HTTP_ENDPOINT + "iiif/2/" + file_name
            file_json = file_url + "/info.json"
            image_json = self.fetch(file_json)
            return image_json, file_url

        def get_image_count(manifest):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            return len(manifest.manifest['sequences'][0]['canvases'])

        def change_manifest_info(manifest, name, desc):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            if name != "":
                manifest.label = name
                manifest.manifest["label"] = name
            if desc != "":
                manifest.description = desc
                manifest.manifest["description"] = desc
            manifest.save()
            return manifest

        def change_manifest_metadata(manifest, metadata_dict): # To be fixed
            manifest = models.IIIFManifest.objects.get(url=manifest)
            for k,v in metadata_dict.items():
                manifest.manifest['metadata'].append({'label':k,'value':v})
            manifest.save()
            return manifest

        def change_canvas_label(manifest, canvas_id, label):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            #canvas_id = canvas['images'][0]['resource']['service']['@id']
            canvases = manifest.manifest['sequences'][0]['canvases']
            for canvas in canvases:
                if canvas['images'][0]['resource']['service']['@id'] == canvas_id:
                    canvas['label'] = label
            manifest.save()
            return manifest


        acceptable_types = [
            ".jpg",
            ".jpeg",
            ".tiff",
            ".tif",
            ".png",
        ]

        files = request.FILES.getlist("files")
        name = request.POST.get("manifest_title")
        desc = request.POST.get("manifest_description")
        operation = request.POST.get('operation')
        selected_canvases = json.loads(request.POST.get('selected_canvases'))
        manifest = request.POST.get('manifest')
        canvas_label = request.POST.get('canvas_label')
        canvas_id = request.POST.get('canvas_id')
        metadata_label = request.POST.get('metadata_label')
        metadata_values = request.POST.get('metadata_values')

        if not os.path.exists(CANTALOUPE_DIR):
            os.mkdir(CANTALOUPE_DIR)

        if operation == 'create':
            canvases = []
            for f in files:
                if os.path.splitext(f.name)[1].lower() in acceptable_types:
                    try:
                        image_json, file_url = create_image(f)
                    except:
                        return
                    canvas = create_canvas(image_json, file_url, os.path.splitext(f.name)[0])
                    canvases.append(canvas)
                else:
                    logger.warn("filetype unacceptable: " + f.name)

            pres_dict = create_manifest(name, desc, file_url, canvases)

            # create a manuscript record in the db
            manifest = models.IIIFManifest.objects.create(label=name, description=desc, manifest=pres_dict)
            manifest_id = manifest.id
            json_url = f"/manifest/{manifest_id}"

            pres_dict = create_manifest(name, desc, file_url, canvases)

            manifest.url = json_url
            manifest.save()

            return JSONResponse(manifest)

        if operation == 'delete':
            updated_manifest = delete_manifest(manifest)
            return JSONResponse(updated_manifest)

        if name != "undefined" or desc != "undefined":
            updated_manifest = change_manifest_info(manifest, name, desc)
            # It does not return JSONResponse and then keep going to the next step

        if canvas_label != "undefined":
            updated_manifest = change_canvas_label(manifest, canvas_id, canvas_label)

        if len(selected_canvases) > 0:
            updated_manifest = delete_canvas(manifest, selected_canvases)

        if len(files) > 0:
            try:
                canvases = []
                i = get_image_count(manifest)
                for f in files:
                    if os.path.splitext(f.name)[1].lower() in acceptable_types:
                        try:
                            image_json, file_url = create_image(f)
                        except:
                            return
                        canvas = create_canvas(image_json, file_url, os.path.splitext(f.name)[0])
                        canvases.append(canvas)
                        i += 1
                    else:
                        logger.warn("filetype unacceptable: " + f.name)
                updated_manifest = add_canvases(manifest, canvases)
            except:
                logger.warning("You have to select a manifest to add images")
                return None
        
        if len(metadata_values) > 0 and len(metadata_label) > 0:
            metadata_values_list = metadata_values.split(',')
            metadata_dict = {metadata_label: metadata_values_list}
            updated_manifest = change_manifest_metadata(manifest, metadata_dict)

        return JSONResponse(updated_manifest)

    def fetch(self, url):
        try:
            resp = requests.get(url)
            return resp.json()
        except:
            logger.warn("Manifest not created. Check if Cantaloupe running")
            return None

    def on_import(self, tile):
        raise NotImplementedError

    def after_function_save(self, tile, request):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError
