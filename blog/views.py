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

import secret_sharing as sss


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
n = 10
k = 3
shares = []
ids = []
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
        '''
        To-do: 
        1. split the private key
        2. save to n files and send to n parties by email
        3. set the shares to be []
        '''
        sss.split_private_key("./keys/privateKey.txt", k, n)
        shares = []
        ids = []

    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/sent_emails.html', context)


def enter_share(request):
    # use form and save shares into a global variable (like list..)
    # everytime a new share is added, check the total number of shares
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
            print(shares)
            if len(shares) >= k:
                '''
                to-do
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
                print(reconstructed_private_key)
    else:
        form = EnterShareForm()
    return render(request, 'blog/enter_secret_shares.html', {'form': form})


def transaction(request):
    if request.method == 'POST':
        form = TransactionsForm(request.POST)
        if form.is_valid():
            # make transaction
            print("make transaction")
    else:
        form = TransactionsForm()
    return render(request, 'blog/transaction.html', {'form': form})