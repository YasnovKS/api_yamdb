from rest_framework.validators import UniqueTogetherValidator


class TitleUniqueTogetherValidator(UniqueTogetherValidator):
    related_querysets = {}

    def __init__(self, queryset, fields, related_querysets, message=None):
        super().__init__(queryset, fields, message)
        self.related_querysets = related_querysets

    def filter_queryset(self, attrs, queryset, serializer):
        """
        Filter the queryset to all instances matching the given attributes.
        """
        # field names => field sources
        sources = [
            serializer.fields[field_name].source for field_name in self.fields
        ]

        exclude_from_related = set()

        # If this is an update, then any unprovided field should
        # have it's value set based on the existing instance attribute.
        if serializer.instance is not None:
            for source in sources:
                if source not in attrs:
                    attrs[source] = getattr(serializer.instance, source)
                    # exclude field since its value already taken from instance
                    exclude_from_related.add(source)

        # Determine the filter keyword arguments and filter the queryset.
        filter_kwargs = {source: attrs[source] for source in sources}

        updated_filter_kwargs = {}
        for arg, kwargs in filter_kwargs.items():
            # if for field there is related queryset and it is not excluded,
            # retrieve related model and use it to filter queryset
            if (
                arg in self.related_querysets
                and arg not in exclude_from_related
            ):
                kwargs = filter_kwargs.get(arg)
                related_instance = self.related_querysets[arg].get(**kwargs)
                updated_filter_kwargs[arg] = related_instance
            else:
                updated_filter_kwargs[arg] = kwargs

        qs = queryset.filter(**updated_filter_kwargs)
        return qs
