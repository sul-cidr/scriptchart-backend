""" API endpoint to return all the information necessary to construct the
    script chart.
"""

# pylint: disable=import-error

# drf
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# dash
from scripts.models import Coordinates


@api_view(http_method_names=['GET'])
def get_letters(request):
    """
    Query Params:
        ms_ids (required):     pipe ("|") delimited list of manuscript IDs
        letter_ids (required): pipe ("|") delimited list of letter IDs
        count (optional):      number of examples to return (defaults to 3)

    Reurns:
      {
        "mss" {
          "<ms_id>": {
            "<letter_id>": {
              "id": coords.id,
              "binaryurl": coords.binary_url,
              "height": coords.height,
              "width": coords.width,
              "top": coords.top,
              "left": coords.left,
              "letter": coords.letter.id,
              "page": coords.page.id,
              "pageurl": coords.page.url,
              "pageheight": coords.page.height,
              "pagewidth": coords.page.width,
            },
            ...
          },
          ...
        }
      }
    """

    if 'ms_ids' not in request.query_params:
        return Response(
            {'error': 'No Manuscripts Specified!'},
            status=status.HTTP_400_BAD_REQUEST)

    if 'letter_ids' not in request.query_params:
        return Response(
            {'error': 'No Letters Specified!'},
            status=status.HTTP_400_BAD_REQUEST)

    count = int(request.query_params.get('count', 3))
    ms_ids = request.query_params['ms_ids'].split('|')
    letter_ids = request.query_params['letter_ids'].split('|')

    mss_dict = {}

    for ms_id in ms_ids:
        letters_dict = {}

        for letter_id in letter_ids:
            images = []

            for coords in Coordinates.objects\
                    .select_related('letter', 'page')\
                    .filter(
                        page__manuscript_id=ms_id,
                        binary_url__isnull=False,
                        letter_id=letter_id
                    )[:count]:

                images.append({
                    "id": coords.id,
                    "binaryurl": coords.binary_url,
                    "height": coords.height,
                    "width": coords.width,
                    "top": coords.top,
                    "left": coords.left,

                    "letter": coords.letter.id,

                    "page": coords.page.id,
                    "pageurl": coords.page.url,
                    "pageheight": coords.page.height,
                    "pagewidth": coords.page.width,
                })

            letters_dict[letter_id] = images

        mss_dict[ms_id] = letters_dict

    response_dict = {"mss": mss_dict}

    return Response(response_dict)
