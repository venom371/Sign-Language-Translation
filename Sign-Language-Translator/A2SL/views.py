import nltk
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


def home_view(request):
    return render(request, 'home.html')


@login_required(login_url="login")
def animation_view(request):
    if request.method == 'POST':
        text = request.POST.get('sen')
        # tokenizing the sentence
        text.lower()
        # tokenizing the sentence
        words = word_tokenize(text)

        tagged = nltk.pos_tag(words)
        tense = {"future": len([word for word in tagged if word[1] == "MD"]),
                 "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
                 "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
                 "present_continuous": len([word for word in tagged if word[1] in ["VBG"]])}

        # stopwords that will be removed
        stop_words = {"mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've", 'off',
                      'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't",
                      "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll",
                      "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have',
                      'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an',
                      'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such',
                      'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't",
                      "won't"}
        sign_words = {"After", "Again", "Against", "Age", "All", "Alone", "Also", "Also", "And", "Ask", "At", "Be",
                      "Beautiful", "Before", "Best", "Better", "Busy", "But", "Bye", "Can", "Cannot", "Change",
                      "College", "Come", "Computer", "Day", "Distance", "Do not", "Do", "Does not", "Eat", "Engineer",
                      "Fight", "Finish", "From", "Glitter", "Go", "God", "Gold", "Good", "Great", "Hand", "Hands",
                      "Happy", "Hello", "Help", "Her", "Here", "His", "Home", "Homepage", "How", "Invent", "It", "Keep",
                      "Language", "Laugh", "Learn", "Me", "More", "My", "Name", "Next", "Not", "Now", "Of", "On", "Our",
                      "Out", "Pretty", "Right", "Sad", "Safe", "See", "Self", "Sign", "Sing", "So", "Sound", "Stay",
                      "Study", "Talk", "Television", "Thank you", "Thank", "That", "They", "This", "Those", "Time",
                      "To", "Type", "Us", "Walk", "Wash", "Way", "We", "Welcome", "What", "When", "Where", "Which",
                      "Who", "Whole", "Whose", "Your", "Why", "Will", "With", "Without", "Words", "Work", "World",
                      "Wrong", "You", "Yourself"}
        # removing stopwords and applying lemmatizing nlp process to words
        lr = WordNetLemmatizer()
        filtered_text = []
        for w, p in zip(words, tagged):
            if w not in stop_words:
                if p[1] == 'VBG' or p[1] == 'VBD' or p[1] == 'VBZ' or p[1] == 'VBN' or p[1] == 'NN':
                    filtered_text.append(lr.lemmatize(w, pos='v'))
                elif p[1] == 'JJ' or p[1] == 'JJR' or p[1] == 'JJS' or p[1] == 'RBR' or p[1] == 'RBS':
                    filtered_text.append(lr.lemmatize(w, pos='a'))

                else:
                    filtered_text.append(lr.lemmatize(w))

        # adding the specific word to specify tense
        words = filtered_text
        temp = []
        for w in words:
            if w == 'I':
                temp.append('Me')
            else:
                temp.append(w)
        words = temp
        probable_tense = max(tense, key=tense.get)

        if probable_tense == "past" and tense["past"] >= 1:
            temp = ["Before"]
            temp = temp + words
            words = temp
        elif probable_tense == "future" and tense["future"] >= 1:
            if "Will" not in words:
                temp = ["Will"]
                temp = temp + words
                words = temp
            else:
                pass
        elif probable_tense == "present":
            if tense["present_continuous"] >= 1:
                temp = ["Now"]
                temp = temp + words
                words = temp

        filtered_text = []
        for w in words:
            w = w.capitalize()
            if w not in sign_words:
                for c in w:
                    filtered_text.append(c)
            else:
                filtered_text.append(w)
        words = filtered_text

        return render(request, 'animation.html', {'words': words, 'text': text})
    else:
        return render(request, 'animation.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # log the user in
            return redirect('animation')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log in user
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('animation')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect("home")
