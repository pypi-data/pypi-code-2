from django.shortcuts import render_to_response, redirect



from bookreader.forms import DSpaceCollectionForm, DSpaceBookForm



def collection(request, **kwargs):
    kwargs.setdefault('template_name','bookreader/load/collection.html')
    kwargs.setdefault('redirect_to', reverse)
    
    
    form = DSpaceCollectionForm()
    
    if request.method == 'POST':
        form = DSpaceCollectionForm(request.POST)
        
        if form.is_valid():
            pass
