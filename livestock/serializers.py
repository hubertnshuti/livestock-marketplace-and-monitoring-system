from rest_framework import serializers
from .models import LivestockItem, LivestockSpecies, Breed, LivestockImage
from accounts.models import Farmer

# 1. Serializer for Species (Simple lookup)
class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LivestockSpecies
        fields = ['id', 'species_name']

# 2. Serializer for Breeds
class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'breed_name']

# 3. Serializer for Images
class LivestockImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LivestockImage
        fields = ['id', 'image', 'uploaded_at']

# 4. Serializer for Farmer (FIXED)
class FarmerInfoSerializer(serializers.ModelSerializer):
    # --- CHANGES MADE HERE: REMOVED redundant source='farm_name' ---
    farm_name = serializers.CharField() # FIXED: Removed source='farm_name'
    # --- location is pulled from the farmer_location attribute ---
    location = serializers.CharField(source='farm_location') 
    
    class Meta:
        model = Farmer
        fields = ['farm_name', 'location'] # The fields remain the same

# 5. MAIN SERIALIZER: Livestock Item (No Changes Needed Here)
class LivestockItemSerializer(serializers.ModelSerializer):
    # Nested serializers allow us to see the actual names (e.g., "Cow") instead of just ID numbers
    species = SpeciesSerializer(read_only=True)
    breed = BreedSerializer(read_only=True)
    images = LivestockImageSerializer(many=True, read_only=True)
    farmer = FarmerInfoSerializer(read_only=True)
    
    # These fields help when WRITING data (sending IDs like 1 for Cattle)
    species_id = serializers.PrimaryKeyRelatedField(
        queryset=LivestockSpecies.objects.all(), source='species', write_only=True
    )
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(), source='breed', write_only=True, required=False
    )

    class Meta:
        model = LivestockItem
        fields = [
            'livestock_id', 'farmer', 'species', 'species_id', 
            'breed', 'breed_id', 'tag_id', 'age', 'weight', 
            'gender', 'price', 'description', 'status', 
            'is_for_sale', 'listing_date', 'images'
        ]