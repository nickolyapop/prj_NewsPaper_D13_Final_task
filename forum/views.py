from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from .models import Post, Response, Reply, Category
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import PostForm, PostResponseForm, ReplyForm
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormMixin
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


class PostList(ListView):
    model = Post
    template_name = 'forum/posts.html'
    context_object_name = 'posts'
    paginate_by = 6


class PostDetailView(DetailView, FormMixin):
    template_name = 'forum/post.html'
    model = Post
    context_object_name = 'post_detail'

    form_class = PostResponseForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = form.save(commit=False)
        response.responseUser = self.request.user
        response.responsePost = Post.objects.get(id=self.kwargs['pk'])
        author_post = Post.objects.get(id=self.kwargs['pk'])
        user_post = author_post.author
        user_email = user_post.email
        response.save()
        subject = 'Пользователь оставил отклик на ваше объявление'
        message = f'Пользователь {response.responseUser.username} оставил ответ на ваш отклик.'
        from_email = 'nickolya212008@yandex.ru'
        recipient_list = [user_email]

        send_mail(subject, message, from_email, recipient_list)

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('post_detail', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = Response.objects.filter(responsePost=self.object)
        return context


class ResponseListView(DetailView, FormMixin):
    model = Response
    template_name = 'forum/post.html'
    context_object_name = 'response'
    form_class = ReplyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responseUser'] = self.request.user

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'forum/post_create.html'
    form_class = PostForm
    permission_required = ('post.add_post',)
    success_url = reverse_lazy('posts')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)

        post.save()
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'forum/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy('posts')
    permission_required = ('post.change_post')

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'forum/post_delete.html'
    model = Post
    queryset = Post.objects.all()
    success_url = reverse_lazy('posts')
    permission_required = 'post.delete_post'


class PrivatelistView(ListView, FormMixin):
    model = Response
    template_name = 'forum/private_response.html'
    context_object_name = 'responses'
    form_class = ReplyForm
    success_url = '/index/'

    def get_queryset(self):
        user = self.request.user
        responses_by_user = Response.objects.filter(responsePost__author=user)
        user_responses_to_other_ads = Response.objects.filter(responseUser=user)

        combined_responses = user_responses_to_other_ads | responses_by_user
        combined_responses = combined_responses.order_by('-dateCreation')

        return combined_responses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        form = ReplyForm(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.user = self.request.user

        reply.response_reply_id = int(self.request.POST.get("response_post_id"))
        print(reply.response_reply_id)
        reply.replied_to_user_id = int(self.request.POST.get("response_user_id"))

        replied_to_user = User.objects.get(id=reply.replied_to_user_id)

        print(reply.replied_to_user_id)
        reply.save()
        subject = 'Новый ответ на ваш отклик'
        message = f'Пользователь {reply.user.username} оставил ответ на ваш отклик.'
        from_email = 'nickolya212008@yandex.ru'
        recipient_list = [replied_to_user.email]

        send_mail(subject, message, from_email, recipient_list)
        return super().form_valid(form)


class ReplyList(ListView):
    model = Reply
    template_name = 'forum/private_response.html'
    context_object_name = 'response_rep'


class DeleteResponseView(DeleteView):
    model = Response
    success_url = reverse_lazy('privatelist')


class CategoryView(DetailView):
    model = Category
    template_name = 'forum/category.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['category'] = Category.objects.get(pk=self.kwargs['pk'])
        context['subscribers'] = category.subscribers.all()
        context['posts_sub'] = category.post_set.all()
        return context


@login_required
def subscribe_from_category(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_from_category(request, pk):
    category = Сategory.objects.get(pk=pk)
    category.subscribers.remove(request.user.id)
    return redirect(request.META.get('HTTP_REFERER'))


class SearchList(ListView):
    model = Response
