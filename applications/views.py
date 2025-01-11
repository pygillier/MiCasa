from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext as _
from .models import Application
from .forms import ApplicationForm


class IndexView(ListView):
    model = Application
    template_name = "applications/index.html"
    context_object_name = "applications"


class HomeView(ListView):
    model = Application
    template_name = "applications/home.html"
    context_object_name = "applications"

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.GET.get("pinned", default="true") == "true":
            print("Got pinned")
            qs = qs.filter(is_pinned=True)

        if self.request.user.is_anonymous:
            return qs.filter(is_public=True)
        else:
            return qs


class ManageAppMixin(ContextMixin):
    extra_context = {"current": "applications"}


class ManageListView(LoginRequiredMixin, ManageAppMixin, ListView):
    model = Application
    template_name = "applications/manage.html"
    context_object_name = "applications"


class CreateApplicationView(LoginRequiredMixin, SuccessMessageMixin, ManageAppMixin, CreateView):
    model = Application
    template_name = "applications/create.html"
    form_class = ApplicationForm

    success_url = reverse_lazy("applications:manage")
    success_message = _("app.manage.success.created %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class UpdateApplicationView(LoginRequiredMixin, SuccessMessageMixin, ManageAppMixin, UpdateView):
    model = Application
    template_name = "applications/update.html"
    form_class = ApplicationForm

    success_url = reverse_lazy("applications:manage")
    success_message = _("app.manage.success.updated %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class DeleteApplicationView(LoginRequiredMixin, SuccessMessageMixin, ManageAppMixin, DeleteView):
    template_name = "applications/delete.html"
    context_object_name = "application"
    model = Application

    success_url = reverse_lazy("applications:manage")
    success_message = _("app.manage.success.deleted %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class ReorderApplicationView(LoginRequiredMixin, TemplateView):
    template_name = "applications/manage/_list.html"

    def post(self, request, *args, **kwargs):
        pks = request.POST.getlist("pk")
        print(pks)
        apps = []

        for position, pk in enumerate(pks):
            app = Application.objects.get(pk=pk)
            app.position = position
            apps.append(app)

        Application.objects.bulk_update(apps, ["position"])

        context = self.get_context_data(**kwargs)
        context["applications"] = Application.objects.all()

        return self.render_to_response(context)
