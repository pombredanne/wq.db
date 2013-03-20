from django.contrib.contenttypes.models import ContentType as DjangoContentType
from wq.db.patterns.models import AnnotatedModel, IdentifiedModel, LocatedModel, RelatedModel
from wq.db.patterns.models import RelationshipType

class ContentType(DjangoContentType):
    @property
    def identifier(self):
        return self.name.replace(' ', '')

    @property
    def urlbase(self):
        cls = self.model_class()
        if cls is None:
             return None
        return getattr(cls, 'slug', self.identifier + 's')

    @property
    def is_annotated(self):
        cls = self.model_class()
        return issubclass(cls, AnnotatedModel)

    @property
    def is_identified(self):
        cls = self.model_class()
        return issubclass(cls, IdentifiedModel)

    @property
    def is_located(self):
        cls = self.model_class()
        return issubclass(cls, LocatedModel)
        
    @property
    def is_related(self):
        cls = self.model_class()
        return issubclass(cls, RelatedModel)
        
    # Get foreign keys for this content type
    def get_parents(self):
        cls = self.model_class()
        if cls is None:
            return []
        parents = []
        for f in cls._meta.fields:
            if f.rel is not None and type(f.rel).__name__ == 'ManyToOneRel':
                parents.append(get_ct(f.rel.to))
        return parents

    # Get foreign keys and RelationshipType parents for this content type
    def get_all_parents(self):
        parents = self.get_parents()
        if not self.is_related:
            return parents
        for rtype in RelationshipType.objects.filter(to_type=self):
            ctype = rtype.from_type
            # This is a DjangoContentType, swap for our custom version
            ctype = ContentType.objects.get(pk=ctype.pk)
            parents.append(ctype)
        return parents

    def get_children(self, include_rels=False):
        cls = self.model_class()
        if cls is None:
            return [];
        rels = cls._meta.get_all_related_objects()
        if include_rels:
            return [(get_ct(rel.model), rel) for rel in rels]
        else:
            return [get_ct(rel.model) for rel in rels]

    def get_all_children(self):
        children = self.get_children()
        if not self.is_related:
            return children
        for rtype in RelationshipType.objects.filter(from_type=self):
            ctype = rtype.to_type
            # This is a DjangoContentType, swap for our custom version
            ctype = ContentType.objects.get(pk=ctype.pk)
            children.append(ctype)
        return children

    class Meta:
        proxy = True

def get_ct(model):
    return ContentType.objects.get_for_model(model)

def get_object_id(instance):
    ct = get_ct(instance)
    if ct.is_identified:
        ids = instance.identifiers.filter(is_primary=True)
        if len(ids) > 0:
            return ids[0].slug
    return instance.pk

class MultiQuerySet(object):
    querysets = []
    def __init__(self, *args, **kwargs):
        self.querysets = args

    def __getitem__(self, index):
        if isinstance(index, slice):
            multi = True
        else:
            multi = False
            index = slice(index, index + 1)
        
        result = []
        for qs in self.querysets:
             if index.start < qs.count():
                 result.extend(qs[index])
             index = slice(index.start - qs.count(),
                           index.stop  - qs.count())
             if index.start < 0:
                 if index.stop < 0:
                     break
                 index = slice(0, index.stop)
        if multi:
            return (item for item in result)
        else:
            return result[0]

    def __iter__(self):
        for qs in self.querysets:
            for item in qs:
                yield item

    def count(self):
        result = 0
        for qs in self.querysets:
            result += qs.count()
        return result