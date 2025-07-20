from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.contrib import messages

from .models import Article, Category, ReadingHistory, UserPreference

# -----------------------------
# ARTICLE LIST VIEW
# -----------------------------
class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    ordering = ['-published_date']

    def get_queryset(self):
        queryset = super().get_queryset()

        category_name = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        # ✅ Filter by category from dropdown
        if category_name and category_name != 'All':
            queryset = queryset.filter(category__name__iexact=category_name)
            return queryset  # Show only this category

        # ✅ Filter by search query
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # ✅ Personalized feed for logged-in users
        if self.request.user.is_authenticated:
            try:
                user_pref = self.request.user.preference
                preferred_categories = user_pref.preferred_categories.all()

                if preferred_categories.exists():
                    queryset = queryset.filter(category__in=preferred_categories).distinct()
                    messages.info(self.request, "Showing personalized articles.")
                else:
                    messages.info(self.request, "No preferences set. Showing all articles.")
            except UserPreference.DoesNotExist:
                messages.info(self.request, "Set your preferences to customize your feed.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ Category list with article counts
        context['categories'] = Category.objects.annotate(
            article_count=Count('articles')  # article = related_name from ForeignKey in Article model
        ).order_by('name')

        context['current_category'] = self.request.GET.get('category', 'All')
        context['search_query'] = self.request.GET.get('q', '')
        context['recommendations'] = []

        # ✅ Recommendation logic
        if self.request.user.is_authenticated:
            try:
                preferred = self.request.user.preference.preferred_categories.all()
                if preferred.exists():
                    read_ids = ReadingHistory.objects.filter(
                        user=self.request.user
                    ).values_list('article_id', flat=True)

                    recommended = Article.objects.filter(
                        category__in=preferred
                    ).exclude(id__in=read_ids).distinct().order_by('-published_date')[:5]

                    context['recommendations'] = recommended
            except UserPreference.DoesNotExist:
                pass

        return context

# -----------------------------
# ARTICLE DETAIL VIEW
# -----------------------------
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # ✅ Track reading history
        if self.request.user.is_authenticated:
            ReadingHistory.objects.get_or_create(
                user=self.request.user,
                article=obj
            )
        return obj
