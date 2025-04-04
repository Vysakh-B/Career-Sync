from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ChatSession, ChatMessage
import json
import google.generativeai as genai
from Jobsfetch.models import Job,JobApplication
import torch
from chatbot.model import NeuralNet  # Ensure this matches your model definition
from chatbot.nltk_utils import tokenize,bag_of_words

# Load the trained data
MODEL_PATH = r"C:\Users\HP\Desktop\S4\Project\JobInterview\chatbot\data.pth"
data = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
genai.configure(api_key="AIzaSyAfYd_rzyNuxWhrocGltVZlmJK-0_UQLs8")
# Extract saved data
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

# Initialize and load the model
model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()  # Set to evaluation mode

def redirecting_chat(request):
    flag = False
    sessions = ChatSession.objects.filter(user=request.user).exclude(company_name="Free Chat", position_name="General")
    if sessions:
        flag=True
    else:
        flag=False
    # Process each session to modify the position name
    # for session in sessions:
        
    #     session.short_position_name = session.position_name.split(",")[0] if "," in session.position_name else session.position_name

    # return render(request, 'chat.html', {'sessions': sessions,'flag':flag})
    return render(request, 'Redirect.html', {'sessions': sessions,'flag':flag})

def read_interview(request, id):
    sesion = ChatSession.objects.get(id=id)
    job = sesion.jobid
    application = JobApplication.objects.get(user=request.user, jobid=job)
    if application.interview_date:
        return redirect('chat', id=id) # 'success_page'
    if request.method == 'POST':
        dates = request.POST.get('interview_date', '').strip()

        if not dates:
            return render(request, 'Read_interview.html', {
                'app': application,
                'sessionid': id,
                'error': "Please enter a valid date."
            })

        # Process the date (save in DB, etc.)
        application.interview_date = dates
        application.save()
        return redirect('chat', id=id) # 'success_page'

    return render(request, 'Read_interview.html', {'app': application, 'sessionid': id})



@login_required
@ensure_csrf_cookie
def chats(request):
    return redirect('redirecting_chat')
    sessions = ChatSession.objects.filter(user=request.user)
    # Process each session to modify the position name
    # for session in sessions:
        
    #     session.short_position_name = session.position_name.split(",")[0] if "," in session.position_name else session.position_name

    return render(request, 'chat.html', {'sessions': sessions})
    # return render(request, 'Redirect.html', {'sessions': sessions,'flag':flag})

def chat(request,id):
    sessions = ChatSession.objects.get(id=id,user=request.user)
    # Process each session to modify the position name
    # for session in sessions:
        
    #     session.short_position_name = session.position_name.split(",")[0] if "," in session.position_name else session.position_name

    return render(request, 'chat.html', {'session': sessions})
    # return render(request, 'Redirect.html', {'sessions': sessions,'flag':flag})
def freechat(request):
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        jobid=None,  # Mark it as a free chat session
        company_name="Free Chat",
        position_name="General"
    )
    return render(request, 'chat.html', {'session': session})

    # Process each session to modify the position name
    # for session in sessions:
        
    #     session.short_position_name = session.position_name.split(",")[0] if "," in session.position_name else session.position_name

    return render(request, 'chat.html', {'session': sessions})
    # return render(request, 'Redirect.html', {'sessions': sessions,'flag':flag})

@login_required
def get_messages(request, session_id):
    chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(chat_session=chat_session).order_by("timestamp")

    response_data = {
        "messages": [{"message": msg.message, "sender": msg.sender} for msg in messages]
    }
    return JsonResponse(response_data)

@login_required
@csrf_exempt  # Optional, depends on your frontend setup

def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        session_id = data.get("session_id")
        message = data.get("message")

        if not message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)

        # Save user message
        ChatMessage.objects.create(
            chat_session=chat_session,
            sender="user",
            message=message
        )

        # **Process message with ML chatbot model**
        sentence = tokenize(message)
        X = bag_of_words(sentence, all_words)
        X = torch.tensor(X, dtype=torch.float).unsqueeze(0)

        with torch.no_grad():
            output = model(X)  # ML model (do not rename this)
            _, predicted = torch.max(output, dim=1)
            tag = tags[predicted.item()]

        # Load response from intents.json
        try:
            with open(r"C:\Users\HP\Desktop\S4\Project\JobInterview\chatbot\intents.json", "r") as f:
                intents = json.load(f)
        except Exception as e:
            print(f"Error Loading intents.json: {e}")
            return JsonResponse({"error": "Chatbot data not found"}, status=500)

        bot_reply = None  # Initialize empty bot reply

        for intent in intents["intents"]:
            if intent["tag"] == tag:
                bot_reply = intent["responses"][0]  # Pick first response
                print(tag)
                break
        # **Detect if the trained model response is generic or irrelevant**
        default_responses = [
            "Hello! How can I assist you with your interview preparation?",
            "I'm here to help you with interview-related queries!",
            "Research the company, practice common questions, and be confident. Mock interviews help a lot!"
        ]

        # **If trained model has no reply, use Gemini API**
        if not bot_reply or bot_reply == "I'm not sure how to respond." or bot_reply in default_responses:
            print("Fallback to Gemini API")
            try:
                gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # Use a different variable name
                response = gemini_model.generate_content(message)  # Pass user input
                bot_reply = response.text
            except Exception as e:
                print(f"Error calling Gemini API: {e}")
                bot_reply = "I'm unable to generate a response at the moment."

        # Save AI response
        ChatMessage.objects.create(
            chat_session=chat_session,
            sender="ai",
            message=bot_reply
        )

        return JsonResponse({"status": "Message sent", "bot_reply": bot_reply})

    return JsonResponse({"error": "Invalid request method"}, status=400)

def get_chatbot_response(user_input):
    """
    Uses the ML model to generate a response.
    """
    processed_input = preprocess_input(user_input)  # Convert text to model format
    input_tensor = torch.tensor([processed_input], dtype=torch.float32)  # Convert to tensor

    with torch.no_grad():  # Disable gradient calculation (for efficiency)
        model_output = chatbot_model(input_tensor)

    response = postprocess_output(model_output)  # Convert model output back to text
    return response
