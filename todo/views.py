from rest_framework import generics, permissions

from .models import Todo
from .serializers import TodoSerializer
from .permissions import IsOwnerOnly
# Create your views here.


class TodoListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user)
    

class TodoDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = (IsOwnerOnly,)
    lookup_field = 'pk'

    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user)
    