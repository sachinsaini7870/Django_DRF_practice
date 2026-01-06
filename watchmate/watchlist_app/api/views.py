# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import generics

# from rest_framework import mixins
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.throttling import (
    UserRateThrottle,
    AnonRateThrottle,
    ScopedRateThrottle,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from watchlist_app.api.permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly
from watchlist_app.models import Watchlist, StreamingPlatform, Review
from watchlist_app.api.serializers import (
    WatchListSerializer,
    StreamingPlatformSerializer,
    ReviewSerializer,
)
from watchlist_app.api.throttling import ReviewCreateThrottle, ReviewListThrottle
from watchlist_app.api.pagination import WatchListPagination, WatchListLOPagination


class UserReview(generics.ListAPIView):
    serializer_class = ReviewSerializer
    # throttle_classes = [ReviewListThrottle, AnonRateThrottle]

    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Review.objects.filter(review_user__username=username)

    def get_queryset(self):
        username = self.request.query_params.get("username")
        return Review.objects.filter(review_user__username=username)


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get("pk")
        watchlist = Watchlist.objects.get(pk=pk)

        review_user = self.request.user
        review_queryset = Review.objects.filter(
            watchlist=watchlist, review_user=review_user
        )

        if review_queryset.exists():
            raise ValidationError("You have already reviewed this movie!")

        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data["rating"]
        else:
            watchlist.avg_rating = (
                watchlist.avg_rating + serializer.validated_data["rating"]
            ) / 2

        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()

        serializer.save(watchlist=watchlist, review_user=review_user)


class ReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]  # specific class or object level permision
    throttle_classes = [ReviewListThrottle, AnonRateThrottle]  # Local Throttling
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["review_user__username", "active"]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        return Review.objects.filter(watchlist=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsReviewUserOrReadOnly
    ]  # specific class or object level permision
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # Local Throttling
    throttle_classes = [ScopedRateThrottle]  # Global Throttling
    throttle_scope = "review_detail"  # Global Throttling


# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)


# class ReviewList(
#     mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
# ):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# # ModelViewSet for only GET method
# class StreamingPlatformVS(viewsets.ReadOnlyModelViewSet):
#     queryset = StreamingPlatform.objects.all()
#     serializer_class = StreamingPlatformSerializer


# ModelViewSet for all methods GET, PUT, PATCH, POST, DELETE
class StreamingPlatformVS(viewsets.ModelViewSet):
    queryset = StreamingPlatform.objects.all()
    serializer_class = StreamingPlatformSerializer
    permission_classes = [IsAdminOrReadOnly]


# class SreamingPlatformVS(viewsets.ViewSet):

#     def list(self, request):
#         queryset = StreamingPlatform.objects.all()
#         serializer = StreamingPlatformSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamingPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamingPlatformSerializer(watchlist)
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = StreamingPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, pk=None):
#         platform = StreamingPlatform.objects.get(pk=pk)
#         serializer = StreamingPlatformSerializer(platform)
#         name = serializer.data.get('name')
#         platform.delete()
#         content = {"message": f"'{name}' deleted successfully."}
#         return Response(content, status=status.HTTP_204_NO_CONTENT)


class StreamingPlatformAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        platform = StreamingPlatform.objects.all()
        serializer = StreamingPlatformSerializer(
            platform, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = StreamingPlatformSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamingPlatformDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            platform = StreamingPlatform.objects.get(pk=pk)
        except StreamingPlatform.DoesNotExist:
            return Response(
                {"Error": "Platform not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = StreamingPlatformSerializer(platform, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        platform = StreamingPlatform.objects.get(pk=pk)
        serializer = StreamingPlatformSerializer(
            platform, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        platform = StreamingPlatform.objects.get(pk=pk)
        serializer = StreamingPlatformSerializer(platform, context={"request": request})
        name = serializer.data.get("name")
        platform.delete()
        content = {"message": f"'{name}' deleted successfully."}
        return Response(content, status=status.HTTP_204_NO_CONTENT)


# This class only for test purpose
class WatchListGV(generics.ListAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchListSerializer
    pagination_class = WatchListLOPagination


class WatchListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        movie = Watchlist.objects.all()
        serializer = WatchListSerializer(movie, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchDetailsAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            movie = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response(
                {"Error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = WatchListSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = Watchlist.objects.get(pk=pk)
        serializer = WatchListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = Watchlist.objects.get(pk=pk)
        serializer = WatchListSerializer(movie)
        title = serializer.data.get("title")
        movie.delete()
        content = {"message": f"'{title}' deleted successfully."}
        return Response(content, status=status.HTTP_204_NO_CONTENT)


# @api_view(["GET", "POST"])
# def movie_list(request):
#     if request.method == "GET":
#         movie = Movie.objects.all()
#         serializer = MovieSerializer(movie, many=True)
#         return Response(serializer.data)

#     if request.method == "POST":
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["GET", "PUT", "DELETE"])
# def movie_details(request, pk):
#     if request.method == "GET":

#         try:
#             movie = Movie.objects.get(pk=pk)
#         except Movie.DoesNotExist:
#             return Response(
#                 {"Error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)

#     if request.method == "PUT":
#         movie = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer(movie, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     if request.method == "DELETE":
#         movie = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer(movie)
#         movie.delete()
#         content = {"message": f"'{serializer.data.get('name')}' deleted successfully."}
#         return Response(content, status=status.HTTP_204_NO_CONTENT)
