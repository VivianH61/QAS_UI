from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from .forms import SssSettingForm, EnterShareForm, TransactionsForm
from django.contrib import messages

import ShamirSecretSharing as sss


from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

import smtplib, ssl



def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['name', 'email']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['name', 'email']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


# set the parameters of SSS
# default value of n and k: 6 and 3
n = 6
k = 3
ids = []
shares = []
def setting(request):
    if request.method == 'POST':
        form = SssSettingForm(request.POST)
        if form.is_valid():
            # form.save()
            global n
            global k
            n = form.cleaned_data.get('Set_the_number_of_participants')
            k = form.cleaned_data.get('Least_number_of_participants_for_key_reconstruction')
    else:
        form = SssSettingForm()
    return render(request, 'blog/setting.html', {'form': form})

def sent_emails(request):
    if request.method == "GET":
        # generate the secret shares for each party in the "./keys" folder
        sss.split_private_key("./keys/privateKey.txt", k, n)
        # send the shares to n parties by email
        posts = Post.objects.all()
        i = 0
        for post in posts:
            email_from = settings.EMAIL_HOST_USER
            subject = '[QASTokenApp] Your partial key'
            to = [post.email]
            #text_content = 'Hi,\n\nThe admin account is making a transaction, if you decide to authorize this transaction, please enter your partial private key in the link below.\n\nhttp://127.0.0.1:8000/enter_share/\n Thank you!'
            text_content = "Hi, this is the partial private key for the admin account. Please keep in a save place. Thanks!"
            message = EmailMultiAlternatives(subject, text_content, email_from, to)
            message.attach_file('keys/partial_key_' + str(i) + '.txt')
            i += 1
            message.send()

        
        global shares, ids
        ids = []
        shares = []
        

    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/sent_emails.html', context)


def enter_share(request):
    if request.method == 'POST':
        form = EnterShareForm(request.POST)
        if form.is_valid():
            # form.save()
            party_id = form.cleaned_data.get('party_id')
            partial_key = form.cleaned_data.get('partial_key')
            global shares
            global ids
            shares.append(partial_key)
            ids.append(party_id)
            '''
            When enough parties provide their shares, the backend will automatically reconstruct the private key and save into the file "./key/new_private_key.txt"
            '''
            if len(shares) >= k:
                '''
                save shares into a file, call reconstruct func
                save the reconstructed private key into a file
                approve the transaction
                '''
                file1 = open('./keys/received_shares.txt', 'w')
                for i in range(k):
                    file1.write(str(ids[i]) + '|' + shares[i] + '\n')
                # Closing file
                file1.close()
                # reconstruct the private key
                reconstructed_private_key = sss.reconstruct_private_key('./keys/received_shares.txt', k)
                print("reconstructed: " + reconstructed_private_key)
                file2 = open('./keys/new_private_key.txt', 'w')
                file2.write(reconstructed_private_key)
                file2.close()
                ### make transaction
                '''
                sendInitialEther(reconstructed_private_key, send_to_address)
                '''
    else:
        form = EnterShareForm()
    return render(request, 'blog/enter_secret_shares.html', {'form': form})

# admin account making a transaction
def transaction(request):
    if request.method == 'POST':
        form = TransactionsForm(request.POST)
        if form.is_valid():
            posts = Post.objects.all()
            i = 0
            for post in posts:
                email_from = settings.EMAIL_HOST_USER
                subject = '[QASTokenApp] Action Required'
                to = [post.email]
                text_content = 'Hi,\n\nThe admin account is making a transaction, if you decide to authorize this transaction, please enter your partial private key in the link below.\n\nhttp://127.0.0.1:8000/enter_share/\n Thank you!'
                message = EmailMultiAlternatives(subject, text_content, email_from, to)
                i += 1
                message.send()

    else:
        form = TransactionsForm()
    return render(request, 'blog/transaction.html', {'form': form})