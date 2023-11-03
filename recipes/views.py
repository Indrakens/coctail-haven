from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Recipe
from .forms import CommentForm


class RecipeList(generic.ListView):
    model = Recipe
    queryset = Recipe.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 6
            

class RecipeDetail(LoginRequiredMixin, View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Recipe.objects.filter(status=1)
        cocktail = get_object_or_404(queryset, slug=slug)
        comments = cocktail.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if cocktail.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "recipe.html",
            {
                "cocktail": cocktail,
                "comments": comments,
                "commented": False, 
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        queryset = Recipe.objects.filter(status=1)
        cocktail = get_object_or_404(queryset, slug=slug)
        comments = cocktail.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if cocktail.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.cocktail = cocktail
            comment.save()
        else:
            comment_form = CommentForm()        

        return render(
            request,
            "recipe.html",
            {
                "cocktail": cocktail,
                "comments": comments,
                "commented": True, 
                "liked": liked,
                "comment_form": CommentForm()
            },
        ) 


class RecipeLike(LoginRequiredMixin, View):
    
    def post(self, request, slug, *args, **kwargs):
        cocktail = get_object_or_404(Recipe, slug=slug)
        if cocktail.likes.filter(id=request.user.id).exists():
            cocktail.likes.remove(request.user)
        else:
            cocktail.likes.add(request.user)

        return HttpResponseRedirect(reverse('recipe', args=[slug]))


class RecipeCreate(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Recipe
    fields = [
            'name',
            'slug',
            'user',
            'featured_image',
            'serving',
            'time',
            'description',
            'ingredients',
            'directions'
        ]
    success_message = "You have successfully added a cocktail!"         
    template_name = 'add-cocktail-form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        return super(RecipeCreate, self).form_valid(form)


class RecipeUpdate(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Recipe
    fields = [
            'name',
            'slug',
            'featured_image',
            'serving',
            'time',
            'description',
            'ingredients',
            'directions'
        ]
    template_name = 'add-cocktail-form.html'
    success_url = reverse_lazy('home')
    success_message = "You have successfully updated a cocktail!" 


class RecipeDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, generic.DeleteView):
    model = Recipe
    template_name = 'delete_cocktail.html'
    success_url = reverse_lazy('home')
    success_message = "Cocktail-recipe have been deleted!"

    def test_func(self):
        return self.request.user == self.get_object().user    
