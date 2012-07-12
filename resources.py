from djangorestframework.resources import ModelResource as RestModelResource

from django.contrib.contenttypes.models import ContentType
from wq.db.annotate.models import Annotation, AnnotatedModel, AnnotationType

_resource_map = {}

class ModelResource(RestModelResource):

    def get_fields(self, obj):
        fields = []
        for f in self.model._meta.fields:
            if f.rel is None:
                fields.append(f.name)
            else:
                if type(f.rel).__name__ == 'OneToOneRel':
                    pass
                elif f.rel.to == ContentType:
                    fields.append('for')
                else:
                    fields.append(f.name + '_id')
        if (self.view.method in ("PUT", "POST") and issubclass(self.model, AnnotatedModel)):
            fields.append("updates")
        return fields

    def updates(self, instance):
        ct = ContentType.objects.get_for_model(instance)
        idname = get_id(ct) + '_id'
        annots = Annotation.objects.filter(content_type=ct, object_id=instance.pk)
        updates = []
        for a in annots:
            updates.append({'id': a.pk,
                            'annotationtype_id': a.type.pk,
                            idname:    instance.pk,
                            'value':   a.value})
        return {'annotation': updates}

    def validate_request(self, data, files=None):
        extra_fields = ()
        if issubclass(self.model, AnnotatedModel):
            ct = ContentType.objects.get_for_model(self.model)
            atypes = AnnotationType.objects.filter(contenttype=ct)
            extra_fields = ('annotation-%s' % at.pk for at in atypes)
        data = self._validate(data, files, extra_fields)
        return data

    def serialize_model(self, instance):
        data = super(ModelResource, self).serialize_model(instance)
        for f in self.model._meta.fields:
            if f.rel is not None and f.rel.to == ContentType:
                data['for'] = get_id(getattr(instance, f.name))
        return data

class AnnotationResource(ModelResource):
    model = Annotation
    def serialize_model(self, instance):
        idname = get_id(instance.content_type) + '_id'
        return {'id': instance.pk,
                'annotationtype_id': instance.type.pk,
                idname:    instance.object_id,
                'value':   instance.value}

def register(model_class, resource_class):
    _resource_map[model_class] = resource_class

def get_for_model(model_class):
    if model_class in _resource_map:
        return _resource_map[model_class]
    else:
        return type(model_class.__name__ + "Resource", (ModelResource,),
                    {'model': model_class})

def get_id(contenttype):
    if contenttype is None:
        return 'NONE'
    return contenttype.name.replace(' ', '')

register(Annotation, AnnotationResource)