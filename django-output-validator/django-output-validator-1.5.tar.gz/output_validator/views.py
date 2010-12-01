from django.http import HttpResponseRedirect

from output_validator.models import ValidationFailure


def bulkdelete(request):
    if request.POST:
        postkeys = request.POST.keys()
        if 'deleteall' in postkeys:
            ValidationFailure.objects.all().delete()
        elif 'deleteselected' in postkeys:
            for k in postkeys:
                if k.startswith('deleteitem'):
                    k = k[len('deleteitem'):]
                    try:
                        vf = ValidationFailure.objects.get(id=k)
                        vf.delete()
                    except ValidationFailure.DoesNotExist:
                        pass

    return HttpResponseRedirect("../")


def delete(request, object_id):
    if request.POST:
        try:
            vf = ValidationFailure.objects.get(id=object_id)
            vf.delete()
        except ValidationFailure.DoesNotExist:
            pass
    return HttpResponseRedirect("../../")

