
import django_filters
from .models import Cow


class CowFilter(django_filters.FilterSet):
    breed         = django_filters.CharFilter(lookup_expr="iexact")
    health_status = django_filters.CharFilter(lookup_expr="iexact")
    is_alive      = django_filters.BooleanFilter()
    district      = django_filters.NumberFilter(field_name="district_id")
    beneficiary   = django_filters.NumberFilter(field_name="beneficiary_id")
    risk_min      = django_filters.NumberFilter(field_name="mortality_risk_score", lookup_expr="gte")
    risk_max      = django_filters.NumberFilter(field_name="mortality_risk_score", lookup_expr="lte")

    class Meta:
        model = Cow
        fields = ["breed","health_status","is_alive","district","beneficiary"]
