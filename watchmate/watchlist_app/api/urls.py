from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from watchlist_app.api.views import movie_list, movie_details
from watchlist_app.api.views import (
    WatchListAV,
    WatchDetailsAV,
    StreamingPlatformAV,
    StreamingPlatformDetailAV,
    ReviewList,
    ReviewDetail,
    ReviewCreate,
    StreamingPlatformVS,
)

router = DefaultRouter()
router.register("stream", StreamingPlatformVS, basename="streamingplatform")

urlpatterns = [
    path("list/", WatchListAV.as_view(), name="movie-list"),
    path("<int:pk>/", WatchDetailsAV.as_view(), name="movie-detail"),

    path("", include(router.urls)),

    # path("stream/", StreamingPlatformAV.as_view(), name="stream-list"),
    # path("stream/<int:pk>", StreamingPlatformDetailAV.as_view(), name="streamingplatform-detail"),
    
    # path("review/", ReviewList.as_view(), name="review-list"),
    # path("review/<int:pk>", ReviewDetail.as_view(), name="review-detail"),
    
    path("<int:pk>/review-create/", ReviewCreate.as_view(), name="review-create"),    
    path("<int:pk>/reviews/", ReviewList.as_view(), name="review-list"),    
    path("review/<int:pk>/", ReviewDetail.as_view(), name="review-detail"),
]
