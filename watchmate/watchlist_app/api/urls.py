from django.urls import path, include

# from watchlist_app.api.views import movie_list, movie_details
from watchlist_app.api.views import WatchListAV, WatchDetailsAV, StreamingPlatformAV, StreamPlatformDetailAV




urlpatterns = [
    path("list/", WatchListAV.as_view(), name="movie-list"),
    path("<int:pk>", WatchDetailsAV.as_view(), name="movie-details"),
    path("stream/", StreamingPlatformAV.as_view(), name="stream"),
    path("stream/<int:pk>", StreamPlatformDetailAV.as_view(), name="stream-details"),

]
