from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import PaymentSerializer

class PaymentTestView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            # For now, just return the data
            return Response({"message": "Payment endpoint hit", "data": serializer.validated_data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)