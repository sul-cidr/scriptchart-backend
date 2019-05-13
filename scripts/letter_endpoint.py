""" API endpoint to return all the information necessary to construct the
    script chart.
"""

# TODO:
# These changes all need to be made in coordination with frontend changes
# * remove empty lists from response
# * change top-level key from 'mss' to 'examples'
# * remove unnecessary fields from response
#   all that's required, I think, is:
#   - height, width, top, left
#   - maybe that's it (becasue ms_id / ms_slug is already available)?
#   - consider pre-composing the url(s), or are these best composed
#     on the frontend?


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

    Returns:
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

    examples = Coordinates.objects.select_related('page').filter(
        manuscript_id__in=ms_ids, letter_id__in=letter_ids,
        priority__lte=count)

    # the frontend depends on empty lists for missing values, so...
    # examples_dict = defaultdict(lambda: defaultdict(list))
    examples_dict = dict(
        (int(ms_id), dict((int(letter_id), []) for letter_id in letter_ids))
        for ms_id in ms_ids
    )

    for example in examples:
        examples_dict[example.manuscript_id][example.letter_id].append({
            "id": example.id,
            "binaryurl": example.binary_url,
            "height": example.height,
            "width": example.width,
            "top": example.top,
            "left": example.left,

            "letter": example.letter_id,

            "page": example.page.number,
            "pageurl": example.page.url,
            "pageheight": example.page.height,
            "pagewidth": example.page.width,
        })

    return Response({'mss': examples_dict})
