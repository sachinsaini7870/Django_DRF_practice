from django.urls import path, include

# from watchlist_app.api.views import movie_list, movie_details
from watchlist_app.api.views import (
    WatchListAV,
    WatchDetailsAV,
    StreamingPlatformAV,
    StreamPlatformDetailAV,
    ReviewList,
    ReviewDetail
)


urlpatterns = [
    path("list/", WatchListAV.as_view(), name="movie-list"),
    path("<int:pk>", WatchDetailsAV.as_view(), name="movie-detail"),
    path("stream/", StreamingPlatformAV.as_view(), name="stream-list"),
    path("stream/<int:pk>", StreamPlatformDetailAV.as_view(), name="streamingplatform-detail"),
    path("review", ReviewList.as_view(), name="review-list"),
    path("review/<int:pk>", ReviewDetail.as_view(), name="review-detail"),
]
