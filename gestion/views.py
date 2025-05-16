# gestion/views.py
from rest_framework import generics
# Import models and serializers from the same app (gestion)
from .models import Salle, Laboratoire, Bureau, PC
from .serializers import SalleSerializer, LaboratoireSerializer, BureauSerializer, PCSerializer

# Liste et création des salles
class SalleListCreateView(generics.ListCreateAPIView):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

# Détail, modification et suppression d'une salle
class SalleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

# Liste et création des laboratoires
class LaboratoireListCreateView(generics.ListCreateAPIView):
    queryset = Laboratoire.objects.all()
    serializer_class = LaboratoireSerializer

# Détail, modification et suppression d'un laboratoire
class LaboratoireDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Laboratoire.objects.all()
    serializer_class = LaboratoireSerializer

# Liste et création des bureaux
class BureauListCreateView(generics.ListCreateAPIView):
    queryset = Bureau.objects.all()
    serializer_class = BureauSerializer

# Détail, modification et suppression d'un bureau
class BureauDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bureau.objects.all()
    serializer_class = BureauSerializer

# Liste et création des PC
class PCListCreateView(generics.ListCreateAPIView):
    queryset = PC.objects.all()
    serializer_class = PCSerializer

# Liste des PCs par laboratoire
class PCsByLaboratoireView(generics.ListAPIView):
    serializer_class = PCSerializer

    def get_queryset(self):
        # Use get_object_or_404 here for robustness if the lab ID doesn't exist
        laboratoire_id = self.kwargs['laboratoire_id']
        # You might want to check if the lab exists first, though filter will just return empty
        # labo = get_object_or_404(Laboratoire, id=laboratoire_id) # If you wanted to raise 404 for invalid lab ID
        return PC.objects.filter(laboratoire_id=laboratoire_id)

# Détail, modification et suppression d'un PC
class PCDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PC.objects.all()
    serializer_class = PCSerializer