from rest_framework import viewsets, permissions
from .models import LivestockItem, LivestockSpecies
from .serializers import LivestockItemSerializer, SpeciesSerializer

# 1. Species API (Read Only is usually fine for lists)
class SpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LivestockSpecies.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [permissions.AllowAny] # Public can see species

# 2. Livestock API (The main marketplace API)
class LivestockViewSet(viewsets.ModelViewSet):
    queryset = LivestockItem.objects.all()
    serializer_class = LivestockItemSerializer
    
    # Permissions: Anyone can READ (list/retrieve), but only Authenticated users can CREATE/UPDATE
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    # Automatic filtering: Only show 'is_for_sale' items to the public list
    def get_queryset(self):
        queryset = LivestockItem.objects.all()
        # If looking at the main list, only show available items
        if self.action == 'list':
            return queryset.filter(is_for_sale=True, status='available')
        return queryset

    # Auto-link the farmer when creating an item via API
    def perform_create(self, serializer):
        # Assumes the user is a farmer
        serializer.save(farmer=self.request.user.farmer_profile)