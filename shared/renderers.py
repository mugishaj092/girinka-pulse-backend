"""Standard JSON response renderer for all API responses."""
from rest_framework.renderers import JSONRenderer


class GirinkaJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200
        success = status_code < 400
        if isinstance(data, dict) and "results" in data:
            wrapped = {"success": success, "data": data.get("results"), "message": "OK",
                       "errors": None, "meta": {"count": data.get("count"), "next": data.get("next"), "previous": data.get("previous")}}
        elif not success:
            wrapped = {"success": False, "data": None,
                       "message": data.get("detail", "An error occurred") if isinstance(data, dict) else str(data),
                       "errors": data if isinstance(data, dict) else {"detail": str(data)}, "meta": None}
            if isinstance(data, dict) and "error_code" in data:
                wrapped["error_code"] = data["error_code"]
        else:
            wrapped = {"success": True, "data": data, "message": "OK", "errors": None, "meta": None}
        return super().render(wrapped, accepted_media_type, renderer_context)
