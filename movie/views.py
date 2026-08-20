import io
import base64
from collections import Counter


from django.shortcuts import render
from django.http import HttpResponse


from .models import Movie

# Create your views here.

def home(request):
 #return HttpResponse('<h1>Welcome to home </h1>')
 #return render(request, 'home.html')
 #return render(request, 'home.html', {'name': 'Johan Peña '})

 searchTerm = request.GET.get('searchMovie')
 if searchTerm:
     movies = Movie.objects.filter(title__icontains=searchTerm)
 else:
     movies = Movie.objects.all()
 return render(request, 'home.html', {'movies': movies, 'searchTerm': searchTerm})

def about(request):
    # return HttpResponse('<h1>Welcome to About </h1>')
     return render(request, 'about.html')

def statistics_view(request):
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {}

    for year in years:
        if year:
            movie_counts_by_year[year] = Movie.objects.filter(year=year).count()
        else:
            movie_counts_by_year['None'] = Movie.objects.filter(year__isnull=True).count()

    genres = Movie.objects.values_list('genre', flat=True)
    genre_counts = Counter()

    for genre in genres:
        if not genre:
            continue

        first_genre = genre.split(',')[0].strip()
        if first_genre:
            genre_counts[first_genre] += 1

    year_labels = list(movie_counts_by_year.keys())
    year_values = list(movie_counts_by_year.values())
    year_positions = range(len(year_labels))

    plt.figure(figsize=(10, 5))
    plt.bar(year_positions, year_values, width=0.5, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(year_positions, year_labels, rotation=90)
    plt.subplots_adjust(bottom=0.3)
    year_graphic = self_to_base64_figure(plt)

    genre_labels = list(genre_counts.keys())
    genre_values = list(genre_counts.values())
    genre_positions = range(len(genre_labels))

    plt.figure(figsize=(10, 5))
    plt.bar(genre_positions, genre_values, width=0.5, align='center')
    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(genre_positions, genre_labels, rotation=90)
    plt.subplots_adjust(bottom=0.3)
    genre_graphic = self_to_base64_figure(plt)

    return render(
        request,
        'statistics.html',
        {
            'year_graphic': year_graphic,
            'genre_graphic': genre_graphic,
        },
    )


def self_to_base64_figure(plt_module):
    buffer = io.BytesIO()
    plt_module.savefig(buffer, format='png')
    buffer.seek(0)
    plt_module.close()
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    return graphic.decode('utf-8')