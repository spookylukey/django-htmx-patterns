from django.forms.renderers import TemplatesSetting


class BulmaFormRenderer(TemplatesSetting):
    form_template_name = "forms/bulma/div.html"


class BulmaFormMixin:
    default_renderer = BulmaFormRenderer()

    def __init__(self, *args, **kwargs) -> None:
        return super().__init__(*args, label_suffix="", **kwargs)


# Pure currently unused
class PureFormRenderer(TemplatesSetting):
    form_template_name = "forms/pure/div.html"


class PureFormMixin:
    default_renderer = PureFormRenderer()
    template_name_label = "forms/pure/label.html"
