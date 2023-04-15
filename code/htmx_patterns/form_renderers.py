from django.forms.renderers import TemplatesSetting


class BulmaFormRenderer(TemplatesSetting):
    form_template_name = "forms/bulma/div.html"
    single_field_row_template = "forms/bulma/field_row.html"


class BulmaFormMixin:
    default_renderer = BulmaFormRenderer()
    do_htmx_validation = False  # Set to True in subclasses

    def __init__(self, *args, **kwargs) -> None:
        return super().__init__(*args, label_suffix="", **kwargs)

    def get_context(self, *args, **kwargs):
        return super().get_context(*args, **kwargs) | {
            "do_htmx_validation": self.do_htmx_validation,
            "single_field_row_template": self.renderer.single_field_row_template,
        }


# Pure currently unused
class PureFormRenderer(TemplatesSetting):
    form_template_name = "forms/pure/div.html"


class PureFormMixin:
    default_renderer = PureFormRenderer()
    template_name_label = "forms/pure/label.html"
