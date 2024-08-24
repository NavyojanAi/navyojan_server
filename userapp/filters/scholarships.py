import django_filters
from django.utils import timezone
from userapp.models import ScholarshipData

class ScholarshipDataFilter(django_filters.FilterSet):
    category_name = django_filters.CharFilter(field_name='categories__name', lookup_expr='iexact')
    published_after = django_filters.DateFilter(field_name='published_on', lookup_expr='gte')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = ScholarshipData
        fields = ['category_name', 'published_after', 'amount_min', 'amount_max']
