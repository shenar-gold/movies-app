from django.shortcuts import render, redirect
from django.contrib import messages
from airtable import Airtable
import os


AT = Airtable(os.environ.get('AIRTABLE_MOVIESTABLE_BASE_ID'),
              'Movies',
              api_key=os.environ.get('AIRTABLE_API_KEY'))

# Create your views here.
def home_page(request):
    user_query = str(request.GET.get('query', ''))
    search_result = AT.get_all(formula="FIND('" + user_query.lower() + "', LOWER({Name}))")
    stuff_for_frontend = {'search_result': search_result}
    return render(request, 'movies/movies_stuff.html', stuff_for_frontend)


def create(request):
    if request.method == 'POST':
        data = {
            'Name': request.POST.get('name'),
            'Pictures': [{'url': request.POST.get('url') or 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'}],
            'Rating': int(request.POST.get('rating')),
            'Notes': request.POST.get('notes')
        }
        try:
            response = AT.insert(data);
            # notify on create
            messages.success(request, "New Movie Added: {}".format(response['fields'].get('Name')));
        except Exception as e:
            messages.warning(request, "Got an error when trying to create a movie: {}".format(e));
    return redirect('/');

def edit(request, movie_id):
    if request.method == 'POST':
        data = {
            'Name': request.POST.get('name'),
            'Pictures': [{'url': request.POST.get('url')}],
            'Rating': int(request.POST.get('rating')),
            'Notes': request.POST.get('notes')
        }

        try:
            response = AT.update(movie_id, data);
            #notify on update
            messages.success(request, "Movie Updated: {}".format(response['fields'].get('Name')));
        except Exception as e:
            messages.warning(request, "Got an error when trying to update a movie: {}".format(e));

    return redirect('/')

def delete(request, movie_id):
    try:
        #print(movie_id);
        movie_name = AT.get(movie_id)['fields']['Name'];
        AT.delete(movie_id);
        #notify on delete
        messages.warning(request, "Deleted movie: {}".format(movie_name));
    except Exception as e:
        messages.warning(request, "Got an error when trying to delete a movie: {}".format(e));
    return redirect('/')
