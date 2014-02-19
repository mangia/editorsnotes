# -*- coding: utf-8 -*- 

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from editorsnotes.main.models import Topic, TopicNode

from .. import forms
from common import BaseAdminView

class TopicAdminView(BaseAdminView):
    model = Topic
    form_class = forms.TopicForm
    formset_classes = (
        forms.topics.AlternateNameFormset,
        #forms.topics.TopicSummaryFormset,
        # forms.TopicAssignmentFormset,
        forms.topics.CitationFormset,
    )
    template_name = 'topic_admin.html'
    def get_object(self, topic_node_id=None):
        return topic_node_id and get_object_or_404(
            Topic, topic_node_id=topic_node_id, project__slug=self.project.slug)
    def get_breadcrumb(self):
        breadcrumbs = (
            (self.project.name, self.project.get_absolute_url()),
            ('Topics', reverse('all_topics_view',
                               kwargs={'project_slug': self.project.slug})),
        )
        if self.object is None:
            breadcrumbs += (
                ('Add', None),
            )
        else:
            breadcrumbs += (
                (self.object.as_text(), self.object.get_absolute_url()),
                ('Edit', None)
            )
        return breadcrumbs
    def set_additional_object_properties(self, obj, form):
        if not obj.id:
            existing_node_id = self.request.GET.get('topic_node')
            if existing_node_id:
                topic_node = get_object_or_404(TopicNode, id=existing_node_id)
            else:
                topic_node = TopicNode.objects.create(
                    _preferred_name=obj.preferred_name,
                    type=form.cleaned_data['topic_type'],
                    creator=self.request.user,
                    last_updater=self.request.user)
            obj.topic_node_id = topic_node.id
            obj.project_id = self.project.id
        return obj
    def save_citation_formset_form(self, form):
        obj = form.save(commit=False)
        if not obj.id:
            obj.content_object = self.object
            obj.creator = self.request.user
        obj.last_updater = self.request.user
        obj.save()
    def save_alternatename_formset_form(self, form):
        obj = form.save(commit=False)
        if not obj.id:
            obj.creator = self.request.user
        obj.topic = self.object
        obj.save()
