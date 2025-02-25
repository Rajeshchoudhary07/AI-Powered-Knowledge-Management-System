from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document
import openai

openai.api_key = "your_openai_api_key"

class DocumentChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, doc_id):
        question = request.data.get("question", "")
        document = Document.objects.get(id=doc_id, user=request.user)

        prompt = f"Based on the following document:\n\n{document.text_content}\n\nAnswer this question:\n{question}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI assistant."},
                      {"role": "user", "content": prompt}]
        )

        return Response({"answer": response["choices"][0]["message"]["content"]})
